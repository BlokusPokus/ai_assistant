import React from 'react';
import { PrivacyHeader } from './PrivacyHeader';
import { PrivacyFeaturesGrid } from './PrivacyFeaturesGrid';
import { PrivacyCTA } from './PrivacyCTA';
import styles from '../../styles/PrivacySection.module.css';

export const PrivacySection: React.FC = () => {
  return (
    <section className={styles.privacySection}>
      <PrivacyHeader />
      <PrivacyFeaturesGrid />
      <PrivacyCTA />
    </section>
  );
};
