import React from 'react';
import { ModernLifeSection } from './ModernLifeSection';
import styles from '../../styles/ProblemSection.module.css';

export const ProblemSection: React.FC = () => {
  return (
    <section className={styles.problemSection}>
      <ModernLifeSection />
    </section>
  );
};
