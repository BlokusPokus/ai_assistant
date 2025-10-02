import React from 'react';
import { Check, Star, Zap } from 'lucide-react';
import { Header } from '../components/landing/components/Header/Header';
import styles from '../components/landing/styles/PricingPage.module.css';

interface PricingTier {
  name: string;
  price: string;
  period: string;
  description: string;
  features: string[];
  ctaText: string;
  ctaVariant: 'primary' | 'secondary' | 'outline';
  popular?: boolean;
  icon: React.ReactNode;
}

const PricingPage: React.FC = () => {
  const pricingTiers: PricingTier[] = [
    {
      name: 'Free Trial',
      price: '$0',
      period: '14 days',
      description: 'Perfect for getting started and exploring our features',
      features: [
        'Full access to all features',
        'AI-powered task management',
        'Calendar integration',
        'Basic SMS notifications',
        'Email classification',
        'Note-taking and todos',
        '14-day trial period',
        'Community support',
      ],
      ctaText: 'Start Free Trial',
      ctaVariant: 'outline',
      icon: <Zap className="w-6 h-6" />,
    },
    {
      name: 'Premium',
      price: '$9',
      period: 'per month',
      description: 'For individuals who want to maximize their productivity',
      features: [
        'Everything in Free Trial',
        'Advanced AI task scheduling',
        'Priority SMS notifications',
        'Advanced email filtering',
        'Custom integrations',
        'Enhanced calendar features',
        'Priority support',
        'Advanced analytics',
      ],
      ctaText: 'Upgrade to Premium',
      ctaVariant: 'primary',
      popular: true,
      icon: <Star className="w-6 h-6" />,
    },
    {
      name: 'Pro',
      price: '$14',
      period: 'per month',
      description: 'For power users and small teams who need advanced features',
      features: [
        'Everything in Premium',
        'Team collaboration features',
        'Custom AI model training',
        'Advanced automation workflows',
        'API access',
        'White-label options',
        'Dedicated account manager',
        'Custom integrations',
        'Advanced security features',
      ],
      ctaText: 'Go Pro',
      ctaVariant: 'secondary',
      icon: <Star className="w-6 h-6" />,
    },
  ];

  const handleCTAClick = (tier: string) => {
    // TODO: Implement actual signup/upgrade logic
    console.log(`Clicked ${tier} CTA`);
  };

  return (
    <div className={styles.pricingPage}>
      <Header />
      <div className={styles.container}>
        {/* Header Section */}
        <div className={styles.header}>
          <h1 className={styles.title}>
            Choose Your <span className={styles.highlightedText}>Plan</span>
          </h1>
          <p className={styles.subtitle}>
            Start with our free trial and upgrade when you're ready to unlock
            more features
          </p>
        </div>

        {/* Pricing Cards */}
        <div className={styles.pricingGrid}>
          {pricingTiers.map(tier => (
            <div
              key={tier.name}
              className={`${styles.pricingCard} ${tier.popular ? styles.popular : ''}`}
            >
              {tier.popular && (
                <div className={styles.popularBadge}>
                  <span>Most Popular</span>
                </div>
              )}

              <div className={styles.cardHeader}>
                <div className={styles.tierIcon}>{tier.icon}</div>
                <h3 className={styles.tierName}>{tier.name}</h3>
                <div className={styles.priceContainer}>
                  <span className={styles.price}>{tier.price}</span>
                  <span className={styles.period}>/{tier.period}</span>
                </div>
                <p className={styles.tierDescription}>{tier.description}</p>
              </div>

              <div className={styles.featuresList}>
                {tier.features.map((feature, featureIndex) => (
                  <div key={featureIndex} className={styles.featureItem}>
                    <Check className={styles.checkIcon} />
                    <span>{feature}</span>
                  </div>
                ))}
              </div>

              <button
                className={`${styles.ctaButton} ${styles[tier.ctaVariant]}`}
                onClick={() => handleCTAClick(tier.name)}
              >
                {tier.ctaText}
              </button>
            </div>
          ))}
        </div>

        {/* FAQ Section */}
        <div className={styles.faqSection}>
          <h2 className={styles.faqTitle}>Frequently Asked Questions</h2>
          <div className={styles.faqGrid}>
            <div className={styles.faqItem}>
              <h3>Can I change plans anytime?</h3>
              <p>
                Yes, you can upgrade or downgrade your plan at any time. Changes
                take effect immediately.
              </p>
            </div>
            <div className={styles.faqItem}>
              <h3>What happens after my free trial?</h3>
              <p>
                After 14 days, you'll need to choose a paid plan to continue
                using the service. No automatic charges.
              </p>
            </div>
            <div className={styles.faqItem}>
              <h3>Do you offer refunds?</h3>
              <p>
                We offer a 30-day money-back guarantee for all paid plans. No
                questions asked.
              </p>
            </div>
            <div className={styles.faqItem}>
              <h3>Is there a setup fee?</h3>
              <p>
                No setup fees for any plan. You only pay the monthly
                subscription cost.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PricingPage;
