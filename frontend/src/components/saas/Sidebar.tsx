import React from 'react';
import { getAvailableFeatures, planNames } from './planConfig';

interface SidebarProps {
  currentPage: string;
  onNavigate: (page: string) => void;
  user?: {
    name: string;
    plan: string;
    email: string;
  };
}

interface MenuItem {
  id: string;
  label: string;
  icon: string;
  badge?: string;
  badgeColor?: string;
  locked?: boolean;
}

const allMenuItems: MenuItem[] = [
  { id: 'plans', label: 'Planos', icon: '💎' },
  { id: 'downloads', label: 'Downloads', icon: '📦' },
  { id: 'instances', label: 'Instância', icon: '⚡' },
  { id: 'jarvis', label: 'Jarvis', icon: '🤖' },
  { id: 'commands', label: 'Commands', icon: '📜' },
  { id: 'triggers', label: 'Gatilhos', icon: '🔥' },
  { id: 'chatbot', label: 'ChatBot', icon: '💬', badge: 'PRO', badgeColor: '#8b5cf6' },
  { id: 'leads', label: 'Radar de Leads', icon: '📊', badge: 'BETA', badgeColor: '#10b981' },
  { id: 'reports', label: 'Relatórios', icon: '📈' },
  { id: 'announcements', label: 'Comunicado', icon: '📢' },
  { id: 'campaigns', label: 'Campanha Manual', icon: '🚀' },
  { id: 'auto-group', label: 'Msg Auto Grupo', icon: '💬' },
  { id: 'auto-private', label: 'Msg Auto Privado', icon: '✉️' },
  { id: 'pix', label: 'PIX', icon: '📱' },
  { id: 'settings', label: 'Configurações', icon: '⚙️' },
];

const Sidebar: React.FC<SidebarProps> = ({ currentPage, onNavigate, user }) => {
  const userPlan = user?.plan || 'free';
  const availableFeatures = getAvailableFeatures(userPlan);

  const menuItems = allMenuItems.map(item => ({
    ...item,
    locked: !availableFeatures.includes(item.id),
  }));

  const handleLogout = () => {
    localStorage.removeItem('saas_token');
    localStorage.removeItem('saas_user');
    window.location.reload();
  };

  const handleItemClick = (item: MenuItem) => {
    if (item.locked) {
      alert(`Este recurso está disponível no plano ${planNames[userPlan] || 'superior'}. Faça upgrade para acessar!`);
      return;
    }
    onNavigate(item.id);
  };

  return (
    <div className="saas-sidebar" style={styles.sidebar}>
      <div style={styles.header}>
        <div style={styles.logoContainer}>
          <div style={styles.logo}>a</div>
          <span style={styles.appName}>DEEP-OS</span>
        </div>
        <div style={styles.statusBadge}>
          <div style={styles.statusDot} />
          <span style={styles.statusText}>online</span>
        </div>
      </div>

      <nav style={styles.menu}>
        {menuItems.map((item) => (
          <button
            key={item.id}
            style={{
              ...styles.menuItem,
              ...(currentPage === item.id ? styles.menuItemActive : {}),
              ...(item.locked ? styles.menuItemLocked : {}),
            }}
            onClick={() => handleItemClick(item)}
          >
            <span style={styles.menuIcon}>{item.icon}</span>
            <span style={styles.menuLabel}>{item.label}</span>
            {item.locked && (
              <span style={styles.lockIcon}>🔒</span>
            )}
            {item.badge && !item.locked && (
              <span
                style={{
                  ...styles.badge,
                  background: item.badgeColor || '#8b5cf6',
                }}
              >
                {item.badge}
              </span>
            )}
          </button>
        ))}
      </nav>

      <div style={styles.footer}>
        <div style={styles.userInfo}>
          <div style={styles.avatar}>
            {user?.name?.charAt(0).toUpperCase() || 'D'}
          </div>
          <div style={styles.userDetails}>
            <span style={styles.userName}>{user?.name || 'Demo User'}</span>
            <span style={styles.userPlan}>{planNames[userPlan] || 'Free'}</span>
          </div>
        </div>
        <button style={styles.logoutButton} onClick={handleLogout}>
          <span style={styles.logoutIcon}>🚪</span>
          <span>Sair</span>
        </button>
      </div>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  sidebar: {
    width: '240px',
    height: '100vh',
    background: 'var(--saas-bg-sidebar)',
    backdropFilter: 'blur(var(--saas-glass-blur))',
    WebkitBackdropFilter: 'blur(var(--saas-glass-blur))',
    borderRight: '1px solid var(--saas-border)',
    display: 'flex',
    flexDirection: 'column',
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
    position: 'fixed',
    left: 0,
    top: 0,
    zIndex: 100,
  },
  header: {
    padding: '20px',
    borderBottom: '1px solid var(--saas-border)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  logoContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
  },
  logo: {
    width: '36px',
    height: '36px',
    background: 'linear-gradient(135deg, var(--saas-accent) 0%, var(--accent-green) 100%)',
    borderRadius: '10px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '16px',
    fontWeight: 'bold',
    color: '#000000',
  },
  appName: {
    fontSize: '16px',
    fontWeight: 'bold',
    color: 'var(--saas-text)',
  },
  statusBadge: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    background: 'rgba(16, 185, 129, 0.15)',
    padding: '4px 10px',
    borderRadius: '20px',
  },
  statusDot: {
    width: '8px',
    height: '8px',
    background: '#10b981',
    borderRadius: '50%',
    animation: 'pulse 2s infinite',
  },
  statusText: {
    fontSize: '12px',
    color: '#10b981',
    fontWeight: '500',
  },
  menu: {
    flex: 1,
    padding: '12px',
    overflowY: 'auto',
    display: 'flex',
    flexDirection: 'column',
    gap: '2px',
  },
  menuItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '12px 14px',
    border: 'none',
    borderRadius: '8px',
    background: 'transparent',
    color: 'var(--saas-text-muted)',
    fontSize: '14px',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    textAlign: 'left',
    width: '100%',
  },
  menuItemActive: {
    background: 'rgba(0, 217, 255, 0.12)',
    color: 'var(--saas-accent)',
  },
  menuItemLocked: {
    opacity: 0.5,
  },
  menuIcon: {
    fontSize: '16px',
    width: '20px',
    textAlign: 'center',
  },
  menuLabel: {
    flex: 1,
  },
  lockIcon: {
    fontSize: '12px',
    opacity: 0.6,
  },
  badge: {
    fontSize: '10px',
    fontWeight: 'bold',
    padding: '2px 6px',
    borderRadius: '4px',
    color: '#ffffff',
  },
  footer: {
    padding: '16px',
    borderTop: '1px solid var(--saas-border)',
  },
  userInfo: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    marginBottom: '12px',
  },
  avatar: {
    width: '36px',
    height: '36px',
    background: 'linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%)',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '14px',
    fontWeight: 'bold',
    color: '#ffffff',
  },
  userDetails: {
    display: 'flex',
    flexDirection: 'column',
  },
  userName: {
    fontSize: '14px',
    fontWeight: '500',
    color: 'var(--saas-text)',
  },
  userPlan: {
    fontSize: '12px',
    color: 'var(--saas-text-muted)',
    textTransform: 'capitalize',
  },
  logoutButton: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    width: '100%',
    padding: '10px',
    border: 'none',
    borderRadius: '8px',
    background: 'rgba(239, 68, 68, 0.1)',
    color: '#ef4444',
    fontSize: '14px',
    cursor: 'pointer',
    transition: 'background 0.2s ease',
  },
  logoutIcon: {
    fontSize: '14px',
  },
};

export default Sidebar;
