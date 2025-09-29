import React from 'react';
import { FeatureButton } from './FeatureButton';
import styles from '../../styles/FeatureButtons.module.css';

const features = [
  {
    id: 'tasks' as const,
    title: 'Tasks',
    description:
      'Smart task management that learns your patterns and helps you stay organized without the overwhelm.',
    iconPath:
      'M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4',
    colorScheme: 'green',
  },
  {
    id: 'notes' as const,
    title: 'Notes',
    description:
      'Capture thoughts, memories, and ideas with intelligent organization that makes everything findable.',
    iconPath:
      'M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z',
    colorScheme: 'blue',
  },
  {
    id: 'calendar' as const,
    title: 'Calendar',
    description:
      'Intelligent scheduling that helps you balance work, life, and everything in between.',
    iconPath:
      'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z',
    colorScheme: 'purple',
  },
  {
    id: 'reminders' as const,
    title: 'Reminders',
    description:
      'Proactive reminders that help you stay on top of what matters most in your life.',
    iconPath:
      'M15 17h5l-5 5v-5zM4.828 7l2.586 2.586a2 2 0 002.828 0L12.828 7H4.828zM4.828 17H9l-2.586 2.586a2 2 0 01-2.828 0L4.828 17z',
    colorScheme: 'orange',
  },
  {
    id: 'insights' as const,
    title: 'Insights',
    description:
      'AI-powered analytics that help you understand your patterns and optimize your life.',
    iconPath:
      'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
    colorScheme: 'indigo',
  },
];

interface FeatureButtonsProps {
  activeFeature: 'tasks' | 'notes' | 'calendar' | 'reminders' | 'insights';
  onFeatureChange: (
    feature: 'tasks' | 'notes' | 'calendar' | 'reminders' | 'insights'
  ) => void;
}

export const FeatureButtons: React.FC<FeatureButtonsProps> = ({
  activeFeature,
  onFeatureChange,
}) => {
  return (
    <div className={styles.featureButtons}>
      {features.map(feature => (
        <FeatureButton
          key={feature.id}
          feature={feature}
          isActive={activeFeature === feature.id}
          onClick={() => onFeatureChange(feature.id)}
        />
      ))}
    </div>
  );
};
