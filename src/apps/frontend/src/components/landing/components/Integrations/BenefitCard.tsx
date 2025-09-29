import React from 'react';
import styles from '../../styles/BenefitCard.module.css';

interface BenefitCardProps {
  title: string;
  description: string;
  backgroundColor: string;
  iconPath: string;
}

export const BenefitCard: React.FC<BenefitCardProps> = ({
  title,
  description,
  backgroundColor,
  iconPath,
}) => {
  return (
    <div className={styles.benefitCard}>
      <div className={styles.iconContainer} style={{ backgroundColor }}>
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
