import React from 'react';
import { AIHeader } from './AIHeader';
import { AIFeaturesGrid } from './AIFeaturesGrid';
import styles from '../../styles/AIIntelligenceSection.module.css';

export const AIIntelligenceSection: React.FC = () => {
  return (
    <section className={styles.aiIntelligenceSection}>
      <AIHeader />
      <AIFeaturesGrid />
    </section>
  );
};
