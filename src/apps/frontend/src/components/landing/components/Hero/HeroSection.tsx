import React from 'react';

import styles from '../../styles/HeroSection.module.css';
import { HeroDescription } from './HeroDescription';
import { HeroHeadline } from './HeroHeadline';
import { HeroCTAButtons } from './HeroCTAButtons';

export const HeroSection: React.FC = () => {
  return (
    <section className={styles.heroSection}>
      <div className={styles.heroContainer}>
        <div className={styles.heroContent}>
          <HeroHeadline />
          <HeroDescription />
          <HeroCTAButtons />
        </div>
        <div className={styles.heroImageContainer}>
          <img
            src="/handphone.png"
            alt="Personal Assistant App"
            className={styles.heroImage}
          />
        </div>
      </div>
    </section>
  );
};
