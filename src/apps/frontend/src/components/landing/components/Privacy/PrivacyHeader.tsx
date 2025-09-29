import React from 'react';
import styles from '../../styles/PrivacyHeader.module.css';

export const PrivacyHeader: React.FC = () => {
  return (
    <div className={styles.privacyHeader}>
      <h2 className={styles.title}>Your data is yours</h2>
      <p className={styles.description}>
        We believe in complete transparency and user control. Your personal
        information, conversations, and data remain private and secure.
      </p>
    </div>
  );
};
