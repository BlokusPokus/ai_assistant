import React from 'react';
import styles from '../../styles/PrivacyFeatureCard.module.css';

interface PrivacyFeatureCardProps {
  title: string;
  description: string;
  iconPath: string;
}

export const PrivacyFeatureCard: React.FC<PrivacyFeatureCardProps> = ({
  title,
  description,
  iconPath,
}) => {
  return (
    <div className={styles.privacyFeatureCard}>
      <div className={styles.iconContainer}>
        <svg
          className={styles.icon}
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
    </div>
  );
};
