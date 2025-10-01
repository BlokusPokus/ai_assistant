import React from 'react';
import { Link } from 'react-router-dom';
import styles from '../../styles/HeroCTAButtons.module.css';

export const HeroCTAButtons: React.FC = () => {
  return (
    <div className={styles.ctaContainer}>
      <Link to="/login" className={styles.primaryButton}>
        Send Your First SMS{' '}
      </Link>
      {/* <button className={styles.secondaryButton}>Watch Demo</button> */}
    </div>
  );
};
