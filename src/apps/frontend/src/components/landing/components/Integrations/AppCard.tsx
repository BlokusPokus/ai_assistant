import React from 'react';
import styles from '../../styles/AppCard.module.css';

interface AppCardProps {
  name: string;
  gradientFrom: string;
  gradientTo: string;
  iconPaths: string[];
}

export const AppCard: React.FC<AppCardProps> = ({
  name,
  gradientFrom,
  gradientTo,
  iconPaths,
}) => {
  return (
    <div className={styles.appCard}>
      <div className={styles.cardContent}>
        <div
          className={styles.iconContainer}
          style={{
            background: `linear-gradient(to right, ${gradientFrom}, ${gradientTo})`,
          }}
        >
          <svg className={styles.icon} fill="currentColor" viewBox="0 0 24 24">
            {iconPaths.map((path, index) => (
              <path key={index} d={path} />
            ))}
          </svg>
        </div>
        <p className={styles.appName}>{name}</p>
      </div>
    </div>
  );
};
