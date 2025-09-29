import React from 'react';
import { Link } from 'react-router-dom';
import styles from '../../styles/Navigation.module.css';

export const Navigation: React.FC = () => {
  return (
    <nav className={styles.navigation}>
      {/* <Link className={styles.navLink} to="/features">
        Features
      </Link>
      <Link className={styles.navLink} to="/pricing">
        Pricing
      </Link>
      <button className={styles.navButton}>About</button>
      <button className={styles.navButton}>Contact</button> */}
    </nav>
  );
};
