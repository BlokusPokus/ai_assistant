import React from 'react';
import styles from '../../styles/LinkSection.module.css';

interface LinkSectionProps {
  title: string;
  links: Array<{ label: string; href: string }>;
}

export const LinkSection: React.FC<LinkSectionProps> = ({ title, links }) => {
  return (
    <div className={styles.linkSection}>
      <h3 className={styles.title}>{title}</h3>
      <ul className={styles.linksList}>
        {links.map(link => (
          <li key={link.label}>
            <a href={link.href} className={styles.link}>
              {link.label}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
};
