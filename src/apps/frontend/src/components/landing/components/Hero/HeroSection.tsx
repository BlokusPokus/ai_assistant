import React, { useEffect, useRef } from 'react';

import styles from '../../styles/HeroSection.module.css';
import { HeroDescription } from './HeroDescription';
import { HeroHeadline } from './HeroHeadline';
import { HeroCTAButtons } from './HeroCTAButtons';

export const HeroSection: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (videoRef.current) {
        videoRef.current.play();
      }
    }, 5000); // 5 seconds delay

    return () => clearTimeout(timer);
  }, []);

  return (
    <section className={styles.heroSection}>
      <div className={styles.heroContainer}>
        <div className={styles.heroContent}>
          <HeroHeadline />
          <HeroDescription />
          <HeroCTAButtons />
        </div>
        <div className={styles.heroImageContainer}>
          <video
            ref={videoRef}
            src="/walking_phone.mp4"
            muted
            playsInline
            className={styles.heroImage}
          />
        </div>
      </div>
    </section>
  );
};
