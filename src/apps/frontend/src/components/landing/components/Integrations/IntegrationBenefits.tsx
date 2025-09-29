import React from 'react';
import { BenefitCard } from './BenefitCard';
import styles from '../../styles/IntegrationBenefits.module.css';

const benefits = [
  {
    id: 'instant-sync',
    title: 'Instant Sync',
    description:
      'All your data syncs instantly across every connected app. No more manual updates or lost information.',
    backgroundColor: '#98a758',
    iconPath: 'M13 10V3L4 14h7v7l9-11h-7z',
  },
  {
    id: 'smart-automation',
    title: 'Smart Automation',
    description:
      'Bloop learns your patterns and automates routine tasks across all your connected services.',
    backgroundColor: '#5b8e4f',
    iconPath: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
  },
  {
    id: 'unified-experience',
    title: 'Unified Experience',
    description:
      'One clean interface to manage everything. No more context switching or app fatigue.',
    backgroundColor: '#265f2e',
    iconPath:
      'M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z',
  },
];

export const IntegrationBenefits: React.FC = () => {
  return (
    <div className={styles.integrationBenefits}>
      {benefits.map(benefit => (
        <BenefitCard
          key={benefit.id}
          title={benefit.title}
          description={benefit.description}
          backgroundColor={benefit.backgroundColor}
          iconPath={benefit.iconPath}
        />
      ))}
    </div>
  );
};
