import React from 'react';
import { BlurCircles } from './BlurCircles';
import { ColumnOverlays } from './ColumnOverlays';
import styles from '../../styles/AnimatedBackground.module.css';

export const AnimatedBackground: React.FC = () => {
  return (
    <div className={styles.animatedBackground}>
      <BlurCircles />
      <ColumnOverlays />
    </div>
  );
};
