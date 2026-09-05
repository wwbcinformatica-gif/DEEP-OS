import React, { useState, useRef, useEffect, useCallback } from 'react';

interface TranscriptEntry {
  speaker: string;
  text: string;
  time: string;
}

const VOICES = [
  { id: 'Charon', label: 'Charon', type: 'Masculino (padrao)' },
  { id: 'Puck', label: 'Puck', type: 'Masculino' },
  { id: 'Fenrir', label: 'Fenrir', type: 'Masculino' },
  { id: 'Orus', label: 'Orus', type: 'Masculino' },
  { id: 'Kore', label: 'Kore', type: 'Feminino' },
  { id: 'Leda', label: 'Leda', type: 'Feminino' },
  { id: 'Aoede', label: 'Aoede', type: 'Feminino' },
  { id: 'Zephyr', label: 'Zephyr', type: 'Feminino' },
];

const MIC_WORKLET = `
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

const PLAYBACK_WORKLET = `
class PlaybackProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this._ringSize = 192000;
    this._ring = new Float32Array(this._ringSize);
    this._writePos = 0;
    this._readPos = 0;
    this._available = 0;
    this._prebuf = 12000;
    this._started = false;
    this._lastChunkHash = 0;
    this._dupCount = 0;
    this.port.onmessage = (e) => {
      if (e.data && e.data.type === 'clear') {
        this._writePos = 0; this._readPos = 0; this._available = 0;
        this._started = false; this._lastChunkHash = 0; this._dupCount = 0;
        return;
      }
      const pcm16 = new Int16Array(e.data);
      let hash = 0;
      const step = Math.max(1, Math.floor(pcm16.length / 16));
      for (let i = 0; i < pcm16.length; i += step) hash = ((hash << 5) - hash + pcm16[i]) | 0;
      if (hash !== 0 && hash === this._lastChunkHash) {
        this._dupCount++;
        if (this._dupCount > 2) return;
      } else {
        this._dupCount = 0;
      }
      this._lastChunkHash = hash;
      for (let i = 0; i < pcm16.length; i++) {
        this._ring[this._writePos] = pcm16[i] / 32768;
        this._writePos = (this._writePos + 1) % this._ringSize;
        if (this._available < this._ringSize) this._available++;
        else this._readPos = (this._readPos + 1) % this._ringSize;
      }
      if (!this._started && this._available >= this._prebuf) this._started = true;
    };
  }
  process(inputs, outputs) {
    const output = outputs[0];
    if (!output || !output[0]) return true;
    const ch = output[0];
    if (!this._started) { for (let i = 0; i < ch.length; i++) ch[i] = 0; return true; }
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
  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${proto}//${host}:${window.location.port || (window.location.protocol === 'https:' ? '443' : '80')}/ws/voice`;
}

const CharonPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'chat' | 'config'>('chat');
  const [transcripts, setTranscripts] = useState<TranscriptEntry[]>([]);
  const [activityLog, setActivityLog] = useState<TranscriptEntry[]>([]);
  const [inputText, setInputText] = useState('');
  const [voiceName, setVoiceName] = useState('Charon');
  const [userName, setUserName] = useState('');
  const [assistantName, setAssistantName] = useState('DEEP-OS');
  const [accentColor, setAccentColor] = useState('#b478ff');
  const [apiKey, setApiKey] = useState('');
  const [contextFilter, setContextFilter] = useState('');
  const [voiceStatus, setVoiceStatus] = useState<string>('idle');
  const [isCharonActive, setIsCharonActive] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [textareaHeight, setTextareaHeight] = useState(60);
  const textareaHeightRef = useRef(60);
  const [rightPanelWidth, setRightPanelWidth] = useState(340);
  const rightPanelWidthRef = useRef(340);

  const listRef = useRef<HTMLDivElement>(null);
  const rightListRef = useRef<HTMLDivElement>(null);
  const activityRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const micCtxRef = useRef<AudioContext | null>(null);
  const playCtxRef = useRef<AudioContext | null>(null);
  const micNodeRef = useRef<AudioWorkletNode | null>(null);
  const playNodeRef = useRef<AudioWorkletNode | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const startedRef = useRef(false);
  const lastSendTimeRef = useRef<number>(0);
  const lastAudioHashRef = useRef(0);
  const dupCountRef = useRef(0);
  const audioBufRef = useRef<Int16Array[]>([]);
  const audioFlushRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const connectVoiceRef = useRef<() => void>(() => {});
  const manualDisconnectRef = useRef(false);
  const voiceNameRef = useRef('Charon');
  const assistantNameRef = useRef('DEEP-OS');
  const userNameRef = useRef('');
  const contextFilterRef = useRef('');

  useEffect(() => {
    const savedKey = localStorage.getItem('saas_api_key') || '';
    const savedVoice = localStorage.getItem('charon_voice') || 'Charon';
    const savedFilter = localStorage.getItem('charon_context_filter') || '';
    const savedHeight = parseInt(localStorage.getItem('charon_textarea_height') || '60');
    const savedWidth = parseInt(localStorage.getItem('charon_right_panel_width') || '340');
    setApiKey(savedKey);
    setVoiceName(savedVoice);
    setContextFilter(savedFilter);
    setTextareaHeight(savedHeight);
    textareaHeightRef.current = savedHeight;
    setRightPanelWidth(savedWidth);
    rightPanelWidthRef.current = savedWidth;
    contextFilterRef.current = savedFilter;
    // Carrega identity do backend config.yaml
    fetch('/api/config/identity')
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        if (data) {
          const name = data.assistant_name || 'DEEP-OS';
          const user = data.user_name || '';
          const voice = data.voice || '';
          setAssistantName(name);
          setUserName(user);
          assistantNameRef.current = name;
          userNameRef.current = user;
          localStorage.setItem('charon_assistant_name', name);
          localStorage.setItem('charon_user_name', user);
          if (voice) {
            setVoiceName(voice);
            voiceNameRef.current = voice;
            localStorage.setItem('charon_voice', voice);
          }
        }
      })
      .catch(() => {
        // Fallback para localStorage
        const savedAssistant = localStorage.getItem('charon_assistant_name') || 'DEEP-OS';
        const savedUser = localStorage.getItem('charon_user_name') || '';
        setAssistantName(savedAssistant);
        setUserName(savedUser);
        assistantNameRef.current = savedAssistant;
        userNameRef.current = savedUser;
      });

    // Auto-start: Charon ativa quando a pagina carrega
    // Timeout maior para garantir que os states do localStorage foram carregados
    setTimeout(() => {
      if (!startedRef.current) {
        connectVoiceRef.current();
      }
    }, 300);
  }, []);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: 'smooth' });
    rightListRef.current?.scrollTo({ top: rightListRef.current.scrollHeight, behavior: 'smooth' });
    activityRef.current?.scrollTo({ top: activityRef.current.scrollHeight, behavior: 'smooth' });
  }, [transcripts, activityLog]);

  const now = () => new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });

  const addUserTranscript = useCallback((text: string) => {
    setTranscripts(prev => [...prev, { speaker: 'user', text, time: now() }]);
  }, []);

  const addCharonTranscript = useCallback((text: string) => {
    setTranscripts(prev => [...prev, { speaker: 'charon', text, time: now() }]);
  }, []);

  const addActivity = useCallback((text: string, speaker: string = 'system') => {
    setActivityLog(prev => [...prev, { speaker, text, time: now() }]);
  }, []);

  const renderActivity = (t: TranscriptEntry) => {
    const isWebSearch = t.text.startsWith('web_search:') && t.text.includes('Source:');
    if (!isWebSearch) {
      return (
        <div key={t.time + t.text.slice(0, 20)} style={{ ...s.messageItem, borderLeft: t.speaker === 'tool' ? '2px solid #b478ff' : t.speaker === 'error' ? '2px solid #f44' : '2px solid #0c0', marginLeft: 4 }}>
          <div style={s.messageSpeaker}>
            {t.speaker === 'tool' ? '🔧 TOOL' : t.speaker === 'error' ? '❌ ERRO' : 'SYSTEM'} - {t.time}
          </div>
          <div style={{ ...s.messageText, whiteSpace: 'pre-wrap', wordBreak: 'break-word', overflowWrap: 'break-word', fontFamily: "'Cascadia Code', 'Fira Code', 'Consolas', monospace", fontSize: 11, lineHeight: 1.6 }}>{t.text}</div>
        </div>
      );
    }
    const lines = t.text.split('\n');
    const header = lines[0] || '';
    const query = header.replace('web_search: Search results for: ', '');
    const results: { num: string; title: string; snippet: string; source: string }[] = [];
    let cur: { num: string; title: string; snippet: string; source: string } | null = null;
    for (const line of lines.slice(1)) {
      const numMatch = line.match(/^(\d+)\.\s+(.+)/);
      if (numMatch) {
        if (cur) results.push(cur);
        cur = { num: numMatch[1], title: numMatch[2], snippet: '', source: '' };
      } else if (line.startsWith('Source: ')) {
        if (cur) cur.source = line.replace('Source: ', '');
      } else if (cur && line.trim()) {
        cur.snippet += (cur.snippet ? ' ' : '') + line.trim();
      }
    }
    if (cur) results.push(cur);
    return (
      <div key={t.time + 'ws'} style={{ ...s.messageItem, borderLeft: '2px solid #b478ff', marginLeft: 4, padding: '8px 10px', background: '#1a1a2e', borderRadius: 6, marginBottom: 6 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
          <span style={{ fontSize: 11, color: '#b478ff', fontWeight: 700 }}>🔍 WEB SEARCH</span>
          <span style={{ fontSize: 10, color: '#999' }}>•</span>
          <span style={{ fontSize: 10, color: '#ccc', fontStyle: 'italic' }}>"{query}"</span>
          <span style={{ fontSize: 9, color: '#666', marginLeft: 'auto' }}>{t.time}</span>
        </div>
        {results.map((r) => (
          <div key={r.num} style={{ padding: '6px 8px', marginBottom: 4, background: '#12121f', borderRadius: 4, border: '1px solid #222' }}>
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: 6 }}>
              <span style={{ fontSize: 10, color: '#b478ff', fontWeight: 700, minWidth: 14 }}>{r.num}.</span>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 11, color: '#e0e0e0', fontWeight: 600, lineHeight: 1.3 }}>{r.title}</div>
                {r.snippet && <div style={{ fontSize: 10, color: '#999', marginTop: 2, lineHeight: 1.4 }}>{r.snippet}</div>}
                {r.source && <div style={{ fontSize: 9, color: '#b478ff', marginTop: 3, wordBreak: 'break-all' }}>🔗 {r.source}</div>}
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const setupPlayback = useCallback(async () => {
    if (playCtxRef.current) return;
    const ctx = new AudioContext({ sampleRate: 24000 });
    if (ctx.state === 'suspended') await ctx.resume();
    const blob = new Blob([PLAYBACK_WORKLET], { type: 'application/javascript' });
    const url = URL.createObjectURL(blob);
    await ctx.audioWorklet.addModule(url);
    URL.revokeObjectURL(url);
    const node = new AudioWorkletNode(ctx, 'playback-proc', {
      numberOfInputs: 0, numberOfOutputs: 1, outputChannelCount: [1],
    });
    node.connect(ctx.destination);
    playCtxRef.current = ctx;
    playNodeRef.current = node;
  }, []);

  const connectVoice = useCallback(async () => {
    if (startedRef.current) return;
    startedRef.current = true;
    manualDisconnectRef.current = false;
    setVoiceStatus('connecting');
    setError(null);

    try {
      await setupPlayback();

      // Buffer intermediario: acumula chunks de audio e envia ao worklet a cada 20ms
      audioBufRef.current = [];
      if (audioFlushRef.current) clearInterval(audioFlushRef.current);
      audioFlushRef.current = setInterval(() => {
        const chunks = audioBufRef.current;
        if (chunks.length === 0) return;
        audioBufRef.current = [];
        let totalLen = 0;
        for (const c of chunks) totalLen += c.length;
        const merged = new Int16Array(totalLen);
        let offset = 0;
        for (const c of chunks) { merged.set(c, offset); offset += c.length; }
        if (playNodeRef.current && playCtxRef.current) {
          if (playCtxRef.current.state === 'suspended') playCtxRef.current.resume();
          playNodeRef.current.port.postMessage(merged.buffer, [merged.buffer]);
        }
      }, 20);

      const ws = new WebSocket(getWsUrl());
      wsRef.current = ws;

      ws.onopen = () => {
        ws.send(JSON.stringify({
          type: 'start',
          voice: voiceNameRef.current,
          assistant_name: assistantNameRef.current,
          user_name: userNameRef.current,
        }));
      };

      ws.onmessage = async (e) => {
        if (e.data instanceof Blob) {
          const buf = await e.data.arrayBuffer();
          const bytes = new Uint8Array(buf);
          if (bytes.length >= 2) {
            const pcm16 = new Int16Array(bytes.buffer, bytes.byteOffset, bytes.length / 2);
            let hash = 0;
            const step = Math.max(1, Math.floor(pcm16.length / 16));
            for (let i = 0; i < pcm16.length; i += step) hash = ((hash << 5) - hash + pcm16[i]) | 0;
            if (hash !== 0 && hash === lastAudioHashRef.current) {
              dupCountRef.current++;
              if (dupCountRef.current > 1) return;
            } else {
              dupCountRef.current = 0;
            }
            lastAudioHashRef.current = hash;
            // Buffer intermediario: acumula chunks e envia a cada 20ms
            audioBufRef.current.push(pcm16);
          }
          setVoiceStatus('speaking');
          return;
        }
        try {
          const m = JSON.parse(e.data);
          if (m.type === 'connected') {
            setVoiceStatus('listening');
            setIsCharonActive(true);
          } else if (m.type === 'status') {
            setVoiceStatus('processing');
          } else if (m.type === 'transcript') {
            if (m.speaker === 'user') addUserTranscript(m.text);
            else addCharonTranscript(m.text);
          } else if (m.type === 'tool_result') {
            addActivity(`${m.tool}: ${m.result}`, 'tool');
          } else if (m.type === 'tool_start') {
            addActivity(`Executando: ${m.tool}...`, 'tool');
          } else if (m.type === 'turn_complete') {
            setVoiceStatus('listening');
            if (playNodeRef.current) playNodeRef.current.port.postMessage({ type: 'clear' });
          } else if (m.type === 'error') {
            setError(m.message);
            setVoiceStatus('error');
            addActivity(`Erro: ${m.message}`, 'error');
          }
        } catch {}
      };

      ws.onerror = () => {
        setError('Erro de conexao');
        setVoiceStatus('error');
      };

      ws.onclose = () => {
        if (micNodeRef.current) { micNodeRef.current.disconnect(); micNodeRef.current = null; }
        if (streamRef.current) { streamRef.current.getTracks().forEach(t => t.stop()); streamRef.current = null; }
        if (micCtxRef.current) { try { micCtxRef.current.close(); } catch {} micCtxRef.current = null; }
        if (audioFlushRef.current) { clearInterval(audioFlushRef.current); audioFlushRef.current = null; }
        audioBufRef.current = [];
        wsRef.current = null;
        startedRef.current = false;
        setIsCharonActive(false);
        setVoiceStatus('idle');
        // So reconecta automaticamente se nao foi desconexao manual (queda acidental)
        if (!manualDisconnectRef.current) {
          setTimeout(() => {
            if (!startedRef.current) connectVoice();
          }, 3000);
        }
      };

      await new Promise<void>((resolve, reject) => {
        const orig = ws.onopen;
        ws.onopen = (ev) => { (orig as any)?.(ev); resolve(); };
        ws.onerror = () => reject(new Error('WS error'));
      });

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: { channelCount: 1, sampleRate: 48000, echoCancellation: true, noiseSuppression: true, autoGainControl: true },
      });
      streamRef.current = stream;

      const micCtx = new AudioContext({ sampleRate: 48000 });
      micCtxRef.current = micCtx;

      const blob = new Blob([MIC_WORKLET], { type: 'application/javascript' });
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
          lastSendTimeRef.current = Date.now();
        }
        let sum = 0;
        for (let i = 0; i < pcm16.length; i++) sum += Math.abs(pcm16[i]);
        setAudioLevel(Math.min(1, (sum / pcm16.length / 0x8000) * 3));
      };

      source.connect(node);
      setVoiceStatus('listening');
      setIsCharonActive(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro');
      setVoiceStatus('error');
      startedRef.current = false;
    }
  }, [setupPlayback, addUserTranscript, addCharonTranscript]);

  // Mantem o ref atualizado com a funcao connectVoice mais recente
  useEffect(() => {
    connectVoiceRef.current = connectVoice;
  }, [connectVoice]);

  // Atualiza voiceNameRef quando a voz muda (para WebSocket enviar a nova voz)
  useEffect(() => {
    voiceNameRef.current = voiceName;
  }, [voiceName]);

  const disconnectVoice = useCallback(() => {
    manualDisconnectRef.current = true;
    if (wsRef.current) { wsRef.current.close(); wsRef.current = null; }
    if (micNodeRef.current) { micNodeRef.current.disconnect(); micNodeRef.current = null; }
    if (streamRef.current) { streamRef.current.getTracks().forEach(t => t.stop()); streamRef.current = null; }
    if (micCtxRef.current) { try { micCtxRef.current.close(); } catch {} micCtxRef.current = null; }
    if (audioFlushRef.current) { clearInterval(audioFlushRef.current); audioFlushRef.current = null; }
    audioBufRef.current = [];
    if (playNodeRef.current) { playNodeRef.current.port.postMessage({ type: 'clear' }); }
    startedRef.current = false;
    setIsCharonActive(false);
    setVoiceStatus('idle');
    setAudioLevel(0);
  }, []);

  const toggleCharon = () => {
    if (isCharonActive) {
      disconnectVoice();
    } else {
      connectVoice();
    }
  };

  const sendText = (text: string) => {
    if (!text.trim() || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
    wsRef.current.send(JSON.stringify({ type: 'text', text: text.trim() }));
    addUserTranscript(text.trim());
    setInputText('');
  };

  const handleSend = () => {
    const text = inputText.trim();
    if (!text) return;
    sendText(text);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  const handleSaveVoice = async () => {
    localStorage.setItem('charon_voice', voiceName);
    try {
      await fetch('/api/config/identity', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          assistant_name: assistantName,
          user_name: userName,
          custom_color: '',
          voice: voiceName
        })
      });
      await fetch('/voice/disconnect-all', { method: 'POST' }).catch(() => {});
    } catch (e) {
      console.error('Erro ao salvar voz:', e);
    }
    alert('Voz salva! Aplicada na proxima vez que reiniciar o Charon.');
  };

  const handleSaveApiKey = () => {
    localStorage.setItem('saas_api_key', apiKey);
    alert('Chave API salva!');
  };

  const handleSaveContextFilter = () => {
    localStorage.setItem('charon_context_filter', contextFilter);
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'context_filter', filter: contextFilter }));
    }
    alert('Filtro de contexto salvo!');
  };

