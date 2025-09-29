import React from 'react';
import { Header } from './components/Header';
import { HeroSection } from './components/Hero';
import { ProblemSection } from './components/Problem';
import { SolutionSection } from './components/Solution';
import { IntegrationsSection } from './components/Integrations';
import { AIIntelligenceSection } from './components/AIIntelligence';
import { PrivacySection } from './components/Privacy';
import { Footer } from './components/Footer';
import { AnimatedBackground } from './components/Background';
import styles from './styles/LandingPage.module.css';
import './styles/animations.css';

const LandingPage: React.FC = () => {
  return (
    <div className={styles.landingPage}>
      {/* Animated Background */}
      <AnimatedBackground />

      {/* Header */}
      <Header />

      {/* Main Content */}
      <main className={styles.mainContent}>
        <HeroSection />
        <ProblemSection />
        <SolutionSection />
        <IntegrationsSection />
        <AIIntelligenceSection />
        <PrivacySection />
      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
};

export default LandingPage;
