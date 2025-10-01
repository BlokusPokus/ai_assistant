import React from 'react';
import styles from '../../styles/ModernLifeSection.module.css';

const painPoints = [
  {
    id: 'missed-connections',
    title: 'Missed Connections',
    description:
      "You realize you haven't texted your mom in weeks or made time to see close friends.",
    icon: '💝',
  },
  {
    id: 'neglected-wellbeing',
    title: 'Neglected Well-Being',
    description:
      'Supplements get forgotten, workouts skipped, and sleep overlooked as life gets busy.',
    icon: '💊',
  },
  {
    id: 'digital-overload',
    title: 'Digital Overload',
    description:
      'Emails pile up, notifications never stop, and what really matters gets buried in the noise.',
    icon: '📱',
  },
  {
    id: 'lost-opportunities',
    title: 'Lost Opportunities',
    description:
      "You want to learn new skills or discover local events you'd love — but the effort to search and plan feels overwhelming.",
    icon: '⚡',
  },
  {
    id: 'administrative-load',
    title: 'Administrative Load',
    description:
      'You spend hours hunting for grocery deals, comparing insurance rates, and managing household tasks that eat up your precious time.',
    icon: '📋',
  },
];

export const ModernLifeSection: React.FC = () => {
  return (
    <section className={styles.modernLifeSection}>
      <div className={styles.container}>
        <div className={styles.contentWrapper}>
          {/* Text Content */}
          <div className={styles.textContent}>
            <header className={styles.header}>
              <h2 className={styles.title}>Modern Life moves fast</h2>
              <p className={styles.description}>
                Important things slip through the cracks. You want to live
                intentionally, but instead you're juggling apps, distractions,
                and endless to-dos.
              </p>
            </header>
          </div>

          {/* Image Content */}
          <div className={styles.imageContent}>
            <div className={styles.imageContainer}>
              <img
                src="/chaos_solarpunk.png"
                alt="Modern life chaos with AI assistance"
                className={styles.heroImage}
              />
              <div className={styles.imageOverlay}>
                {/* Pain Points Grid */}
                <div className={styles.painPointsGrid}>
                  {painPoints.map(point => (
                    <div key={point.id} className={styles.painPointCard}>
                      <div className={styles.painPointIcon}>{point.icon}</div>
                      <div className={styles.painPointContent}>
                        <h3 className={styles.painPointTitle}>{point.title}</h3>
                        <p className={styles.painPointDescription}>
                          {point.description}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
