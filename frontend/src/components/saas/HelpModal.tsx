import React, { useState } from 'react';

interface HelpModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const HelpModal: React.FC<HelpModalProps> = ({ isOpen, onClose }) => {
  const [activeSection, setActiveSection] = useState('getting-started');

  if (!isOpen) return null;

  const sections = [
    { id: 'getting-started', title: 'Primeiros Passos', icon: '🚀' },
    { id: 'instances', title: 'Instâncias', icon: '⚡' },
    { id: 'chatbot', title: 'ChatBot', icon: '🤖' },
    { id: 'billing', title: 'Cobranca', icon: '💳' },
    { id: 'faq', title: 'Perguntas Frequentes', icon: '❓' },
  ];

  const renderContent = () => {
    switch (activeSection) {
      case 'getting-started':
        return (
          <div>
            <h3 style={styles.helpTitle}>Bem-vindo ao DEEP-OS!</h3>
            <p style={styles.helpText}>
              Sua plataforma de agentes de IA esta pronta para uso. Siga os passos abaixo para comecar:
            </p>
            <div style={styles.helpSteps}>
              <div style={styles.helpStep}>
                <span style={styles.stepNumber}>1</span>
                <div>
                  <strong>Crie sua conta</strong>
                  <p>Voce ja fez isso! Bem-vindo!</p>
                </div>
              </div>
              <div style={styles.helpStep}>
                <span style={styles.stepNumber}>2</span>
                <div>
                  <strong>Escolha um plano</strong>
                  <p>Acesse "Planos" para ver as opcoes disponiveis</p>
                </div>
              </div>
              <div style={styles.helpStep}>
                <span style={styles.stepNumber}>3</span>
                <div>
                  <strong>Crie uma instancia</strong>
                  <p>Va em "Instancia" e crie seu primeiro agente</p>
                </div>
              </div>
              <div style={styles.helpStep}>
                <span style={styles.stepNumber}>4</span>
                <div>
                  <strong>Configure e use</strong>
                  <p>Personalize seu agente e comece a usar!</p>
                </div>
              </div>
            </div>
          </div>
        );
      case 'instances':
        return (
          <div>
            <h3 style={styles.helpTitle}>Gerenciando Instancias</h3>
            <p style={styles.helpText}>
              Instancias sao ambientes isolados onde seus agentes de IA rodam.
            </p>
            <div style={styles.helpSection}>
              <h4>Criar nova instancia:</h4>
              <ol style={styles.helpList}>
                <li>Clique em "Instancia" no menu lateral</li>
                <li>Clique em "Nova Instancia"</li>
                <li>Escolha um nome para a instancia</li>
                <li>Selecione o modelo de IA</li>
                <li>Clique em "Criar"</li>
              </ol>
            </div>
            <div style={styles.helpSection}>
              <h4>Limites por plano:</h4>
              <ul style={styles.helpList}>
                <li><strong>Gratuito:</strong> 1 instancia</li>
                <li><strong>Mensal:</strong> 3 instancias</li>
                <li><strong>Trimestral:</strong> 5 instancias</li>
                <li><strong>Anual:</strong> 10 instancias</li>
              </ul>
            </div>
          </div>
        );
      case 'chatbot':
        return (
          <div>
            <h3 style={styles.helpTitle}>Usando o ChatBot</h3>
            <p style={styles.helpText}>
              O ChatBot permite conversar com agentes de IA em tempo real.
            </p>
            <div style={styles.helpSection}>
              <h4>Como usar:</h4>
              <ol style={styles.helpList}>
                <li>Acesse "ChatBot" no menu lateral</li>
                <li>Selecione a instancia ativa</li>
                <li>Digite sua mensagem</li>
                <li>Pressione Enter para enviar</li>
              </ol>
            </div>
            <div style={styles.helpSection}>
              <h4>Comandos especiais:</h4>
              <ul style={styles.helpList}>
                <li><code>/novo</code> - Nova conversa</li>
                <li><code>/limpar</code> - Limpar historico</li>
                <li><code>/ajuda</code> - Ver comandos</li>
              </ul>
            </div>
            <div style={styles.proTip}>
              <strong>Dica PRO:</strong> O ChatBot esta disponivel para planos Mensal e superiores.
            </div>
          </div>
        );
      case 'billing':
        return (
          <div>
            <h3 style={styles.helpTitle}>Cobranca e Pagamentos</h3>
            <p style={styles.helpText}>
              Gerencie sua assinatura e forme de pagamento.
            </p>
            <div style={styles.helpSection}>
              <h4>Formas de pagamento aceitas:</h4>
              <ul style={styles.helpList}>
                <li><strong>PIX:</strong> Aprovacao instantanea</li>
                <li><strong>Cartao de Credito:</strong> Ate 12x</li>
                <li><strong>Boleto:</strong> Vencimento em 3 dias</li>
              </ul>
            </div>
            <div style={styles.helpSection}>
              <h4>Gerenciar assinatura:</h4>
              <ul style={styles.helpList}>
                <li>Acesse "Configuracoes" no menu</li>
                <li>Clique em "Gerenciar Assinatura"</li>
                <li>Altere ou cancele quando quiser</li>
              </ul>
            </div>
          </div>
        );
      case 'faq':
        return (
          <div>
            <h3 style={styles.helpTitle}>Perguntas Frequentes</h3>
            <div style={styles.faqItem}>
              <strong>Posso usar em multiplos dispositivos?</strong>
              <p>Sim! Acesse de qualquer navegador.</p>
            </div>
            <div style={styles.faqItem}>
              <strong>O que acontece se eu atingir o limite?</strong>
              <p>Aguarde ate o proximo dia ou faca upgrade do plano.</p>
            </div>
            <div style={styles.faqItem}>
              <strong>Meus dados estao seguros?</strong>
              <p>Sim! Usamos criptografia e isolamento completo.</p>
            </div>
            <div style={styles.faqItem}>
              <strong>Como alterar meu plano?</strong>
              <p>Acesse "Planos" e escolha o novo plano.</p>
            </div>
            <div style={styles.faqItem}>
              <strong>Posso cancelar a qualquer momento?</strong>
              <p>Sim, sem multa. Mantem acesso ate o fim do periodo.</p>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div style={styles.modalOverlay} onClick={onClose}>
      <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div style={styles.modalHeader}>
          <h2 style={styles.modalTitle}>Central de Ajuda</h2>
          <button style={styles.closeButton} onClick={onClose}>X</button>
        </div>
        
        <div style={styles.modalBody}>
          <div style={styles.helpSidebar}>
            {sections.map((section) => (
              <button
                key={section.id}
                style={{
                  ...styles.helpNavItem,
                  ...(activeSection === section.id ? styles.helpNavItemActive : {}),
                }}
                onClick={() => setActiveSection(section.id)}
              >
                <span>{section.icon}</span>
                <span>{section.title}</span>
              </button>
            ))}
          </div>
          
          <div style={styles.helpContent}>
            {renderContent()}
          </div>
        </div>
      </div>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
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
    padding: '20px',
  },
  modal: {
    background: '#1a1a2e',
    borderRadius: '16px',
    width: '100%',
    maxWidth: '800px',
    maxHeight: '80vh',
    overflow: 'hidden',
    border: '1px solid rgba(255, 255, 255, 0.1)',
  },
  modalHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '20px 24px',
    borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
  },
  modalTitle: {
    margin: 0,
    fontSize: '20px',
    fontWeight: 'bold',
    color: '#ffffff',
  },
  closeButton: {
    background: 'rgba(255, 255, 255, 0.1)',
    border: 'none',
    borderRadius: '8px',
    color: '#ffffff',
    width: '32px',
    height: '32px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: 'bold',
  },
  modalBody: {
    display: 'flex',
    minHeight: '400px',
  },
  helpSidebar: {
    width: '200px',
    borderRight: '1px solid rgba(255, 255, 255, 0.1)',
    padding: '16px 0',
  },
  helpNavItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    width: '100%',
    padding: '12px 16px',
    border: 'none',
    background: 'transparent',
    color: '#a0a0a0',
    cursor: 'pointer',
    textAlign: 'left',
    fontSize: '14px',
  },
  helpNavItemActive: {
    background: 'rgba(0, 217, 255, 0.1)',
    color: '#00d9ff',
    borderLeft: '3px solid #00d9ff',
  },
  helpContent: {
    flex: 1,
    padding: '24px',
    overflowY: 'auto',
    color: '#ffffff',
  },
  helpTitle: {
    fontSize: '18px',
    fontWeight: 'bold',
    marginTop: 0,
    marginBottom: '16px',
    color: '#00d9ff',
  },
  helpText: {
    color: '#a0a0a0',
    lineHeight: 1.6,
    marginBottom: '20px',
  },
  helpSteps: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  helpStep: {
    display: 'flex',
    gap: '16px',
    alignItems: 'flex-start',
  },
  stepNumber: {
    width: '28px',
    height: '28px',
    background: 'linear-gradient(135deg, #00d9ff 0%, #00ff88 100%)',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontWeight: 'bold',
    color: '#000',
    flexShrink: 0,
  },
  helpSection: {
    marginBottom: '24px',
  },
  helpList: {
    paddingLeft: '20px',
    color: '#a0a0a0',
    lineHeight: 1.8,
  },
  proTip: {
    background: 'rgba(139, 92, 246, 0.1)',
    border: '1px solid rgba(139, 92, 246, 0.3)',
    borderRadius: '8px',
    padding: '12px 16px',
    color: '#a78bfa',
    fontSize: '14px',
  },
  faqItem: {
    marginBottom: '16px',
    paddingBottom: '16px',
    borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
  },
};

export default HelpModal;
