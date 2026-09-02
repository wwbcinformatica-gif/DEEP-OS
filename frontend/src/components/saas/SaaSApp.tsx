import React, { useState, useEffect } from 'react';
import AuthPage from './AuthPage';
import PricingPage from './PricingPage';
import Sidebar from './Sidebar';
import InstancesPage from './InstancesPage';
import SettingsPage from './SettingsPage';
import HelpModal from './HelpModal';
import SpaceBackground from './SpaceBackground';
import AdminLogin from './AdminLogin';
import AdminDashboard from './AdminDashboard';
import DownloadsPage from './DownloadsPage';
import JarvisPage from './JarvisPage';
import { AppSettingsProvider } from './AppSettingsContext';

interface User {
  id: string;
  name: string;
  email: string;
  plan: string;
  status: string;
}

const SaaSApp: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [currentPage, setCurrentPage] = useState('plans');
  const [showHelp, setShowHelp] = useState(false);
  
  // Admin state
  const [isAdminRoute, setIsAdminRoute] = useState(false);
  const [isAdminAuthenticated, setIsAdminAuthenticated] = useState(false);
  const [adminEmail, setAdminEmail] = useState('');

  useEffect(() => {
    // Check if URL is /admin
    setIsAdminRoute(window.location.pathname === '/admin');
    
    // Check user auth
    const token = localStorage.getItem('saas_token');
    const savedUser = localStorage.getItem('saas_user');
    
    if (token && savedUser) {
      setIsAuthenticated(true);
      setUser(JSON.parse(savedUser));
    }
    
    // Check admin auth
    const adminToken = localStorage.getItem('admin_token');
    const savedAdminEmail = localStorage.getItem('admin_email');
    
    if (adminToken && savedAdminEmail) {
      setIsAdminAuthenticated(true);
      setAdminEmail(savedAdminEmail);
    }

    // Listen for URL changes
    const handlePopState = () => {
      setIsAdminRoute(window.location.pathname === '/admin');
    };
    
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const handleAuth = (token: string, userData: any) => {
    setIsAuthenticated(true);
    setUser(userData);
  };

  const handleAdminLogin = (token: string, email: string) => {
    setIsAdminAuthenticated(true);
    setAdminEmail(email);
  };

  const handleAdminLogout = () => {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_email');
    setIsAdminAuthenticated(false);
    setAdminEmail('');
    window.location.href = '/';
  };

  const handleNavigate = (page: string) => {
    if (page === 'help') {
      setShowHelp(true);
    } else {
      setCurrentPage(page);
    }
  };

  // Admin route
  if (isAdminRoute) {
    if (!isAdminAuthenticated) {
      return (
        <AppSettingsProvider>
          <SpaceBackground />
          <AdminLogin onLogin={handleAdminLogin} />
        </AppSettingsProvider>
      );
    }
    
    return (
      <AppSettingsProvider>
        <SpaceBackground />
        <AdminDashboard onLogout={handleAdminLogout} />
      </AppSettingsProvider>
    );
  }

  // User route
  if (!isAuthenticated) {
    return (
      <AppSettingsProvider>
        <SpaceBackground />
        <AuthPage onAuth={handleAuth} />
      </AppSettingsProvider>
    );
  }

  const renderContent = () => {
    switch (currentPage) {
      case 'plans':
        return <PricingPage />;
      case 'instances':
        return <InstancesPage />;
      case 'settings':
        return <SettingsPage />;
      case 'downloads':
        return <DownloadsPage />;
      case 'jarvis':
        return <JarvisPage />;
      case 'commands':
        return (
          <div style={styles.placeholder}>
            <span style={styles.placeholderIcon}>📜</span>
            <h2>Commands</h2>
            <p>Gerencie comandos personalizados para seus agentes</p>
            <div style={styles.comingSoon}>Em breve</div>
          </div>
        );
      case 'triggers':
        return (
          <div style={styles.placeholder}>
            <span style={styles.placeholderIcon}>🔥</span>
            <h2>Gatilhos</h2>
            <p>Configure gatilhos automaticos para acoes</p>
            <div style={styles.comingSoon}>Em breve</div>
          </div>
        );
      case 'chatbot':
        return (
          <div style={styles.placeholder}>
            <span style={styles.placeholderIcon}>💬</span>
            <h2>ChatBot</h2>
            <p>Configure seu chatbot inteligente</p>
            <div style={styles.proBadge}>PRO</div>
          </div>
        );
      case 'leads':
        return (
          <div style={styles.placeholder}>
            <span style={styles.placeholderIcon}>📊</span>
            <h2>Radar de Leads</h2>
            <p>Monitore e capture leads automaticamente</p>
            <div style={styles.betaBadge}>BETA</div>
          </div>
        );
      case 'reports':
        return (
          <div style={styles.placeholder}>
            <span style={styles.placeholderIcon}>📈</span>
            <h2>Relatórios</h2>
            <p>Visualize metricas e analises detalhadas</p>
            <div style={styles.comingSoon}>Em breve</div>
          </div>
        );
      case 'announcements':
        return (
          <div style={styles.placeholder}>
            <span style={styles.placeholderIcon}>📢</span>
            <h2>Comunicados</h2>
            <p>Veja as ultimas novidades e comunicados</p>
            <div style={styles.comingSoon}>Em breve</div>
          </div>
        );
      case 'campaigns':
        return (
          <div style={styles.placeholder}>
            <span style={styles.placeholderIcon}>🚀</span>
            <h2>Campanha Manual</h2>
            <p>Crie e gerencie campanhas de mensagens</p>
            <div style={styles.comingSoon}>Em breve</div>
          </div>
        );
      case 'auto-group':
        return (
          <div style={styles.placeholder}>
            <span style={styles.placeholderIcon}>💬</span>
            <h2>Mensagens Auto Grupo</h2>
            <p>Automatize mensagens para grupos</p>
            <div style={styles.comingSoon}>Em breve</div>
          </div>
        );
      case 'auto-private':
        return (
          <div style={styles.placeholder}>
            <span style={styles.placeholderIcon}>💬</span>
            <h2>Mensagens Auto Privado</h2>
            <p>Automatize mensagens privadas</p>
            <div style={styles.comingSoon}>Em breve</div>
          </div>
        );
      case 'pix':
        return (
          <div style={styles.placeholder}>
            <span style={styles.placeholderIcon}>📱</span>
            <h2>PIX</h2>
            <p>Gerencie seus recebimentos via PIX</p>
            <div style={styles.comingSoon}>Em breve</div>
          </div>
        );
      case 'download':
        return (
          <div style={styles.placeholder}>
            <span style={styles.placeholderIcon}>📥</span>
            <h2>Download Jarvis</h2>
            <p>Baixe o Jarvis para seu computador</p>
            <button style={styles.downloadBtn}>
              Baixar Jarvis v2.0
            </button>
          </div>
        );
      default:
        return <PricingPage />;
    }
  };

  return (
    <AppSettingsProvider>
      <div style={styles.appContainer}>
        <SpaceBackground />
        <Sidebar
          currentPage={currentPage}
          onNavigate={handleNavigate}
          user={user || undefined}
        />
        <main style={styles.mainContent}>
          {renderContent()}
        </main>
        
        <HelpModal isOpen={showHelp} onClose={() => setShowHelp(false)} />
      </div>
    </AppSettingsProvider>
  );
};

const styles: Record<string, React.CSSProperties> = {
  appContainer: {
    display: 'flex',
    minHeight: '100vh',
    position: 'relative',
    zIndex: 1,
  },
  mainContent: {
    flex: 1,
    marginLeft: '240px',
    minHeight: '100vh',
    overflowY: 'auto',
    paddingBottom: '40px',
    background: 'transparent',
    position: 'relative',
    zIndex: 1,
  },
  placeholder: {
    padding: '60px 40px',
    textAlign: 'center',
    color: '#ffffff',
  },
  placeholderIcon: {
    fontSize: '64px',
    display: 'block',
    marginBottom: '24px',
  },
  comingSoon: {
    display: 'inline-block',
    marginTop: '24px',
    padding: '8px 16px',
    background: 'rgba(0, 217, 255, 0.1)',
    borderRadius: '8px',
    color: '#00d9ff',
    fontSize: '14px',
    fontWeight: '500',
  },
  proBadge: {
    display: 'inline-block',
    marginTop: '24px',
    padding: '8px 16px',
    background: 'linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%)',
    borderRadius: '8px',
    color: '#ffffff',
    fontSize: '14px',
    fontWeight: 'bold',
  },
  betaBadge: {
    display: 'inline-block',
    marginTop: '24px',
    padding: '8px 16px',
    background: 'rgba(16, 185, 129, 0.1)',
    borderRadius: '8px',
    color: '#10b981',
    fontSize: '14px',
    fontWeight: '500',
  },
  downloadBtn: {
    marginTop: '24px',
    padding: '14px 32px',
    background: 'linear-gradient(135deg, #00d9ff 0%, #00ff88 100%)',
    border: 'none',
    borderRadius: '8px',
    color: '#000',
    fontSize: '16px',
    fontWeight: '600',
    cursor: 'pointer',
  },
};

export default SaaSApp;
