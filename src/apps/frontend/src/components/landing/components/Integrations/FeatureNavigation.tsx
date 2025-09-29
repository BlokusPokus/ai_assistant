import React, { useState } from 'react';
import { FeatureButtons } from './FeatureButtons';
import { FeaturePreview } from './FeaturePreview';
import styles from '../../styles/FeatureNavigation.module.css';

export const FeatureNavigation: React.FC = () => {
  const [activeFeature, setActiveFeature] = useState<
    'tasks' | 'notes' | 'calendar' | 'reminders' | 'insights'
  >('tasks');

  return (
    <div className={styles.featureNavigation}>
      <div className={styles.featureContainer}>
        <FeatureButtons
          activeFeature={activeFeature}
          onFeatureChange={setActiveFeature}
        />
        <FeaturePreview activeFeature={activeFeature} />
      </div>
    </div>
  );
};
