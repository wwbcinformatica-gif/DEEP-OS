import { useState, useRef, useEffect } from 'react';

const WORKLET_CODE = `
class MicProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this._buf = [];
    this._size = 1024;
  }
  process(inputs) {
    const input = inputs[0];
    if (!input || !input[0]) return true;
    const ch = input[0];
    const ratio = 3;
    const downsampled = Math.floor(ch.length / ratio);
    const pcm16 = new Int16Array(downsampled);
    for (let i = 0; i < downsampled; i++) {
      const idx = i * ratio;
      const avg = (ch[idx] + ch[idx + 1] + ch[idx + 2]) / 3;
      const s = Math.max(-1, Math.min(1, avg));
      pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
    }
    for (let i = 0; i < pcm16.length; i++) this._buf.push(pcm16[i]);
    while (this._buf.length >= this._size) {
      const chunk = new Int16Array(this._size);
      for (let i = 0; i < this._size; i++) chunk[i] = this._buf.shift();
      this.port.postMessage(chunk.buffer, [chunk.buffer]);
    }
    return true;
  }
}
registerProcessor('mic-proc', MicProcessor);
`;

const PLAYBACK_CODE = `
class PlaybackProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this._ringSize = 480000;
    this._ring = new Float32Array(this._ringSize);
    this._writePos = 0;
    this._readPos = 0;
    this._available = 0;
    this._prebuf = 30000;
    this._started = false;
    this.port.onmessage = (e) => {
      if (e.data && e.data.type === 'clear') {
        this._writePos = 0; this._readPos = 0; this._available = 0;
        this._started = false;
        return;
      }
      const pcm16 = new Int16Array(e.data);
      for (let i = 0; i < pcm16.length; i++) {
        this._ring[this._writePos] = pcm16[i] / 32768;
        this._writePos = (this._writePos + 1) % this._ringSize;
        if (this._available < this._ringSize) this._available++;
        else this._readPos = (this._readPos + 1) % this._ringSize;
      }
      if (!this._started && this._available >= this._prebuf) {
        this._started = true;
      }
    };
  }
  process(inputs, outputs) {
    const output = outputs[0];
    if (!output || !output[0]) return true;
    const ch = output[0];
    if (!this._started) {
      for (let i = 0; i < ch.length; i++) ch[i] = 0;
      return true;
    }
    for (let i = 0; i < ch.length; i++) {
      if (this._available > 0) {
        ch[i] = this._ring[this._readPos];
        this._readPos = (this._readPos + 1) % this._ringSize;
        this._available--;
      } else {
        ch[i] = 0;
      }
    }
    return true;
  }
}
registerProcessor('playback-proc', PlaybackProcessor);
`;

function getWsUrl(): string {
  const host = window.location.hostname || 'localhost';
  return `ws://${host}:8001/ws/voice`;
}

interface VoiceHudProps {
  onUserTranscript?: (text: string) => void;
  onJarvisTranscript?: (text: string) => void;
  termOpen?: boolean;
  setTermOpen?: (v: boolean) => void;
  thinkOpen?: boolean;
  setThinkOpen?: (v: boolean) => void;
}

