import React from 'react';
import { PrivacyFeatureCard } from './PrivacyFeatureCard';
import styles from '../../styles/PrivacyFeaturesGrid.module.css';

const privacyFeatures = [
  {
    id: 'encryption',
    title: 'End-to-End Encryption',
    description:
      'All your data is encrypted in transit and at rest, ensuring maximum security.',
    iconPath:
      'M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z',
  },
  {
    id: 'privacy-first',
    title: 'Privacy First',
    description:
      'We never sell your data or use it for advertising. Your privacy is our priority.',
    iconPath:
      'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z',
  },
  {
    id: 'data-export',
    title: 'Data Export',
    description:
      'Export all your data anytime. You own your information and can take it with you.',
    iconPath: 'M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12',
  },
];

export const PrivacyFeaturesGrid: React.FC = () => {
  return (
    <div className={styles.privacyFeaturesGrid}>
      {privacyFeatures.map(feature => (
        <PrivacyFeatureCard
          key={feature.id}
          title={feature.title}
          description={feature.description}
          iconPath={feature.iconPath}
        />
      ))}
    </div>
  );
};
