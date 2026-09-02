import React, { useEffect, useState } from 'react';

interface AdminDashboardProps {
  onLogout: () => void;
}

interface DashboardStats {
  total_tenants: number;
  active_tenants: number;
  tenants_by_plan: Record<string, number>;
  mrr: number;
  new_this_month: number;
}

interface Tenant {
  id: string;
  name: string;
  email: string;
  plan: string;
  status: string;
  created_at: string;
  last_login: string | null;
}

const AdminDashboard: React.FC<AdminDashboardProps> = ({ onLogout }) => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'tenants' | 'plans'>('overview');

  const token = localStorage.getItem('admin_token');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [statsRes, tenantsRes] = await Promise.all([
        fetch('/admin/dashboard/stats', {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch('/admin/tenants?limit=50', {
          headers: { Authorization: `Bearer ${token}` },
        }),
      ]);

      if (statsRes.ok) {
        setStats(await statsRes.json());
      }

      if (tenantsRes.ok) {
        const data = await tenantsRes.json();
        setTenants(data.tenants || []);
      }
    } catch (error) {
      console.error('Erro ao buscar dados:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSuspendTenant = async (tenantId: string) => {
    if (!confirm('Tem certeza que deseja suspender este tenant?')) return;

    try {
      await fetch(`/admin/tenants/${tenantId}/suspend`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      fetchData();
    } catch (error) {
      console.error('Erro ao suspender:', error);
    }
  };

  const handleReactivateTenant = async (tenantId: string) => {
    try {
      await fetch(`/admin/tenants/${tenantId}/reactivate`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      fetchData();
    } catch (error) {
      console.error('Erro ao reativar:', error);
    }
  };

  const getPlanColor = (plan: string) => {
    switch (plan) {
      case 'free': return '#6b7280';
      case 'monthly': return '#3b82f6';
      case 'quarterly': return '#8b5cf6';
      case 'annual': return '#10b981';
      default: return '#6b7280';
    }
  };

  const getPlanName = (plan: string) => {
    switch (plan) {
      case 'free': return 'Gratuito';
      case 'monthly': return 'Mensal';
      case 'quarterly': return 'Trimestral';
      case 'annual': return 'Anual';
      default: return plan;
    }
  };

  if (loading) {
    return (
      <div style={styles.loading}>
        <div style={styles.spinner} />
        <p>Carregando dados...</p>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      {/* Header */}
      <header style={styles.header}>
        <div style={styles.headerLeft}>
          <div style={styles.logo}>A</div>
          <div>
            <h1 style={styles.headerTitle}>Painel Mestre</h1>
            <p style={styles.headerSubtitle}>DEEP-OS Admin</p>
          </div>
        </div>
        <div style={styles.headerRight}>
          <span style={styles.adminBadge}>ADMIN</span>
          <button style={styles.logoutBtn} onClick={onLogout}>
            Sair
          </button>
        </div>
      </header>

      {/* Tabs */}
      <div style={styles.tabs}>
        <button
          style={{...styles.tab, ...(activeTab === 'overview' ? styles.tabActive : {})}}
          onClick={() => setActiveTab('overview')}
        >
          Visão Geral
        </button>
        <button
          style={{...styles.tab, ...(activeTab === 'tenants' ? styles.tabActive : {})}}
          onClick={() => setActiveTab('tenants')}
        >
          Assinantes
        </button>
        <button
          style={{...styles.tab, ...(activeTab === 'plans' ? styles.tabActive : {})}}
          onClick={() => setActiveTab('plans')}
        >
          Planos
        </button>
      </div>

      {/* Content */}
      <main style={styles.main}>
        {activeTab === 'overview' && stats && (
          <div style={styles.overview}>
            {/* Stats Cards */}
            <div style={styles.statsGrid}>
              <div style={styles.statCard}>
                <span style={styles.statIcon}>👥</span>
                <div style={styles.statInfo}>
                  <span style={styles.statValue}>{stats.total_tenants}</span>
                  <span style={styles.statLabel}>Total de Assinantes</span>
                </div>
              </div>
              <div style={{...styles.statCard, borderColor: '#10b981'}}>
                <span style={styles.statIcon}>✅</span>
                <div style={styles.statInfo}>
                  <span style={{...styles.statValue, color: '#10b981'}}>{stats.active_tenants}</span>
                  <span style={styles.statLabel}>Ativos</span>
                </div>
              </div>
              <div style={{...styles.statCard, borderColor: '#8b5cf6'}}>
                <span style={styles.statIcon}>💰</span>
                <div style={styles.statInfo}>
                  <span style={{...styles.statValue, color: '#8b5cf6'}}>R$ {stats.mrr.toFixed(2)}</span>
                  <span style={styles.statLabel}>Receita Mensal</span>
                </div>
              </div>
              <div style={{...styles.statCard, borderColor: '#f59e0b'}}>
                <span style={styles.statIcon}>📈</span>
                <div style={styles.statInfo}>
                  <span style={{...styles.statValue, color: '#f59e0b'}}>{stats.new_this_month}</span>
                  <span style={styles.statLabel}>Novos este Mês</span>
                </div>
              </div>
            </div>

            {/* Plan Distribution */}
            <div style={styles.card}>
              <h3 style={styles.cardTitle}>Distribuição por Plano</h3>
              <div style={styles.planDistribution}>
                {Object.entries(stats.tenants_by_plan).map(([plan, count]) => (
                  <div key={plan} style={styles.planBar}>
                    <div style={styles.planBarHeader}>
                      <span style={styles.planBarName}>{getPlanName(plan)}</span>
                      <span style={styles.planBarCount}>{count}</span>
                    </div>
                    <div style={styles.planBarTrack}>
                      <div 
                        style={{
                          ...styles.planBarFill,
                          width: `${stats.total_tenants > 0 ? (count / stats.total_tenants) * 100 : 0}%`,
                          background: getPlanColor(plan),
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'tenants' && (
          <div style={styles.tenantsSection}>
            <div style={styles.card}>
              <h3 style={styles.cardTitle}>Todos os Assinantes ({tenants.length})</h3>
              
              {tenants.length === 0 ? (
                <div style={styles.emptyState}>
                  <span style={styles.emptyIcon}>👥</span>
                  <p>Nenhum assinante ainda</p>
                </div>
              ) : (
                <div style={styles.tableContainer}>
                  <table style={styles.table}>
                    <thead>
                      <tr>
                        <th style={styles.th}>Nome</th>
                        <th style={styles.th}>Email</th>
                        <th style={styles.th}>Plano</th>
                        <th style={styles.th}>Status</th>
                        <th style={styles.th}>Criado em</th>
                        <th style={styles.th}>Ações</th>
                      </tr>
                    </thead>
                    <tbody>
                      {tenants.map((tenant) => (
                        <tr key={tenant.id} style={styles.tr}>
                          <td style={styles.td}>{tenant.name}</td>
                          <td style={styles.td}>{tenant.email}</td>
                          <td style={styles.td}>
                            <span style={{
                              ...styles.planBadge,
                              background: getPlanColor(tenant.plan) + '20',
                              color: getPlanColor(tenant.plan),
                            }}>
                              {getPlanName(tenant.plan)}
                            </span>
                          </td>
                          <td style={styles.td}>
                            <span style={{
                              ...styles.statusBadge,
                              background: tenant.status === 'active' ? '#10b98120' : '#ef444420',
                              color: tenant.status === 'active' ? '#10b981' : '#ef4444',
                            }}>
                              {tenant.status === 'active' ? 'Ativo' : 'Suspenso'}
                            </span>
                          </td>
                          <td style={styles.td}>
                            {new Date(tenant.created_at).toLocaleDateString('pt-BR')}
                          </td>
                          <td style={styles.td}>
                            <div style={styles.actions}>
                              {tenant.status === 'active' ? (
                                <button 
                                  style={styles.suspendBtn}
                                  onClick={() => handleSuspendTenant(tenant.id)}
                                >
                                  Suspender
                                </button>
                              ) : (
                                <button 
                                  style={styles.reactivateBtn}
                                  onClick={() => handleReactivateTenant(tenant.id)}
                                >
                                  Reativar
                                </button>
                              )}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'plans' && (
          <div style={styles.plansSection}>
            <div style={styles.card}>
              <h3 style={styles.cardTitle}>Planos Disponíveis</h3>
              <div style={styles.plansGrid}>
                <div style={styles.planCard}>
                  <h4 style={styles.planCardName}>Gratuito</h4>
                  <div style={styles.planCardPrice}>R$ 0</div>
                  <ul style={styles.planCardFeatures}>
                    <li>1 instância</li>
                    <li>20 mensagens/dia</li>
                    <li>Suporte básico</li>
                  </ul>
                </div>
                <div style={{...styles.planCard, borderColor: '#3b82f6'}}>
                  <h4 style={styles.planCardName}>Mensal</h4>
                  <div style={styles.planCardPrice}>R$ 14,99</div>
                  <ul style={styles.planCardFeatures}>
                    <li>3 instâncias</li>
                    <li>Mensagens ilimitadas</li>
                    <li>Suporte prioritário</li>
                  </ul>
                </div>
                <div style={{...styles.planCard, borderColor: '#8b5cf6'}}>
                  <h4 style={styles.planCardName}>Trimestral</h4>
                  <div style={styles.planCardPrice}>R$ 29,99</div>
                  <ul style={styles.planCardFeatures}>
                    <li>5 instâncias</li>
                    <li>33% de desconto</li>
                    <li>Radar de Leads</li>
                  </ul>
                </div>
                <div style={{...styles.planCard, borderColor: '#10b981'}}>
                  <h4 style={styles.planCardName}>Anual</h4>
                  <div style={styles.planCardPrice}>R$ 79,99</div>
                  <ul style={styles.planCardFeatures}>
                    <li>10 instâncias</li>
                    <li>71% de desconto</li>
                    <li>Jarvis Vitalício</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #0a0a1a 0%, #1a0a2e 50%, #0a1a2e 100%)',
    color: '#ffffff',
  },
  loading: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100vh',
    gap: '16px',
  },
  spinner: {
    width: '40px',
    height: '40px',
    border: '3px solid rgba(139, 92, 246, 0.3)',
    borderTopColor: '#8b5cf6',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '20px 40px',
    background: 'rgba(10, 10, 20, 0.8)',
    borderBottom: '1px solid rgba(139, 92, 246, 0.2)',
  },
  headerLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
  },
  logo: {
    width: '48px',
    height: '48px',
    background: 'linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%)',
    borderRadius: '12px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '24px',
    fontWeight: 'bold',
  },
  headerTitle: {
    fontSize: '24px',
    fontWeight: 'bold',
    margin: 0,
    background: 'linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
  },
  headerSubtitle: {
    fontSize: '12px',
    color: '#a0a0a0',
    margin: 0,
  },
  headerRight: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
  },
  adminBadge: {
    background: 'rgba(139, 92, 246, 0.2)',
    color: '#8b5cf6',
    padding: '6px 12px',
    borderRadius: '8px',
    fontSize: '12px',
    fontWeight: 'bold',
  },
  logoutBtn: {
    background: 'rgba(239, 68, 68, 0.1)',
    border: '1px solid rgba(239, 68, 68, 0.3)',
    borderRadius: '8px',
    padding: '10px 20px',
    color: '#ef4444',
    fontSize: '14px',
    cursor: 'pointer',
  },
  tabs: {
    display: 'flex',
    gap: '4px',
    padding: '20px 40px 0',
    background: 'rgba(10, 10, 20, 0.5)',
  },
  tab: {
    padding: '12px 24px',
    border: 'none',
    borderRadius: '8px 8px 0 0',
    background: 'rgba(255, 255, 255, 0.03)',
    color: '#a0a0a0',
    fontSize: '14px',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'all 0.2s',
  },
  tabActive: {
    background: 'rgba(139, 92, 246, 0.1)',
    color: '#8b5cf6',
  },
  main: {
    padding: '40px',
  },
  overview: {},
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
    gap: '20px',
    marginBottom: '32px',
  },
  statCard: {
    background: 'rgba(255, 255, 255, 0.03)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    borderRadius: '16px',
    padding: '24px',
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
  },
  statIcon: {
    fontSize: '32px',
  },
  statInfo: {
    display: 'flex',
    flexDirection: 'column',
  },
  statValue: {
    fontSize: '28px',
    fontWeight: 'bold',
    color: '#ffffff',
  },
  statLabel: {
    fontSize: '13px',
    color: '#a0a0a0',
  },
  card: {
    background: 'rgba(255, 255, 255, 0.03)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    borderRadius: '16px',
    padding: '24px',
  },
  cardTitle: {
    fontSize: '18px',
    fontWeight: '600',
    margin: '0 0 24px 0',
    color: '#ffffff',
  },
  planDistribution: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  planBar: {},
  planBarHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: '8px',
  },
  planBarName: {
    fontSize: '14px',
    color: '#d0d0d0',
  },
  planBarCount: {
    fontSize: '14px',
    color: '#ffffff',
    fontWeight: '600',
  },
  planBarTrack: {
    height: '8px',
    background: 'rgba(255, 255, 255, 0.05)',
    borderRadius: '4px',
    overflow: 'hidden',
  },
  planBarFill: {
    height: '100%',
    borderRadius: '4px',
    transition: 'width 0.3s ease',
  },
  tenantsSection: {},
  emptyState: {
    textAlign: 'center',
    padding: '60px 20px',
    color: '#a0a0a0',
  },
  emptyIcon: {
    fontSize: '48px',
    display: 'block',
    marginBottom: '16px',
  },
  tableContainer: {
    overflowX: 'auto',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
  },
  th: {
    textAlign: 'left',
    padding: '12px 16px',
    borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
    color: '#a0a0a0',
    fontSize: '12px',
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },
  tr: {
    borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
  },
  td: {
    padding: '16px',
    fontSize: '14px',
  },
  planBadge: {
    padding: '4px 10px',
    borderRadius: '6px',
    fontSize: '12px',
    fontWeight: '500',
  },
  statusBadge: {
    padding: '4px 10px',
    borderRadius: '6px',
    fontSize: '12px',
    fontWeight: '500',
  },
  actions: {
    display: 'flex',
    gap: '8px',
  },
  suspendBtn: {
    background: 'rgba(239, 68, 68, 0.1)',
    border: '1px solid rgba(239, 68, 68, 0.3)',
    borderRadius: '6px',
    padding: '6px 12px',
    color: '#ef4444',
    fontSize: '12px',
    cursor: 'pointer',
  },
  reactivateBtn: {
    background: 'rgba(16, 185, 129, 0.1)',
    border: '1px solid rgba(16, 185, 129, 0.3)',
    borderRadius: '6px',
    padding: '6px 12px',
    color: '#10b981',
    fontSize: '12px',
    cursor: 'pointer',
  },
  plansSection: {},
  plansGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
    gap: '20px',
  },
  planCard: {
    background: 'rgba(255, 255, 255, 0.02)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    borderRadius: '16px',
    padding: '24px',
  },
  planCardName: {
    fontSize: '18px',
    fontWeight: '600',
    margin: '0 0 12px 0',
    color: '#ffffff',
  },
  planCardPrice: {
    fontSize: '32px',
    fontWeight: 'bold',
    color: '#8b5cf6',
    marginBottom: '16px',
  },
  planCardFeatures: {
    listStyle: 'none',
    padding: 0,
    margin: 0,
  },
};

export default AdminDashboard;
