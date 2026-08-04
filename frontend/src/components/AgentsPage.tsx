import React from 'react';
import { AGENTS_LIST } from '../lib/constants';

export default function AgentsPage() {
  return (
    <div style={{ flex: 1, overflow: 'auto', padding: '20px' }}>
      <h2
        style={{
          fontFamily: 'inherit',
          fontSize: '1em',
          fontWeight: 600,
          color: 'var(--accent)',
          margin: '0 0 4px',
        }}
      >
        // agentes
      </h2>
      <p
        style={{
          fontFamily: 'inherit',
          fontSize: '1em',
          fontWeight: 600,
          color: '#9cdcfe',
          margin: '0 0 20px',
        }}
      >
        $ roteamento inteligente de tarefas
      </p>
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(190px, 1fr))',
          gap: '12px',
        }}
      >
        {AGENTS_LIST.map((a) => (
          <div
            key={a.name}
            style={{
              border: '1px solid var(--line)',
              borderRadius: '4px',
              padding: '16px',
              background: 'var(--bg)',
            }}
          >
            <h3
              style={{
                fontFamily: 'inherit',
                fontSize: '1em',
                fontWeight: 600,
                color: a.color,
                margin: '0 0 6px',
              }}
            >
              {'>'} {a.name}
            </h3>
            <p
              style={{
                fontFamily: 'inherit',
                fontSize: '1em',
                fontWeight: 600,
                color: 'var(--muted)',
                margin: 0,
              }}
            >
              {a.desc}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
