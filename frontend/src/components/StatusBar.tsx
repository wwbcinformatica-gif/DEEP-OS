import React from 'react';
import StatusIndicator from './StatusIndicator';

interface OllamaStatus {
  running: boolean;
  models?: string[];
}

interface StatusBarProps {
  prov: string;
  model: string;
  mood: string;
  ollSt?: OllamaStatus;
  termOpen: boolean;
  setTermOpen: (v: boolean) => void;
  theme: string;
  toggleTheme: () => void;
}

const StatusBar: React.FC<StatusBarProps> = ({
  prov,
  model,
  mood,
  ollSt,
  termOpen,
  setTermOpen,
  theme,
  toggleTheme,
}) => {
  return (
    <div className="status-bar">
      <div className="status-left" style={{ display: 'flex', flexDirection: 'row', gap: '12px', alignItems: 'center', whiteSpace: 'nowrap', minWidth: 0, overflow: 'hidden' }}>
        <span style={{ fontWeight: 700, whiteSpace: 'nowrap', flexShrink: 0 }}>
          openclaude
        </span>
        <span style={{ opacity: 0.5, whiteSpace: 'nowrap', flexShrink: 0 }}>|</span>
        <span style={{ whiteSpace: 'nowrap', flexShrink: 0 }}>{prov}</span>
        <span style={{ opacity: 0.5, whiteSpace: 'nowrap', flexShrink: 0 }}>|</span>
        <span
          style={{
            whiteSpace: 'nowrap',
            flexShrink: 0,
            maxWidth: 140,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
          }}
        >
          {model.split(':')[0]}
        </span>
        <span style={{ opacity: 0.5, whiteSpace: 'nowrap', flexShrink: 0 }}>|</span>
        <span style={{ whiteSpace: 'nowrap', flexShrink: 0 }}>{mood}</span>
      </div>
      <div className="status-right">
        <span
          style={{
            opacity: 0.45,
            marginRight: 8,
            letterSpacing: '0.3px',
          }}
        >
          Copyright © Empresa: WBC 2026
        </span>
        <button
          onClick={() => setTermOpen(!termOpen)}
          style={{
            background: termOpen ? 'rgba(255,122,26,0.15)' : 'transparent',
            border: '1px solid',
            borderColor: termOpen ? 'var(--accent)' : 'var(--line)',
            borderRadius: 4,
            fontSize: '10px',
            color: termOpen ? 'var(--accent)' : 'inherit',
            cursor: 'pointer',
            padding: '2px 8px',
            display: 'flex',
            alignItems: 'center',
            gap: 4,
            whiteSpace: 'nowrap',
          }}
          title="Abrir/fechar terminal (Ctrl+Shift+T)"
        >
          ⌨ {termOpen ? 'terminal aberto' : 'terminal'}
        </button>
        <button
          onClick={toggleTheme}
          style={{
            background: 'transparent',
            border: 'none',
            fontSize: '13px',
            color: 'inherit',
            cursor: 'pointer',
            opacity: 0.8,
            lineHeight: 1,
          }}
          title={`switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          aria-label={`switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
        >
          {theme === 'dark' ? '☀' : '☾'}
        </button>
        <StatusIndicator provider={prov} ollamaRunning={ollSt?.running} />
      </div>
    </div>
  );
};

export default StatusBar;
