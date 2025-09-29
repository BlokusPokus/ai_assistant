import React from 'react';
import { AIFeatureCard } from './index';
import styles from '../../styles/AIFeaturesGrid.module.css';

const aiFeatures = [
  {
    id: 'intelligent-scheduling',
    title: 'Intelligent Task Scheduling',
    description:
      'AI-powered scheduling that learns your patterns and optimizes task timing for maximum productivity and minimal stress.',
    poweredBy:
      'Advanced AI algorithms, Celery background processing, smart timing optimization',
    iconBgColor: '#e0f2fe',
    iconColor: '#0369a1',
    iconPath: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z',
  },
  {
    id: 'automated-execution',
    title: 'Automated Task Execution',
    description:
      'Tasks execute automatically with AI-powered decision making, context awareness, and intelligent result processing.',
    poweredBy:
      'AgentCore AI, enhanced prompt architecture, metadata integration',
    iconBgColor: '#f0fdf4',
    iconColor: '#16a34a',
    iconPath:
      'M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z',
  },
  {
    id: 'smart-evaluation',
    title: 'Smart Event Evaluation',
    description:
      'AI analyzes your calendar events, identifies patterns, and suggests intelligent actions to optimize your schedule.',
    poweredBy:
      'AIEventEvaluator, recurrence pattern analysis, action recommendations',
    iconBgColor: '#fef3c7',
    iconColor: '#d97706',
    iconPath:
      'M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z',
  },
];

export const AIFeaturesGrid: React.FC = () => {
  return (
    <div className={styles.aiFeaturesGrid}>
      {aiFeatures.map(feature => (
        <AIFeatureCard
          key={feature.id}
          title={feature.title}
          description={feature.description}
          poweredBy={feature.poweredBy}
          iconBgColor={feature.iconBgColor}
          iconColor={feature.iconColor}
          iconPath={feature.iconPath}
        />
      ))}
    </div>
  );
};
