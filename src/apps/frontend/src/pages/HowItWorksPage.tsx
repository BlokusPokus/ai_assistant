import React from 'react';
import {
  ArrowRight,
  UserPlus,
  Link,
  MessageSquare,
  Settings,
} from 'lucide-react';
import { Header } from '../components/landing/components/Header/Header';
import styles from '../components/landing/styles/HowItWorksPage.module.css';

interface Step {
  id: number;
  title: string;
  description: string;
  icon: React.ReactNode;
  image: string;
  features: string[];
}

const HowItWorksPage: React.FC = () => {
  const steps: Step[] = [
    {
      id: 1,
      title: 'Register',
      description: 'Create your account and get started with a free trial',
      icon: <UserPlus className="w-8 h-8" />,
      image: '/signup_screenshot.png',
      features: [
        'Quick signup process',
        '14-day free trial',
        'No credit card required',
        'Instant access to all features',
      ],
    },
    {
      id: 2,
      title: 'Connect to Integrations',
      description:
        'Link the productivity tools and services you want to automate',
      icon: <Link className="w-8 h-8" />,
      image: '/integrations_screenshot.png',
      features: [
        'Email (Gmail, Outlook)',
        'Calendar (Google Calendar, Outlook)',
        'Task management tools',
        'SMS notifications',
      ],
    },
    {
      id: 3,
      title: 'Text Your Number',
      description:
        'Send a text message to your assigned number to start interacting with your AI assistant',
      icon: <MessageSquare className="w-8 h-8" />,
      image: '/sms_text.png',
      features: [
        'Get your personal AI phone number',
        'Send commands via SMS',
        'Receive notifications and updates',
        '24/7 AI assistance',
      ],
    },
    {
      id: 4,
      title: 'Create Automations',
      description:
        'Set up custom automation rules and workflows to streamline your productivity',
      icon: <Settings className="w-8 h-8" />,
      image: '/automations_text.png',
      features: [
        'Custom automation rules',
        'Smart task scheduling',
        'Email filtering and responses',
        'Calendar management',
      ],
    },
  ];

  const features = [
    {
      icon: <UserPlus className="w-6 h-6" />,
      title: 'Easy Registration',
      description: 'Get started in minutes with our simple signup process',
    },
    {
      icon: <Link className="w-6 h-6" />,
      title: 'Powerful Integrations',
      description: 'Connect with all your favorite productivity tools',
    },
    {
      icon: <MessageSquare className="w-6 h-6" />,
      title: 'SMS Interface',
      description: 'Control everything through simple text messages',
    },
    {
      icon: <Settings className="w-6 h-6" />,
      title: 'Smart Automations',
      description: 'Create custom workflows that work for your needs',
    },
  ];

  return (
    <div className={styles.howItWorksPage}>
      <Header />
      <div className={styles.container}>
        {/* Header Section */}
        <div className={styles.header}>
          <h1 className={styles.title}>
            How <span className={styles.highlightedText}>Bloop</span> Works
          </h1>
          <p className={styles.subtitle}>
            Transform your productivity with AI-powered automation that learns
            from your habits
          </p>
        </div>

        {/* Steps Section */}
        <div className={styles.stepsSection}>
          <h2 className={styles.sectionTitle}>Simple 4-Step Process</h2>
          <div className={styles.stepsContainer}>
            {steps.map((step, index) => (
              <div key={step.id} className={styles.stepCard}>
                <div className={styles.stepNumber}>{step.id}</div>
                <div className={styles.stepContent}>
                  <div className={styles.stepHeader}>
                    <div className={styles.stepIcon}>{step.icon}</div>
                    <h3 className={styles.stepTitle}>{step.title}</h3>
                  </div>
                  <p className={styles.stepDescription}>{step.description}</p>

                  <div className={styles.stepImage}>
                    <img
                      src={step.image}
                      alt={step.title}
                      className={styles.screenshot}
                    />
                  </div>

                  <div className={styles.stepFeatures}>
                    <h4>Key Features:</h4>
                    <ul>
                      {step.features.map((feature, featureIndex) => (
                        <li key={featureIndex}>{feature}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                {index < steps.length - 1 && (
                  <div className={styles.stepArrow}>
                    <ArrowRight className="w-6 h-6" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Features Overview */}
        <div className={styles.featuresSection}>
          <h2 className={styles.sectionTitle}>Core Features</h2>
          <div className={styles.featuresGrid}>
            {features.map((feature, index) => (
              <div key={index} className={styles.featureCard}>
                <div className={styles.featureIcon}>{feature.icon}</div>
                <h3 className={styles.featureTitle}>{feature.title}</h3>
                <p className={styles.featureDescription}>
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* CTA Section */}
        <div className={styles.ctaSection}>
          <h2 className={styles.ctaTitle}>Ready to Get Started?</h2>
          <p className={styles.ctaDescription}>
            Join thousands of users who have transformed their productivity with
            Bloop
          </p>
          <div className={styles.ctaButtons}>
            <a href="/pricing" className={styles.primaryButton}>
              View Pricing
            </a>
            <a href="/login" className={styles.secondaryButton}>
              Start Free Trial
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HowItWorksPage;
