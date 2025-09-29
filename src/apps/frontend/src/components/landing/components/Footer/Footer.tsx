import React from 'react';
import { CompanyInfo } from './CompanyInfo';
import { FooterLinks } from './FooterLinks';
import { FooterBottom } from './FooterBottom';
import styles from '../../styles/Footer.module.css';

export const Footer: React.FC = () => {
  return (
    <footer className={styles.footer}>
      <div className={styles.footerContent}>
        <div className={styles.footerGrid}>
          <CompanyInfo />
          <FooterLinks />
        </div>
        <FooterBottom />
      </div>
    </footer>
  );
};
