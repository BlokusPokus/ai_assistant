import React from 'react';
import { LinkSection } from './LinkSection';
import styles from '../../styles/FooterLinks.module.css';

const linkSections = [
  {
    title: 'Product',
    links: [
      { label: 'Features', href: '#' },
      { label: 'Pricing', href: '#' },
      { label: 'Integrations', href: '#' },
      { label: 'API', href: '#' },
    ],
  },
  {
    title: 'Support',
    links: [
      { label: 'Help Center', href: '#' },
      { label: 'Contact Us', href: '#' },
      { label: 'Status', href: '#' },
      { label: 'Community', href: '#' },
    ],
  },
];

export const FooterLinks: React.FC = () => {
  return (
    <div className={styles.footerLinks}>
      {linkSections.map(section => (
        <LinkSection
          key={section.title}
          title={section.title}
          links={section.links}
        />
      ))}
    </div>
  );
};
