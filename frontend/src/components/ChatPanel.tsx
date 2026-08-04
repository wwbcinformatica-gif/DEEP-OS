import React, { useRef, useEffect, useState, useCallback } from 'react';
import type { Msg, TLog, FileTab, Provider, Mood } from '../lib/constants';
import { API_BASE, MODELS, SETTINGS_KEY } from '../lib/constants';
import MarkdownBlock from './MarkdownBlock';
import PlanMessage from './PlanMessage';
import PermissionDialog from './PermissionDialog';
import ActionCard, { parseActionCard } from './ActionCard';
import StatusIndicator from './StatusIndicator';
import TaskChecklist from './TaskChecklist';

interface ChatPanelProps {
  msgs: Msg[];
  input: string;
  setInput: (v: string) => void;
  loading: boolean;
  stream: string;
  thinking: string;
  thinkOn: boolean;
  thinkOpen: boolean;
  setThinkOpen: (v: boolean) => void;
  toolLogs: TLog[];
  prov: Provider;
  model: string;
  setProv: (v: Provider) => void;
  setModel: (v: string) => void;
  oModels: { value: string; label: string }[];
  orModels: { value: string; label: string }[];
  curTab: FileTab | undefined;
  chatW: number;
  send: (text?: string, images?: string[]) => void;
  newChat: () => void;
  stopGen: () => void;
  analyzeFile: (tab: FileTab) => void;
  voicePreset:
    | 'google-female'
    | 'francisca'
    | 'maria'
    | 'google-male'
    | 'antonio'
    | 'daniel'
    | 'jarvis-cinematic'
    | 'edge-francisca'
    | 'edge-thalita';
  jarvisRate: number;
  voicePitch: number;
  onConfirmPlan: (taskId: string) => void;
  onRejectPlan: (taskId: string) => void;
  pendingToolConfirm: {
    confirmId: string;
    tool: string;
    label: string;
    risk_level?: string;
    params: Record<string, any>;
    taskId: string;
  } | null;
  onApproveTool: () => void;
  onRejectTool: () => void;
  checklistSteps: { label: string; status: string; error?: string }[];
}

