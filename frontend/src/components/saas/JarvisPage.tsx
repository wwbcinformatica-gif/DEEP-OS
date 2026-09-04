import React, { useState, useRef, useEffect } from 'react';

interface ToolCall {
  name: string;
  params: any;
  result?: string;
  status: 'running' | 'done' | 'error';
}

interface Message {
  id: string;
  role: 'user' | 'jarvis';
  content: string;
  timestamp: Date;
  tools?: ToolCall[];
  isStreaming?: boolean;
}

const OLLAMA_MODELS = [
  { id: 'bonsai', label: 'Bonsai (Local)', provider: 'ollama' },
  { id: 'qwen2.5-coder:14b', label: 'Qwen 2.5 Coder (Local)', provider: 'ollama' },
  { id: 'qwen3:14b', label: 'Qwen 3 (Local)', provider: 'ollama' },
];

const CLOUD_MODELS = [
  { id: 'gemini-2.5-flash', label: 'Gemini 2.5 Flash (Cloud)', provider: 'gemini' },
  { id: 'gemini-2.0-flash', label: 'Gemini 2.0 Flash (Cloud)', provider: 'gemini' },
];

const JarvisPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'jarvis',
      content: 'Olá! Sou o Jarvis, seu assistente inteligente. Posso ouvir você, executar tarefas e usar ferramentas. Como posso ajudar?',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [selectedModel, setSelectedModel] = useState('gemini-2.5-flash');
  const [selectedProvider, setSelectedProvider] = useState('gemini');
  const [apiKey, setApiKey] = useState('');
  const [showSettings, setShowSettings] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);
  const synthRef = useRef<SpeechSynthesis | null>(null);

  useEffect(() => {
    const savedKey = localStorage.getItem('saas_api_key') || '';
    setApiKey(savedKey);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      synthRef.current = window.speechSynthesis;
    }
  }, []);

  const startListening = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert('Seu navegador não suporta reconhecimento de voz. Use Chrome.');
      return;
    }

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = 'pt-BR';
    recognition.interimResults = true;
    recognition.continuous = false;

    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);
    recognition.onerror = () => setIsListening(false);

    recognition.onresult = (event: any) => {
      let transcript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
      }
      setInput(transcript);
      if (event.results[event.results.length - 1].isFinal) {
        handleSendMessageDirect(transcript);
      }
    };

    recognitionRef.current = recognition;
    recognition.start();
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
  };

  const speak = (text: string) => {
    if (!synthRef.current) return;
    synthRef.current.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'pt-BR';
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    synthRef.current.speak(utterance);
  };

  const stopSpeaking = () => {
    if (synthRef.current) {
      synthRef.current.cancel();
      setIsSpeaking(false);
    }
  };

  const handleSendMessageDirect = async (text: string) => {
    if (!text.trim()) return;

    const userMessage: Message = {
      id: String(Date.now()),
      role: 'user',
      content: text,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);

    const jarvisMsg: Message = {
      id: String(Date.now() + 1),
      role: 'jarvis',
      content: '',
      timestamp: new Date(),
      isStreaming: true,
      tools: [],
    };
    setMessages(prev => [...prev, jarvisMsg]);

    try {
      const token = localStorage.getItem('saas_token');
      const resp = await fetch('/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          user: text,
          provider: selectedProvider,
          model: selectedModel,
          api_key: apiKey,
          temperature: 0.7,
          session_id: `saas-${localStorage.getItem('saas_user') || 'default'}`,
        }),
      });

      if (!resp.ok) {
        throw new Error(`Erro ${resp.status}: ${resp.statusText}`);
      }

      const reader = resp.body?.getReader();
      const decoder = new TextDecoder();
      let fullAnswer = '';
      let buffer = '';

      if (reader) {
        while (true) {
          const { value, done } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (!line.trim()) continue;
            try {
              const event = JSON.parse(line);

              if (event.type === 'token') {
                fullAnswer += event.content || '';
                setMessages(prev => {
                  const updated = [...prev];
                  const last = updated[updated.length - 1];
                  if (last.id === jarvisMsg.id) {
                    updated[updated.length - 1] = { ...last, content: fullAnswer };
                  }
                  return updated;
                });
              } else if (event.type === 'tool_start') {
                const tools = [...(jarvisMsg.tools || [])];
                tools.push({
                  name: event.tool_name || 'unknown',
                  params: event.params || {},
                  status: 'running',
                });
                setMessages(prev => {
                  const updated = [...prev];
                  const idx = updated.findIndex(m => m.id === jarvisMsg.id);
                  if (idx >= 0) updated[idx] = { ...updated[idx], tools };
                  return updated;
                });
              } else if (event.type === 'tool_end') {
                setMessages(prev => {
                  const updated = [...prev];
                  const idx = updated.findIndex(m => m.id === jarvisMsg.id);
                  if (idx >= 0) {
                    const tools = [...(updated[idx].tools || [])];
                    const lastTool = tools.length - 1;
                    if (lastTool >= 0) {
                      tools[lastTool] = { ...tools[lastTool], result: event.result, status: 'done' };
                    }
                    updated[idx] = { ...updated[idx], tools };
                  }
                  return updated;
                });
              } else if (event.type === 'error') {
                fullAnswer += `\n\n❌ Erro: ${event.message}`;
                setMessages(prev => {
                  const updated = [...prev];
                  const last = updated[updated.length - 1];
                  if (last.id === jarvisMsg.id) {
                    updated[updated.length - 1] = { ...last, content: fullAnswer };
                  }
                  return updated;
                });
              } else if (event.type === 'done') {
                fullAnswer = event.answer || fullAnswer;
              }
            } catch (e) {}
          }
        }
      }

      setMessages(prev => {
        const updated = [...prev];
        const idx = updated.findIndex(m => m.id === jarvisMsg.id);
        if (idx >= 0) {
          updated[idx] = { ...updated[idx], content: fullAnswer, isStreaming: false };
        }
        return updated;
      });

      if (fullAnswer) speak(fullAnswer);

    } catch (err: any) {
      setMessages(prev => {
        const updated = [...prev];
        const idx = updated.findIndex(m => m.id === jarvisMsg.id);
        if (idx >= 0) {
          updated[idx] = {
            ...updated[idx],
            content: `Desculpe, ocorreu um erro: ${err.message}. Verifique se o backend está rodando e se sua chave de API está configurada.`,
            isStreaming: false,
          };
        }
        return updated;
      });
    }

    setIsTyping(false);
  };

  const handleSendMessage = async () => {
    handleSendMessageDirect(input);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
    // Auto-resize textarea
    const target = e.target;
    setTimeout(() => {
      target.style.height = 'auto';
      target.style.height = Math.min(target.scrollHeight, 150) + 'px';
    }, 0);
  };

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <div style={styles.headerLeft}>
          <div style={styles.jarvisIcon}>🤖</div>
          <div>
            <h1 style={styles.title}>Jarvis</h1>
            <p style={styles.subtitle}>Assistente Inteligente com Voz e Ferramentas</p>
          </div>
        </div>
        <div style={styles.headerRight}>
          <select
            value={`${selectedProvider}:${selectedModel}`}
            onChange={(e) => {
              const [prov, model] = e.target.value.split(':');
              setSelectedProvider(prov);
              setSelectedModel(model);
            }}
            style={styles.modelSelect}
          >
            <optgroup label="Cloud">
              {CLOUD_MODELS.map(m => (
                <option key={m.id} value={`${m.provider}:${m.id}`}>{m.label}</option>
              ))}
            </optgroup>
            <optgroup label="Local (Ollama)">
              {OLLAMA_MODELS.map(m => (
                <option key={m.id} value={`${m.provider}:${m.id}`}>{m.label}</option>
              ))}
            </optgroup>
          </select>
          <button style={styles.settingsBtn} onClick={() => setShowSettings(!showSettings)}>
            ⚙️
          </button>
        </div>
      </div>

      {/* Chat Area */}
      <div style={styles.chatContainer}>
        <div style={styles.messagesArea}>
          {messages.map(msg => (
            <div
              key={msg.id}
              style={{
                ...styles.message,
                ...(msg.role === 'jarvis' ? styles.messageJarvis : styles.messageUser),
              }}
            >
              {msg.role === 'jarvis' && (
                <div style={styles.avatarJarvis}>J</div>
              )}
              <div style={styles.messageContent}>
                <p style={styles.messageText}>
                  {msg.content}
                  {msg.isStreaming && <span style={styles.cursor}>▌</span>}
                </p>

                {/* Tool Calls */}
                {msg.tools && msg.tools.length > 0 && (
                  <div style={styles.toolsContainer}>
                    {msg.tools.map((tool, i) => (
                      <div key={i} style={{
                        ...styles.toolCard,
                        borderColor: tool.status === 'running' ? '#f59e0b' :
                                   tool.status === 'done' ? '#10b981' : '#ef4444',
                      }}>
                        <div style={styles.toolHeader}>
                          <span style={styles.toolIcon}>🔧</span>
                          <span style={styles.toolName}>{tool.name}</span>
                          <span style={{
                            ...styles.toolStatus,
                            color: tool.status === 'running' ? '#f59e0b' :
                                  tool.status === 'done' ? '#10b981' : '#ef4444',
                          }}>
                            {tool.status === 'running' ? '⏳ Executando...' :
                             tool.status === 'done' ? '✅ Concluído' : '❌ Erro'}
                          </span>
                        </div>
                        {tool.result && (
                          <pre style={styles.toolResult}>{tool.result}</pre>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                <span style={styles.messageTime}>
                  {msg.timestamp.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
              {msg.role === 'user' && (
                <div style={styles.avatarUser}>W</div>
              )}
            </div>
          ))}

          {isTyping && (
            <div style={{...styles.message, ...styles.messageJarvis}}>
              <div style={styles.avatarJarvis}>J</div>
              <div style={styles.messageContent}>
                <div style={styles.typingIndicator}>
                  <span style={styles.typingDot}></span>
                  <span style={styles.typingDot}></span>
                  <span style={styles.typingDot}></span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div style={styles.inputArea}>
          <button
            style={{
              ...styles.voiceBtn,
              background: isListening ? '#ef4444' : 'var(--saas-bg-card)',
              color: isListening ? '#fff' : 'var(--saas-text)',
            }}
            onClick={isListening ? stopListening : startListening}
            title={isListening ? 'Parar de ouvir' : 'Ouvir voz'}
          >
            {isListening ? '⏹' : '🎤'}
          </button>

          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={isListening ? 'Ouvindo...' : 'Digite sua mensagem...'}
            rows={1}
            style={{
              ...styles.textarea,
              borderColor: isListening ? '#ef4444' : 'var(--saas-border)',
            }}
            disabled={isTyping}
          />

          <button
            style={styles.sendBtn}
            onClick={handleSendMessage}
            disabled={!input.trim() || isTyping}
          >
            {isTyping ? '⏳' : 'Enviar'}
          </button>

          {isSpeaking && (
            <button style={styles.stopSpeakBtn} onClick={stopSpeaking}>
              🔇 Parar
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

const OllamaStatus: React.FC = () => {
  const [status, setStatus] = useState<'loading' | 'online' | 'offline'>('loading');

  useEffect(() => {
    fetch('http://localhost:11434/api/tags')
      .then(r => r.ok ? setStatus('online') : setStatus('offline'))
      .catch(() => setStatus('offline'));
  }, []);

  return (
    <div style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
      <div style={{
        width: '10px', height: '10px', borderRadius: '50%',
        background: status === 'online' ? '#10b981' : status === 'loading' ? '#f59e0b' : '#ef4444',
      }}/>
      <span style={{fontSize: '13px', color: 'var(--saas-text-muted)'}}>
        {status === 'online' ? 'Ollama conectado' :
         status === 'loading' ? 'Verificando...' : 'Ollama offline (instale em ollama.com)'}
      </span>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    height: 'calc(100vh - 80px)',
    padding: '20px 40px',
    color: 'var(--saas-text)',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '16px',
    flexShrink: 0,
  },
  headerLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
  },
  jarvisIcon: {
    width: '56px',
    height: '56px',
    background: 'linear-gradient(135deg, var(--saas-accent), #00ff88)',
    borderRadius: '16px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '28px',
  },
  title: { fontSize: '24px', fontWeight: 'bold', margin: 0 },
  subtitle: { fontSize: '14px', color: 'var(--saas-text-muted)', margin: 0 },
  headerRight: { display: 'flex', gap: '8px', alignItems: 'center' },
  modelSelect: {
    padding: '8px 12px',
    background: 'var(--saas-bg-card)',
    border: '1px solid var(--saas-border)',
    borderRadius: '8px',
    color: 'var(--saas-text)',
    fontSize: '13px',
    cursor: 'pointer',
  },
  settingsBtn: {
    padding: '8px 12px',
    background: 'var(--saas-bg-card)',
    border: '1px solid var(--saas-border)',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '16px',
  },
  chatContainer: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    background: 'var(--saas-bg-card)',
    border: '1px solid var(--saas-border)',
    borderRadius: '16px',
    overflow: 'hidden',
    marginBottom: '16px',
  },
  messagesArea: {
    flex: 1,
    padding: '20px',
    overflowY: 'auto',
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  message: { display: 'flex', gap: '12px', maxWidth: '85%' },
  messageJarvis: { alignSelf: 'flex-start' },
  messageUser: { alignSelf: 'flex-end', flexDirection: 'row-reverse' },
  avatarJarvis: {
    width: '36px', height: '36px',
    background: 'linear-gradient(135deg, var(--saas-accent), #00ff88)',
    borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center',
    fontSize: '14px', fontWeight: 'bold', color: '#000', flexShrink: 0,
  },
  avatarUser: {
    width: '36px', height: '36px',
    background: 'linear-gradient(135deg, #8b5cf6, #a78bfa)',
    borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center',
    fontSize: '14px', fontWeight: 'bold', color: '#fff', flexShrink: 0,
  },
  messageContent: {
    background: 'var(--saas-bg-input)',
    border: '1px solid var(--saas-border)',
    borderRadius: '12px',
    padding: '12px 16px',
  },
  messageText: { margin: 0, fontSize: '14px', lineHeight: 1.6, whiteSpace: 'pre-wrap' },
  cursor: { animation: 'blink 1s infinite', color: 'var(--saas-accent)' },
  toolsContainer: { marginTop: '12px', display: 'flex', flexDirection: 'column', gap: '8px' },
  toolCard: {
    padding: '10px 12px',
    background: 'var(--saas-bg-card)',
    border: '1px solid',
    borderRadius: '8px',
  },
  toolHeader: { display: 'flex', alignItems: 'center', gap: '8px' },
  toolIcon: { fontSize: '14px' },
  toolName: { fontSize: '13px', fontWeight: '600', color: 'var(--saas-text)' },
  toolStatus: { fontSize: '12px', marginLeft: 'auto' },
  toolResult: {
    marginTop: '8px',
    padding: '8px',
    background: 'var(--saas-bg-input)',
    borderRadius: '6px',
    fontSize: '11px',
    fontFamily: 'monospace',
    color: 'var(--saas-text-muted)',
    overflow: 'auto',
    maxHeight: '150px',
    whiteSpace: 'pre-wrap',
  },
  messageTime: { fontSize: '11px', color: 'var(--saas-text-muted)', marginTop: '4px', display: 'block' },
  typingIndicator: { display: 'flex', gap: '4px', padding: '4px 0' },
  typingDot: {
    width: '8px', height: '8px', background: 'var(--saas-text-muted)',
    borderRadius: '50%', animation: 'pulse 1.4s infinite',
  },
  inputArea: {
    display: 'flex', gap: '8px', padding: '12px',
    borderTop: '1px solid var(--saas-border)',
    background: 'var(--saas-bg-input)',
  },
  voiceBtn: {
    padding: '12px', border: '1px solid var(--saas-border)',
    borderRadius: '8px', cursor: 'pointer', fontSize: '18px',
    transition: 'all 0.2s', flexShrink: 0,
  },
  sendBtn: {
    padding: '12px 20px', background: 'var(--saas-accent)',
    border: 'none', borderRadius: '8px', color: '#ffffff',
    fontSize: '14px', fontWeight: '600', cursor: 'pointer', flexShrink: 0,
  },
  stopSpeakBtn: {
    padding: '12px', background: 'rgba(239, 68, 68, 0.1)',
    border: '1px solid rgba(239, 68, 68, 0.3)',
    borderRadius: '8px', color: '#ef4444', fontSize: '12px', cursor: 'pointer',
  },
  textarea: {
    flex: 1,
    padding: '12px 16px',
    background: 'var(--saas-bg-input)',
    border: '1px solid var(--saas-border)',
    borderRadius: '8px',
    color: 'var(--saas-text)',
    fontSize: '14px',
    resize: 'vertical' as const,
    minHeight: '44px',
    maxHeight: '150px',
    lineHeight: 1.5,
    fontFamily: 'inherit',
    outline: 'none',
    overflow: 'auto',
  },
};

export default JarvisPage;
