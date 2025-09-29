import React from 'react';
import { ProblemHeader } from './ProblemHeader';
import { PainPointGrid } from './PainPointGrid';
import styles from '../../styles/ProblemSection.module.css';

export const ProblemSection: React.FC = () => {
  return (
    <section className={styles.problemSection}>
      <ProblemHeader />
      <PainPointGrid />
    </section>
  );
};
