import React from 'react';
import styles from '../../styles/AIFeatureCard.module.css';

interface AIFeatureCardProps {
  title: string;
  description: string;
  poweredBy: string;
  iconBgColor: string;
  iconColor: string;
  iconPath: string;
}

export const AIFeatureCard: React.FC<AIFeatureCardProps> = ({
  title,
  description,
  poweredBy,
  iconBgColor,
  iconColor,
  iconPath,
}) => {
  return (
    <div className={styles.aiFeatureCard}>
      <div
        className={styles.iconContainer}
        style={{ backgroundColor: iconBgColor }}
      >
        <svg
          className={styles.icon}
          style={{ color: iconColor }}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            d={iconPath}
          />
        </svg>
      </div>
      <h3 className={styles.title}>{title}</h3>
      <p className={styles.description}>{description}</p>
      <div className={styles.poweredBy}>
        <p className={styles.poweredByLabel}>Powered by:</p>
        <p className={styles.poweredByText}>{poweredBy}</p>
      </div>
    </div>
  );
};
