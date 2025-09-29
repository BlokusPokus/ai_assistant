import React from 'react';
import { SolutionHeader } from './SolutionHeader';
import { ValueCardsGrid } from './ValueCardsGrid';
import styles from '../../styles/SolutionSection.module.css';

export const SolutionSection: React.FC = () => {
  return (
    <section className={styles.solutionSection}>
      <SolutionHeader />
      <ValueCardsGrid />
    </section>
  );
};
