import React from 'react';
import { Link } from 'react-router-dom';
import styles from '../../styles/CTAButtons.module.css';

export const CTAButtons: React.FC = () => {
  return (
    <div className={styles.ctaButtons}>
      <Link to="/login" className={styles.loginButton}>
        Log in
      </Link>
      <Link to="/login" className={styles.signupButton}>
        Sign up
      </Link>
    </div>
  );
};
