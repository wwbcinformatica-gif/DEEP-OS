import React, { useState, useEffect } from 'react';
import type { Provider, Mood, AccentTheme } from '../lib/constants';
import { MODELS, PROVIDERS, MOODS, SETTINGS_KEY, API_BASE, ACCENT_THEMES } from '../lib/constants';
import { SecurityToggle } from './SecurityToggle';

type VoicePreset =
  | 'google-female'
  | 'francisca'
  | 'maria'
  | 'google-male'
  | 'antonio'
  | 'daniel'
  | 'jarvis-cinematic'
  | 'edge-francisca'
  | 'edge-thalita'
  | 'eleven-natasha'
  | 'eleven-serafina'
  | 'eleven-ivy'
  | 'eleven-ingmar'
  | 'dani-brandi';

type Tab = 'geral' | 'aparencia' | 'voz' | 'agente' | 'dev';

interface Props {
  prov: Provider;
  setProv: (v: Provider) => void;
  model: string;
  setModel: (v: string) => void;
  mood: Mood;
  setMood: (v: Mood) => void;
  temp: number;
  setTemp: (v: number) => void;
  sysPr: string;
  setSysPr: (v: string) => void;
  snd: boolean;
  setSnd: (v: boolean) => void;
  bright: number;
  setBright: (v: number) => void;
  fsize: number;
  setFsize: (v: number) => void;
  apiKey: string;
  setApiKey: (v: string) => void;
  orApiKey: string;
  setOrApiKey: (v: string) => void;
  groqApiKey: string;
  setGroqApiKey: (v: string) => void;
  openaiApiKey: string;
  setOpenaiApiKey: (v: string) => void;
  geminiApiKey: string;
  setGeminiApiKey: (v: string) => void;
  mimoApiKey: string;
  setMimoApiKey: (v: string) => void;
  nvidiaApiKey: string;
  setNvidiaApiKey: (v: string) => void;
  oModels: { value: string; label: string }[];
  orModels: { value: string; label: string }[];
  llamacppModels: { value: string; label: string; available: boolean }[];
  customM: string;
  setCustomM: (v: string) => void;
  showCust: boolean;
  setShowCust: (v: boolean) => void;
  voicePreset: VoicePreset;
  setVoicePreset: (v: VoicePreset) => void;
  jarvisRate: number;
  setJarvisRate: (v: number) => void;
  voicePitch: number;
  setVoicePitch: (v: number) => void;
  deepSilenceSec: number;
  setDeepSilenceSec: (v: number) => void;
  ollSt: { running: boolean; models: string[] } | undefined;
  accentTheme: AccentTheme;
  setAccentTheme: (v: AccentTheme) => void;
  gpuEnabled: boolean;
  setGpuEnabled: (v: boolean) => void;
}

const base: React.CSSProperties = {
  fontFamily: 'var(--font-ui)',
  fontSize: 'var(--font-size-base)',
  fontWeight: 600,
  color: 'var(--ink)',
};

function s(extra: React.CSSProperties = {}): React.CSSProperties {
  return { ...base, ...extra };
}

function inputStyle(): React.CSSProperties {
  return {
    background: 'transparent',
    border: '1px solid var(--line-strong)',
    borderRadius: '4px',
    color: 'var(--ink)',
    padding: '6px 10px',
    outline: 'none',
    ...base,
  };
}

function btnStyle(c: string, b?: string): React.CSSProperties {
  return {
    background: 'transparent',
    border: `1px solid ${b || 'var(--line-strong)'}`,
    borderRadius: '4px',
    color: c,
    cursor: 'pointer',
    padding: '4px 10px',
    ...base,
    fontSize: '12px',
  };
}

const TABS: { key: Tab; label: string }[] = [
  { key: 'geral', label: 'Geral' },
  { key: 'aparencia', label: 'Aparencia' },
  { key: 'voz', label: 'Voz' },
  { key: 'agente', label: 'Agente' },
  { key: 'dev', label: 'Dev' },
];

