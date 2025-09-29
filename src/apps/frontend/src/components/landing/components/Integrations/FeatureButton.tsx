import React from 'react';
import styles from '../../styles/FeatureButton.module.css';

interface FeatureButtonProps {
  feature: {
    id: 'tasks' | 'notes' | 'calendar' | 'reminders' | 'insights';
    title: string;
    description: string;
    iconPath: string;
    colorScheme: 'green' | 'blue' | 'purple' | 'orange' | 'indigo';
  };
  isActive: boolean;
  onClick: () => void;
}

export const FeatureButton: React.FC<FeatureButtonProps> = ({
  feature,
  isActive,
  onClick,
}) => {
  const getColorClasses = (colorScheme: string) => {
    const colorMap = {
      green: {
        buttonActive: 'bg-green-50 border-green-200 shadow-md',
        buttonInactive:
          'bg-white border-gray-200 hover:border-gray-300 hover:shadow-md',
        iconActive: 'text-green-600',
        iconInactive: 'text-gray-600',
        titleActive: 'text-green-900',
        titleInactive: 'text-gray-900',
        progressGradient: 'linear-gradient(to right, #4ade80, #22c55e)', // green-400 to green-500
      },
      blue: {
        buttonActive: 'bg-blue-50 border-blue-200 shadow-md',
        buttonInactive:
          'bg-white border-gray-200 hover:border-gray-300 hover:shadow-md',
        iconActive: 'text-blue-600',
        iconInactive: 'text-gray-600',
        titleActive: 'text-blue-900',
        titleInactive: 'text-gray-900',
        progressGradient: 'linear-gradient(to right, #60a5fa, #3b82f6)', // blue-400 to blue-500
      },
      purple: {
        buttonActive: 'bg-purple-50 border-purple-200 shadow-md',
        buttonInactive:
          'bg-white border-gray-200 hover:border-gray-300 hover:shadow-md',
        iconActive: 'text-purple-600',
        iconInactive: 'text-gray-600',
        titleActive: 'text-purple-900',
        titleInactive: 'text-gray-900',
        progressGradient: 'linear-gradient(to right, #a78bfa, #8b5cf6)', // purple-400 to purple-500
      },
      orange: {
        buttonActive: 'bg-orange-50 border-orange-200 shadow-md',
        buttonInactive:
          'bg-white border-gray-200 hover:border-gray-300 hover:shadow-md',
        iconActive: 'text-orange-600',
        iconInactive: 'text-gray-600',
        titleActive: 'text-orange-900',
        titleInactive: 'text-gray-900',
        progressGradient: 'linear-gradient(to right, #fb923c, #f97316)', // orange-400 to orange-500
      },
      indigo: {
        buttonActive: 'bg-indigo-50 border-indigo-200 shadow-md',
        buttonInactive:
          'bg-white border-gray-200 hover:border-gray-300 hover:shadow-md',
        iconActive: 'text-indigo-600',
        iconInactive: 'text-gray-600',
        titleActive: 'text-indigo-900',
        titleInactive: 'text-gray-900',
        progressGradient: 'linear-gradient(to right, #818cf8, #6366f1)', // indigo-400 to indigo-500
      },
    };

    return colorMap[colorScheme as keyof typeof colorMap];
  };

  const colors = getColorClasses(feature.colorScheme);

  return (
    <button
      onClick={onClick}
      className={`${styles.featureButton} ${isActive ? colors.buttonActive : colors.buttonInactive}`}
    >
      <div className={styles.buttonContent}>
        <div className={styles.iconTitle}>
          <svg
            className={`${styles.icon} ${isActive ? colors.iconActive : colors.iconInactive}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d={feature.iconPath}
            />
          </svg>
          <span
            className={`${styles.title} ${isActive ? colors.titleActive : colors.titleInactive}`}
          >
            {feature.title}
          </span>
        </div>
        <p className={styles.description}>{feature.description}</p>
      </div>
      <div className={styles.progressBar}>
        <div
          className={`${styles.progressFill} ${isActive ? styles.active : styles.inactive}`}
          style={{
            background: colors.progressGradient,
          }}
        ></div>
      </div>
    </button>
  );
};
