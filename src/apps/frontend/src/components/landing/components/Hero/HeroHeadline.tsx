import React from 'react';
import styles from '../../styles/HeroHeadline.module.css';

export const HeroHeadline: React.FC = () => {
  return (
    <div className={styles.headlineContainer}>
      <h1 className={styles.headline}>
        <span className={styles.betaText}>(BETA)</span>
        <div>
          <span className={styles.moreContainer}>Squeeze MORE</span> out of{' '}
          <span className={styles.highlightedText}>Life</span>
        </div>
      </h1>
    </div>
  );
};
