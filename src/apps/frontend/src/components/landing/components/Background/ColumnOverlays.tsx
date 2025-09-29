import React from 'react';
import styles from '../../styles/ColumnOverlays.module.css';

export const ColumnOverlays: React.FC = () => {
  return (
    <>
      {/* Columns - Left Side */}
      <div
        className={styles.column}
        style={{ left: '0px', backgroundColor: 'rgba(255, 255, 255, 0.5)' }}
      />
      <div
        className={styles.column}
        style={{ left: '80px', backgroundColor: 'rgba(255, 255, 255, 0.45)' }}
      />
      <div
        className={styles.column}
        style={{ left: '160px', backgroundColor: 'rgba(255, 255, 255, 0.4)' }}
      />
      <div
        className={styles.column}
        style={{ left: '240px', backgroundColor: 'rgba(255, 255, 255, 0.35)' }}
      />
      <div
        className={styles.column}
        style={{ left: '320px', backgroundColor: 'rgba(255, 255, 255, 0.3)' }}
      />
      <div
        className={styles.column}
        style={{ left: '400px', backgroundColor: 'rgba(255, 255, 255, 0.25)' }}
      />
      <div
        className={styles.column}
        style={{ left: '480px', backgroundColor: 'rgba(255, 255, 255, 0.2)' }}
      />
      <div
        className={styles.column}
        style={{ left: '560px', backgroundColor: 'rgba(255, 255, 255, 0.15)' }}
      />

      {/* Columns - Right Side */}
      <div
        className={styles.column}
        style={{ right: '0px', backgroundColor: 'rgba(255, 255, 255, 0.5)' }}
      />
      <div
        className={styles.column}
        style={{ right: '80px', backgroundColor: 'rgba(255, 255, 255, 0.45)' }}
      />
      <div
        className={styles.column}
        style={{ right: '160px', backgroundColor: 'rgba(255, 255, 255, 0.4)' }}
      />
      <div
        className={styles.column}
        style={{ right: '240px', backgroundColor: 'rgba(255, 255, 255, 0.35)' }}
      />
      <div
        className={styles.column}
        style={{ right: '320px', backgroundColor: 'rgba(255, 255, 255, 0.3)' }}
      />
      <div
        className={styles.column}
        style={{ right: '400px', backgroundColor: 'rgba(255, 255, 255, 0.25)' }}
      />
      <div
        className={styles.column}
        style={{ right: '480px', backgroundColor: 'rgba(255, 255, 255, 0.2)' }}
      />
      <div
        className={styles.column}
        style={{ right: '560px', backgroundColor: 'rgba(255, 255, 255, 0.15)' }}
      />

      {/* Middle Columns - Fill the center gap */}
      <div
        className={styles.column}
        style={{ left: '640px', backgroundColor: 'rgba(255, 255, 255, 0.1)' }}
      />
      <div
        className={styles.column}
        style={{ left: '720px', backgroundColor: 'rgba(255, 255, 255, 0.05)' }}
      />
    </>
  );
};
