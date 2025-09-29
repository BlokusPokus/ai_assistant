import React from 'react';
import { Link } from 'react-router-dom';
import styles from '../../styles/PrivacyCTA.module.css';

export const PrivacyCTA: React.FC = () => {
  return (
    <div className={styles.privacyCTA}>
      <Link to="/login" className={styles.ctaButton}>
        Get started free
      </Link>
    </div>
  );
};
