import React, { useState } from 'react';

interface Instance {
  id: string;
  name: string;
  status: 'active' | 'inactive' | 'error';
  model: string;
  messagesUsed: number;
  createdAt: string;
}

const InstancesPage: React.FC = () => {
  const [instances, setInstances] = useState<Instance[]>([
    {
      id: '1',
      name: 'Agente Principal',
      status: 'active',
      model: 'MiMo V2.5',
      messagesUsed: 45,
      createdAt: '01/09/2026',
    },
  ]);

  const [showNewModal, setShowNewModal] = useState(false);
  const [newInstanceName, setNewInstanceName] = useState('');
  const [newInstanceModel, setNewInstanceModel] = useState('mimo-v2.5');

  const handleCreateInstance = () => {
    if (!newInstanceName.trim()) return;

    const newInstance: Instance = {
      id: String(Date.now()),
      name: newInstanceName,
      status: 'active',
      model: newInstanceModel,
      messagesUsed: 0,
      createdAt: new Date().toLocaleDateString('pt-BR'),
    };

    setInstances([...instances, newInstance]);
    setNewInstanceName('');
    setShowNewModal(false);
  };

  const handleDeleteInstance = (id: string) => {
    if (confirm('Tem certeza que deseja excluir esta instancia?')) {
      setInstances(instances.filter((i) => i.id !== id));
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return '#10b981';
      case 'inactive': return '#6b7280';
      case 'error': return '#ef4444';
      default: return '#6b7280';
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div>
          <h1 style={styles.title}>Instâncias</h1>
          <p style={styles.subtitle}>Gerencie seus agentes de IA</p>
        </div>
        <button style={styles.newButton} onClick={() => setShowNewModal(true)}>
          + Nova Instância
        </button>
      </div>

      {/* Stats */}
      <div style={styles.stats}>
        <div style={styles.statCard}>
          <span style={styles.statValue}>{instances.length}</span>
          <span style={styles.statLabel}>Total</span>
        </div>
        <div style={styles.statCard}>
          <span style={{...styles.statValue, color: '#10b981'}}>
            {instances.filter(i => i.status === 'active').length}
          </span>
          <span style={styles.statLabel}>Ativas</span>
        </div>
        <div style={styles.statCard}>
          <span style={styles.statValue}>1</span>
          <span style={styles.statLabel}>Limite</span>
        </div>
      </div>

      {/* Instances List */}
      <div style={styles.instancesList}>
        {instances.map((instance) => (
          <div key={instance.id} style={styles.instanceCard}>
            <div style={styles.instanceHeader}>
              <div style={styles.instanceInfo}>
                <h3 style={styles.instanceName}>{instance.name}</h3>
                <span style={{
                  ...styles.statusBadge,
                  backgroundColor: getStatusColor(instance.status) + '20',
                  color: getStatusColor(instance.status),
                }}>
                  {instance.status === 'active' ? 'Ativa' : 
                   instance.status === 'inactive' ? 'Inativa' : 'Erro'}
                </span>
              </div>
              <div style={styles.instanceActions}>
                <button style={styles.actionButton}>Configurar</button>
                <button 
                  style={{...styles.actionButton, ...styles.deleteButton}}
                  onClick={() => handleDeleteInstance(instance.id)}
                >
                  Excluir
                </button>
              </div>
            </div>
            
            <div style={styles.instanceDetails}>
              <div style={styles.detailItem}>
                <span style={styles.detailLabel}>Modelo:</span>
                <span style={styles.detailValue}>{instance.model}</span>
              </div>
              <div style={styles.detailItem}>
                <span style={styles.detailLabel}>Mensagens:</span>
                <span style={styles.detailValue}>{instance.messagesUsed}/20</span>
              </div>
              <div style={styles.detailItem}>
                <span style={styles.detailLabel}>Criada em:</span>
                <span style={styles.detailValue}>{instance.createdAt}</span>
              </div>
            </div>

            {/* Usage Bar */}
            <div style={styles.usageBar}>
              <div style={{
                ...styles.usageProgress,
                width: `${(instance.messagesUsed / 20) * 100}%`,
              }} />
            </div>
          </div>
        ))}

        {instances.length === 0 && (
          <div style={styles.emptyState}>
            <span style={styles.emptyIcon}>⚡</span>
            <h3>Nenhuma instancia criada</h3>
            <p>Crie sua primeira instancia para comecar a usar os agentes de IA.</p>
            <button style={styles.newButton} onClick={() => setShowNewModal(true)}>
              + Criar Primeira Instancia
            </button>
          </div>
        )}
      </div>

      {/* New Instance Modal */}
      {showNewModal && (
        <div style={styles.modalOverlay} onClick={() => setShowNewModal(false)}>
          <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
            <h2 style={styles.modalTitle}>Nova Instancia</h2>
            
            <div style={styles.formGroup}>
              <label style={styles.label}>Nome da Instancia</label>
              <input
                type="text"
                value={newInstanceName}
                onChange={(e) => setNewInstanceName(e.target.value)}
                placeholder="Ex: Meu Agente"
                style={styles.input}
              />
            </div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Modelo de IA</label>
              <select
                value={newInstanceModel}
                onChange={(e) => setNewInstanceModel(e.target.value)}
                style={styles.select}
              >
                <option value="mimo-v2.5">MiMo V2.5 (Gratis)</option>
                <option value="qwen2.5-coder">Qwen 2.5 Coder</option>
                <option value="deepseek-v4">DeepSeek V4 Flash</option>
              </select>
            </div>

            <div style={styles.modalActions}>
              <button style={styles.cancelButton} onClick={() => setShowNewModal(false)}>
                Cancelar
              </button>
              <button style={styles.createButton} onClick={handleCreateInstance}>
                Criar Instancia
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    padding: '40px',
    color: '#ffffff',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '32px',
  },
  title: {
    fontSize: '28px',
    fontWeight: 'bold',
    margin: '0 0 8px 0',
  },
  subtitle: {
    color: '#a0a0a0',
    margin: 0,
  },
  newButton: {
    background: 'linear-gradient(135deg, #00d9ff 0%, #00ff88 100%)',
    color: '#000',
    border: 'none',
    borderRadius: '8px',
    padding: '12px 24px',
    fontSize: '14px',
    fontWeight: '600',
    cursor: 'pointer',
  },
  stats: {
    display: 'flex',
    gap: '16px',
    marginBottom: '32px',
  },
  statCard: {
    background: 'rgba(255, 255, 255, 0.03)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    borderRadius: '12px',
    padding: '20px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    minWidth: '120px',
  },
  statValue: {
    fontSize: '28px',
    fontWeight: 'bold',
    color: '#00d9ff',
  },
  statLabel: {
    fontSize: '12px',
    color: '#a0a0a0',
    marginTop: '4px',
  },
  instancesList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  instanceCard: {
    background: 'rgba(255, 255, 255, 0.03)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    borderRadius: '12px',
    padding: '20px',
  },
  instanceHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '16px',
  },
  instanceInfo: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  instanceName: {
    margin: 0,
    fontSize: '18px',
    fontWeight: '600',
  },
  statusBadge: {
    padding: '4px 10px',
    borderRadius: '12px',
    fontSize: '12px',
    fontWeight: '500',
  },
  instanceActions: {
    display: 'flex',
    gap: '8px',
  },
  actionButton: {
    background: 'rgba(255, 255, 255, 0.05)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    borderRadius: '6px',
    padding: '8px 12px',
    color: '#a0a0a0',
    fontSize: '12px',
    cursor: 'pointer',
  },
  deleteButton: {
    color: '#ef4444',
    borderColor: 'rgba(239, 68, 68, 0.3)',
  },
  instanceDetails: {
    display: 'flex',
    gap: '24px',
    marginBottom: '16px',
  },
  detailItem: {},
  detailLabel: {
    fontSize: '12px',
    color: '#a0a0a0',
    display: 'block',
  },
  detailValue: {
    fontSize: '14px',
    color: '#ffffff',
  },
  usageBar: {
    height: '4px',
    background: 'rgba(255, 255, 255, 0.1)',
    borderRadius: '2px',
    overflow: 'hidden',
  },
  usageProgress: {
    height: '100%',
    background: 'linear-gradient(90deg, #00d9ff 0%, #00ff88 100%)',
    borderRadius: '2px',
    transition: 'width 0.3s ease',
  },
  emptyState: {
    textAlign: 'center',
    padding: '60px 40px',
    background: 'rgba(255, 255, 255, 0.02)',
    borderRadius: '12px',
    border: '1px dashed rgba(255, 255, 255, 0.1)',
  },
  emptyIcon: {
    fontSize: '48px',
    display: 'block',
    marginBottom: '16px',
  },
  modalOverlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'rgba(0, 0, 0, 0.8)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
  },
  modal: {
    background: '#1a1a2e',
    borderRadius: '16px',
    padding: '32px',
    width: '100%',
    maxWidth: '400px',
    border: '1px solid rgba(255, 255, 255, 0.1)',
  },
  modalTitle: {
    margin: '0 0 24px 0',
    fontSize: '20px',
    fontWeight: 'bold',
  },
  formGroup: {
    marginBottom: '20px',
  },
  label: {
    display: 'block',
    fontSize: '14px',
    color: '#a0a0a0',
    marginBottom: '8px',
  },
  input: {
    width: '100%',
    padding: '12px 16px',
    background: 'rgba(255, 255, 255, 0.05)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    borderRadius: '8px',
    color: '#ffffff',
    fontSize: '14px',
    boxSizing: 'border-box',
  },
  select: {
    width: '100%',
    padding: '12px 16px',
    background: 'rgba(255, 255, 255, 0.05)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    borderRadius: '8px',
    color: '#ffffff',
    fontSize: '14px',
    boxSizing: 'border-box',
  },
  modalActions: {
    display: 'flex',
    gap: '12px',
    justifyContent: 'flex-end',
  },
  cancelButton: {
    background: 'rgba(255, 255, 255, 0.05)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    borderRadius: '8px',
    padding: '10px 20px',
    color: '#a0a0a0',
    cursor: 'pointer',
  },
  createButton: {
    background: 'linear-gradient(135deg, #00d9ff 0%, #00ff88 100%)',
    border: 'none',
    borderRadius: '8px',
    padding: '10px 20px',
    color: '#000',
    fontWeight: '600',
    cursor: 'pointer',
  },
};

export default InstancesPage;