const VOICE_OPTIONS = [
  { key: 'google-female' as const, label: 'Google PT-BR Feminino', desc: 'Voz clara e natural' },
  { key: 'francisca' as const, label: 'Francisca (Feminino)', desc: 'Voz feminina brasileira classica' },
  { key: 'maria' as const, label: 'Maria (Feminino)', desc: 'Voz feminina suave e natural' },
  { key: 'google-male' as const, label: 'Google PT-BR Masculino', desc: 'Voz masculina nativa' },
  { key: 'antonio' as const, label: 'Antonio (Masculino)', desc: 'Voz masculina brasileira profunda' },
  { key: 'daniel' as const, label: 'Daniel (Masculino)', desc: 'Voz masculina estavel e clara' },
  { key: 'jarvis-cinematic' as const, label: 'Jarvis Cinematic', desc: 'Tom grave, levemente cinematografico' },
  { key: 'edge-francisca' as const, label: 'Francisca Neural (Edge)', desc: 'Voz feminina natural Microsoft Neural' },
  { key: 'edge-thalita' as const, label: 'Thalita Neural (Edge)', desc: 'Voz feminina clara Microsoft Neural' },
  { key: 'dani-brandi' as const, label: 'Dani Brandi (Google)', desc: 'Voz feminina brasileira bonita e natural' },
  { key: 'eleven-natasha' as const, label: 'Natasha (ElevenLabs)', desc: 'Sensual, hipnotica e brincalhona' },
  { key: 'eleven-serafina' as const, label: 'Serafina (ElevenLabs)', desc: 'Sedutora sensual e charmosa' },
  { key: 'eleven-ivy' as const, label: 'Ivy (ElevenLabs)', desc: 'Suave, expressiva e calorosa' },
  { key: 'eleven-ingmar' as const, label: 'Ingmar (ElevenLabs)', desc: 'Masculina, misteriosa e envolvente' },
];

