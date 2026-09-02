import React, { useState } from 'react';

interface PlanFeature {
  label: string;
  included: boolean;
  highlight?: boolean;
}

interface Plan {
  id: string;
  name: string;
  price: number;
  interval: string;
  period: string;
  description: string;
  features: PlanFeature[];
  popular?: boolean;
  discount?: string;
  cta: string;
  ctaStyle: 'primary' | 'secondary' | 'dark';
}

const plans: Plan[] = [
  {
    id: 'monthly',
    name: 'Mensal',
    price: 14.99,
    interval: 'mês',
    period: '/mês',
    description: 'Acesso completo com instâncias e suporte',
    features: [
      { label: 'Instâncias', included: true },
      { label: 'Suporte', included: true },
      { label: 'Acesso ao Painel', included: true },
    ],
    cta: 'Assinar Agora',
    ctaStyle: 'secondary',
  },
  {
    id: 'quarterly',
    name: 'Trimestral',
    price: 29.99,
    interval: 'trimestre',
    period: '/trimestre',
    description: 'Tudo do Mensal + 33% de desconto',
    features: [
      { label: 'Tudo do Mensal', included: true, highlight: true },
      { label: '33% de desconto', included: true },
      { label: 'Suporte', included: true },
      { label: 'Acesso ao painel', included: true },
    ],
    popular: true,
    discount: '33% OFF',
    cta: 'ASSINAR AGORA',
    ctaStyle: 'primary',
  },
  {
    id: 'annual',
    name: 'Anual',
    price: 79.99,
    interval: 'ano',
    period: '/ano',
    description: 'Tudo do Trimestral + 71% de desconto',
    features: [
      { label: 'Tudo do Trimestral', included: true, highlight: true },
      { label: '71% de desconto', included: true },
      { label: 'Suporte', included: true },
      { label: 'Jarvis Vitalício de Brinde', included: true },
    ],
    cta: 'Assinar Agora',
    ctaStyle: 'dark',
  },
];