export default function ChatPanel({
  msgs,
  input,
  setInput,
  loading,
  stream,
  thinking,
  thinkOn,
  thinkOpen,
  setThinkOpen,
  toolLogs,
  prov,
  model,
  setProv,
  setModel,
  oModels,
  orModels,
  curTab,
  chatW,
  send,
  newChat,
  stopGen,
  analyzeFile,
  voicePreset,
  jarvisRate,
  voicePitch,
  onConfirmPlan,
  onRejectPlan,
  pendingToolConfirm,
  onApproveTool,
  onRejectTool,
  checklistSteps,
}: ChatPanelProps) {
  const chatEnd = useRef<HTMLDivElement>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    chatEnd.current?.scrollIntoView({ behavior: 'smooth' });
  }, [msgs, stream]);

  const [copiedIdx, setCopiedIdx] = useState<number | null>(null);
  const [isListening, setIsListening] = useState(false);
  const [isJarvisVoice, setIsJarvisVoice] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);

  const inputValueRef = useRef('');
  const isSpeakingRef = useRef(false); // previne feedback loop: Jarvis não ouve a si mesmo
  const lastSpokenTimeRef = useRef(0); // previne falar múltiplas vezes a mesma resposta



  // ─── @ Mention & / Command popover ────────────────────────────────
  const [mentionQuery, setMentionQuery] = useState<string | null>(null);
  const [commandQuery, setCommandQuery] = useState<string | null>(null);
  const [showPlusMenu, setShowPlusMenu] = useState(false);
  const [plusMenuFilter, setPlusMenuFilter] = useState('');

  const AGENTS = [
    { id: 'mimo', label: '@mimo', desc: 'MiMo-V2.5 rapido e gratis', icon: 'M' },
    { id: 'coder', label: '@coder', desc: 'Programador especialista', icon: '>' },
    { id: 'writer', label: '@writer', desc: 'Escritor/documentador', icon: '#' },
    { id: 'helper', label: '@helper', desc: 'Assistente geral', icon: '?' },
    { id: 'planner', label: '@planner', desc: 'Planejador estrategico', icon: '~' },
    { id: 'reviewer', label: '@reviewer', desc: 'Revisor de codigo', icon: '!' },
    { id: 'debugger', label: '@debugger', desc: 'Especialista em debugging', icon: '&' },
    { id: 'architect', label: '@architect', desc: 'Arquiteto de software', icon: '^' },
    { id: 'analyst', label: '@analyst', desc: 'Analista de dados', icon: '%' },
  ];

  const SKILLS = [
    { id: 'web_search', label: '@web_search', desc: 'Pesquisar na internet', icon: '*' },
    { id: 'file_picker', label: '@file_picker', desc: 'Navegar arquivos', icon: '/' },
    { id: 'terminal_run', label: '@terminal_run', desc: 'Executar no terminal', icon: '$' },
    { id: 'code_review', label: '@code_review', desc: 'Revisar codigo', icon: '>' },
    { id: 'test_runner', label: '@test_runner', desc: 'Executar testes', icon: 'T' },
    { id: 'doc_generator', label: '@doc_generator', desc: 'Gerar documentacao', icon: 'D' },
    { id: 'refactor', label: '@refactor', desc: 'Refatorar codigo', icon: 'R' },
    { id: 'explore', label: '@explore', desc: 'Explorar projeto', icon: 'E' },
    { id: 'plan', label: '@plan', desc: 'Criar plano de execucao', icon: 'P' },
  ];

  const SLASH_COMMANDS = [
    { cmd: '/goal', desc: 'Definir objetivo de longo prazo', icon: '?' },
    { cmd: '/run', desc: 'Executar comando/scriptId', icon: '>' },
    { cmd: '/clear', desc: 'Limpar contexto atual', icon: 'X' },
    { cmd: '/help', desc: 'Ver comandos disponiveis', icon: '?' },
    { cmd: '/status', desc: 'Status do sistema', icon: 'i' },
    { cmd: '/stop', desc: 'Parar execucao', icon: '!' },
  ];

  const PLUS_ACTIONS = [
    { id: 'goal', label: '/goal', desc: 'Definir objetivo', icon: '?' },
    { id: 'run', label: '/run', desc: 'Executar comando', icon: '>' },
    { id: 'clear', label: '/clear', desc: 'Limpar contexto', icon: 'X' },
    { id: 'web_search', label: '@web_search', desc: 'Pesquisar web', icon: '*' },
    { id: 'terminal', label: '@terminal_run', desc: 'Abrir terminal', icon: '$' },
    { id: 'help', label: '/help', desc: 'Ajuda', icon: '?' },
  ];

  // Parse input for @ and / triggers
  useEffect(() => {
    const val = input;
    const cursorPos = val.length;
    const textBeforeCursor = val.slice(0, cursorPos);

    // Check for @ mention
    const atMatch = textBeforeCursor.match(/@(\w*)$/);
    if (atMatch) {
      setMentionQuery(atMatch[1].toLowerCase());
      setCommandQuery(null);
      setShowPlusMenu(false);
      return;
    }

    // Check for / command (only at start of input)
    const slashMatch = textBeforeCursor.match(/^\/(\w*)$/);
    if (slashMatch) {
      setCommandQuery(slashMatch[1].toLowerCase());
      setMentionQuery(null);
      setShowPlusMenu(false);
      return;
    }

    setMentionQuery(null);
    setCommandQuery(null);
  }, [input]);

  const insertMention = (label: string) => {
    const atIdx = input.lastIndexOf('@');
    if (atIdx >= 0) {
      setInput(input.slice(0, atIdx) + label + ' ');
    }
    setMentionQuery(null);
  };

  const insertCommand = (cmd: string) => {
    setInput(cmd + ' ');
    setCommandQuery(null);
  };

  const filteredMentions = mentionQuery !== null ? [
    ...AGENTS.filter(a => a.id.includes(mentionQuery) || a.label.toLowerCase().includes(mentionQuery)),
    ...SKILLS.filter(s => s.id.includes(mentionQuery) || s.label.toLowerCase().includes(mentionQuery)),
  ] : [];

  const filteredCommands = commandQuery !== null
    ? SLASH_COMMANDS.filter(c => c.cmd.includes('/' + commandQuery))
    : SLASH_COMMANDS;

  const filteredPlusActions = plusMenuFilter
    ? PLUS_ACTIONS.filter(a => a.label.toLowerCase().includes(plusMenuFilter) || a.desc.toLowerCase().includes(plusMenuFilter))
    : PLUS_ACTIONS;

  // Close popovers on click outside
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (!target.closest('[data-popover]')) {
        setShowPlusMenu(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  // Inicializa o SpeechRecognition uma vez
  useEffect(() => {
    const SpeechRecognition =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition ||
      (window as any).mozSpeechRecognition ||
      (window as any).msSpeechRecognition;
    setSpeechSupported(!!SpeechRecognition);
    if (!SpeechRecognition) return;

    const recognition = new SpeechRecognition();
    recognition.lang = 'pt-BR';
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      // Acumula todos os resultados (interim + final) para não cortar frases longas
      let finalTranscript = '';
      for (let i = 0; i < event.results.length; i++) {
        finalTranscript += event.results[i][0].transcript;
      }
      const transcript = finalTranscript.trim();
      if (!transcript) return;
      setInput(transcript);
      inputValueRef.current = transcript;
      // Para de ouvir quando todos os resultados são finais e envia após 4s
      const allFinal = Array.from(event.results).every((r) => r.isFinal);
      if (allFinal) {
        try { recognitionRef.current?.stop(); } catch {}
        setIsListening(false);
        setTimeout(() => {
          if (inputValueRef.current.trim()) {
            handleSend(inputValueRef.current);
          }
        }, 4000);
      }
    };

    recognition.onerror = () => {
      setIsListening(false);
    };
    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;
    return () => {
      try {
        recognition.abort();
      } catch {}
    };
  }, [setInput]);

  const toggleMic = () => {
    const SpeechRecognition =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition ||
      (window as any).mozSpeechRecognition ||
      (window as any).msSpeechRecognition;
    if (!SpeechRecognition) {
      // Não há suporte ao Web Speech API neste navegador
      setSpeechSupported(false);
      setIsListening(false);
      return;
    }

    // Inicializa sob demanda se ainda não houver instância
    if (!recognitionRef.current) {
      try {
        const r = new SpeechRecognition();
        r.lang = 'pt-BR';
        r.continuous = true;
        r.interimResults = true;
        r.onresult = (event: SpeechRecognitionEvent) => {
          let finalTranscript = '';
          for (let i = 0; i < event.results.length; i++) {
            finalTranscript += event.results[i][0].transcript;
          }
          const transcript = finalTranscript.trim();
          if (!transcript) return;
          setInput(transcript);
          inputValueRef.current = transcript;
          const allFinal = Array.from(event.results).every((r) => r.isFinal);
          if (allFinal) {
            try { r.stop(); } catch {}
            setIsListening(false);
            setTimeout(() => {
              if (inputValueRef.current.trim()) {
                handleSend(inputValueRef.current);
              }
            }, 4000);
          }
        };
        r.onerror = () => {
          setIsListening(false);
        };
        r.onend = () => {
          setIsListening(false);
        };
        recognitionRef.current = r;
      } catch (e) {
        console.warn('Falha ao inicializar SpeechRecognition:', e);
        setIsListening(false);
        return;
      }
    }

    const recognition = recognitionRef.current as any;
    if (isListening) {
      try {
        recognition.stop();
      } catch {}
      setIsListening(false);
    } else {
      try {
        recognition.start();
        setIsListening(true);
      } catch (e) {
        console.warn('Erro ao iniciar reconhecimento:', e);
        setIsListening(false);
      }
    }
    // Cancela fala atual se usuário for falar
    try {
      window.speechSynthesis?.cancel?.();
    } catch {}
  };

  const SpeechRecognitionCtor =
    typeof window !== 'undefined'
      ? (window as any).SpeechRecognition ||
        (window as any).webkitSpeechRecognition ||
        (window as any).mozSpeechRecognition ||
        (window as any).msSpeechRecognition
      : undefined;

  // ─── Jarvis Voice (Text-to-Speech) ────────────────────────────

  const lastSpeakId = useRef(0);

  // Extrai apenas o texto limpo para o Jarvis falar
  const stripMarkdown = (text: string): string => {
    return text
      .replace(/```[\s\S]*?```/g, '') // blocos de codigo
      .replace(/`([^`]+)`/g, '$1') // inline code
      .replace(/\*\*([^*]+)\*\*/g, '$1') // **bold**
      .replace(/\*([^*]+)\*/g, '$1') // *italic*
      .replace(/~~([^~]+)~~/g, '$1') // ~~strikethrough~~
      .replace(/#{1,6}\s/g, '') // headings #
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // links [text](url)
      .replace(/>\s/g, '') // blockquotes
      .replace(/[-*+]\s/g, '') // list markers
      .replace(/\n{2,}/g, '. ') // paragrafos
      .trim();
  };

  const EDGE_VOICES: Record<string, string> = {
    'jarvis-cinematic': 'pt-BR-AntonioNeural',
    'edge-francisca': 'pt-BR-FranciscaNeural',
    'edge-thalita': 'pt-BR-ThalitaMultilingualNeural',
  };

  // Fala o texto INTEIRO (sem resumir) - mantem todo o contexto
  const speakText = useCallback(
    async (text: string) => {
      const id = ++lastSpeakId.current;
      try {
        if (!window.speechSynthesis) return;
        window.speechSynthesis.cancel?.();

        const clean = stripMarkdown(text);
        if (!clean) return;

        // Pausa o microfone para não gravar a própria voz (anti-eco)
        isSpeakingRef.current = true;
        if (recognitionRef.current && isListening) {
          try { recognitionRef.current.stop(); } catch {}
          setIsListening(false);
        }

        await new Promise((resolve) => setTimeout(resolve, 0));
        if (id !== lastSpeakId.current) { isSpeakingRef.current = false; return; }

        if (voicePreset in EDGE_VOICES) {
          if (audioRef.current) {
            audioRef.current.pause();
            audioRef.current.currentTime = 0;
            audioRef.current.src = '';
            audioRef.current = null;
          }

          const response = await fetch(`${API_BASE}/api/tts`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: clean, voice: EDGE_VOICES[voicePreset] }),
          });

          if (!response.ok) {
            throw new Error(`TTS backend falhou: ${response.status}`);
          }
          if (id !== lastSpeakId.current) { isSpeakingRef.current = false; return; }

          const mimeType = 'audio/mpeg';
          const mediaSource = new MediaSource();
          const audio = new Audio();
          audioRef.current = audio;
          audio.src = URL.createObjectURL(mediaSource);

          let appendInProgress = false;
          let streamEnded = false;

          mediaSource.addEventListener('sourceopen', async () => {
            const sourceBuffer = mediaSource.addSourceBuffer(mimeType);
            const reader = response.body!.getReader();

            sourceBuffer.addEventListener('updateend', () => {
              appendInProgress = false;
              if (streamEnded && mediaSource.readyState === 'open') {
                mediaSource.endOfStream();
              }
            });

            const pump = async () => {
              try {
                while (true) {
                  const { done, value } = await reader.read();
                  if (done) {
                    streamEnded = true;
                    if (!appendInProgress && mediaSource.readyState === 'open') {
                      mediaSource.endOfStream();
                    }
                    return;
                  }
                  if (id !== lastSpeakId.current) {
                    streamEnded = true;
                    reader.cancel();
                    return;
                  }
                  if (sourceBuffer.updating) {
                    await new Promise((r) =>
                      sourceBuffer.addEventListener('updateend', r, { once: true }),
                    );
                  }
                  if (id !== lastSpeakId.current) return;
                  if (mediaSource.readyState === 'open') {
                    appendInProgress = true;
                    sourceBuffer.appendBuffer(value);
                  }
                }
              } catch (err) {
                console.warn('Erro no streaming TTS:', err);
              }
            };

            pump();

            setTimeout(() => {
              if (id === lastSpeakId.current) {
                audio.play().catch((err) => console.warn('Erro TTS:', err));
              }
            }, 300);
          });

          const finishSpeaking = () => {
            URL.revokeObjectURL(audio.src);
            if (audioRef.current === audio) audioRef.current = null;
            isSpeakingRef.current = false;
          };
          audio.onended = finishSpeaking;
          audio.onerror = finishSpeaking;
          return;
        }

        // Browser speech synthesis path
        const utterance = new SpeechSynthesisUtterance(clean);
        utterance.lang = 'pt-BR';
        utterance.volume = 1.0;
        utterance.rate = 0.5 + (jarvisRate / 100) * 1.5;
        utterance.pitch = 0.5 + (voicePitch / 100) * 1.0;

        const voices = Array.isArray(window.speechSynthesis.getVoices?.())
          ? window.speechSynthesis.getVoices()
          : [];
        const searchMap: Record<string, string[]> = {
          'google-female': ['google', 'female', 'pt'],
          francisca: ['francisca', 'pt'],
          maria: ['maria', 'pt'],
          'google-male': ['google', 'male', 'pt'],
          antonio: ['antonio', 'pt'],
          daniel: ['daniel', 'pt'],
        };
        const keywords = searchMap[voicePreset] || ['pt'];
        const normalized = (voice: SpeechSynthesisVoice) =>
          `${String(voice.name || '').toLowerCase()} ${String(voice.lang || '').toLowerCase()}`;
        const selectedVoice =
          voices.find((v) => keywords.every((keyword) => normalized(v).includes(keyword))) ||
          voices.find((v) =>
            String(v.lang || '')
              .toLowerCase()
              .startsWith('pt'),
          ) ||
          voices[0];
        if (selectedVoice) utterance.voice = selectedVoice;

        utterance.onend = () => {
          isSpeakingRef.current = false;
        };
        utterance.onerror = () => {
          isSpeakingRef.current = false;
        };

        if (id !== lastSpeakId.current) { isSpeakingRef.current = false; return; }
        window.speechSynthesis.speak(utterance);
      } catch (e) {
        console.warn('Falha ao reproduzir Jarvis:', e);
        isSpeakingRef.current = false;
      }
    },
    [jarvisRate, voicePitch, voicePreset, isListening],
  );

  const stopJarvis = () => {
    lastSpeakId.current++; // invalida chamadas speakText em andamento
    isSpeakingRef.current = false;
    window.speechSynthesis.cancel();
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current.src = '';
      audioRef.current = null;
    }
  };

  const toggleJarvis = () => {
    if (isJarvisVoice) {
      stopJarvis();
      setIsJarvisVoice(false);
    } else {
      setIsJarvisVoice(true);
    }
  };

  // Disparo automático quando o stream chegar ao fim
  const prevStreamRef = useRef(stream);
  const lastSpokenMsgRef = useRef(''); // texto da última mensagem falada
  useEffect(() => {
    const finished = prevStreamRef.current && !stream;
    if (finished && isJarvisVoice && stream === '' && msgs.length > 0) {
      const lastBotMsg = [...msgs].reverse().find((m) => m.from === 'bot');
      if (lastBotMsg) {
        const now = Date.now();
        // Só fala se: mensagem é nova (diferente da última falada) OU passaram >3s desde última fala
        const isNewMsg = lastBotMsg.text !== lastSpokenMsgRef.current;
        const cooldownOk = now - lastSpokenTimeRef.current > 3000;
        if (isNewMsg || cooldownOk) {
          lastSpokenMsgRef.current = lastBotMsg.text;
          lastSpokenTimeRef.current = now;
          speakText(lastBotMsg.text);
        }
      }
    }
    prevStreamRef.current = stream;
  }, [stream, isJarvisVoice, msgs, speakText]);

  // Cancela fala ao enviar nova mensagem
  const handleSend = (text?: string) => {
    lastSpeakId.current++;
    lastSpokenMsgRef.current = ''; // reseta guard para próxima resposta ser falada
    try {
      window.speechSynthesis?.cancel?.();
    } catch {}
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current.src = '';
      audioRef.current = null;
    }
    let msg = text ?? input;
    if (imagePreviews.length > 0) {
      const saved = JSON.parse(localStorage.getItem(SETTINGS_KEY) || '{}');
      if (saved.imageInputMode === 'image') {
        send(msg, imagePreviews);
      } else {
        const imgMd = imagePreviews.map((b64) => `![image](${b64})`).join('\n');
        msg = msg ? `${msg}\n\n${imgMd}` : imgMd;
        send(msg);
      }
    } else {
      send(msg);
    }
    setImagePreviews([]);
  };

  // ─── Textarea resize ──────────────────────────────────
  const [textareaH, setTextareaH] = useState(120);
  const dragging = useRef(false);
  const dragStartY = useRef(0);
  const dragStartH = useRef(0);

  const onDragStart = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    dragging.current = true;
    dragStartY.current = e.clientY;
    dragStartH.current = textareaH;
    const onMove = (ev: MouseEvent) => {
      if (!dragging.current) return;
      const delta = dragStartY.current - ev.clientY;
      setTextareaH(Math.max(36, Math.min(400, dragStartH.current + delta)));
    };
    const onUp = () => {
      dragging.current = false;
      window.removeEventListener('mousemove', onMove);
      window.removeEventListener('mouseup', onUp);
    };
    window.addEventListener('mousemove', onMove);
    window.addEventListener('mouseup', onUp);
  }, [textareaH]);

  // ─── Image upload (paste / drag-drop) ──────────────────
  const [imagePreviews, setImagePreviews] = useState<string[]>([]);

  const MAX_IMG_DIM = 1024;
  const MAX_IMG_QUALITY = 0.7;

  const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  };

  const compressImage = async (b64: string): Promise<string> => {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        let { width, height } = img;
        if (width <= MAX_IMG_DIM && height <= MAX_IMG_DIM) {
          resolve(b64);
          return;
        }
        const ratio = Math.min(MAX_IMG_DIM / width, MAX_IMG_DIM / height);
        width = Math.round(width * ratio);
        height = Math.round(height * ratio);
        const c = document.createElement('canvas');
        c.width = width;
        c.height = height;
        const ctx = c.getContext('2d');
        if (!ctx) {
          resolve(b64);
          return;
        }
        ctx.drawImage(img, 0, 0, width, height);
        resolve(c.toDataURL('image/jpeg', MAX_IMG_QUALITY));
      };
      img.onerror = reject;
      img.src = b64;
    });
  };

  const handleImageInput = async (file: File) => {
    const b64 = await fileToBase64(file);
    const compressed = await compressImage(b64);
    setImagePreviews((prev) => [...prev, compressed]);
  };

  const handlePaste = async (e: React.ClipboardEvent) => {
    const items = Array.from(e.clipboardData.items);
    const imageItems = items.filter((item) => item.type.indexOf('image') !== -1);
    if (imageItems.length === 0) return;
    e.preventDefault();
    for (const item of imageItems) {
      const file = item.getAsFile();
      if (!file) continue;
      await handleImageInput(file);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    const files = Array.from(e.dataTransfer.files);
    const imageFiles = files.filter((f) => f.type.indexOf('image') !== -1);
    for (const file of imageFiles) {
      await handleImageInput(file);
    }
  };

  // ─── Plan pending detection ──────────────────────────────
  const pendingPlan = msgs.find((m) => m.planData && m.planStatus === 'pending');

  // ─── Modelos ────────────────────────────────────────────

  const loadedModels =
    prov === 'ollama' && oModels.length
      ? oModels
      : prov === 'openrouter' && orModels.length
        ? orModels
        : MODELS[prov] || [];

  const models = loadedModels.some((m) => m.value === model)
    ? loadedModels
    : [{ value: model, label: model }, ...loadedModels];

  return (
    <div
      style={{
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        background: 'var(--bg)',
      }}
    >
      {/* header */}
      <div className="panel-header">
        <span className="panel-title" style={{ color: 'var(--pink)' }}>
          CHAT
        </span>
        <div style={{ display: 'flex', gap: '4px' }}>
          {loading && (
            <button className="btn btn-red" onClick={stopGen}>
              ■ stop
            </button>
          )}
          <button className="btn" onClick={newChat}>
            + novo
          </button>
        </div>
      </div>

      {/* provider / model row */}
      <div
        style={{
          display: 'flex',
          gap: '4px',
          padding: '5px 12px',
          borderBottom: '1px solid var(--line)',
        }}
      >
        <select
          value={prov}
          onChange={(e) => {
            const p = e.target.value as Provider;
            setProv(p);
            const ms = MODELS[p];
            if (ms?.length) setModel(ms[0].value);
          }}
          className="select-input"
          style={{ flex: 1, padding: '3px 5px', fontSize: '11px' }}
        >
          {['ollama', 'openclaude', 'opencode', 'groq', 'openrouter', 'openai', 'gemini', 'mimo'].map(
            (p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ),
          )}
        </select>
        <select
          value={model}
          onChange={(e) => setModel(e.target.value)}
          className="select-input"
          style={{ flex: 2, padding: '3px 5px', fontSize: '11px' }}
        >
          {models.map((m) => (
            <option key={m.value} value={m.value}>
              {m.label}
            </option>
          ))}
        </select>
        <div style={{ alignSelf: 'center', flexShrink: 0 }}>
          <StatusIndicator provider={prov} />
        </div>
      </div>

      {/* messages */}
      <div
        style={{
          flex: 1,
          padding: '12px',
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column',
          gap: '10px',
        }}
      >
        {msgs.map((m, i) => (
          <div
            key={i}
            style={{
              display: 'flex',
              flexDirection: m.from === 'bot' ? 'column' : 'row',
              gap: '8px',
              alignItems: m.from === 'bot' ? 'flex-start' : 'flex-start',
              justifyContent: m.from === 'user' ? 'flex-end' : 'flex-start',
              width: '100%',
            }}
          >
            {m.from === 'bot' && (
              <div
                style={{
                  width: 24,
                  height: 24,
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  background: 'var(--accent)',
                  color: 'var(--selection-fg)',
                  flexShrink: 0,
                  fontWeight: 700,
                  fontSize: '9px',
                  letterSpacing: '-0.3px',
                }}
              >
                OC
              </div>
            )}
            <div
              style={{
                position: m.from === 'bot' ? 'relative' : 'static',
                maxWidth: m.from === 'bot' ? '100%' : '85%',
                padding: m.planData ? '0' : '4px 8px',
                paddingTop: m.from === 'bot' && !m.planData ? '20px' : undefined,
                borderRadius: '4px',
                display: 'flex',
                flexDirection: 'column',
                gap: '4px',
                background: 'transparent',
                border: 'none',
              }}
            >
              {m.permissionData ? (
                <PermissionDialog
                  title={m.permissionData.title}
                  description={m.permissionData.description}
                  patterns={m.permissionData.patterns}
                  onAllowOnce={() => handleSend(`/allow-once ${m.permissionData!.permissionId}`)}
                  onAllowAlways={() => handleSend(`/allow-always ${m.permissionData!.permissionId}`)}
                  onReject={() => handleSend(`/reject ${m.permissionData!.permissionId}`)}
                />
              ) : m.planData ? (
                <PlanMessage msg={m} onConfirm={onConfirmPlan} onReject={onRejectPlan} />
              ) : (() => {
                const actionCardData = parseActionCard(m.text);
                if (actionCardData) {
                  return (
                    <ActionCard
                      data={actionCardData}
                      onAction={(action) => handleSend(action)}
                    />
                  );
                }
                return (
                  <>
                    <MarkdownBlock text={m.text} />
                    {m.isLoopError && (
                    <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
                      <button
                        onClick={() => handleSend('continue')}
                        style={{
                          padding: '6px 14px',
                          border: 'none',
                          borderRadius: '4px',
                          background: 'var(--accent)',
                          color: 'var(--selection-fg)',
                          cursor: 'pointer',
                          fontWeight: 600,
                          fontSize: '12px',
                          fontFamily: 'inherit',
                        }}
                      >
                        ▶ Continuar
                      </button>
                      <button
                        onClick={newChat}
                        style={{
                          padding: '6px 14px',
                          border: '1px solid var(--line)',
                          borderRadius: '4px',
                          background: 'transparent',
                          color: 'var(--muted)',
                          cursor: 'pointer',
                          fontWeight: 600,
                          fontSize: '12px',
                          fontFamily: 'inherit',
                        }}
                      >
                        + Novo Chat
                      </button>
                    </div>
                  )}
                  {m.images && m.images.length > 0 && (
                    <div
                      style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '6px' }}
                    >
                      {m.images.map((img, idx) => (
                        <img
                          key={idx}
                          src={img.startsWith('data:') ? img : `data:image/jpeg;base64,${img}`}
                          style={{
                            maxWidth: 240,
                            maxHeight: 240,
                            borderRadius: '4px',
                            objectFit: 'contain',
                            border: '1px solid var(--line)',
                          }}
                          alt={`image-${idx}`}
                        />
                      ))}
                    </div>
                  )}
                </>
                );
              })()}
              {m.time && (
                <span style={{ fontSize: '10px', color: 'var(--muted)', alignSelf: 'flex-end' }}>
                  {typeof m.time === 'number'
                    ? new Date(m.time).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
                    : m.time}
                </span>
              )}
              {m.from === 'bot' && (
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(m.text);
                    setCopiedIdx(i);
                    setTimeout(() => setCopiedIdx(null), 2000);
                  }}
                  style={{
                    position: 'absolute',
                    top: '4px',
                    right: '4px',
                    border: '1px solid var(--line)',
                    borderRadius: '3px',
                    background: 'var(--bg)',
                    color: 'var(--muted)',
                    cursor: 'pointer',
                    fontSize: '9px',
                    fontFamily: 'var(--font-ui)',
                    padding: '1px 5px',
                    lineHeight: '1.4',
                    transition: 'color 0.15s',
                  }}
                >
                  {copiedIdx === i ? 'Copiado! ✓' : 'copiar'}
                </button>
              )}
            </div>
            {m.from === 'user' && (
              <div
                style={{
                  width: 24,
                  height: 24,
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  background: 'var(--blue)',
                  color: 'var(--selection-fg)',
                  flexShrink: 0,
                  fontWeight: 700,
                  fontSize: '10px',
                }}
              >
                U
              </div>
            )}
          </div>
        ))}

        {/* Texto streaming em tempo real */}
        {loading && stream && (
          <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-start', width: '100%' }}>
            <div style={{ width: 24, height: 24, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--accent)', color: 'var(--selection-fg)', flexShrink: 0, fontWeight: 700, fontSize: '9px' }}>
              OC
            </div>
            <div style={{
              flex: 1,
              fontSize: '13px',
              lineHeight: 1.5,
              color: '#cccccc',
              padding: '6px 0',
              whiteSpace: 'pre-wrap' as const,
              fontFamily: 'var(--font-mono), "Cascadia Code", "Fira Code", Consolas, monospace',
              fontWeight: 400,
            }}>
              {stream}
              {stream.startsWith('>') && <span style={{ animation: 'blink 0.8s step-end infinite', color: '#808080' }}> ...</span>}
              {!stream.startsWith('>') && <span style={{ animation: 'blink 0.8s step-end infinite', color: 'var(--accent)' }}>|</span>}
            </div>
          </div>
        )}

        {/* Task Checklist - sequencia de tarefas como no VS Code */}
        {loading && checklistSteps.length > 0 && (
          <div style={{ width: '100%', paddingLeft: 32 }}>
            <TaskChecklist steps={checklistSteps} />
          </div>
        )}

        {/* Bolinhas de processo - dots animados quando carregando sem stream */}
        {loading && !stream && (
          <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-start', width: '100%' }}>
            <div style={{ width: 24, height: 24, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--accent)', color: 'var(--selection-fg)', flexShrink: 0, fontWeight: 700, fontSize: '9px' }}>
              OC
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 4, padding: '8px 12px', background: 'var(--bg-2)', borderRadius: '8px', border: '1px solid var(--line)' }}>
              {[0, 1, 2].map((i) => (
                <span key={i} style={{
                  width: 6, height: 6, borderRadius: '50%',
                  background: 'var(--accent)',
                  animation: `dotPulse 1.4s ease-in-out infinite`,
                  animationDelay: `${i * 0.2}s`,
                }} />
              ))}
              <span style={{ fontSize: '10px', color: 'var(--muted)', marginLeft: 4 }}>
                {thinkOn ? 'pensando...' : 'processando...'}
              </span>
            </div>
          </div>
        )}

        <div ref={chatEnd} />
      </div>

      {/* input */}
      <div style={{ padding: '10px 12px', borderTop: '1px solid var(--line)' }}>
        {pendingPlan && (
          <div
            style={{
              display: 'flex',
              gap: '6px',
              marginBottom: '8px',
              padding: '8px 10px',
              borderRadius: '4px',
              background: 'var(--bg-2)',
              border: '1px solid var(--line)',
              alignItems: 'center',
            }}
          >
            <span
              style={{
                flex: 1,
                fontSize: '11px',
                color: 'var(--muted)',
                fontFamily: 'var(--font-ui)',
              }}
            >
              Plano pendente — {pendingPlan.planData?.steps?.length || 0} etapa(s)
            </span>
            <button
              onClick={() => onConfirmPlan(pendingPlan.planTaskId || '')}
              style={{
                padding: '6px 14px',
                border: 'none',
                borderRadius: '4px',
                background: 'var(--accent)',
                color: 'var(--selection-fg)',
                cursor: 'pointer',
                fontWeight: 600,
                fontSize: '11px',
                fontFamily: 'inherit',
              }}
            >
              ✓ Aceitar
            </button>
            <button
              onClick={() => onRejectPlan(pendingPlan.planTaskId || '')}
              style={{
                padding: '6px 14px',
                border: '1px solid var(--line)',
                borderRadius: '4px',
                background: 'transparent',
                color: 'var(--muted)',
                cursor: 'pointer',
                fontWeight: 600,
                fontSize: '11px',
                fontFamily: 'inherit',
              }}
            >
              ✕ Rejeitar
            </button>
          </div>
        )}

        {pendingToolConfirm && (
          <div
            style={{
              display: 'flex',
              gap: '6px',
              marginBottom: '8px',
              padding: '8px 10px',
              borderRadius: '4px',
              background: pendingToolConfirm.risk_level === 'critical' ? 'rgba(239,68,68,0.1)' : 'var(--accent-soft)',
              border: `1px solid ${pendingToolConfirm.risk_level === 'critical' ? 'rgba(239,68,68,0.4)' : 'var(--accent-line)'}`,
              alignItems: 'center',
            }}
          >
            <span style={{ fontSize: '13px', flexShrink: 0 }}>
              {pendingToolConfirm.risk_level === 'critical' ? '🔴' : '⚠️'}
            </span>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--ink)', fontFamily: 'var(--font-ui)' }}>
                {pendingToolConfirm.risk_level === 'critical' ? 'RISCO CRITICO' : 'Confirmacao'}
                {pendingToolConfirm.tool && <span style={{ fontWeight: 400, color: 'var(--muted)', marginLeft: 4 }}>({pendingToolConfirm.tool})</span>}
              </div>
              <div style={{ fontSize: '10px', color: 'var(--muted)', fontFamily: 'var(--font-ui)', marginTop: '2px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {pendingToolConfirm.label}
              </div>
              {pendingToolConfirm.params && Object.keys(pendingToolConfirm.params).length > 0 && (
                <div style={{ fontSize: '10px', color: 'var(--muted)', fontFamily: 'var(--font-ui)', marginTop: '2px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {Object.entries(pendingToolConfirm.params)
                    .filter(([k]) => k !== 'root')
                    .map(([k, v]) => `${k}: ${typeof v === 'string' ? (v.length > 40 ? v.slice(0, 40) + '...' : v) : JSON.stringify(v)}`)
                    .join(' · ')}
                </div>
              )}
            </div>
            <button
              onClick={onApproveTool}
              style={{
                padding: '6px 14px',
                border: 'none',
                borderRadius: '4px',
                background: 'var(--accent)',
                color: 'var(--selection-fg)',
                cursor: 'pointer',
                fontWeight: 600,
                fontSize: '11px',
                fontFamily: 'inherit',
                flexShrink: 0,
              }}
            >
              ✓ Executar
            </button>
            <button
              onClick={onRejectTool}
              style={{
                padding: '6px 14px',
                border: '1px solid var(--line)',
                borderRadius: '4px',
                background: 'transparent',
                color: 'var(--muted)',
                cursor: 'pointer',
                fontWeight: 600,
                fontSize: '11px',
                fontFamily: 'inherit',
                flexShrink: 0,
              }}
            >
              ✕ Cancelar
            </button>
          </div>
        )}

        {curTab && (
          <button
            onClick={() => analyzeFile(curTab)}
            style={{
              width: '100%',
              textAlign: 'left',
              marginBottom: '8px',
              fontSize: '12px',
              padding: '6px 10px',
              border: '1px solid var(--line)',
              borderRadius: '4px',
              background: 'var(--bg-2)',
              color: 'var(--accent)',
              cursor: 'pointer',
              fontWeight: 600,
              fontFamily: 'inherit',
              transition: 'border-color 0.15s',
            }}
          >
            $ analisar: {curTab.name}
          </button>
        )}

        {imagePreviews.length > 0 && (
          <div
            style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 8, padding: '4px 0' }}
          >
            {imagePreviews.map((img, i) => (
              <div key={i} style={{ position: 'relative' }}>
                <img
                  src={img}
                  alt={`preview ${i}`}
                  style={{
                    width: 60,
                    height: 60,
                    objectFit: 'cover',
                    borderRadius: 4,
                    border: '1px solid var(--line)',
                  }}
                />
                <button
                  onClick={() => setImagePreviews((prev) => prev.filter((_, j) => j !== i))}
                  style={{
                    position: 'absolute',
                    top: -6,
                    right: -6,
                    width: 18,
                    height: 18,
                    borderRadius: '50%',
                    border: '1px solid var(--line)',
                    background: 'var(--bg)',
                    color: 'var(--muted)',
                    cursor: 'pointer',
                    fontSize: 10,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontFamily: 'inherit',
                    padding: 0,
                  }}
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        )}

        <div
          style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          {/* Textarea em cima */}
          <div style={{ width: '100%', position: 'relative' }}>
            {/* @ Mention Popover */}
            {mentionQuery !== null && filteredMentions.length > 0 && (
              <div data-popover style={{
                position: 'absolute',
                bottom: '100%',
                left: 0,
                right: 0,
                marginBottom: 4,
                background: 'var(--bg-2)',
                border: '1px solid var(--line)',
                borderRadius: 6,
                maxHeight: 240,
                overflowY: 'auto',
                zIndex: 100,
                boxShadow: '0 -4px 12px rgba(0,0,0,0.3)',
              }}>
                {filteredMentions.filter(m => AGENTS.some(a => a.id === m.id)).length > 0 && (
                  <div style={{ padding: '6px 10px', fontSize: '10px', color: 'var(--muted)', fontWeight: 600, letterSpacing: '0.5px' }}>
                    AGENTES
                  </div>
                )}
                {filteredMentions.filter(m => AGENTS.some(a => a.id === m.id)).map((item) => (
                  <div key={item.id} onClick={() => insertMention(item.label)} style={{
                    padding: '7px 10px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8,
                    fontSize: '12px', color: 'var(--ink)', fontFamily: 'var(--font-ui)',
                    borderBottom: '1px solid var(--line)',
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = 'var(--accent-soft)'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                  >
                    <span style={{ width: 20, textAlign: 'center', color: 'var(--accent)', fontWeight: 700, fontSize: '11px' }}>{item.icon}</span>
                    <span style={{ fontWeight: 600 }}>{item.label}</span>
                    <span style={{ color: 'var(--muted)', fontSize: '11px', flex: 1 }}>{item.desc}</span>
                  </div>
                ))}
                {filteredMentions.filter(m => SKILLS.some(s => s.id === m.id)).length > 0 && (
                  <div style={{ padding: '6px 10px', fontSize: '10px', color: 'var(--muted)', fontWeight: 600, letterSpacing: '0.5px', borderTop: '1px solid var(--line)' }}>
                    SKILLS
                  </div>
                )}
                {filteredMentions.filter(m => SKILLS.some(s => s.id === m.id)).map((item) => (
                  <div key={item.id} onClick={() => insertMention(item.label)} style={{
                    padding: '7px 10px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8,
                    fontSize: '12px', color: 'var(--ink)', fontFamily: 'var(--font-ui)',
                    borderBottom: '1px solid var(--line)',
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = 'var(--accent-soft)'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                  >
                    <span style={{ width: 20, textAlign: 'center', color: 'var(--teal)', fontWeight: 700, fontSize: '11px' }}>{item.icon}</span>
                    <span style={{ fontWeight: 600 }}>{item.label}</span>
                    <span style={{ color: 'var(--muted)', fontSize: '11px', flex: 1 }}>{item.desc}</span>
                  </div>
                ))}
              </div>
            )}

            {/* / Command Popover */}
            {commandQuery !== null && filteredCommands.length > 0 && (
              <div data-popover style={{
                position: 'absolute',
                bottom: '100%',
                left: 0,
                right: 0,
                marginBottom: 4,
                background: 'var(--bg-2)',
                border: '1px solid var(--line)',
                borderRadius: 6,
                maxHeight: 240,
                overflowY: 'auto',
                zIndex: 100,
                boxShadow: '0 -4px 12px rgba(0,0,0,0.3)',
              }}>
                <div style={{ padding: '6px 10px', fontSize: '10px', color: 'var(--muted)', fontWeight: 600, letterSpacing: '0.5px' }}>
                  COMANDOS
                </div>
                {filteredCommands.map((cmd) => (
                  <div key={cmd.cmd} onClick={() => insertCommand(cmd.cmd)} style={{
                    padding: '7px 10px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8,
                    fontSize: '12px', color: 'var(--ink)', fontFamily: 'var(--font-ui)',
                    borderBottom: '1px solid var(--line)',
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = 'var(--accent-soft)'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                  >
                    <span style={{ width: 20, textAlign: 'center', color: 'var(--accent)', fontWeight: 700, fontSize: '11px' }}>{cmd.icon}</span>
                    <span style={{ fontWeight: 600, color: 'var(--accent)' }}>{cmd.cmd}</span>
                    <span style={{ color: 'var(--muted)', fontSize: '11px', flex: 1 }}>{cmd.desc}</span>
                  </div>
                ))}
              </div>
            )}

            {/* + Quick Actions Popover */}
            {showPlusMenu && (
              <div data-popover style={{
                position: 'absolute',
                bottom: '100%',
                left: 0,
                marginBottom: 4,
                background: 'var(--bg-2)',
                border: '1px solid var(--line)',
                borderRadius: 6,
                width: 220,
                zIndex: 100,
                boxShadow: '0 -4px 12px rgba(0,0,0,0.3)',
              }}>
                <input
                  value={plusMenuFilter}
                  onChange={(e) => setPlusMenuFilter(e.target.value.toLowerCase())}
                  placeholder="Filtrar acoes..."
                  autoFocus
                  style={{
                    width: '100%', padding: '6px 10px', border: 'none', borderBottom: '1px solid var(--line)',
                    background: 'transparent', color: 'var(--ink)', fontSize: '12px', fontFamily: 'var(--font-ui)',
                    outline: 'none', boxSizing: 'border-box',
                  }}
                />
                {filteredPlusActions.map((action) => (
                  <div key={action.id} onClick={() => {
                    setInput(action.label + ' ');
                    setShowPlusMenu(false);
                    setPlusMenuFilter('');
                  }} style={{
                    padding: '7px 10px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8,
                    fontSize: '12px', color: 'var(--ink)', fontFamily: 'var(--font-ui)',
                    borderBottom: '1px solid var(--line)',
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = 'var(--accent-soft)'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                  >
                    <span style={{ width: 20, textAlign: 'center', color: 'var(--accent)', fontWeight: 700, fontSize: '11px' }}>{action.icon}</span>
                    <span style={{ fontWeight: 600 }}>{action.label}</span>
                    <span style={{ color: 'var(--muted)', fontSize: '11px', flex: 1 }}>{action.desc}</span>
                  </div>
                ))}
              </div>
            )}

            <div
              onMouseDown={onDragStart}
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                height: 6,
                cursor: 'ns-resize',
                zIndex: 2,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
              title="Arraste para redimensionar"
            >
              <div style={{ width: 32, height: 2, borderRadius: 1, background: 'var(--line)' }} />
            </div>
            <textarea
              value={input}
              onChange={(e) => { setInput(e.target.value); inputValueRef.current = e.target.value; }}
              onKeyDown={(e) => {
                if (e.key === 'Escape') {
                  setMentionQuery(null);
                  setCommandQuery(null);
                  setShowPlusMenu(false);
                } else if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                } else if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                  if (mentionQuery !== null || commandQuery !== null) {
                    e.preventDefault();
                  }
                }
              }}
              onPaste={handlePaste}
              onDragOver={handleDragOver}
              onDrop={handleDrop}
              onContextMenu={(e) => e.stopPropagation()}
              placeholder="Digite ou use Superwhisper (Ctrl+Espaço) para falar..."
              disabled={false}
              style={{
                width: '100%',
                height: textareaH,
                resize: 'none',
                padding: '10px',
                paddingTop: 12,
                borderRadius: 6,
                border: '1px solid var(--line)',
                background: 'var(--bg)',
                color: 'var(--ink)',
                fontFamily: 'inherit',
                fontSize: '13px',
                lineHeight: 1.4,
              }}
            />
          </div>

          {/* Botões embaixo */}
          <div style={{ display: 'flex', gap: '6px', alignItems: 'center', justifyContent: 'space-between' }}>
            {/* Esquerda: Jarvis + Mic */}
            <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
              {/* TOGGLE JARVIS VOICE */}
              <button
                onClick={toggleJarvis}
                style={{
                  width: 36,
                  height: 36,
                  borderRadius: 4,
                  border: `1px solid ${isJarvisVoice ? 'var(--accent)' : 'var(--line)'}`,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                  background: isJarvisVoice ? 'var(--accent)' : 'transparent',
                  color: isJarvisVoice ? 'var(--selection-fg)' : 'var(--muted)',
                  fontFamily: 'var(--font-ui)',
                  fontSize: '12px',
                  transition: 'all 0.2s ease',
                }}
                title={
                  isJarvisVoice
                    ? 'Jarvis Ativo - clique para desligar (velocidade em Configurações)'
                    : 'Jarvis Desligado - clique para ativar (ajuste em Configurações)'
                }
              >
                {isJarvisVoice ? '🔊' : '🔇'}
              </button>

              {/* MICROFONE */}
              <button
                onClick={toggleMic}
                style={{
                  width: 36,
                  height: 36,
                  borderRadius: 4,
                  border: '1px solid var(--line)',
                  cursor: SpeechRecognitionCtor ? 'pointer' : 'not-allowed',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                  background: isListening
                    ? '#e53e3e'
                    : SpeechRecognitionCtor
                      ? 'transparent'
                      : 'rgba(255, 122, 26, 0.12)',
                  color: isListening ? '#fff' : SpeechRecognitionCtor ? 'var(--muted)' : '#999',
                  fontFamily: 'var(--font-ui)',
                  fontSize: '16px',
                  transition: 'all 0.2s ease',
                }}
                title={
                  !SpeechRecognitionCtor
                    ? 'Reconhecimento de voz não suportado aqui'
                    : isListening
                      ? 'Gravando... clique para parar'
                      : 'Clique para falar'
                }
                disabled={!SpeechRecognitionCtor}
              >
                {isListening ? '🔴' : '🎙️'}
              </button>

            </div>
            {/* Direita: Plus + Enviar */}
            <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
              <button
                data-popover
                onClick={() => setShowPlusMenu(!showPlusMenu)}
                style={{
                  width: 36,
                  height: 36,
                  borderRadius: 6,
                  border: `1px solid ${showPlusMenu ? 'var(--accent)' : 'var(--line)'}`,
                  color: showPlusMenu ? 'var(--accent)' : 'var(--muted)',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                  background: showPlusMenu ? 'var(--accent-soft)' : 'transparent',
                  fontSize: '16px',
                  fontWeight: 600,
                  fontFamily: 'inherit',
                  transition: 'all 0.15s ease',
                }}
                title="Acoes rapidas (+)"
              >
                +
              </button>

              <button
                onClick={() => handleSend()}
                disabled={false}
                style={{
                  width: 36,
                  height: 36,
                  borderRadius: 6,
                  border: `1px solid var(--accent)`,
                  color: 'var(--accent)',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                  background: 'transparent',
                }}
              >
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <line x1="22" y1="2" x2="11" y2="13" />
                  <polygon points="22 2 15 22 11 13 2 9 22 2" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
