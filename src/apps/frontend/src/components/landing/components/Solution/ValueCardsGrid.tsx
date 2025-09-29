import React from 'react';
import { ValueCard } from './ValueCard';
import styles from '../../styles/ValueCardsGrid.module.css';

const valueCards = [
  {
    id: 'family-friends',
    title: 'Family & Friends',
    description:
      'Strengthen relationships and create meaningful connections with loved ones.',
    aiSuggestions:
      'Weekly family calls, gratitude journaling, memory-making activities',
    iconBgColor: '#fef3c7',
    iconColor: '#d97706',
    iconPath:
      'M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z',
  },
  {
    id: 'health',
    title: 'Health',
    description: 'Build sustainable habits for physical and mental wellness.',
    aiSuggestions:
      'Daily movement goals, hydration tracking, sleep optimization',
    iconBgColor: '#d1fae5',
    iconColor: '#059669',
    iconPath:
      'M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z',
  },
  {
    id: 'resilience',
    title: 'Resilience',
    description: 'Develop mental strength and bounce back from challenges.',
    aiSuggestions:
      'Stress management, mindfulness practice, growth mindset exercises',
    iconBgColor: '#e0e7ff',
    iconColor: '#3730a3',
    iconPath: 'M13 10V3L4 14h7v7l9-11h-7z',
  },
  {
    id: 'organization',
    title: 'Organization',
    description:
      'Create systems and habits for a more structured, efficient life.',
    aiSuggestions: 'Time blocking, decluttering schedules, priority management',
    iconBgColor: '#fce7f3',
    iconColor: '#be185d',
    iconPath:
      'M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4',
  },
  {
    id: 'social-life',
    title: 'Social Life',
    description:
      'Expand your social circle and engage in meaningful activities and experiences.',
    aiSuggestions:
      'Local meetups, hobby groups, networking events, community activities',
    iconBgColor: '#fef2f2',
    iconColor: '#dc2626',
    iconPath:
      'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z',
  },
  {
    id: 'nature-lover',
    title: 'Nature Lover',
    description:
      'Connect with the outdoors and develop a deeper appreciation for the natural world.',
    aiSuggestions:
      'Hiking trails, nature photography, gardening, outdoor meditation, wildlife watching',
    iconBgColor: '#ecfdf5',
    iconColor: '#16a34a',
    iconPath:
      'M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z',
  },
  {
    id: 'creative',
    title: 'Creative',
    description:
      'Express your artistic side and explore creative pursuits that inspire and fulfill you.',
    aiSuggestions:
      'Art projects, writing prompts, music practice, design challenges, creative workshops',
    iconBgColor: '#f3e8ff',
    iconColor: '#7c3aed',
    iconPath:
      'M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zM21 5a2 2 0 00-2-2h-4a2 2 0 00-2 2v12a4 4 0 004 4h4a2 2 0 002-2V5z',
  },
  {
    id: 'create-your-own',
    title: 'Create Your Own',
    description:
      'Define your own values and goals. Customize your journey with personalized guidance.',
    aiSuggestions:
      'Custom goals, personal projects, unique challenges, tailored recommendations',
    iconBgColor: '#fef3c7',
    iconColor: '#d97706',
    iconPath: 'M12 6v6m0 0v6m0-6h6m-6 0H6',
  },
];

export const ValueCardsGrid: React.FC = () => {
  return (
    <div className={styles.valueCardsGrid}>
      {valueCards.map(card => (
        <ValueCard
          key={card.id}
          title={card.title}
          description={card.description}
          aiSuggestions={card.aiSuggestions}
          iconBgColor={card.iconBgColor}
          iconColor={card.iconColor}
          iconPath={card.iconPath}
        />
      ))}
    </div>
  );
};
