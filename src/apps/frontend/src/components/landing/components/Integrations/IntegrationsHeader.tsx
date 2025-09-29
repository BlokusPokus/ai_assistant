import React from 'react';
import styles from '../../styles/IntegrationsHeader.module.css';

export const IntegrationsHeader: React.FC = () => {
  return (
    <div className={styles.integrationsHeader}>
      <h2 className={styles.title}>All your apps, one interface</h2>
      <p className={styles.description}>
        Connect all your favorite tools and services in one unified workspace.
        No more switching between apps or losing context.
      </p>
    </div>
  );
};
