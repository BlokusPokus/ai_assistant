import React from 'react';
import styles from '../../styles/HeroHeadline.module.css';

export const HeroHeadline: React.FC = () => {
  return (
    <div className={styles.headlineContainer}>
      <h1 className={styles.headline}>
        <span className={styles.moreContainer}>
          <img
            src="/construction.png"
            alt="Under Construction"
            className={styles.constructionImage}
          />
          MORE
        </span>{' '}
        out of <span className={styles.highlightedText}>Life</span>
      </h1>
    </div>
  );
};