const PricingPage: React.FC = () => {
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null);

  const handleSubscribe = (planId: string) => {
    setSelectedPlan(planId);
    // Aqui seria integrado com gateway de pagamento
    alert(`Plano ${planId} selecionado! Em breve integracao com pagamento.`);
  };

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <h1 style={styles.title}>Planos</h1>
        <p style={styles.subtitle}>Planos flexíveis para qualquer tamanho de operação.</p>
      </div>

      {/* Plans Grid */}
      <div style={styles.plansGrid}>
        {plans.map((plan) => (
          <div
            key={plan.id}
            style={{
              ...styles.planCard,
              ...(plan.popular ? styles.planCardPopular : {}),
            }}
          >
            {/* Popular Badge */}
            {plan.popular && (
              <div style={styles.popularBadge}>MAIS POPULAR</div>
            )}

            {/* Discount Badge */}
            {plan.discount && (
              <div style={styles.discountBadge}>{plan.discount}</div>
            )}

            {/* Plan Name */}
            <h2 style={styles.planName}>{plan.name}</h2>

            {/* Price */}
            <div style={styles.priceContainer}>
              <span style={styles.currency}>R$</span>
              <span style={styles.price}>{plan.price.toFixed(2).replace('.', ',')}</span>
              <span style={styles.period}>{plan.period}</span>
            </div>

            {/* Features */}
            <ul style={styles.featureList}>
              {plan.features.map((feature, index) => (
                <li
                  key={index}
                  style={{
                    ...styles.featureItem,
                    ...(feature.highlight ? styles.featureItemHighlight : {}),
                  }}
                >
                  <span style={styles.checkmark}>✓</span>
                  {feature.label}
                </li>
              ))}
            </ul>

            {/* CTA Button */}
            <button
              style={{
                ...styles.ctaButton,
                ...(plan.ctaStyle === 'primary' ? styles.ctaPrimary : {}),
                ...(plan.ctaStyle === 'dark' ? styles.ctaDark : {}),
              }}
              onClick={() => handleSubscribe(plan.id)}
            >
              {plan.cta}
            </button>
          </div>
        ))}
      </div>

      {/* Jarvis Lifetime Banner */}
      <div style={styles.jarvisBanner}>
        <div style={styles.jarvisContent}>
          <div style={styles.jarvisInfo}>
            <span style={styles.jarvisIcon}>🤖</span>
            <span style={styles.jarvisLabel}>JARVIS</span>
            <span style={styles.jarvisBadge}>VITALÍCIO</span>
          </div>
          <p style={styles.jarvisDescription}>
            Seu próprio Jarvis, personalizável e com acesso vitalício. Clientes do plano anual recebem
            este item como brinde.
          </p>
        </div>
        <button style={styles.downloadButton}>
          <span style={styles.downloadIcon}>⬇</span>
          Baixar Jarvis
        </button>
      </div>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    padding: '40px',
    minHeight: '100vh',
    position: 'relative',
    zIndex: 1,
    background: 'transparent',
  },
  header: {
    textAlign: 'center',
    marginBottom: '60px',
  },
  title: {
    fontSize: '48px',
    fontWeight: 'bold',
    marginBottom: '16px',
    background: 'linear-gradient(135deg, #00d9ff 0%, #00ff88 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
  },
  subtitle: {
    fontSize: '18px',
    color: '#a0a0a0',
    maxWidth: '500px',
    margin: '0 auto',
  },
  plansGrid: {
    display: 'flex',
    justifyContent: 'center',
    gap: '24px',
    flexWrap: 'wrap',
    maxWidth: '1200px',
    margin: '0 auto 60px',
  },
  planCard: {
    background: 'rgba(255, 255, 255, 0.03)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    borderRadius: '16px',
    padding: '32px',
    width: '320px',
    position: 'relative',
    transition: 'transform 0.3s ease, box-shadow 0.3s ease',
    display: 'flex',
    flexDirection: 'column',
  },
  planCardPopular: {
    background: 'rgba(139, 92, 246, 0.1)',
    border: '2px solid #8b5cf6',
    transform: 'scale(1.05)',
    boxShadow: '0 0 40px rgba(139, 92, 246, 0.3)',
  },
  popularBadge: {
    position: 'absolute',
    top: '-12px',
    left: '50%',
    transform: 'translateX(-50%)',
    background: 'linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%)',
    color: '#ffffff',
    padding: '6px 16px',
    borderRadius: '20px',
    fontSize: '12px',
    fontWeight: 'bold',
    letterSpacing: '0.5px',
  },
  discountBadge: {
    position: 'absolute',
    top: '16px',
    right: '16px',
    background: 'rgba(0, 217, 255, 0.2)',
    color: '#00d9ff',
    padding: '4px 8px',
    borderRadius: '8px',
    fontSize: '11px',
    fontWeight: 'bold',
  },
  planName: {
    fontSize: '24px',
    fontWeight: '600',
    marginBottom: '16px',
    color: '#ffffff',
  },
  priceContainer: {
    display: 'flex',
    alignItems: 'baseline',
    marginBottom: '24px',
  },
  currency: {
    fontSize: '24px',
    fontWeight: '600',
    color: '#00d9ff',
    marginRight: '4px',
  },
  price: {
    fontSize: '48px',
    fontWeight: 'bold',
    color: '#ffffff',
    lineHeight: 1,
  },
  period: {
    fontSize: '16px',
    color: '#a0a0a0',
    marginLeft: '4px',
  },
  featureList: {
    listStyle: 'none',
    padding: 0,
    margin: '0 0 32px 0',
    flex: 1,
  },
  featureItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '12px 0',
    borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
    color: '#d0d0d0',
    fontSize: '15px',
  },
  featureItemHighlight: {
    color: '#00ff88',
    fontWeight: '500',
  },
  checkmark: {
    color: '#00d9ff',
    fontWeight: 'bold',
    fontSize: '16px',
  },
  ctaButton: {
    width: '100%',
    padding: '16px 24px',
    borderRadius: '12px',
    border: 'none',
    fontSize: '16px',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    background: 'rgba(255, 255, 255, 0.1)',
    color: '#ffffff',
  },
  ctaPrimary: {
    background: 'linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%)',
    color: '#ffffff',
    boxShadow: '0 4px 20px rgba(139, 92, 246, 0.4)',
  },
  ctaDark: {
    background: 'linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%)',
    color: '#ffffff',
    border: '1px solid rgba(255, 255, 255, 0.2)',
  },
  jarvisBanner: {
    maxWidth: '800px',
    margin: '0 auto',
    background: 'rgba(0, 217, 255, 0.05)',
    border: '1px solid rgba(0, 217, 255, 0.2)',
    borderRadius: '16px',
    padding: '24px 32px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: '24px',
    flexWrap: 'wrap' as const,
  },
  jarvisContent: {
    flex: 1,
    minWidth: '300px',
  },
  jarvisInfo: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginBottom: '8px',
  },
  jarvisIcon: {
    fontSize: '24px',
  },
  jarvisLabel: {
    fontSize: '18px',
    fontWeight: 'bold',
    color: '#ffffff',
  },
  jarvisBadge: {
    background: '#00d9ff',
    color: '#000000',
    padding: '4px 8px',
    borderRadius: '6px',
    fontSize: '11px',
    fontWeight: 'bold',
  },
  jarvisDescription: {
    color: '#a0a0a0',
    fontSize: '14px',
    margin: 0,
    lineHeight: 1.5,
  },
  downloadButton: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    background: 'linear-gradient(135deg, #00d9ff 0%, #00ff88 100%)',
    color: '#000000',
    padding: '12px 24px',
    borderRadius: '12px',
    border: 'none',
    fontSize: '14px',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'transform 0.2s ease',
    whiteSpace: 'nowrap' as const,
  },
  downloadIcon: {
    fontSize: '16px',
  },
};

export default PricingPage;
