import React from 'react';
import styles from '../../styles/FeaturePreview.module.css';

interface FeaturePreviewProps {
  activeFeature: 'tasks' | 'notes' | 'calendar' | 'reminders' | 'insights';
}
const featureImages = {
  tasks: '/bloop_examples.png',
  notes: '/bloop_examples.png',
  calendar: '/bloop_examples.png',
  reminders: '/bloop_examples.png',
  insights: '/bloop_examples.png',
};

const featureDescriptions = {
  tasks: 'Smart task management interface',
  notes: 'Intelligent note-taking workspace',
  calendar: 'Advanced calendar and scheduling',
  reminders: 'Proactive reminder system',
  insights: 'AI-powered analytics dashboard',
};

export const FeaturePreview: React.FC<FeaturePreviewProps> = ({
  activeFeature,
}) => {
  return (
    <div className={styles.featurePreview}>
      <div className={styles.previewContainer}>
        <img
          src={featureImages[activeFeature]}
          alt={`${activeFeature} feature preview`}
          className={styles.previewImage}
        />
        <div className={styles.imageOverlay}></div>
        <div className={styles.imageContent}>
          <h3 className={styles.imageTitle}>{activeFeature}</h3>
          <p className={styles.imageDescription}>
            {featureDescriptions[activeFeature]}
          </p>
        </div>
      </div>
    </div>
  );
};
