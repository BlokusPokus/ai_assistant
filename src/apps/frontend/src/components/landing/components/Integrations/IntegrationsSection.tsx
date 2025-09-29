import React from 'react';
import { IntegrationsHeader } from './IntegrationsHeader';
import { AppCarousel } from './AppCarousel';
import { FeatureNavigation } from './FeatureNavigation';
import { IntegrationBenefits } from './IntegrationBenefits';
import styles from '../../styles/IntegrationsSection.module.css';

export const IntegrationsSection: React.FC = () => {
  return (
    <section className={styles.integrationsSection}>
      <IntegrationsHeader />
      <AppCarousel />
      <FeatureNavigation />
      <IntegrationBenefits />
    </section>
  );
};
