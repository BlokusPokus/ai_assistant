import React, { useState } from 'react';
import styles from './PrototypePage.module.css';
import { Link } from 'react-router-dom';

const PrototypePage: React.FC = () => {
  const [prototypeData, setPrototypeData] = useState({
    title: 'Prototype Page',
    description: 'This is a new page for quick prototyping and iteration',
    features: [
      'Quick iteration without affecting existing pages',
      'Clean slate for new features',
      'Easy to modify and test',
    ],
  });

  const [activeFeature, setActiveFeature] = useState('tasks');

  const featureImages = {
    tasks: '/src/pages/dashboard/image.png',
    notes: '/src/pages/dashboard/image.png',
    calendar: '/src/pages/dashboard/image.png',
    reminders: '/src/pages/dashboard/image.png',
    insights: '/src/pages/dashboard/image.png',
  };

  const handleUpdateData = (field: string, value: string) => {
    setPrototypeData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  return (
    <div className="min-h-screen relative overflow-hidden bg-white">
      {/* Header */}
      <header className="fixed top-1 left-0 right-0 py-3 md:py-6 md:max-w-[95%] max-w-full md:px-0 px-2 mx-auto w-full z-20">
        <div className="h-2" />
        <div className="w-full flex items-center justify-between relative px-3 md:px-4">
          <div className="flex-1 min-w-0">
            <Link to="/" className="flex items-center gap-2 shrink-0">
              <img src="/orca3d.png" alt="Bloop Logo" className="w-8 h-8" />
              <span
                className="text-lg md:text-xl font-medium"
                style={{ color: '#1a4835' }}
              >
                Bloop
              </span>
            </Link>
          </div>

          <nav className="hidden md:flex absolute left-1/2 -translate-x-1/2 items-center gap-6">
            <Link
              className="text-sm transition-colors hover:opacity-80"
              style={{ color: '#62795d' }}
              to="/features"
            >
              Features
            </Link>
            <Link
              className="text-sm transition-colors hover:opacity-80"
              style={{ color: '#62795d' }}
              to="/pricing"
            >
              Pricing
            </Link>
            <button
              className="text-sm transition-colors hover:opacity-80 cursor-pointer"
              style={{ color: '#62795d' }}
            >
              About
            </button>
            <button
              className="text-sm transition-colors hover:opacity-80"
              style={{ color: '#62795d' }}
            >
              Contact
            </button>
          </nav>

          <div className="flex-1 flex items-center gap-4 md:gap-6 justify-end">
            <div
              className="hidden md:flex items-center justify-end gap-6"
              style={{ color: '#62795d' }}
            >
              <a
                aria-label="Discord"
                className="hover:opacity-80 transition-colors"
                href="#"
                target="_blank"
                rel="noopener noreferrer"
              >
                <svg
                  className="w-5 h-5"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028c.462-.63.874-1.295 1.226-1.994a.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z" />
                </svg>
              </a>
              <a
                aria-label="X"
                className="hover:opacity-80 transition-colors"
                href="#"
                target="_blank"
                rel="noopener noreferrer"
              >
                <svg
                  className="w-5 h-5"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
                </svg>
              </a>
              <a
                aria-label="LinkedIn"
                className="hover:opacity-80 transition-colors"
                href="#"
                target="_blank"
                rel="noopener noreferrer"
              >
                <svg
                  className="w-5 h-5"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
                </svg>
              </a>
            </div>
            <div className="flex items-center text-sm gap-3">
              <button
                className="rounded-md px-3 py-1.5 cursor-pointer transition-all duration-300 hover:opacity-80"
                style={{ backgroundColor: '#e0e083', color: '#1a4835' }}
              >
                Log in
              </button>
              <button
                className="rounded-md px-3 py-1 cursor-pointer transition-all duration-300 hover:opacity-80"
                style={{ backgroundColor: '#1a4835', color: '#ebe2b2' }}
              >
                Sign up
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Animated Background Elements */}
      <div className="fixed inset-0 pointer-events-none">
        {/* Blur Ovals - 4 ovals starting from each corner */}
        <div
          className={`absolute top-0 left-0 w-[500px] h-[350px] blur-3xl ${styles.blurCircleOrange}`}
          style={{
            backgroundColor: '#98a758',
            borderRadius: '0% 50% 50% 0%',
          }}
        ></div>
        <div
          className={`absolute top-0 right-0 w-[700px] h-[500px] blur-3xl ${styles.blurCirclePink}`}
          style={{
            backgroundColor: '#ece5b5',
            borderRadius: '50% 0% 0% 50%',
          }}
        ></div>
        <div
          className={`absolute bottom-0 left-0 w-[750px] h-[550px] blur-3xl ${styles.blurCircleCyan}`}
          style={{
            backgroundColor: '#1a4835',
            borderRadius: '0% 50% 50% 0%',
          }}
        ></div>
        <div
          className={`absolute bottom-0 right-0 w-[650px] h-[450px] blur-3xl ${styles.blurCircleGreen}`}
          style={{
            backgroundColor: '#a0b192',
            borderRadius: '50% 0% 0% 50%',
          }}
        ></div>

        {/* Columns - Left Side */}
        <div
          style={{
            position: 'absolute',
            left: '0px',
            top: '0px',
            width: '80px',
            height: '100vh',
            backgroundColor: 'rgba(255, 255, 255, 0.5)',
            zIndex: 1000,
          }}
        ></div>
        <div
          style={{
            position: 'absolute',
            left: '80px',
            top: '0px',
            width: '80px',
            height: '100vh',
            backgroundColor: 'rgba(255, 255, 255, 0.45)',
            zIndex: 1000,
          }}
        ></div>
        <div
          style={{
            position: 'absolute',
            left: '160px',
            top: '0px',
            width: '80px',
            height: '100vh',
            backgroundColor: 'rgba(255, 255, 255, 0.4)',
            zIndex: 1000,
          }}
        ></div>
        <div
          style={{
            position: 'absolute',
            left: '240px',
            top: '0px',
            width: '80px',
            height: '100vh',
            backgroundColor: 'rgba(255, 255, 255, 0.35)',
            zIndex: 1000,
          }}
        ></div>
        <div
          style={{
            position: 'absolute',
            left: '320px',
            top: '0px',
            width: '80px',
            height: '100vh',
            backgroundColor: 'rgba(255, 255, 255, 0.3)',
            zIndex: 1000,
          }}
        ></div>
        <div
          style={{
            position: 'absolute',
            left: '400px',
            top: '0px',
            width: '80px',
            height: '100vh',
            backgroundColor: 'rgba(255, 255, 255, 0.25)',
            zIndex: 1000,
          }}
        ></div>
        <div
          style={{
            position: 'absolute',
            left: '480px',
            top: '0px',
            width: '80px',
            height: '100vh',
            backgroundColor: 'rgba(255, 255, 255, 0.2)',
            zIndex: 1000,
          }}
        ></div>
        <div
          style={{
            position: 'absolute',
            left: '560px',
            top: '0px',
            width: '80px',
            height: '100vh',
            backgroundColor: 'rgba(255, 255, 255, 0.15)',
            zIndex: 1000,
          }}
        ></div>

        {/* Columns - Right Side */}
        <div
          style={{
            position: 'absolute',
            right: '0px',
            top: '0px',
            width: '80px',
            height: '100vh',
            backgroundColor: 'rgba(255, 255, 255, 0.5)',
            zIndex: 1000,
          }}
        ></div>
        <div
          style={{
            position: 'absolute',
            right: '80px',
            top: '0px',
            width: '80px',
            height: '100vh',
            backgroundColor: 'rgba(255, 255, 255, 0.45)',
            zIndex: 1000,
          }}
        ></div>
        <div
          style={{
            position: 'absolute',
            right: '160px',
            top: '0px',
            width: '80px',
            height: '100vh',
            backgroundColor: 'rgba(255, 255, 255, 0.4)',
            zIndex: 1000,
          }}
        ></div>
        <div
          style={{
            position: 'absolute',
            right: '240px',
            top: '0px',
            width: '80px',
            height: '100vh',
            backgroundColor: 'rgba(255, 255, 255, 0.35)',
            zIndex: 1000,
          }}
        ></div>
        <div
          style={{
            position: 'absolute',
            right: '320px',
            top: '0px',
            width: '80px',
            height: '100vh',
            backgroundColor: 'rgba(255, 255, 255, 0.3)',
            zIndex: 1000,
          }}
        ></div>
        <div
          style={{
            position: 'absolute',
            right: '400px',
            top: '0px',
            width: '80px',
            height: '100vh',
            backgroundColor: 'rgba(255, 255, 255, 0.25)',
            zIndex: 1000,
          }}
        ></div>
        <div
          style={{
            position: 'absolute',
            right: '480px',
            top: '0px',
            width: '80px',
            height: '100vh',
            backgroundColor: 'rgba(255, 255, 255, 0.2)',
            zIndex: 1000,
          }}
        ></div>
        <div
          style={{
            position: 'absolute',
            right: '560px',
            top: '0px',
            width: '80px',
            height: '100vh',
            backgroundColor: 'rgba(255, 255, 255, 0.15)',
            zIndex: 1000,
          }}
        ></div>

        {/* Middle Columns - Fill the center gap */}
        <div
          style={{
            position: 'absolute',
            left: '640px',
            top: '0px',
            width: '80px',
            height: '100vh',
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            zIndex: 1000,
          }}
        ></div>
        <div
          style={{
            position: 'absolute',
            left: '720px',
            top: '0px',
            width: '80px',
            height: '100vh',
            backgroundColor: 'rgba(255, 255, 255, 0.05)',
            zIndex: 1000,
          }}
        ></div>
      </div>

      {/* Main Content */}
      <div className="relative z-10 max-w-7xl mx-auto py-6 sm:px-6 lg:px-8 ">
        {/* Hero Section */}
        <div className="mb-32 mt-16 text-center">
          <div className="text-card-foreground relative max-w-full md:max-w-5xl mx-auto p-16 md:p-20">
            <div className="mb-8">
              <div className="inline-flex items-center space-x-2"></div>
            </div>

            <h1 className="text-5xl md:text-6xl font-black mb-8 leading-tight">
              MORE out of{' '}
              <span
                style={{
                  fontFamily:
                    'GottaCatchWater, PlantasiaGlycine, Poppins, sans-serif',
                  fontWeight: 'normal',
                  background: 'linear-gradient(to right, #98a758, #a0b192)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                  fontSize: '1.2em',
                }}
              >
                Life
              </span>
            </h1>

            <p
              className="text-xl md:text-2xl mb-10 max-w-4xl mx-auto leading-relaxed"
              style={{ color: '#1a1a1a' }}
            >
              Bloop is your intelligent, adaptive, and proactive AI assistant
              designed to support you in experiencing more out of life, because
              everyone has unique needs
            </p>

            {/* Social Proof Stats */}
            <div className="grid grid-cols-3 gap-8 mb-10 max-w-2xl mx-auto"></div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                className="px-8 py-4 text-white rounded-lg font-semibold transition-colors duration-200 shadow-lg"
                style={{ backgroundColor: '#1a4835' }}
              >
                Get started free
              </button>
              {/* <button
                className="px-8 py-4 bg-white rounded-lg font-semibold transition-colors duration-200"
                style={{ color: '#62795d', border: '1px solid #a0b192' }}
              >
                Watch Demo
              </button> */}
            </div>
          </div>
        </div>

        {/* Problem / Pain Section */}
        <div className="relative z-10 max-w-6xl mx-auto mb-24">
          <div className="text-center mb-12">
            <h2
              className="text-3xl md:text-4xl font-bold mb-6"
              style={{ color: '#1a4835' }}
            >
              Modern Life moves fast
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
              Important things slip through the cracks. You want to live
              intentionally, but instead you're juggling apps, distractions, and
              endless to-dos.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-5 gap-8">
            <div className="text-center p-6">
              <div
                className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center"
                style={{ backgroundColor: '#fef2f2' }}
              >
                <svg
                  className="w-8 h-8"
                  style={{ color: '#dc2626' }}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
                  />
                </svg>
              </div>
              <h3
                className="text-xl font-semibold mb-3"
                style={{ color: '#1a4835' }}
              >
                Missed Connections
              </h3>
              <p className="text-gray-600">
                You realize you haven't texted your mom in weeks or made time to
                see close friends.
              </p>
            </div>

            <div className="text-center p-6">
              <div
                className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center"
                style={{ backgroundColor: '#fef2f2' }}
              >
                <svg
                  className="w-8 h-8"
                  style={{ color: '#dc2626' }}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
                  />
                </svg>
              </div>
              <h3
                className="text-xl font-semibold mb-3"
                style={{ color: '#1a4835' }}
              >
                Neglected Well-Being
              </h3>
              <p className="text-gray-600">
                Supplements get forgotten, workouts skipped, and sleep
                overlooked as life gets busy.
              </p>
            </div>

            <div className="text-center p-6">
              <div
                className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center"
                style={{ backgroundColor: '#fef2f2' }}
              >
                <svg
                  className="w-8 h-8"
                  style={{ color: '#dc2626' }}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M15 17h5l-5 5v-5zM4.828 7l2.586 2.586a2 2 0 002.828 0L12.828 7H4.828zM4.828 17H9l-2.586 2.586a2 2 0 01-2.828 0L4.828 17z"
                  />
                </svg>
              </div>
              <h3
                className="text-xl font-semibold mb-3"
                style={{ color: '#1a4835' }}
              >
                Digital Overload
              </h3>
              <p className="text-gray-600">
                Emails pile up, notifications never stop, and what really
                matters gets buried in the noise.
              </p>
            </div>

            <div className="text-center p-6">
              <div
                className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center"
                style={{ backgroundColor: '#fef2f2' }}
              >
                <svg
                  className="w-8 h-8"
                  style={{ color: '#dc2626' }}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M13 10V3L4 14h7v7l9-11h-7z"
                  />
                </svg>
              </div>
              <h3
                className="text-xl font-semibold mb-3"
                style={{ color: '#1a4835' }}
              >
                Lost Opportunities
              </h3>
              <p className="text-gray-600">
                You want to learn new skills or discover local events you'd love
                — but the effort to search and plan feels overwhelming.
              </p>
            </div>

            <div className="text-center p-6">
              <div
                className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center"
                style={{ backgroundColor: '#fef2f2' }}
              >
                <svg
                  className="w-8 h-8"
                  style={{ color: '#dc2626' }}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
                  />
                </svg>
              </div>
              <h3
                className="text-xl font-semibold mb-3"
                style={{ color: '#1a4835' }}
              >
                Administrative Load
              </h3>
              <p className="text-gray-600">
                You spend hours hunting for grocery deals, comparing insurance
                rates, and managing household tasks that eat up your precious
                time.
              </p>
            </div>
          </div>
        </div>

        {/* Solution Reveal Section */}
        <div className="relative z-10 max-w-6xl mx-auto mb-24">
          <div className="text-center mb-12">
            <h2
              className="text-3xl md:text-4xl font-bold mb-6"
              style={{ color: '#1a4835' }}
            >
              Your new Unified AI Assistant
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
              Pick your values, get personalized guidance. Our AI creates
              personalized task presets and guidance tailored to help you grow
              in those areas.
            </p>
          </div>
          {/* Values Section */}
          <div className="mb-24">
            <div className="max-w-6xl mx-auto text-center">
              <div className="grid md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-4 gap-8 mb-12">
                <div className="text-center p-6 rounded-xl border border-gray-200 bg-white hover:shadow-md transition-shadow duration-200">
                  <div
                    className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center"
                    style={{ backgroundColor: '#fef3c7' }}
                  >
                    <svg
                      className="w-8 h-8"
                      style={{ color: '#d97706' }}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
                      />
                    </svg>
                  </div>
                  <h3
                    className="text-xl font-semibold mb-3"
                    style={{ color: '#1a4835' }}
                  >
                    Family & Friends
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Strengthen relationships and create meaningful connections
                    with loved ones.
                  </p>
                  <div className="text-sm text-gray-500">
                    <p className="font-medium mb-1">AI suggests:</p>
                    <p>
                      Weekly family calls, gratitude journaling, memory-making
                      activities
                    </p>
                  </div>
                </div>

                <div className="text-center p-6 rounded-xl border border-gray-200 bg-white hover:shadow-md transition-shadow duration-200">
                  <div
                    className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center"
                    style={{ backgroundColor: '#d1fae5' }}
                  >
                    <svg
                      className="w-8 h-8"
                      style={{ color: '#059669' }}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
                      />
                    </svg>
                  </div>
                  <h3
                    className="text-xl font-semibold mb-3"
                    style={{ color: '#1a4835' }}
                  >
                    Health
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Build sustainable habits for physical and mental wellness.
                  </p>
                  <div className="text-sm text-gray-500">
                    <p className="font-medium mb-1">AI suggests:</p>
                    <p>
                      Daily movement goals, hydration tracking, sleep
                      optimization
                    </p>
                  </div>
                </div>

                <div className="text-center p-6 rounded-xl border border-gray-200 bg-white hover:shadow-md transition-shadow duration-200">
                  <div
                    className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center"
                    style={{ backgroundColor: '#e0e7ff' }}
                  >
                    <svg
                      className="w-8 h-8"
                      style={{ color: '#3730a3' }}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M13 10V3L4 14h7v7l9-11h-7z"
                      />
                    </svg>
                  </div>
                  <h3
                    className="text-xl font-semibold mb-3"
                    style={{ color: '#1a4835' }}
                  >
                    Resilience
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Develop mental strength and bounce back from challenges.
                  </p>
                  <div className="text-sm text-gray-500">
                    <p className="font-medium mb-1">AI suggests:</p>
                    <p>
                      Stress management, mindfulness practice, growth mindset
                      exercises
                    </p>
                  </div>
                </div>

                <div className="text-center p-6 rounded-xl border border-gray-200 bg-white hover:shadow-md transition-shadow duration-200">
                  <div
                    className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center"
                    style={{ backgroundColor: '#fce7f3' }}
                  >
                    <svg
                      className="w-8 h-8"
                      style={{ color: '#be185d' }}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
                      />
                    </svg>
                  </div>
                  <h3
                    className="text-xl font-semibold mb-3"
                    style={{ color: '#1a4835' }}
                  >
                    Organization
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Create systems and habits for a more structured, efficient
                    life.
                  </p>
                  <div className="text-sm text-gray-500">
                    <p className="font-medium mb-1">AI suggests:</p>
                    <p>
                      Time blocking, decluttering schedules, priority management
                    </p>
                  </div>
                </div>

                <div className="text-center p-6 rounded-xl border border-gray-200 bg-white hover:shadow-md transition-shadow duration-200">
                  <div
                    className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center"
                    style={{ backgroundColor: '#fef2f2' }}
                  >
                    <svg
                      className="w-8 h-8"
                      style={{ color: '#dc2626' }}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                      />
                    </svg>
                  </div>
                  <h3
                    className="text-xl font-semibold mb-3"
                    style={{ color: '#1a4835' }}
                  >
                    Social Life
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Expand your social circle and engage in meaningful
                    activities and experiences.
                  </p>
                  <div className="text-sm text-gray-500">
                    <p className="font-medium mb-1">AI suggests:</p>
                    <p>
                      Local meetups, hobby groups, networking events, community
                      activities
                    </p>
                  </div>
                </div>

                <div className="text-center p-6 rounded-xl border border-gray-200 bg-white hover:shadow-md transition-shadow duration-200">
                  <div
                    className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center"
                    style={{ backgroundColor: '#ecfdf5' }}
                  >
                    <svg
                      className="w-8 h-8"
                      style={{ color: '#16a34a' }}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"
                      />
                    </svg>
                  </div>
                  <h3
                    className="text-xl font-semibold mb-3"
                    style={{ color: '#1a4835' }}
                  >
                    Nature Lover
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Connect with the outdoors and develop a deeper appreciation
                    for the natural world.
                  </p>
                  <div className="text-sm text-gray-500">
                    <p className="font-medium mb-1">AI suggests:</p>
                    <p>
                      Hiking trails, nature photography, gardening, outdoor
                      meditation, wildlife watching
                    </p>
                  </div>
                </div>

                <div className="text-center p-6 rounded-xl border border-gray-200 bg-white hover:shadow-md transition-shadow duration-200">
                  <div
                    className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center"
                    style={{ backgroundColor: '#f3e8ff' }}
                  >
                    <svg
                      className="w-8 h-8"
                      style={{ color: '#7c3aed' }}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zM21 5a2 2 0 00-2-2h-4a2 2 0 00-2 2v12a4 4 0 004 4h4a2 2 0 002-2V5z"
                      />
                    </svg>
                  </div>
                  <h3
                    className="text-xl font-semibold mb-3"
                    style={{ color: '#1a4835' }}
                  >
                    Creative
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Express your artistic side and explore creative pursuits
                    that inspire and fulfill you.
                  </p>
                  <div className="text-sm text-gray-500">
                    <p className="font-medium mb-1">AI suggests:</p>
                    <p>
                      Art projects, writing prompts, music practice, design
                      challenges, creative workshops
                    </p>
                  </div>
                </div>

                <div className="text-center p-6 rounded-xl border border-gray-200 bg-white hover:shadow-md transition-shadow duration-200">
                  <div
                    className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center"
                    style={{ backgroundColor: '#fef3c7' }}
                  >
                    <svg
                      className="w-8 h-8"
                      style={{ color: '#d97706' }}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                      />
                    </svg>
                  </div>
                  <h3
                    className="text-xl font-semibold mb-3"
                    style={{ color: '#1a4835' }}
                  >
                    Create Your Own
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Define your own values and goals. Customize your journey
                    with personalized guidance.
                  </p>
                  <div className="text-sm text-gray-500">
                    <p className="font-medium mb-1">AI suggests:</p>
                    <p>
                      Custom goals, personal projects, unique challenges,
                      tailored recommendations
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* All your apps, one interface */}
        <div className="max-w-7xl mx-auto mb-24">
          <div className="text-center mb-12">
            <h2
              className="text-3xl md:text-4xl font-bold mb-6"
              style={{ color: '#1a4835' }}
            >
              All your apps, one interface
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Connect all your favorite tools and services in one unified
              workspace. No more switching between apps or losing context.
            </p>
          </div>

          {/* Connected Apps Carousel */}
          <div className="relative mb-12 flex justify-center">
            <div
              className="flex -space-x-12 overflow-x-auto scrollbar-hide pb-4 px-16"
              style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
            >
              <style>{`
                .scrollbar-hide::-webkit-scrollbar {
                  display: none;
                }
              `}</style>
              {/* Google */}
              <div className="flex-shrink-0 w-32 group cursor-pointer transition-all duration-300 ease-out hover:w-48 hover:z-20 relative z-10">
                <div className="text-center p-4 bg-white rounded-xl shadow-md border border-gray-100 group-hover:shadow-xl transition-all duration-300">
                  <div className="w-12 h-12 mx-auto mb-3 rounded-lg bg-gradient-to-r from-red-500 to-red-600 flex items-center justify-center">
                    <svg
                      className="w-6 h-6 text-white"
                      fill="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                      <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                      <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                      <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                    </svg>
                  </div>
                  <p className="text-sm font-medium text-gray-700">Google</p>
                </div>
              </div>

              {/* Slack */}
              <div className="flex-shrink-0 w-32 group cursor-pointer transition-all duration-300 ease-out hover:w-48 hover:z-20 relative z-10">
                <div className="text-center p-4 bg-white rounded-xl shadow-md border border-gray-100 group-hover:shadow-xl transition-all duration-300">
                  <div className="w-12 h-12 mx-auto mb-3 rounded-lg bg-gradient-to-r from-purple-500 to-purple-600 flex items-center justify-center">
                    <svg
                      className="w-6 h-6 text-white"
                      fill="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path d="M5.042 15.165a2.528 2.528 0 0 1-2.52 2.523A2.528 2.528 0 0 1 0 15.165a2.527 2.527 0 0 1 2.522-2.52h2.52v2.52zM6.313 15.165a2.527 2.527 0 0 1 2.521-2.52 2.527 2.527 0 0 1 2.521 2.52v6.313A2.528 2.528 0 0 1 8.834 24a2.528 2.528 0 0 1-2.521-2.522v-6.313zM8.834 5.042a2.528 2.528 0 0 1-2.521-2.52A2.528 2.528 0 0 1 8.834 0a2.528 2.528 0 0 1 2.521 2.522v2.52H8.834zM8.834 6.313a2.528 2.528 0 0 1 2.521 2.521 2.528 2.528 0 0 1-2.521 2.521H2.522A2.528 2.528 0 0 1 0 8.834a2.528 2.528 0 0 1 2.522-2.521h6.312zM18.956 8.834a2.528 2.528 0 0 1 2.522-2.521A2.528 2.528 0 0 1 24 8.834a2.528 2.528 0 0 1-2.522 2.521h-2.522V8.834zM17.688 8.834a2.528 2.528 0 0 1-2.523 2.521 2.527 2.527 0 0 1-2.52-2.521V2.522A2.527 2.527 0 0 1 15.165 0a2.528 2.528 0 0 1 2.523 2.522v6.312zM15.165 18.956a2.528 2.528 0 0 1 2.523 2.522A2.528 2.528 0 0 1 15.165 24a2.527 2.527 0 0 1-2.52-2.522v-2.522h2.52zM15.165 17.688a2.527 2.527 0 0 1-2.52-2.523 2.526 2.526 0 0 1 2.52-2.52h6.313A2.527 2.527 0 0 1 24 15.165a2.528 2.528 0 0 1-2.522 2.523h-6.313z" />
                    </svg>
                  </div>
                  <p className="text-sm font-medium text-gray-700">Slack</p>
                </div>
              </div>

              {/* Notion */}
              <div className="flex-shrink-0 w-32 group cursor-pointer transition-all duration-300 ease-out hover:w-48 hover:z-20 relative z-10">
                <div className="text-center p-4 bg-white rounded-xl shadow-md border border-gray-100 group-hover:shadow-xl transition-all duration-300">
                  <div className="w-12 h-12 mx-auto mb-3 rounded-lg bg-gradient-to-r from-gray-700 to-gray-800 flex items-center justify-center">
                    <svg
                      className="w-6 h-6 text-white"
                      fill="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path d="M4.459 4.208c.746.606 1.026.56 2.428.466l13.215-.793c.28 0 .047-.28-.046-.326L17.86 1.968c-.42-.326-.981-.7-2.055-.607L3.01 2.295c-.466.046-.56.28-.374.466zm.793 3.08v13.904c0 .747.373 1.027 1.214.98l14.523-.84c.841-.046.935-.56.935-1.167V6.354c0-.606-.233-.933-.748-.887l-15.177.887c-.56.047-.747.327-.747.933zm14.337.745c.093.42 0 .84-.42.888l-.7.14v10.264c-.608.327-1.168.514-1.635.514-.748 0-.935-.234-1.495-.933l-4.577-7.186v6.952L12.21 19s0 .84-1.168.84l-3.222.186c-.093-.186 0-.653.327-.746l.84-.233V9.854L7.822 9.76c-.094-.42.14-1.026.793-1.073l3.456-.233 4.764 7.279v-6.44l-1.215-.139c-.093-.514.28-.887.747-.933zM1.936 1.035l13.177-.794c.327-.047.607-.14.933-.326L18.8.157c.56-.327.981-.514 1.635-.514.748 0 1.495.327 1.495.933v21.77c0 .747-.373 1.027-1.214.98l-15.177-.887c-.747-.046-.935-.56-.935-1.167V2.295c0-.56.233-.933.748-.933z" />
                    </svg>
                  </div>
                  <p className="text-sm font-medium text-gray-700">Notion</p>
                </div>
              </div>

              {/* Spotify */}
              <div className="flex-shrink-0 w-32 group cursor-pointer transition-all duration-300 ease-out hover:w-48 hover:z-20 relative z-10">
                <div className="text-center p-4 bg-white rounded-xl shadow-md border border-gray-100 group-hover:shadow-xl transition-all duration-300">
                  <div className="w-12 h-12 mx-auto mb-3 rounded-lg bg-gradient-to-r from-green-500 to-green-600 flex items-center justify-center">
                    <svg
                      className="w-6 h-6 text-white"
                      fill="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.42 1.56-.299.421-1.02.599-1.559.3z" />
                    </svg>
                  </div>
                  <p className="text-sm font-medium text-gray-700">Spotify</p>
                </div>
              </div>

              {/* Oura Ring */}
              <div className="flex-shrink-0 w-32 group cursor-pointer transition-all duration-300 ease-out hover:w-48 hover:z-20 relative z-10">
                <div className="text-center p-4 bg-white rounded-xl shadow-md border border-gray-100 group-hover:shadow-xl transition-all duration-300">
                  <div className="w-12 h-12 mx-auto mb-3 rounded-lg bg-gradient-to-r from-gray-800 to-black flex items-center justify-center">
                    <svg
                      className="w-6 h-6 text-white"
                      fill="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm0-14c-3.31 0-6 2.69-6 6s2.69 6 6 6 6-2.69 6-6-2.69-6-6-6zm0 10c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4zm0-6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z" />
                    </svg>
                  </div>
                  <p className="text-sm font-medium text-gray-700">Oura Ring</p>
                </div>
              </div>

              {/* Microsoft Suite */}
              <div className="flex-shrink-0 w-32 group cursor-pointer transition-all duration-300 ease-out hover:w-48 hover:z-20 relative z-10">
                <div className="text-center p-4 bg-white rounded-xl shadow-md border border-gray-100 group-hover:shadow-xl transition-all duration-300">
                  <div className="w-12 h-12 mx-auto mb-3 rounded-lg bg-gradient-to-r from-blue-600 to-blue-700 flex items-center justify-center">
                    <svg
                      className="w-6 h-6 text-white"
                      fill="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path d="M11.4 24H0V12.6h11.4V24zM24 24H12.6V12.6H24V24zM11.4 11.4H0V0h11.4v11.4zM24 11.4H12.6V0H24v11.4z" />
                    </svg>
                  </div>
                  <p className="text-sm font-medium text-gray-700">Microsoft</p>
                </div>
              </div>

              {/* Todoist */}
              <div className="flex-shrink-0 w-32 group cursor-pointer transition-all duration-300 ease-out hover:w-48 hover:z-20 relative z-10">
                <div className="text-center p-4 bg-white rounded-xl shadow-md border border-gray-100 group-hover:shadow-xl transition-all duration-300">
                  <div className="w-12 h-12 mx-auto mb-3 rounded-lg bg-gradient-to-r from-red-600 to-red-700 flex items-center justify-center">
                    <svg
                      className="w-6 h-6 text-white"
                      fill="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path d="M21 3H3c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h18c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H3V5h18v14zm-5-7v-2h-2v2h-2v2h2v2h2v-2h2v-2h-2z" />
                    </svg>
                  </div>
                  <p className="text-sm font-medium text-gray-700">Todoist</p>
                </div>
              </div>

              {/* Strava */}
              <div className="flex-shrink-0 w-32 group cursor-pointer transition-all duration-300 ease-out hover:w-48 hover:z-20 relative z-10">
                <div className="text-center p-4 bg-white rounded-xl shadow-md border border-gray-100 group-hover:shadow-xl transition-all duration-300">
                  <div className="w-12 h-12 mx-auto mb-3 rounded-lg bg-gradient-to-r from-orange-500 to-orange-600 flex items-center justify-center">
                    <svg
                      className="w-6 h-6 text-white"
                      fill="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path d="M15.387 17.944l-2.089-4.116h-3.065L15.387 24l5.15-10.172h-3.066m-7.008-5.599l2.836 5.599h4.172L10.463 0l-7.13 14.401h4.169" />
                    </svg>
                  </div>
                  <p className="text-sm font-medium text-gray-700">Strava</p>
                </div>
              </div>

              {/* Mint */}
              <div className="flex-shrink-0 w-32 group cursor-pointer transition-all duration-300 ease-out hover:w-48 hover:z-20 relative z-10">
                <div className="text-center p-4 bg-white rounded-xl shadow-md border border-gray-100 group-hover:shadow-xl transition-all duration-300">
                  <div className="w-12 h-12 mx-auto mb-3 rounded-lg bg-gradient-to-r from-green-500 to-green-600 flex items-center justify-center">
                    <svg
                      className="w-6 h-6 text-white"
                      fill="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
                    </svg>
                  </div>
                  <p className="text-sm font-medium text-gray-700">Mint</p>
                </div>
              </div>

              {/* X */}
              <div className="flex-shrink-0 w-32 group cursor-pointer transition-all duration-300 ease-out hover:w-48 hover:z-20 relative z-10">
                <div className="text-center p-4 bg-white rounded-xl shadow-md border border-gray-100 group-hover:shadow-xl transition-all duration-300">
                  <div className="w-12 h-12 mx-auto mb-3 rounded-lg bg-gradient-to-r from-black to-gray-800 flex items-center justify-center">
                    <svg
                      className="w-6 h-6 text-white"
                      fill="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
                    </svg>
                  </div>
                  <p className="text-sm font-medium text-gray-700">X</p>
                </div>
              </div>

              {/* Ultrahuman */}
              <div className="flex-shrink-0 w-32 group cursor-pointer transition-all duration-300 ease-out hover:w-48 hover:z-20 relative z-10">
                <div className="text-center p-4 bg-white rounded-xl shadow-md border border-gray-100 group-hover:shadow-xl transition-all duration-300">
                  <div className="w-12 h-12 mx-auto mb-3 rounded-lg bg-gradient-to-r from-indigo-600 to-indigo-700 flex items-center justify-center">
                    <svg
                      className="w-6 h-6 text-white"
                      fill="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm0-14c-3.31 0-6 2.69-6 6s2.69 6 6 6 6-2.69 6-6-2.69-6-6-6zm0 10c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4zm0-6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z" />
                    </svg>
                  </div>
                  <p className="text-sm font-medium text-gray-700">
                    Ultrahuman
                  </p>
                </div>
              </div>

              {/* Map My Run */}
              <div className="flex-shrink-0 w-32 group cursor-pointer transition-all duration-300 ease-out hover:w-48 hover:z-20 relative z-10">
                <div className="text-center p-4 bg-white rounded-xl shadow-md border border-gray-100 group-hover:shadow-xl transition-all duration-300">
                  <div className="w-12 h-12 mx-auto mb-3 rounded-lg bg-gradient-to-r from-blue-500 to-blue-600 flex items-center justify-center">
                    <svg
                      className="w-6 h-6 text-white"
                      fill="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z" />
                    </svg>
                  </div>
                  <p className="text-sm font-medium text-gray-700">
                    Map My Run
                  </p>
                </div>
              </div>

              {/* Facebook */}
              <div className="flex-shrink-0 w-32 group cursor-pointer transition-all duration-300 ease-out hover:w-48 hover:z-20 relative z-10">
                <div className="text-center p-4 bg-white rounded-xl shadow-md border border-gray-100 group-hover:shadow-xl transition-all duration-300">
                  <div className="w-12 h-12 mx-auto mb-3 rounded-lg bg-gradient-to-r from-blue-600 to-blue-700 flex items-center justify-center">
                    <svg
                      className="w-6 h-6 text-white"
                      fill="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
                    </svg>
                  </div>
                  <p className="text-sm font-medium text-gray-700">Facebook</p>
                </div>
              </div>
            </div>
          </div>

          {/* Feature Navigation and Preview */}
          <div className="mb-12">
            <div className="flex flex-col lg:flex-row gap-8 max-w-6xl mx-auto justify-center items-center">
              {/* Feature Navigation Buttons - Vertical */}
              <div className="flex flex-col gap-3 lg:w-80">
                {/* Tasks */}
                <button
                  onClick={() => setActiveFeature('tasks')}
                  className={`group relative w-full p-4 text-left rounded-xl border transition-all duration-200 ${
                    activeFeature === 'tasks'
                      ? 'bg-green-50 border-green-200 shadow-md'
                      : 'bg-white border-gray-200 hover:border-gray-300 hover:shadow-md'
                  }`}
                >
                  <div className="flex items-center mb-2">
                    <svg
                      className={`w-4 h-4 mr-3 ${activeFeature === 'tasks' ? 'text-green-600' : 'text-gray-600'}`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
                      />
                    </svg>
                    <span
                      className={`font-semibold ${activeFeature === 'tasks' ? 'text-green-900' : 'text-gray-900'}`}
                    >
                      Tasks
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-3">
                    Smart task management that learns your patterns and helps
                    you stay organized without the overwhelm.
                  </p>
                  <div className="absolute bottom-0 left-0 w-full h-1 bg-gray-100 rounded-b-xl overflow-hidden">
                    <div
                      className={`h-full transition-all duration-300 rounded-b-xl ${
                        activeFeature === 'tasks'
                          ? 'w-full bg-gradient-to-r from-green-400 to-green-500'
                          : 'w-0 group-hover:w-full bg-gradient-to-r from-green-400 to-green-500'
                      }`}
                    ></div>
                  </div>
                </button>

                {/* Notes */}
                <button
                  onClick={() => setActiveFeature('notes')}
                  className={`group relative w-full p-4 text-left rounded-xl border transition-all duration-200 ${
                    activeFeature === 'notes'
                      ? 'bg-blue-50 border-blue-200 shadow-md'
                      : 'bg-white border-gray-200 hover:border-gray-300 hover:shadow-md'
                  }`}
                >
                  <div className="flex items-center mb-2">
                    <svg
                      className={`w-4 h-4 mr-3 ${activeFeature === 'notes' ? 'text-blue-600' : 'text-gray-600'}`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                      />
                    </svg>
                    <span
                      className={`font-semibold ${activeFeature === 'notes' ? 'text-blue-900' : 'text-gray-900'}`}
                    >
                      Notes
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-3">
                    Capture thoughts, memories, and ideas with intelligent
                    organization that makes everything findable.
                  </p>
                  <div className="absolute bottom-0 left-0 w-full h-1 bg-gray-100 rounded-b-xl overflow-hidden">
                    <div
                      className={`h-full transition-all duration-300 rounded-b-xl ${
                        activeFeature === 'notes'
                          ? 'w-full bg-gradient-to-r from-blue-400 to-blue-500'
                          : 'w-0 group-hover:w-full bg-gradient-to-r from-blue-400 to-blue-500'
                      }`}
                    ></div>
                  </div>
                </button>

                {/* Calendar */}
                <button
                  onClick={() => setActiveFeature('calendar')}
                  className={`group relative w-full p-4 text-left rounded-xl border transition-all duration-200 ${
                    activeFeature === 'calendar'
                      ? 'bg-purple-50 border-purple-200 shadow-md'
                      : 'bg-white border-gray-200 hover:border-gray-300 hover:shadow-md'
                  }`}
                >
                  <div className="flex items-center mb-2">
                    <svg
                      className={`w-4 h-4 mr-3 ${activeFeature === 'calendar' ? 'text-purple-600' : 'text-gray-600'}`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                      />
                    </svg>
                    <span
                      className={`font-semibold ${activeFeature === 'calendar' ? 'text-purple-900' : 'text-gray-900'}`}
                    >
                      Calendar
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-3">
                    Intelligent scheduling that helps you balance work, life,
                    and everything in between.
                  </p>
                  <div className="absolute bottom-0 left-0 w-full h-1 bg-gray-100 rounded-b-xl overflow-hidden">
                    <div
                      className={`h-full transition-all duration-300 rounded-b-xl ${
                        activeFeature === 'calendar'
                          ? 'w-full bg-gradient-to-r from-purple-400 to-purple-500'
                          : 'w-0 group-hover:w-full bg-gradient-to-r from-purple-400 to-purple-500'
                      }`}
                    ></div>
                  </div>
                </button>

                {/* Reminders */}
                <button
                  onClick={() => setActiveFeature('reminders')}
                  className={`group relative w-full p-4 text-left rounded-xl border transition-all duration-200 ${
                    activeFeature === 'reminders'
                      ? 'bg-orange-50 border-orange-200 shadow-md'
                      : 'bg-white border-gray-200 hover:border-gray-300 hover:shadow-md'
                  }`}
                >
                  <div className="flex items-center mb-2">
                    <svg
                      className={`w-4 h-4 mr-3 ${activeFeature === 'reminders' ? 'text-orange-600' : 'text-gray-600'}`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M15 17h5l-5 5v-5zM4.828 7l2.586 2.586a2 2 0 002.828 0L12.828 7H4.828zM4.828 17H9l-2.586 2.586a2 2 0 01-2.828 0L4.828 17z"
                      />
                    </svg>
                    <span
                      className={`font-semibold ${activeFeature === 'reminders' ? 'text-orange-900' : 'text-gray-900'}`}
                    >
                      Reminders
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-3">
                    Proactive reminders that help you stay on top of what
                    matters most in your life.
                  </p>
                  <div className="absolute bottom-0 left-0 w-full h-1 bg-gray-100 rounded-b-xl overflow-hidden">
                    <div
                      className={`h-full transition-all duration-300 rounded-b-xl ${
                        activeFeature === 'reminders'
                          ? 'w-full bg-gradient-to-r from-orange-400 to-orange-500'
                          : 'w-0 group-hover:w-full bg-gradient-to-r from-orange-400 to-orange-500'
                      }`}
                    ></div>
                  </div>
                </button>

                {/* Insights */}
                <button
                  onClick={() => setActiveFeature('insights')}
                  className={`group relative w-full p-4 text-left rounded-xl border transition-all duration-200 ${
                    activeFeature === 'insights'
                      ? 'bg-indigo-50 border-indigo-200 shadow-md'
                      : 'bg-white border-gray-200 hover:border-gray-300 hover:shadow-md'
                  }`}
                >
                  <div className="flex items-center mb-2">
                    <svg
                      className={`w-4 h-4 mr-3 ${activeFeature === 'insights' ? 'text-indigo-600' : 'text-gray-600'}`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                      />
                    </svg>
                    <span
                      className={`font-semibold ${activeFeature === 'insights' ? 'text-indigo-900' : 'text-gray-900'}`}
                    >
                      Insights
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-3">
                    AI-powered analytics that help you understand your patterns
                    and optimize your life.
                  </p>
                  <div className="absolute bottom-0 left-0 w-full h-1 bg-gray-100 rounded-b-xl overflow-hidden">
                    <div
                      className={`h-full transition-all duration-300 rounded-b-xl ${
                        activeFeature === 'insights'
                          ? 'w-full bg-gradient-to-r from-indigo-400 to-indigo-500'
                          : 'w-0 group-hover:w-full bg-gradient-to-r from-indigo-400 to-indigo-500'
                      }`}
                    ></div>
                  </div>
                </button>
              </div>

              {/* Feature Preview Image */}
              <div className="flex-1 flex justify-center">
                <div className="relative w-full max-w-xs rounded-2xl overflow-hidden shadow-2xl border border-gray-200">
                  <img
                    src={
                      featureImages[activeFeature as keyof typeof featureImages]
                    }
                    alt={`${activeFeature} feature preview`}
                    className="w-full h-auto transition-all duration-500 ease-in-out"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent"></div>
                  <div className="absolute bottom-4 left-4 text-white">
                    <h3 className="text-lg font-bold capitalize mb-1">
                      {activeFeature}
                    </h3>
                    <p className="text-xs opacity-90">
                      {activeFeature === 'tasks' &&
                        'Smart task management interface'}
                      {activeFeature === 'notes' &&
                        'Intelligent note-taking workspace'}
                      {activeFeature === 'calendar' &&
                        'Advanced calendar and scheduling'}
                      {activeFeature === 'reminders' &&
                        'Proactive reminder system'}
                      {activeFeature === 'insights' &&
                        'AI-powered analytics dashboard'}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Integration Benefits */}
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center p-6">
              <div
                className="w-16 h-16 mx-auto mb-4 rounded-2xl flex items-center justify-center"
                style={{ backgroundColor: '#98a758' }}
              >
                <svg
                  className="w-8 h-8 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M13 10V3L4 14h7v7l9-11h-7z"
                  />
                </svg>
              </div>
              <h3
                className="text-xl font-bold mb-3"
                style={{ color: '#1a4835' }}
              >
                Instant Sync
              </h3>
              <p className="text-gray-600">
                All your data syncs instantly across every connected app. No
                more manual updates or lost information.
              </p>
            </div>

            <div className="text-center p-6">
              <div
                className="w-16 h-16 mx-auto mb-4 rounded-2xl flex items-center justify-center"
                style={{ backgroundColor: '#5b8e4f' }}
              >
                <svg
                  className="w-8 h-8 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <h3
                className="text-xl font-bold mb-3"
                style={{ color: '#1a4835' }}
              >
                Smart Automation
              </h3>
              <p className="text-gray-600">
                Bloop learns your patterns and automates routine tasks across
                all your connected services.
              </p>
            </div>

            <div className="text-center p-6">
              <div
                className="w-16 h-16 mx-auto mb-4 rounded-2xl flex items-center justify-center"
                style={{ backgroundColor: '#265f2e' }}
              >
                <svg
                  className="w-8 h-8 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
                  />
                </svg>
              </div>
              <h3
                className="text-xl font-bold mb-3"
                style={{ color: '#1a4835' }}
              >
                Unified Experience
              </h3>
              <p className="text-gray-600">
                One clean interface to manage everything. No more context
                switching or app fatigue.
              </p>
            </div>
          </div>
        </div>

        {/* Your Data is Yours Section */}
        <div className="mb-24">
          <div className="max-w-4xl mx-auto text-center">
            <h2
              className="text-3xl md:text-4xl font-bold mb-6"
              style={{ color: '#1a4835' }}
            >
              Your data is yours
            </h2>
            <p
              className="text-lg md:text-xl mb-8 leading-relaxed"
              style={{ color: '#62795d' }}
            >
              We believe in complete transparency and user control. Your
              personal information, conversations, and data remain private and
              secure.
            </p>

            <div className="grid md:grid-cols-3 gap-8 mb-12">
              <div className="text-center">
                <div
                  className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center"
                  style={{ backgroundColor: '#e8f5e8' }}
                >
                  <svg
                    className="w-8 h-8"
                    style={{ color: '#1a4835' }}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                    />
                  </svg>
                </div>
                <h3
                  className="text-xl font-semibold mb-3"
                  style={{ color: '#1a4835' }}
                >
                  End-to-End Encryption
                </h3>
                <p className="text-gray-600">
                  All your data is encrypted in transit and at rest, ensuring
                  maximum security.
                </p>
              </div>

              <div className="text-center">
                <div
                  className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center"
                  style={{ backgroundColor: '#e8f5e8' }}
                >
                  <svg
                    className="w-8 h-8"
                    style={{ color: '#1a4835' }}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                    />
                  </svg>
                </div>
                <h3
                  className="text-xl font-semibold mb-3"
                  style={{ color: '#1a4835' }}
                >
                  Privacy First
                </h3>
                <p className="text-gray-600">
                  We never sell your data or use it for advertising. Your
                  privacy is our priority.
                </p>
              </div>

              <div className="text-center">
                <div
                  className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center"
                  style={{ backgroundColor: '#e8f5e8' }}
                >
                  <svg
                    className="w-8 h-8"
                    style={{ color: '#1a4835' }}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"
                    />
                  </svg>
                </div>
                <h3
                  className="text-xl font-semibold mb-3"
                  style={{ color: '#1a4835' }}
                >
                  Data Export
                </h3>
                <p className="text-gray-600">
                  Export all your data anytime. You own your information and can
                  take it with you.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Call to Action */}
        <div className="text-center">
          <button
            className="px-8 py-4 text-white rounded-lg font-semibold transition-colors duration-200 shadow-lg"
            style={{ backgroundColor: '#1a4835' }}
          >
            Get started free
          </button>
        </div>
      </div>

      {/* Why use multiple apps when Bloop does it better? */}

      {/* AI-Powered Intelligence Section */}
      <div className="relative z-10 max-w-6xl mx-auto mb-24">
        <div className="text-center mb-12">
          <h2
            className="text-3xl md:text-4xl font-bold mb-6"
            style={{ color: '#1a4835' }}
          >
            AI-Powered Intelligence That Actually Works
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
            Behind Bloop's simple interface lies sophisticated AI technology
            that learns, adapts, and executes tasks with unprecedented
            intelligence.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
          {/* Intelligent Task Scheduling */}
          <div className="text-center p-8 rounded-xl border border-gray-200 bg-white hover:shadow-lg transition-shadow duration-200">
            <div
              className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center"
              style={{ backgroundColor: '#e0f2fe' }}
            >
              <svg
                className="w-8 h-8"
                style={{ color: '#0369a1' }}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <h3
              className="text-xl font-semibold mb-3"
              style={{ color: '#1a4835' }}
            >
              Intelligent Task Scheduling
            </h3>
            <p className="text-gray-600 mb-4">
              AI-powered scheduling that learns your patterns and optimizes task
              timing for maximum productivity and minimal stress.
            </p>
            <div className="text-sm text-gray-500">
              <p className="font-medium mb-1">Powered by:</p>
              <p>
                Advanced AI algorithms, Celery background processing, smart
                timing optimization
              </p>
            </div>
          </div>

          {/* Automated Task Execution */}
          <div className="text-center p-8 rounded-xl border border-gray-200 bg-white hover:shadow-lg transition-shadow duration-200">
            <div
              className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center"
              style={{ backgroundColor: '#f0fdf4' }}
            >
              <svg
                className="w-8 h-8"
                style={{ color: '#16a34a' }}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                />
              </svg>
            </div>
            <h3
              className="text-xl font-semibold mb-3"
              style={{ color: '#1a4835' }}
            >
              Automated Task Execution
            </h3>
            <p className="text-gray-600 mb-4">
              Tasks execute automatically with AI-powered decision making,
              context awareness, and intelligent result processing.
            </p>
            <div className="text-sm text-gray-500">
              <p className="font-medium mb-1">Powered by:</p>
              <p>
                AgentCore AI, enhanced prompt architecture, metadata integration
              </p>
            </div>
          </div>

          {/* Smart Event Evaluation */}
          <div className="text-center p-8 rounded-xl border border-gray-200 bg-white hover:shadow-lg transition-shadow duration-200">
            <div
              className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center"
              style={{ backgroundColor: '#fef3c7' }}
            >
              <svg
                className="w-8 h-8"
                style={{ color: '#d97706' }}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                />
              </svg>
            </div>
            <h3
              className="text-xl font-semibold mb-3"
              style={{ color: '#1a4835' }}
            >
              Smart Event Evaluation
            </h3>
            <p className="text-gray-600 mb-4">
              AI analyzes your calendar events, identifies patterns, and
              suggests intelligent actions to optimize your schedule.
            </p>
            <div className="text-sm text-gray-500">
              <p className="font-medium mb-1">Powered by:</p>
              <p>
                AIEventEvaluator, recurrence pattern analysis, action
                recommendations
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="relative z-10 bg-white border-t border-gray-200 mt-16">
        <div className="max-w-6xl mx-auto px-4 py-12">
          <div className="grid md:grid-cols-4 gap-8">
            {/* Company Info */}
            <div className="md:col-span-2">
              <div className="flex items-center gap-2 mb-4">
                <img src="/orca3d.png" alt="Bloop Logo" className="w-8 h-8" />
                <span
                  className="text-xl font-bold"
                  style={{ color: '#1a4835' }}
                >
                  Bloop
                </span>
              </div>
              <p className="text-gray-600 mb-4 max-w-md">
                Your intelligent, adaptive, and proactive AI assistant designed
                to help you experience more out of life.
              </p>
              <div className="flex gap-4">
                <a
                  href="#"
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                  aria-label="Discord"
                >
                  <svg
                    className="w-5 h-5"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028c.462-.63.874-1.295 1.226-1.994a.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z" />
                  </svg>
                </a>
                <a
                  href="#"
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                  aria-label="X"
                >
                  <svg
                    className="w-5 h-5"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
                  </svg>
                </a>
                <a
                  href="#"
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                  aria-label="LinkedIn"
                >
                  <svg
                    className="w-5 h-5"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
                  </svg>
                </a>
              </div>
            </div>

            {/* Product */}
            <div>
              <h3 className="font-semibold text-gray-900 mb-4">Product</h3>
              <ul className="space-y-2">
                <li>
                  <a
                    href="#"
                    className="text-gray-600 hover:text-gray-900 transition-colors"
                  >
                    Features
                  </a>
                </li>
                <li>
                  <a
                    href="#"
                    className="text-gray-600 hover:text-gray-900 transition-colors"
                  >
                    Pricing
                  </a>
                </li>
                <li>
                  <a
                    href="#"
                    className="text-gray-600 hover:text-gray-900 transition-colors"
                  >
                    Integrations
                  </a>
                </li>
                <li>
                  <a
                    href="#"
                    className="text-gray-600 hover:text-gray-900 transition-colors"
                  >
                    API
                  </a>
                </li>
              </ul>
            </div>

            {/* Support */}
            <div>
              <h3 className="font-semibold text-gray-900 mb-4">Support</h3>
              <ul className="space-y-2">
                <li>
                  <a
                    href="#"
                    className="text-gray-600 hover:text-gray-900 transition-colors"
                  >
                    Help Center
                  </a>
                </li>
                <li>
                  <a
                    href="#"
                    className="text-gray-600 hover:text-gray-900 transition-colors"
                  >
                    Contact Us
                  </a>
                </li>
                <li>
                  <a
                    href="#"
                    className="text-gray-600 hover:text-gray-900 transition-colors"
                  >
                    Status
                  </a>
                </li>
                <li>
                  <a
                    href="#"
                    className="text-gray-600 hover:text-gray-900 transition-colors"
                  >
                    Community
                  </a>
                </li>
              </ul>
            </div>
          </div>

          {/* Bottom Section */}
          <div className="border-t border-gray-200 mt-8 pt-8">
            <div className="flex flex-col md:flex-row justify-between items-center">
              <div className="text-gray-600 text-sm mb-4 md:mb-0">
                © 2024 Bloop. All rights reserved.
              </div>
              <div className="flex gap-6 text-sm">
                <a
                  href="#"
                  className="text-gray-600 hover:text-gray-900 transition-colors"
                >
                  Privacy Policy
                </a>
                <a
                  href="#"
                  className="text-gray-600 hover:text-gray-900 transition-colors"
                >
                  Terms of Service
                </a>
                <a
                  href="#"
                  className="text-gray-600 hover:text-gray-900 transition-colors"
                >
                  Cookie Policy
                </a>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default PrototypePage;
