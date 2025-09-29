import React from 'react';
import { HeroHeadline } from './HeroHeadline';
import { HeroDescription } from './HeroDescription';
import { HeroCTAButtons } from './HeroCTAButtons';
import styles from '../../styles/HeroSection.module.css';

export const HeroSection: React.FC = () => {
  return (
    <section className={styles.heroSection}>
      <div className={styles.heroContainer}>
        <div className={styles.heroContent}>
          <HeroHeadline />
          <HeroDescription />
          <HeroCTAButtons />
        </div>
      </div>
    </section>
  );
};