export default function SettingsPage(props: Props) {
  const {
    prov, setProv, model, setModel, mood, setMood, temp, setTemp,
    sysPr, setSysPr, snd, setSnd, bright, setBright, fsize, setFsize,
    apiKey, setApiKey, orApiKey, setOrApiKey, groqApiKey, setGroqApiKey,
    openaiApiKey, setOpenaiApiKey, geminiApiKey, setGeminiApiKey,
<<<<<<< HEAD
    mimoApiKey, setMimoApiKey, oModels, orModels, llamacppModels, customM, setCustomM,
=======
    mimoApiKey, setMimoApiKey, nvidiaApiKey, setNvidiaApiKey, oModels, orModels, llamacppModels, customM, setCustomM,
>>>>>>> d436640 (v2.0: GGUF auto-detection, GPU support, vision, thinking panel, monitor fix, portability scripts)
    showCust, setShowCust, voicePreset, setVoicePreset, jarvisRate, setJarvisRate,
    voicePitch, setVoicePitch, deepSilenceSec, setDeepSilenceSec, accentTheme, setAccentTheme, gpuEnabled, setGpuEnabled,
  } = props;
  const [toast, setToast] = useState('');
  const [activeTab, setActiveTab] = useState<Tab>('geral');

  const [maxTurns, setMaxTurns] = useState(25);
  const [maxToolSteps, setMaxToolSteps] = useState(100);
  const [toolset, setToolset] = useState('agent');
  const [imageInputMode, setImageInputMode] = useState('text');
  const [serverPort, setServerPort] = useState(8000);
  const [serverHost, setServerHost] = useState('0.0.0.0');
  const [shell, setShell] = useState('powershell');
  const [watcherIgnore, setWatcherIgnore] = useState('node_modules/**, dist/**, .git/**');
  const [showReasoning, setShowReasoning] = useState(true);
  const [showToolCalls, setShowToolCalls] = useState(true);
  const [compactMode, setCompactMode] = useState(false);
  const [language, setLanguage] = useState('pt-BR');

  useEffect(() => {
    try {
      const saved = JSON.parse(localStorage.getItem(SETTINGS_KEY) || '{}');
      if (saved.maxTurns !== undefined) setMaxTurns(saved.maxTurns);
      if (saved.maxToolSteps !== undefined) setMaxToolSteps(saved.maxToolSteps);
      if (saved.toolset) setToolset(saved.toolset);
      if (saved.imageInputMode) setImageInputMode(saved.imageInputMode);
      if (saved.serverPort !== undefined) setServerPort(saved.serverPort);
      if (saved.serverHost) setServerHost(saved.serverHost);
      if (saved.shell) setShell(saved.shell);
      if (saved.watcherIgnore) setWatcherIgnore(saved.watcherIgnore);
      if (saved.showReasoning !== undefined) setShowReasoning(saved.showReasoning);
      if (saved.showToolCalls !== undefined) setShowToolCalls(saved.showToolCalls);
      if (saved.compactMode !== undefined) setCompactMode(saved.compactMode);
      if (saved.language) setLanguage(saved.language);
    } catch {}
    fetch(`${API_BASE}/api/config`)
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (!data) return;
        const a = data.agent || {};
        if (a.max_turns !== undefined) setMaxTurns(a.max_turns);
        if (a.max_tool_steps !== undefined) setMaxToolSteps(a.max_tool_steps);
        if (a.toolset) setToolset(a.toolset);
        if (a.image_input_mode) setImageInputMode(a.image_input_mode);
        const srv = data.server || {};
        if (srv.port !== undefined) setServerPort(srv.port);
        if (srv.hostname) setServerHost(srv.hostname);
        const t = data.terminal || {};
        if (t.backend) setShell(t.backend);
        const w = data.watcher || {};
        if (w.ignore) setWatcherIgnore(w.ignore.join(', '));
        const d = data.display || {};
        if (d.show_reasoning !== undefined) setShowReasoning(d.show_reasoning);
        if (d.show_tool_calls !== undefined) setShowToolCalls(d.show_tool_calls);
        if (d.compact !== undefined) setCompactMode(d.compact);
        if (d.language) setLanguage(d.language);
      })
      .catch(() => {});
  }, []);

  const card: React.CSSProperties = {
    border: '1px solid var(--line)',
    borderRadius: '4px',
    padding: '14px',
    background: 'var(--bg)',
  };
  const h3: React.CSSProperties = { ...base, fontSize: '11px', fontWeight: 700, color: 'var(--muted)', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.5px' };
  const selectStyle: React.CSSProperties = { ...inputStyle(), width: '100%', cursor: 'pointer' };
  const rangeStyle: React.CSSProperties = { flex: 1, accentColor: 'var(--accent)' };
  const labelStyle: React.CSSProperties = { ...base, fontSize: '11px', color: 'var(--muted)', marginBottom: '6px' };
  const linkStyle: React.CSSProperties = { color: 'var(--accent-2)' };
  const grid2: React.CSSProperties = { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' };

  const Toggle = ({ value, onChange, label }: { value: boolean; onChange: () => void; label: string }) => (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '4px 0' }}>
      <span style={s({ fontSize: '11px' })}>{label}</span>
      <div onClick={onChange} style={{ width: 34, height: 18, borderRadius: 3, cursor: 'pointer', position: 'relative', background: value ? 'var(--accent)' : 'var(--line-strong)', flexShrink: 0 }}>
        <div style={{ width: 14, height: 14, borderRadius: 2, background: 'var(--muted)', position: 'absolute', top: 2, left: value ? 18 : 2, transition: 'left 0.2s' }} />
      </div>
    </div>
  );

  const handleSave = async () => {
    localStorage.setItem(SETTINGS_KEY, JSON.stringify({
      prov, model, mood, temp, sysPr, snd, bright, fsize, voicePreset, jarvisRate, voicePitch,
      apiKey, orApiKey, geminiApiKey, mimoApiKey, accentTheme, maxTurns, maxToolSteps, toolset,
      imageInputMode, serverPort, serverHost, shell, watcherIgnore, showReasoning, showToolCalls,
      compactMode, language,
    }));
    fetch(`${API_BASE}/api/config/accent-theme`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ theme: accentTheme }) }).catch(() => {});
    fetch(`${API_BASE}/api/config`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ section: 'agent', values: { max_turns: maxTurns, max_tool_steps: maxToolSteps, toolset, image_input_mode: imageInputMode, personality: mood, system_prompt: sysPr || '' } }) }).catch(() => {});
    fetch(`${API_BASE}/api/config`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ section: 'display', values: { accent_theme: accentTheme, compact: compactMode, language, show_reasoning: showReasoning, show_tool_calls: showToolCalls, streaming: true } }) }).catch(() => {});
    fetch(`${API_BASE}/api/config`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ section: 'terminal', values: { backend: shell, cwd: '.', timeout: 600, allowed_commands: ['ls','dir','cat','type','echo','pwd','cd','mkdir','copy','move','del','git','npm','node','python','pip','curl','find','grep','rg','ollama'] } }) }).catch(() => {});
    fetch(`${API_BASE}/api/config`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ section: 'server', values: { port: serverPort, hostname: serverHost } }) }).catch(() => {});
    fetch(`${API_BASE}/api/config`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ section: 'watcher', values: { ignore: watcherIgnore.split(',').map(s => s.trim()).filter(Boolean) } }) }).catch(() => {});
    setToast('Configuracoes salvas!');
    setTimeout(() => setToast(''), 2000);
  };

  return (
    <div style={{ flex: 1, overflow: 'auto', padding: '16px 20px' }}>
      {/* Tabs */}
      <div style={{ display: 'flex', gap: '2px', marginBottom: '16px', borderBottom: '1px solid var(--line)', paddingBottom: 0 }}>
        {TABS.map((t) => (
          <button
            key={t.key}
            onClick={() => setActiveTab(t.key)}
            style={{
              padding: '8px 16px',
              border: 'none',
              borderBottom: activeTab === t.key ? '2px solid var(--accent)' : '2px solid transparent',
              background: activeTab === t.key ? 'var(--bg-3)' : 'transparent',
              color: activeTab === t.key ? 'var(--accent)' : 'var(--muted)',
              cursor: 'pointer',
              fontWeight: 700,
              fontSize: '11px',
              fontFamily: 'var(--font-ui)',
              letterSpacing: '0.3px',
              borderRadius: '4px 4px 0 0',
              transition: 'all 0.15s',
            }}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* ── GERAL ── */}
      {activeTab === 'geral' && (
        <div style={{ ...grid2, maxWidth: 700 }}>
          <div style={card}>
            <h3 style={h3}>Provedor</h3>
            <select value={prov} onChange={(e) => { setProv(e.target.value as Provider); const ms = MODELS[e.target.value]; if (ms?.length) setModel(ms[0].value); }} style={selectStyle}>
              {PROVIDERS.map((p) => <option key={p} value={p}>{p}</option>)}
            </select>
          </div>
          <div style={card}>
            <h3 style={h3}>Modelo</h3>
            <select value={model} onChange={(e) => e.target.value === '__c' ? setShowCust(true) : (setModel(e.target.value), setShowCust(false))} style={selectStyle}>
              {(() => {
                let avail: { value: string; label: string }[] = [];
                
                if (prov === 'ollama' && oModels.length) {
                  avail = oModels;
                } else if (prov === 'llamacpp' && llamacppModels.length) {
                  avail = llamacppModels.map(m => ({
                    value: m.value,
                    label: m.available ? m.label : `${m.label} (indisponível)`,
                  }));
                } else if (prov === 'openrouter' && orModels.length) {
                  avail = orModels;
                } else {
                  avail = MODELS[prov] || [];
                }
                
                const list = avail.some((m) => m.value === model) ? avail : [{ value: model, label: model }, ...avail];
                return list.map((m) => <option key={m.value} value={m.value}>{m.label}</option>);
              })()}
              <option value="__c" style={{ color: 'var(--accent-2)' }}>Custom...</option>
            </select>
            {showCust && (
              <div style={{ display: 'flex', gap: '6px', marginTop: '8px' }}>
                <input value={customM} onChange={(e) => setCustomM(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && customM.trim() && (setModel(customM), setShowCust(false), setCustomM(''))} placeholder="nome do modelo..." style={{ ...inputStyle(), flex: 1 }} />
              </div>
            )}
          </div>

          {/* API Keys - shown based on provider */}
          {(prov === 'opencode' || prov === 'openclaude') && (
            <div style={{ ...card, gridColumn: '1 / -1' }}>
              <h3 style={h3}>API Key {prov === 'openclaude' ? 'OpenClaude' : 'OpenCode Zen'}</h3>
              {prov === 'opencode' && <p style={labelStyle}>Cole aqui sua key de <a href="https://opencode.ai/auth" target="_blank" style={linkStyle}>opencode.ai/auth</a></p>}
              <input value={apiKey} onChange={(e) => setApiKey(e.target.value)} placeholder={prov === 'openclaude' ? 'sua-api-key-openclaude' : 'oc_... ou sk-...'} type="password" style={{ ...inputStyle(), width: '100%' }} />
            </div>
          )}
          {prov === 'openrouter' && (
            <div style={{ ...card, gridColumn: '1 / -1' }}>
              <h3 style={h3}>API Key OpenRouter</h3>
              <p style={labelStyle}>Cole aqui sua key de <a href="https://openrouter.ai/keys" target="_blank" style={linkStyle}>openrouter.ai/keys</a></p>
              <input value={orApiKey} onChange={(e) => setOrApiKey(e.target.value)} placeholder="sk-or-v1-..." type="password" style={{ ...inputStyle(), width: '100%' }} />
            </div>
          )}
          {prov === 'groq' && (
            <div style={{ ...card, gridColumn: '1 / -1' }}>
              <h3 style={h3}>API Key Groq</h3>
              <p style={labelStyle}>Cole sua chave de <a href="https://console.groq.com/keys" target="_blank" style={linkStyle}>console.groq.com/keys</a></p>
              <input value={groqApiKey} onChange={(e) => setGroqApiKey(e.target.value)} placeholder="gsk_..." type="password" style={{ ...inputStyle(), width: '100%' }} />
            </div>
          )}
          {prov === 'openai' && (
            <div style={{ ...card, gridColumn: '1 / -1' }}>
              <h3 style={h3}>API Key OpenAI</h3>
              <p style={labelStyle}>Cole sua chave de <a href="https://platform.openai.com/api-keys" target="_blank" style={linkStyle}>platform.openai.com/api-keys</a></p>
              <input value={openaiApiKey} onChange={(e) => setOpenaiApiKey(e.target.value)} placeholder="sk-proj-..." type="password" style={{ ...inputStyle(), width: '100%' }} />
            </div>
          )}
          {prov === 'gemini' && (
            <div style={{ ...card, gridColumn: '1 / -1' }}>
              <h3 style={h3}>API Key Gemini</h3>
              <p style={labelStyle}>Cole sua chave de <a href="https://aistudio.google.com/apikey" target="_blank" style={linkStyle}>aistudio.google.com/apikey</a></p>
              <input value={geminiApiKey} onChange={(e) => setGeminiApiKey(e.target.value)} placeholder="AIza..." type="password" style={{ ...inputStyle(), width: '100%' }} />
            </div>
          )}
          {prov === 'mimo' && (
            <div style={{ ...card, gridColumn: '1 / -1' }}>
              <h3 style={h3}>API Key MiMo (Xiaomi)</h3>
              <p style={labelStyle}>Cole aqui sua key de <a href="https://mimo.mi.com" target="_blank" style={linkStyle}>mimo.mi.com</a></p>
              <input value={mimoApiKey} onChange={(e) => setMimoApiKey(e.target.value)} placeholder="sk-..." type="password" style={{ ...inputStyle(), width: '100%' }} />
              <p style={{ ...s({ color: 'var(--muted)', fontSize: '10px', marginTop: '6px' }) }}>Modelo gratuito: mimo-v2.5</p>
            </div>
          )}
          {prov === 'nvidia' && (
            <div style={{ ...card, gridColumn: '1 / -1' }}>
              <h3 style={h3}>API Key NVIDIA (NIM)</h3>
              <p style={labelStyle}>Cole sua chave de <a href="https://build.nvidia.com/" target="_blank" style={linkStyle}>build.nvidia.com</a></p>
              <input value={nvidiaApiKey} onChange={(e) => setNvidiaApiKey(e.target.value)} placeholder="nvapi-..." type="password" style={{ ...inputStyle(), width: '100%' }} />
            </div>
          )}

          <div style={card}>
            <h3 style={h3}>Personalidade</h3>
            <select value={mood} onChange={(e) => setMood(e.target.value as Mood)} style={selectStyle}>
              {MOODS.map((m) => <option key={m} value={m}>{m}</option>)}
            </select>
          </div>
          <div style={card}>
            <h3 style={h3}>Temperatura</h3>
            <p style={{ ...labelStyle, marginBottom: 4 }}>0 = preciso, 1 = criativo</p>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <input type="range" min="0" max="1" step="0.05" value={temp} onChange={(e) => setTemp(parseFloat(e.target.value))} style={rangeStyle} />
              <span style={s({ minWidth: '32px', textAlign: 'center', color: 'var(--accent)' })}>{temp.toFixed(2)}</span>
            </div>
          </div>
        </div>
      )}

      {/* ── APARENCIA ── */}
      {activeTab === 'aparencia' && (
        <div style={{ ...grid2, maxWidth: 700 }}>
          <div style={card}>
            <h3 style={h3}>Brilho da Interface</h3>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <input type="range" min="50" max="150" step="5" value={bright} onChange={(e) => setBright(+e.target.value)} style={rangeStyle} />
              <span style={s({ minWidth: '40px', textAlign: 'center', color: 'var(--accent)' })}>{bright}%</span>
            </div>
          </div>
          <div style={card}>
            <h3 style={h3}>Tamanho Fonte</h3>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <input type="range" min="10" max="18" step="1" value={fsize} onChange={(e) => setFsize(+e.target.value)} style={rangeStyle} />
              <span style={s({ minWidth: '34px', textAlign: 'center', color: 'var(--accent)' })}>{fsize}px</span>
            </div>
          </div>
          <div style={{ ...card, gridColumn: '1 / -1' }}>
            <h3 style={h3}>Tema de Destaque</h3>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '4px' }}>
              {ACCENT_THEMES.map((t) => {
                const active = accentTheme === t.key;
                return (
                  <div key={t.key} onClick={() => setAccentTheme(t.key)} style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', padding: '6px 10px', borderRadius: '4px', background: active ? 'var(--bg-3)' : 'transparent', border: active ? '1px solid var(--accent)' : '1px solid var(--line)', transition: 'all 0.15s', flex: '1 0 140px' }}>
                    <div style={{ width: 16, height: 16, borderRadius: 3, background: t.color, flexShrink: 0 }} />
                    <span style={{ ...base, fontSize: '11px', color: active ? 'var(--accent)' : 'var(--ink)' }}>{t.label}</span>
                  </div>
                );
              })}
            </div>
          </div>
          <div style={card}>
            <h3 style={h3}>Som</h3>
            <Toggle value={snd} onChange={() => setSnd(!snd)} label="Clique nos botoes" />
          </div>
          <div style={card}>
            <h3 style={h3}>GPU (Ollama + Llamacpp)</h3>
            <Toggle value={gpuEnabled} onChange={() => setGpuEnabled(!gpuEnabled)} label={gpuEnabled ? 'GPU ativada (RTX 3060)' : 'GPU desativada'} />
          </div>
          <div style={card}>
            <h3 style={h3}>Seguranca</h3>
            <SecurityToggle />
          </div>
        </div>
      )}

      {/* ── VOZ ── */}
      {activeTab === 'voz' && (
        <div style={{ maxWidth: 500 }}>
          <div style={card}>
            <h3 style={h3}>Voz</h3>
            <p style={labelStyle}>Selecione uma voz em pt-BR para leitura</p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
              <div style={{ display: 'flex', gap: '6px' }}>
                {[
                  { key: 'google-female' as const, label: 'Natural' },
                  { key: 'jarvis-cinematic' as const, label: 'Jarvis' },
                  { key: 'google-male' as const, label: 'Masculina' },
                ].map((v) => (
                  <button key={v.key} onClick={() => setVoicePreset(v.key)} style={{ flex: 1, padding: '8px 10px', borderRadius: 6, border: voicePreset === v.key ? '1px solid var(--accent)' : '1px solid var(--line-strong)', background: voicePreset === v.key ? 'var(--accent)' : 'transparent', color: voicePreset === v.key ? 'var(--selection-fg)' : 'var(--muted)', cursor: 'pointer', fontSize: '11px', fontWeight: 600 }}>
                    {v.label}
                  </button>
                ))}
              </div>
              <p style={{ ...s({ fontSize: '9px', color: 'var(--quiet)', margin: 0 }) }}>Edge TTS (streaming):</p>
              <div style={{ display: 'flex', gap: '6px' }}>
                {[
                  { key: 'edge-francisca' as const, label: 'Francisca' },
                  { key: 'edge-thalita' as const, label: 'Thalita' },
                ].map((v) => (
                  <button key={v.key} onClick={() => setVoicePreset(v.key)} style={{ flex: 1, padding: '6px 8px', borderRadius: 6, border: voicePreset === v.key ? '1px solid var(--accent)' : '1px solid var(--line-strong)', background: voicePreset === v.key ? 'var(--accent)' : 'transparent', color: voicePreset === v.key ? 'var(--selection-fg)' : 'var(--muted)', cursor: 'pointer', fontSize: '11px' }}>
                    {v.label}
                  </button>
                ))}
              </div>
              <p style={{ ...s({ fontSize: '9px', color: 'var(--quiet)', margin: 0 }) }}>Google Natural:</p>
              <div style={{ display: 'flex', gap: '6px' }}>
                {[
                  { key: 'dani-brandi' as const, label: 'Dani Brandi' },
                ].map((v) => (
                  <button key={v.key} onClick={() => setVoicePreset(v.key)} style={{ flex: 1, padding: '6px 8px', borderRadius: 6, border: voicePreset === v.key ? '1px solid var(--accent)' : '1px solid var(--line-strong)', background: voicePreset === v.key ? 'var(--accent)' : 'transparent', color: voicePreset === v.key ? 'var(--selection-fg)' : 'var(--muted)', cursor: 'pointer', fontSize: '11px' }}>
                    {v.label}
                  </button>
                ))}
              </div>
              <p style={{ ...s({ fontSize: '9px', color: 'var(--quiet)', margin: 0 }) }}>ElevenLabs (requer API key):</p>
              <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                {[
                  { key: 'eleven-natasha' as const, label: 'Natasha' },
                  { key: 'eleven-serafina' as const, label: 'Serafina' },
                  { key: 'eleven-ivy' as const, label: 'Ivy' },
                  { key: 'eleven-ingmar' as const, label: 'Ingmar' },
                ].map((v) => (
                  <button key={v.key} onClick={() => setVoicePreset(v.key)} style={{ flex: '1 0 45%', padding: '6px 8px', borderRadius: 6, border: voicePreset === v.key ? '1px solid var(--accent)' : '1px solid var(--line-strong)', background: voicePreset === v.key ? 'var(--accent)' : 'transparent', color: voicePreset === v.key ? 'var(--selection-fg)' : 'var(--muted)', cursor: 'pointer', fontSize: '11px' }}>
                    {v.label}
                  </button>
                ))}
              </div>
              <p style={{ ...s({ fontSize: '10px', color: 'var(--muted)', margin: 0 }) }}>{VOICE_OPTIONS.find((o) => o.key === voicePreset)?.desc}</p>
            </div>
            <div style={{ display: 'grid', gap: '10px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ ...s(), minWidth: '56px' }}>Velocidade</span>
                <input type="range" min="0" max="100" value={jarvisRate} onChange={(e) => setJarvisRate(+e.target.value)} style={rangeStyle} />
                <span style={s({ minWidth: '32px', textAlign: 'right' })}>{jarvisRate}%</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ ...s(), minWidth: '56px' }}>Tom</span>
                <input type="range" min="-50" max="50" value={voicePitch - 50} onChange={(e) => setVoicePitch(+e.target.value + 50)} style={rangeStyle} />
                <span style={s({ minWidth: '32px', textAlign: 'right' })}>{voicePitch > 50 ? '+' : ''}{voicePitch - 50}</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ ...s(), minWidth: '56px' }} title="Tempo de silêncio no modo Aurea antes de enviar o comando">Escuta</span>
                <input type="range" min="2" max="15" value={deepSilenceSec} onChange={(e) => setDeepSilenceSec(+e.target.value)} style={rangeStyle} />
                <span style={s({ minWidth: '32px', textAlign: 'right' })}>{deepSilenceSec}s</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── AGENTE ── */}
      {activeTab === 'agente' && (
        <div style={{ ...grid2, maxWidth: 700 }}>
          <div style={{ ...card, gridColumn: '1 / -1' }}>
            <h3 style={h3}>Prompt Personalizado</h3>
            <p style={labelStyle}>Instrucao extra enviada ao modelo</p>
            <textarea value={sysPr} onChange={(e) => setSysPr(e.target.value)} rows={3} placeholder='ex: "Responda sempre em portugues..."' style={{ ...inputStyle(), width: '100%', resize: 'vertical', lineHeight: 1.5 }} />
          </div>
          <div style={card}>
            <h3 style={h3}>Agente</h3>
            <div style={labelStyle}>Max Turns</div>
            <input type="number" min="1" max="200" value={maxTurns} onChange={(e) => setMaxTurns(+e.target.value)} style={inputStyle()} />
            <div style={{ ...labelStyle, marginTop: '8px' }}>Max Tool Steps</div>
            <input type="number" min="1" max="500" value={maxToolSteps} onChange={(e) => setMaxToolSteps(+e.target.value)} style={inputStyle()} />
          </div>
          <div style={card}>
            <h3 style={h3}>Toolset</h3>
            <select value={toolset} onChange={(e) => setToolset(e.target.value)} style={selectStyle}>
              <option value="agent">Agent (completo)</option>
              <option value="developer">Developer</option>
              <option value="readonly">Read Only</option>
              <option value="minimal">Minimal</option>
            </select>
            <div style={{ ...labelStyle, marginTop: '8px' }}>Image Input Mode</div>
            <select value={imageInputMode} onChange={(e) => setImageInputMode(e.target.value)} style={selectStyle}>
              <option value="text">Text (descrito)</option>
              <option value="image">Image (base64)</option>
            </select>
          </div>
        </div>
      )}

      {/* ── DEV ── */}
      {activeTab === 'dev' && (
        <div style={{ ...grid2, maxWidth: 700 }}>
          <div style={card}>
            <h3 style={h3}>Servidor</h3>
            <div style={labelStyle}>Server Port</div>
            <input type="number" min="1024" max="65535" value={serverPort} onChange={(e) => setServerPort(+e.target.value)} style={inputStyle()} />
            <div style={{ ...labelStyle, marginTop: '8px' }}>Server Hostname</div>
            <select value={serverHost} onChange={(e) => setServerHost(e.target.value)} style={selectStyle}>
              <option value="0.0.0.0">0.0.0.0 (todas interfaces)</option>
              <option value="127.0.0.1">127.0.0.1 (localhost)</option>
            </select>
          </div>
          <div style={card}>
            <h3 style={h3}>Terminal</h3>
            <div style={labelStyle}>Shell Padrao</div>
            <select value={shell} onChange={(e) => setShell(e.target.value)} style={selectStyle}>
              <option value="powershell">PowerShell</option>
              <option value="cmd">CMD</option>
              <option value="pwsh">PWSh</option>
              <option value="bash">Bash (WSL)</option>
            </select>
            <div style={{ ...labelStyle, marginTop: '8px' }}>Watcher Ignore</div>
            <input value={watcherIgnore} onChange={(e) => setWatcherIgnore(e.target.value)} placeholder="node_modules/**, dist/**" style={inputStyle()} />
          </div>
          <div style={{ ...card, gridColumn: '1 / -1' }}>
            <h3 style={h3}>Exibicao</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4px 20px' }}>
              <Toggle value={showReasoning} onChange={() => setShowReasoning(!showReasoning)} label="Mostrar Raciocinio" />
              <Toggle value={showToolCalls} onChange={() => setShowToolCalls(!showToolCalls)} label="Mostrar Tool Calls" />
              <Toggle value={compactMode} onChange={() => setCompactMode(!compactMode)} label="Modo Compacto" />
            </div>
            <div style={{ ...labelStyle, marginTop: '8px' }}>Idioma</div>
            <select value={language} onChange={(e) => setLanguage(e.target.value)} style={{ ...selectStyle, maxWidth: 200 }}>
              <option value="pt-BR">Portugues (Brasil)</option>
              <option value="en">English</option>
              <option value="es">Espanol</option>
            </select>
          </div>
        </div>
      )}

      {/* Save button */}
      <div style={{ marginTop: '16px', position: 'relative', display: 'inline-block' }}>
        <button onClick={handleSave} style={btnStyle('var(--accent)', 'var(--accent)')}>
          Salvar configuracoes
        </button>
        {toast && (
          <div style={{ position: 'absolute', bottom: -32, left: 0, whiteSpace: 'nowrap', border: '1px solid var(--accent-2)', borderRadius: 3, padding: '3px 10px', ...s({ color: 'var(--accent-2)', fontSize: '11px' }) }}>
            {toast}
          </div>
        )}
      </div>
    </div>
  );
}
