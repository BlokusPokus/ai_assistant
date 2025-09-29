import React from 'react';
import styles from '../../styles/BlurCircles.module.css';

export const BlurCircles: React.FC = () => {
  return (
    <>
      {/* Blur Ovals - 4 ovals starting from each corner */}
      <div
        className={`${styles.blurCircle} ${styles.blurCircleOrange}`}
        style={{
          backgroundColor: '#98a758',
          borderRadius: '0% 50% 50% 0%',
        }}
      />
      <div
        className={`${styles.blurCircle} ${styles.blurCirclePink}`}
        style={{
          backgroundColor: '#ece5b5',
          borderRadius: '50% 0% 0% 50%',
        }}
      />
      <div
        className={`${styles.blurCircle} ${styles.blurCircleCyan}`}
        style={{
          backgroundColor: '#1a4835',
          borderRadius: '0% 50% 50% 0%',
        }}
      />
      <div
        className={`${styles.blurCircle} ${styles.blurCircleGreen}`}
        style={{
          backgroundColor: '#a0b192',
          borderRadius: '50% 0% 0% 50%',
        }}
      />
    </>
  );
};
