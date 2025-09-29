import React from 'react';
import styles from '../../styles/AIHeader.module.css';

export const AIHeader: React.FC = () => {
  return (
    <div className={styles.aiHeader}>
      <h2 className={styles.title}>
        AI-Powered Intelligence That Actually Works
      </h2>
      <p className={styles.description}>
        Behind Bloop's simple interface lies sophisticated AI technology that
        learns, adapts, and executes tasks with unprecedented intelligence.
      </p>
    </div>
  );
};
