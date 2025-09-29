import React from 'react';
import { PainPointCard } from './PainPointCard';
import styles from '../../styles/PainPointGrid.module.css';

const painPoints = [
  {
    id: 'missed-connections',
    title: 'Missed Connections',
    description:
      "You realize you haven't texted your mom in weeks or made time to see close friends.",
    icon: 'heart',
  },
  {
    id: 'neglected-wellbeing',
    title: 'Neglected Well-Being',
    description:
      'Supplements get forgotten, workouts skipped, and sleep overlooked as life gets busy.',
    icon: 'heart',
  },
  {
    id: 'digital-overload',
    title: 'Digital Overload',
    description:
      'Emails pile up, notifications never stop, and what really matters gets buried in the noise.',
    icon: 'overload',
  },
  {
    id: 'lost-opportunities',
    title: 'Lost Opportunities',
    description:
      "You want to learn new skills or discover local events you'd love — but the effort to search and plan feels overwhelming.",
    icon: 'lightning',
  },
  {
    id: 'administrative-load',
    title: 'Administrative Load',
    description:
      'You spend hours hunting for grocery deals, comparing insurance rates, and managing household tasks that eat up your precious time.',
    icon: 'checklist',
  },
];

export const PainPointGrid: React.FC = () => {
  return (
    <div className={styles.painPointGrid}>
      {painPoints.map(painPoint => (
        <PainPointCard
          key={painPoint.id}
          title={painPoint.title}
          description={painPoint.description}
          icon={painPoint.icon}
        />
      ))}
    </div>
  );
};
