import React from 'react';
import { SocialLinks } from '../Header/SocialLinks';
import styles from '../../styles/CompanyInfo.module.css';

export const CompanyInfo: React.FC = () => {
  return (
    <div className={styles.companyInfo}>
      <div className={styles.logoSection}>
        <img src="/orca3d.png" alt="Bloop Logo" className={styles.logo} />
        <span className={styles.logoText}>Bloop</span>
      </div>
      <p className={styles.description}>
        Your intelligent, adaptive, and proactive AI assistant designed to help
        you experience more out of life.
      </p>
      <SocialLinks />
    </div>
  );
};
