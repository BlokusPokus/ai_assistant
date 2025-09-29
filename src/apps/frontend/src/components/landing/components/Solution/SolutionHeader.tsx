import React from 'react';
import styles from '../../styles/SolutionHeader.module.css';

export const SolutionHeader: React.FC = () => {
  return (
    <div className={styles.solutionHeader}>
      <h2 className={styles.title}>Your new Unified AI Assistant</h2>
      <p className={styles.description}>
        Pick your values, get personalized guidance. Our AI creates personalized
        task presets and guidance tailored to help you grow in those areas.
      </p>
    </div>
  );
};
