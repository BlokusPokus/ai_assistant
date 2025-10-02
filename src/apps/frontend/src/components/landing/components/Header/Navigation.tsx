import React from 'react';
import styles from '../../styles/Navigation.module.css';
import { Link } from 'react-router-dom';

export const Navigation: React.FC = () => {
  return (
    <nav className={styles.navigation}>
      <Link className={styles.navLink} to="/">
        Home
      </Link>
      <Link className={styles.navLink} to="/pricing">
        Pricing
      </Link>
      <Link className={styles.navLink} to="/how-it-works">
        How it works
      </Link>
    </nav>
  );
};
