import React, { useState } from 'react';
import { API_BASE } from '../lib/constants';

export const SecurityToggle: React.FC = () => {
  const [isSandboxEnabled, setIsSandboxEnabled] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);

  const handleToggle = async () => {
    setLoading(true);
    const newValue = !isSandboxEnabled;
    try {
      const response = await fetch(`${API_BASE}/api/config/sandbox`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: newValue }),
      });
      if (response.ok) {
        setIsSandboxEnabled(newValue);
      } else {
        const errorData = await response.json().catch(() => ({}));
        alert(`Erro no servidor: ${errorData.detail || response.statusText}`);
      }
    } catch (error) {
      alert('Não foi possível conectar ao servidor. O backend está rodando?');
      console.error('Erro na requisição:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '16px',
        background: 'var(--bg)',
        borderRadius: '8px',
        border: '1px solid var(--bg-2)',
      }}
    >
      <div>
        <h3 style={{ fontSize: '14px', fontWeight: 600, color: 'var(--ink)', margin: 0 }}>
          Modo de Operação
        </h3>
        <p style={{ fontSize: '12px', color: 'var(--muted)', margin: '4px 0 0 0' }}>
          {isSandboxEnabled
            ? '🔒 Modo Restrito (Isolado na pasta do projeto)'
            : '🛠️ Modo Desenvolvedor (Acesso total ao sistema)'}
        </p>
      </div>
      <button
        onClick={handleToggle}
        disabled={loading}
        style={{
          position: 'relative',
          display: 'inline-flex',
          height: '24px',
          width: '44px',
          alignItems: 'center',
          borderRadius: '9999px',
          border: 'none',
          cursor: loading ? 'not-allowed' : 'pointer',
          opacity: loading ? 0.6 : 1,
          transition: 'background 0.2s',
          outline: 'none',
          background: isSandboxEnabled ? 'var(--blue)' : 'var(--accent)',
        }}
      >
        <span
          style={{
            display: 'inline-block',
            height: '16px',
            width: '16px',
            borderRadius: '9999px',
            background: '#fff',
            transition: 'transform 0.2s',
            transform: isSandboxEnabled ? 'translateX(24px)' : 'translateX(4px)',
          }}
        />
      </button>
    </div>
  );
};
