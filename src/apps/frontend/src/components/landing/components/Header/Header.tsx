import React from 'react';
import { Link } from 'react-router-dom';
import { Navigation } from './Navigation';
import { CTAButtons } from './CTAButtons';
import { SocialLinks } from './SocialLinks';
import styles from '../../styles/Header.module.css';

export const Header: React.FC = () => {
  return (
    <header className={styles.header}>
      <div className={styles.headerSpacer} />
      <div className={styles.headerContent}>
        {/* Logo */}
        <div className={styles.logoSection}>
          <Link to="/" className={styles.logoLink}>
            <img src="/orca3d.png" alt="Bloop Logo" className={styles.logo} />
            <span className={styles.logoText}>Bloop</span>
          </Link>
        </div>

        {/* Navigation */}
        <Navigation />

        {/* Right Section */}
        <div className={styles.rightSection}>
          <SocialLinks />
          <CTAButtons />
        </div>
      </div>
    </header>
  );
};
