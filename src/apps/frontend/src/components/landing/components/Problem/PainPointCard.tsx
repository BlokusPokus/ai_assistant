import React from 'react';
import styles from '../../styles/PainPointCard.module.css';

interface PainPointCardProps {
  title: string;
  description: string;
  icon: string;
}

const getIconPath = (icon: string) => {
  switch (icon) {
    case 'heart':
      return 'M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z';
    case 'overload':
      return 'M15 17h5l-5 5v-5zM4.828 7l2.586 2.586a2 2 0 002.828 0L12.828 7H4.828zM4.828 17H9l-2.586 2.586a2 2 0 01-2.828 0L4.828 17z';
    case 'lightning':
      return 'M13 10V3L4 14h7v7l9-11h-7z';
    case 'checklist':
      return 'M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4';
    default:
      return 'M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z';
  }
};

export const PainPointCard: React.FC<PainPointCardProps> = ({
  title,
  description,
  icon,
}) => {
  return (
    <div className={styles.painPointCard}>
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
            d={getIconPath(icon)}
          />
        </svg>
      </div>
      <h3 className={styles.title}>{title}</h3>
      <p className={styles.description}>{description}</p>
    </div>
  );
};
