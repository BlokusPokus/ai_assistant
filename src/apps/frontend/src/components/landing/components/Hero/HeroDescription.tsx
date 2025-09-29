import React from 'react';
import styles from '../../styles/HeroDescription.module.css';

export const HeroDescription: React.FC = () => {
  return (
    <p className={styles.description}>
      Bloop is your intelligent, adaptive, and proactive AI assistant designed
      to support you in experiencing more out of life, because everyone has
      unique needs
    </p>
  );
};
