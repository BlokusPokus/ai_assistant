import React from 'react';
import styles from '../../styles/ProblemHeader.module.css';

export const ProblemHeader: React.FC = () => {
  return (
    <div className={styles.problemHeader}>
      <h2 className={styles.title}>Modern Life moves fast</h2>
      <p className={styles.description}>
        Important things slip through the cracks. You want to live
        intentionally, but instead you're juggling apps, distractions, and
        endless to-dos.
      </p>
    </div>
  );
};