const handleSaveIdentity = async () => {
    localStorage.setItem('charon_assistant_name', assistantName);
    localStorage.setItem('charon_user_name', userName);
    
    // Salva no backend config.yaml via API correta
    try {
      await fetch('/api/config/identity', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          assistant_name: assistantName,
          user_name: userName,
          custom_color: '',
          voice: voiceName
        })
      });
      // Forca reconexao do Charon para usar novo identity
      await fetch('/voice/disconnect-all', { method: 'POST' }).catch(() => {});
    } catch (e) {
      console.error('Erro ao salvar identity:', e);
    }
    
    alert('Identidade salva! Aplicada na proxima vez que reiniciar o Charon.');
};

  const statusColor: Record<string, string> = { idle: '#666', connecting: '#ff0', listening: '#0c0', speaking: '#0af', processing: '#f80', error: '#f44' };
  const statusLabel: Record<string, string> = { idle: 'inativo', connecting: 'conectando', listening: 'ouvindo', speaking: 'falando', processing: 'processando', error: 'erro' };
  const sc = statusColor[voiceStatus] || '#666';
  const sl = statusLabel[voiceStatus] || voiceStatus;

  return (
    <div style={s.container}>
      <div style={s.tabs}>
        <button style={{ ...s.tab, ...(activeTab === 'chat' ? s.tabActive : {}) }} onClick={() => setActiveTab('chat')}>
          Chat
        </button>
        <button style={{ ...s.tab, ...(activeTab === 'config' ? s.tabActive : {}) }} onClick={() => setActiveTab('config')}>
          Configuracoes
        </button>
      </div>

      {activeTab === 'chat' && (
        <div style={s.chatLayout}>
          {/* LEFT PANEL — Log de Atividades (pesquisas, tools, relatorios) */}
          <div style={s.leftPanel}>
            <div style={s.charonHeader}>
              <div style={s.charonTitleArea}>
                <span style={s.charonTitle}>ATIVIDADES</span>
                <button style={s.novoBtn} onClick={() => setActivityLog([])}>+ limpar</button>
              </div>
              <div style={s.modelArea}>
                <span style={{ ...s.greenDot, background: sc }} />
                <span style={{ fontSize: 10, color: '#999', marginLeft: 4 }}>{activityLog.length} registros</span>
              </div>
            </div>

            <div ref={activityRef} style={s.chatArea}>
              {activityLog.length === 0 ? (
                <div style={s.emptyState}>
                  Log de atividades vazio. Pesquisas, ferramentas e resultados do Charon aparecerao aqui.
                </div>
              ) : (
                activityLog.map((t, i) => (
                  <div key={i}>{renderActivity(t)}</div>
                ))
              )}
            </div>

            <div style={s.inputSection}>
              <div
                onPointerDown={(e) => {
                  e.preventDefault();
                  const startY = e.clientY;
                  const startH = textareaHeightRef.current;
                  const move = (ev: PointerEvent) => {
                    const delta = startY - ev.clientY;
                    textareaHeightRef.current = Math.max(36, Math.min(400, startH + delta));
                    setTextareaHeight(textareaHeightRef.current);
                    localStorage.setItem('charon_textarea_height', String(textareaHeightRef.current));
                  };
                  const up = () => {
                    window.removeEventListener('pointermove', move);
                    window.removeEventListener('pointerup', up);
                  };
                  window.addEventListener('pointermove', move);
                  window.addEventListener('pointerup', up);
                }}
                style={{ height: 6, cursor: 'ns-resize', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, margin: '2px 0' }}
              >
                <div style={{ width: 40, height: 3, borderRadius: 2, background: '#444' }} />
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                <textarea
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder={isCharonActive ? 'Digite sua mensagem...' : 'Ative o Charon para enviar'}
                  disabled={!isCharonActive}
                  style={{ ...s.textarea, height: textareaHeight, resize: 'none', opacity: isCharonActive ? 1 : 0.5, background: isCharonActive ? '#1a1a2e' : 'rgba(255,255,255,0.03)' }}
                />
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                    <span style={{ width: 6, height: 6, borderRadius: '50%', background: sc, display: 'inline-block' }} />
                    <span style={{ fontSize: 11, color: sc, fontWeight: 600 }}>
                      {isCharonActive ? 'Charon ativo' : 'Charon inativo'}
                    </span>
                    {audioLevel > 0 && (
                      <div style={{ width: 40, height: 4, background: '#222', borderRadius: 2, overflow: 'hidden', marginLeft: 6 }}>
                        <div style={{ width: `${audioLevel * 100}%`, height: '100%', background: audioLevel > 0.6 ? '#f44' : audioLevel > 0.3 ? '#ff0' : '#0c0', transition: 'width 0.05s' }} />
                      </div>
                    )}
                  </div>
                  <button style={s.sendBtn} onClick={handleSend} disabled={!isCharonActive || !inputText.trim()}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <line x1="22" y1="2" x2="11" y2="13" />
                      <polygon points="22 2 15 22 11 13 2 9 22 2" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* DRAG HANDLE — redimensiona painel lateral */}
          <div
            onPointerDown={(e) => {
              e.preventDefault();
              const startX = e.clientX;
              const startW = rightPanelWidthRef.current;
              const move = (ev: PointerEvent) => {
                const delta = startX - ev.clientX;
                rightPanelWidthRef.current = Math.max(240, Math.min(600, startW + delta));
                setRightPanelWidth(rightPanelWidthRef.current);
                localStorage.setItem('charon_right_panel_width', String(rightPanelWidthRef.current));
              };
              const up = () => {
                window.removeEventListener('pointermove', move);
                window.removeEventListener('pointerup', up);
              };
              window.addEventListener('pointermove', move);
              window.addEventListener('pointerup', up);
            }}
            style={{ width: 5, cursor: 'ew-resize', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, background: '#111' }}
          >
            <div style={{ width: 3, height: 40, borderRadius: 2, background: '#333' }} />
          </div>

          {/* RIGHT PANEL — Voz (escuta + respostas do Charon) */}
          <div style={{ ...s.rightPanel, width: rightPanelWidth }}>
            <div style={s.rightHeader} onClick={toggleCharon} role="button">
              <div style={{ display: 'flex', alignItems: 'center', gap: 4, cursor: 'pointer' }}>
                <span style={{ color: '#b478ff', fontSize: 12 }}>&#9889;</span>
                <span style={{ fontSize: 12, color: '#b478ff', fontWeight: 600 }}>Charon</span>
                <span style={{
                  fontSize: 9,
                  padding: '1px 8px',
                  borderRadius: 4,
                  background: `${sc}33`,
                  color: sc,
                  fontWeight: 500,
                  marginLeft: 4,
                }}>
                  {sl}
                </span>
              </div>
            </div>
            <div ref={rightListRef} style={s.messagesList}>
              {transcripts.length === 0 ? (
                <div style={s.emptyState}>
                  {isCharonActive ? 'Ouvindo... fale com o Charon' : 'Clique em Charon para ativar'}
                </div>
              ) : (
                transcripts.map((t, i) => (
                  <div key={i} style={{
                    marginBottom: 10,
                    padding: '8px 10px',
                    borderRadius: 6,
                    background: t.speaker === 'user' ? 'rgba(180,120,255,0.08)' : 'rgba(0,200,0,0.08)',
                    borderLeft: `3px solid ${t.speaker === 'user' ? '#b478ff' : '#0c0'}`,
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginBottom: 4 }}>
                      <span style={{ fontSize: 12 }}>{t.speaker === 'user' ? '👤' : '⚡'}</span>
                      <span style={{ fontSize: 11, fontWeight: 600, color: t.speaker === 'user' ? '#b478ff' : '#0c0' }}>
                        {t.speaker === 'user' ? 'Voce' : 'Charon'}
                      </span>
                      <span style={{ fontSize: 10, color: '#666', marginLeft: 'auto' }}>{t.time}</span>
                    </div>
                    <div style={{ color: '#ccc', whiteSpace: 'pre-wrap', wordBreak: 'break-word', overflowWrap: 'break-word', fontSize: 12, lineHeight: 1.6, fontFamily: "'Cascadia Code', 'Fira Code', 'Consolas', monospace" }}>{t.text}</div>
                  </div>
                ))
              )}
            </div>
            <div style={s.rightFooter}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <span style={{ width: 5, height: 5, borderRadius: '50%', background: sc }} />
                <span style={{ fontSize: 10, color: sc }}>
                  {isCharonActive ? 'Charon ativo' : 'Charon inativo'}
                </span>
              </div>
              <span style={{ fontSize: 10, color: '#999' }}>·</span>
              <span style={{ fontSize: 10, color: '#999' }}>Voz: {voiceName}</span>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'config' && (
        <div style={s.configPanel}>
          <div style={s.configSection}>
            <h3 style={s.sectionTitle}>Identidade</h3>
            <div style={s.configRow}>
              <div style={s.configField}>
                <label style={s.configLabel}>NOME DO ASSISTENTE</label>
                <input type="text" value={assistantName} onChange={(e) => setAssistantName(e.target.value)} style={s.configInput} />
              </div>
              <div style={s.configField}>
                <label style={s.configLabel}>SEU NOME</label>
                <input type="text" value={userName} onChange={(e) => setUserName(e.target.value)} style={s.configInput} />
              </div>
            </div>
            <button style={{ ...s.saveBtn, marginTop: 12 }} onClick={handleSaveIdentity}>Salvar Identidade</button>
          </div>

          <div style={s.configSection}>
            <h3 style={s.sectionTitle}>Aparencia</h3>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={{ width: 32, height: 32, borderRadius: 6, background: accentColor, border: '2px solid #333' }} />
              <input type="text" value={accentColor} onChange={(e) => setAccentColor(e.target.value)} style={{ ...s.configInput, width: 120 }} />
            </div>
          </div>

          <div style={s.configSection}>
            <h3 style={s.sectionTitle}>Voz do Charon</h3>
            <div style={s.voiceGrid}>
              {VOICES.map((voice) => (
                <button
                  key={voice.id}
                  style={{
                    ...s.voiceCard,
                    borderColor: voiceName === voice.id ? accentColor : '#333',
                    background: voiceName === voice.id ? accentColor + '20' : '#1a1a2e',
                  }}
                  onClick={() => setVoiceName(voice.id)}
                >
                  <span style={s.voiceLabel}>{voice.label}</span>
                  <span style={s.voiceType}>{voice.type}</span>
                </button>
              ))}
            </div>
            <button style={{ ...s.saveBtn, marginTop: 12 }} onClick={handleSaveVoice}>Salvar</button>
          </div>

          <div style={s.configSection}>
            <h3 style={s.sectionTitle}>Chave API</h3>
            <div style={s.configField}>
              <label style={s.configLabel}>Google Gemini</label>
              <div style={{ display: 'flex', gap: 8 }}>
                <input type="password" value={apiKey} onChange={(e) => setApiKey(e.target.value)} placeholder="AIza..." style={{ ...s.configInput, flex: 1 }} />
                <button style={s.saveBtn} onClick={handleSaveApiKey}>Salvar</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const s: Record<string, React.CSSProperties> = {
  container: { display: 'flex', flexDirection: 'column', height: '100%', minHeight: 0, color: '#fff', overflow: 'hidden', background: '#0a0a1a' },
  tabs: { display: 'flex', gap: 0, borderBottom: '1px solid #222', flexShrink: 0 },
  tab: { flex: 1, padding: '10px 16px', border: 'none', background: 'transparent', color: '#999', fontSize: 12, cursor: 'pointer', borderBottom: '2px solid transparent' },
  tabActive: { color: '#fff', borderBottom: '2px solid #b478ff', background: 'rgba(180,120,255,0.05)' },
  chatLayout: { display: 'flex', flex: 1, minHeight: 0, overflow: 'hidden' },
  leftPanel: { flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0, overflow: 'hidden' },
  charonHeader: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 16px', borderBottom: '1px solid #222', flexShrink: 0 },
  charonTitleArea: { display: 'flex', alignItems: 'center', gap: 8 },
  charonTitle: { fontSize: 13, fontWeight: 'bold', color: '#b478ff' },
  novoBtn: { fontSize: 10, padding: '2px 8px', background: '#1a1a2e', border: '1px solid #333', borderRadius: 3, color: '#ccc', cursor: 'pointer' },
  modelArea: { display: 'flex', alignItems: 'center', gap: 8 },
  modelSelect: { fontSize: 11, padding: '4px 8px', background: '#1a1a2e', border: '1px solid #333', borderRadius: 3, color: '#ccc' },
  modelSelectWide: { fontSize: 11, padding: '4px 8px', background: '#1a1a2e', border: '1px solid #333', borderRadius: 3, color: '#ccc', minWidth: 160 },
  greenDot: { width: 6, height: 6, borderRadius: '50%', background: '#0c0' },
  chatArea: { flex: 1, overflowY: 'auto', overflowX: 'hidden', padding: 12, minHeight: 0 },
  emptyState: { color: '#666', textAlign: 'center', marginTop: 40, fontSize: 11 },
  inputSection: { padding: '0 16px 8px 16px', flexShrink: 0 },
  textarea: { width: '100%', height: 60, resize: 'none', padding: '8px', borderRadius: 4, border: '1px solid #333', background: '#1a1a2e', color: '#ccc', fontFamily: 'inherit', fontSize: 11, lineHeight: 1.4, boxSizing: 'border-box', outline: 'none' },
  inputButtons: { display: 'flex', justifyContent: 'flex-end', marginTop: 4 },
  sendBtn: { width: 28, height: 28, borderRadius: 4, border: '1px solid #333', background: '#1a1a2e', color: '#ccc', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' },
  statusLine: { display: 'flex', alignItems: 'center', marginTop: 6 },
  messageItem: { marginBottom: 10, padding: '8px 10px', borderRadius: 6, background: 'rgba(255,255,255,0.02)', overflowWrap: 'break-word', wordBreak: 'break-word' as const },
  messageSpeaker: { fontSize: 10, color: '#b478ff', fontWeight: 600, marginBottom: 4 },
  messageText: { color: '#ccc', whiteSpace: 'pre-wrap' as const, wordBreak: 'break-word' as const, overflowWrap: 'break-word' as const, fontSize: 12, lineHeight: 1.6, fontFamily: "'Cascadia Code', 'Fira Code', 'Consolas', monospace" },
  rightPanel: { width: 340, display: 'flex', flexDirection: 'column', flexShrink: 0, borderLeft: '1px solid #222', minHeight: 0, overflow: 'hidden' },
  rightHeader: { padding: '8px 12px', borderBottom: '1px solid #222', flexShrink: 0 },
  messagesList: { flex: 1, overflowY: 'auto', overflowX: 'hidden', padding: 10, minHeight: 0 },
  rightFooter: { padding: '6px 12px', borderTop: '1px solid #222', display: 'flex', alignItems: 'center', gap: 6, flexShrink: 0 },
  configPanel: { flex: 1, overflowY: 'auto', padding: 20 },
  configSection: { background: '#111', border: '1px solid #222', borderRadius: 8, padding: 16, marginBottom: 16 },
  sectionTitle: { fontSize: 14, fontWeight: '600', margin: '0 0 12px 0', color: '#fff' },
  configRow: { display: 'flex', gap: 16 },
  configField: { flex: 1, marginBottom: 12 },
  configLabel: { display: 'block', fontSize: 10, color: '#999', marginBottom: 4, textTransform: 'uppercase' as const },
  configInput: { width: '100%', padding: '8px 12px', background: '#1a1a2e', border: '1px solid #333', borderRadius: 4, color: '#ccc', fontSize: 12, boxSizing: 'border-box', outline: 'none' },
  voiceGrid: { display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 8 },
  voiceCard: { display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2, padding: '10px 8px', border: '2px solid #333', borderRadius: 6, cursor: 'pointer', transition: 'all 0.2s' },
  voiceLabel: { fontSize: 12, fontWeight: '600', color: '#fff' },
  voiceType: { fontSize: 10, color: '#999' },
  saveBtn: { padding: '6px 16px', background: '#b478ff', border: 'none', borderRadius: 4, color: '#fff', fontSize: 11, fontWeight: '600', cursor: 'pointer' },
};

export default CharonPage;
