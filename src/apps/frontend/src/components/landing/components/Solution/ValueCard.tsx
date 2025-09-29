import React from 'react';
import styles from '../../styles/ValueCard.module.css';

interface ValueCardProps {
  title: string;
  description: string;
  aiSuggestions: string;
  iconBgColor: string;
  iconColor: string;
  iconPath: string;
}

export const ValueCard: React.FC<ValueCardProps> = ({
  title,
  description,
  aiSuggestions,
  iconBgColor,
  iconColor,
  iconPath,
}) => {
  return (
    <div className={styles.valueCard}>
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
      <div className={styles.aiSuggestions}>
        <p className={styles.aiLabel}>AI suggests:</p>
        <p className={styles.aiText}>{aiSuggestions}</p>
      </div>
    </div>
  );
};
