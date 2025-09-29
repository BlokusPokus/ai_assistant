import React from 'react';
import styles from '../../styles/FooterBottom.module.css';

const legalLinks = [
  { label: 'Privacy Policy', href: '#' },
  { label: 'Terms of Service', href: '#' },
  { label: 'Cookie Policy', href: '#' },
];

export const FooterBottom: React.FC = () => {
  return (
    <div className={styles.footerBottom}>
      <div className={styles.copyright}>
        © 2024 Bloop. All rights reserved.
      </div>
      <div className={styles.legalLinks}>
        {legalLinks.map(link => (
          <a key={link.label} href={link.href} className={styles.legalLink}>
            {link.label}
          </a>
        ))}
      </div>
    </div>
  );
};