export default function VoiceHud({ onUserTranscript, onJarvisTranscript, termOpen, setTermOpen, thinkOpen, setThinkOpen }: VoiceHudProps) {
  const [status, setStatus] = useState('idle');
  const [audioLevel, setAudioLevel] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const micCtxRef = useRef<AudioContext | null>(null);
  const playCtxRef = useRef<AudioContext | null>(null);
  const micNodeRef = useRef<AudioWorkletNode | null>(null);
  const playNodeRef = useRef<AudioWorkletNode | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const startedRef = useRef(false);
  const onUserRef = useRef(onUserTranscript);
  const onJarvisRef = useRef(onJarvisTranscript);
  onUserRef.current = onUserTranscript;
  onJarvisRef.current = onJarvisTranscript;

  // Setup playback worklet
  useEffect(() => {
    let mounted = true;
    (async () => {
      const ctx = new AudioContext();
      if (ctx.state === 'suspended') await ctx.resume();
      const blob = new Blob([PLAYBACK_CODE], { type: 'application/javascript' });
      const url = URL.createObjectURL(blob);
      await ctx.audioWorklet.addModule(url);
      URL.revokeObjectURL(url);
      if (!mounted) { ctx.close(); return; }
      const node = new AudioWorkletNode(ctx, 'playback-proc', {
        numberOfInputs: 0, numberOfOutputs: 1, outputChannelCount: [1],
      });
      node.connect(ctx.destination);
      playCtxRef.current = ctx;
      playNodeRef.current = node;
    })();
    return () => {
      mounted = false;
      if (playNodeRef.current) { playNodeRef.current.disconnect(); playNodeRef.current = null; }
      if (playCtxRef.current) { playCtxRef.current.close().catch(() => {}); playCtxRef.current = null; }
    };
  }, []);

  // Setup WebSocket + mic
  useEffect(() => {
    if (startedRef.current) return;
    startedRef.current = true;

    let stopped = false;

    const start = async () => {
      try {
        setStatus('connecting');
        setError(null);

        // WebSocket
        const ws = new WebSocket(getWsUrl());
        wsRef.current = ws;

        ws.onopen = () => {
          ws.send(JSON.stringify({ type: 'start', voice: 'Charon' }));
        };

        ws.onmessage = async (e) => {
          if (e.data instanceof Blob) {
            const buf = await e.data.arrayBuffer();
            const bytes = new Uint8Array(buf);
            const pcm16 = new Int16Array(bytes.buffer);
            if (playNodeRef.current && playCtxRef.current) {
              if (playCtxRef.current.state === 'suspended') playCtxRef.current.resume();
              playNodeRef.current.port.postMessage(pcm16.buffer, [pcm16.buffer]);
            }
            setStatus('speaking');
            return;
          }
          try {
            const m = JSON.parse(e.data);
            if (m.type === 'connected') {
              setStatus('listening');
            } else if (m.type === 'transcript') {
              if (m.speaker === 'user') onUserRef.current?.(m.text);
              else onJarvisRef.current?.(m.text);
            } else if (m.type === 'turn_complete') {
              setStatus('listening');
            } else if (m.type === 'error') {
              setError(m.message);
              setStatus('error');
            }
          } catch {}
        };

        ws.onerror = () => {
          setError('Erro de conexao');
          setStatus('error');
        };

        ws.onclose = () => {
          if (!stopped) {
            setStatus('idle');
          }
        };

        // Wait for connection
        await new Promise<void>((resolve, reject) => {
          const orig = ws.onopen;
          ws.onopen = (ev) => {
            (orig as any)?.(ev);
            resolve();
          };
          ws.onerror = (ev) => { reject(new Error('WS error')); };
        });

        // Mic
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: {
            channelCount: 1,
            sampleRate: 48000,
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true,
          },
        });
        streamRef.current = stream;

        const micCtx = new AudioContext({ sampleRate: 48000 });
        micCtxRef.current = micCtx;

        const blob = new Blob([WORKLET_CODE], { type: 'application/javascript' });
        const url = URL.createObjectURL(blob);
        await micCtx.audioWorklet.addModule(url);
        URL.revokeObjectURL(url);

        const source = micCtx.createMediaStreamSource(stream);
        const node = new AudioWorkletNode(micCtx, 'mic-proc', {
          numberOfInputs: 1, numberOfOutputs: 0, channelCount: 1,
        });
        micNodeRef.current = node;

        node.port.onmessage = (ev: MessageEvent) => {
          const pcm16 = new Int16Array(ev.data);
          const bytes = new Uint8Array(pcm16.buffer);
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(bytes);
          }
          // Audio level (use original 48kHz data)
          let sum = 0;
          for (let i = 0; i < pcm16.length; i++) sum += Math.abs(pcm16[i]);
          setAudioLevel(Math.min(1, (sum / pcm16.length / 0x8000) * 3));
        };

        source.connect(node);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erro');
        setStatus('error');
      }
    };

    start();

    return () => {
      stopped = true;
      startedRef.current = false;
      if (wsRef.current) { wsRef.current.close(); wsRef.current = null; }
      if (micNodeRef.current) { micNodeRef.current.disconnect(); micNodeRef.current = null; }
      if (streamRef.current) { streamRef.current.getTracks().forEach(t => t.stop()); streamRef.current = null; }
      if (micCtxRef.current) { micCtxRef.current.close().catch(() => {}); micCtxRef.current = null; }
    };
  }, []);

  const interrupt = () => {
    if (playNodeRef.current) playNodeRef.current.port.postMessage({ type: 'clear' });
    setStatus('listening');
  };

  const color: Record<string, string> = { idle: '#666', connecting: '#ff0', listening: '#0f0', speaking: '#0af', error: '#f44' };
  const label: Record<string, string> = { idle: 'Off', connecting: 'Conectando', listening: 'Ouvindo', speaking: 'Falando', error: 'Erro' };
  const c = color[status] || '#666';
  const l = label[status] || status;

  return (
    <div style={{
      position: 'fixed', bottom: 24, left: '50%', transform: 'translateX(-50%)', zIndex: 9999,
      background: '#000', border: `1px solid ${c}33`, borderRadius: 8,
      padding: '8px 12px', fontFamily: 'monospace', fontSize: 11, color: c,
      display: 'flex', gap: 8, alignItems: 'center',
    }}>
      <div style={{ width: 8, height: 8, borderRadius: '50%', background: c, animation: status === 'listening' ? 'pulse 1s infinite' : 'none' }} />
      <span style={{ minWidth: 55 }}>{l}</span>
      <span style={{ color: '#555', fontSize: 9 }}>Charon</span>
      <div style={{ width: 45, height: 6, background: '#222', borderRadius: 3, overflow: 'hidden' }}>
        <div style={{ width: `${audioLevel * 100}%`, height: '100%', background: audioLevel > 0.6 ? '#f44' : audioLevel > 0.3 ? '#ff0' : '#0f0', transition: 'width 0.05s' }} />
      </div>
      {error && <span style={{ color: '#f44', fontSize: 9 }} title={error}>⚠</span>}
      {setTermOpen && (
        <button onClick={() => setTermOpen(!termOpen)} title="Terminal" style={{ background: termOpen ? 'rgba(255,122,26,0.15)' : 'none', border: `1px solid ${termOpen ? 'var(--accent)' : '#333'}`, color: termOpen ? 'var(--accent)' : '#666', cursor: 'pointer', padding: '2px 8px', borderRadius: 3, fontSize: 10, fontWeight: 700 }}>T</button>
      )}
      {setThinkOpen && (
        <button onClick={() => setThinkOpen(!thinkOpen)} title="Thinking" style={{ background: thinkOpen ? 'rgba(0,170,255,0.15)' : 'none', border: `1px solid ${thinkOpen ? 'var(--accent)' : '#333'}`, color: thinkOpen ? 'var(--accent)' : '#666', cursor: 'pointer', padding: '2px 8px', borderRadius: 3, fontSize: 10, fontWeight: 700 }}>H</button>
      )}
      <button onClick={interrupt} title="Interromper" style={{ background: 'none', border: '1px solid #f443', color: '#f88', cursor: 'pointer', padding: '2px 6px', borderRadius: 3, fontSize: 10 }}>⏹</button>
    </div>
  );
}
