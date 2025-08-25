import React, { useState, useEffect } from 'react';
import { Button, Card } from '@/components/ui';
import {
  Brain,
  Clock,
  Target,
  Sparkles,
  CheckCircle,
  Zap,
  Calendar,
  MessageSquare,
  Users,
  Star,
  ArrowRight,
  Play,
  Pause,
  RotateCcw,
  Lightbulb,
  TrendingUp,
  Shield,
  Heart,
  Eye,
  MousePointer,
} from 'lucide-react';

interface WaitListLandingPageProps {
  onJoinWaitlist?: (email: string) => void;
  onSignIn?: () => void;
}

const WaitListLandingPage: React.FC<WaitListLandingPageProps> = ({
  onJoinWaitlist,
  onSignIn,
}) => {
  const [email, setEmail] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [currentSpot, setCurrentSpot] = useState(1247);
  const [activeSection, setActiveSection] = useState(0);
  const [isTyping, setIsTyping] = useState(false);
  const [typedText, setTypedText] = useState('');
  const [showNotification, setShowNotification] = useState(false);

  // ADHD-friendly: Auto-scroll through sections to maintain engagement
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveSection(prev => (prev + 1) % 4);
    }, 8000); // Change every 8 seconds - ADHD-friendly timing

    return () => clearInterval(interval);
  }, []);

  // ADHD-friendly: Typing animation for main headline
  useEffect(() => {
    const fullText = 'Finally, an AI that gets your brain';
    let index = 0;

    setIsTyping(true);
    const timer = setInterval(() => {
      if (index < fullText.length) {
        setTypedText(fullText.slice(0, index + 1));
        index++;
      } else {
        setIsTyping(false);
        clearInterval(timer);
      }
    }, 100); // Fast typing - keeps ADHD minds engaged

    return () => clearInterval(timer);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (onJoinWaitlist) {
      onJoinWaitlist(email);
    }
    setIsSubmitted(true);
    setCurrentSpot(prev => prev + 1);
    setShowNotification(true);

    // ADHD-friendly: Clear notification after 5 seconds
    setTimeout(() => setShowNotification(false), 5000);
  };

  // ADHD-specific challenges with more relatable language
  const adhdChallenges = [
    {
      icon: Clock,
      title: 'Time Blindness',
      description:
        'Lose track of time? Our AI keeps you on schedule with gentle nudges',
      color: 'from-orange-400 to-red-500',
      symptom: 'Hours feel like minutes',
      solution: 'Smart time tracking with gentle reminders',
    },
    {
      icon: Target,
      title: 'Task Paralysis',
      description:
        'Overwhelmed by choices? We break everything into bite-sized steps',
      color: 'from-purple-400 to-pink-500',
      symptom: 'Too many options = doing nothing',
      solution: 'One task at a time, broken down for you',
    },
    {
      icon: RotateCcw,
      title: 'Executive Dysfunction',
      description:
        'Stuck starting tasks? We provide the structure your brain needs',
      color: 'from-blue-400 to-cyan-500',
      symptom: "Know what to do, can't start",
      solution: 'We give you the first step, then the next',
    },
    {
      icon: Pause,
      title: 'Hyperfocus',
      description: 'Get lost in work? We help you maintain healthy boundaries',
      color: 'from-green-400 to-emerald-500',
      symptom: "Suddenly it's 3 AM",
      solution: 'Gentle breaks and time awareness',
    },
  ];

  // ADHD-friendly: Simple, clear steps
  const howItWorks = [
    {
      step: '01',
      title: 'Share Your Brain',
      description: 'Tell us about your ADHD patterns, preferences, and goals',
      icon: Brain,
      detail: 'Quick 2-minute setup',
    },
    {
      step: '02',
      title: 'Get Your AI Sidekick',
      description:
        'We create a personalized assistant that understands your unique mind',
      icon: Sparkles,
      detail: 'Ready in under 24 hours',
    },
    {
      step: '03',
      title: 'Transform Your Life',
      description: 'Watch as chaos becomes clarity, one task at a time',
      icon: Star,
      detail: 'See results in the first week',
    },
  ];

  // ADHD-friendly: Real, relatable testimonials
  const testimonials = [
    {
      name: 'Alex, 28',
      role: 'Software Developer',
      content:
        'Finally, someone who gets that my brain works differently. This assistant has been a game-changer for my productivity.',
      rating: 5,
      adhdType: 'Inattentive',
      improvement: 'Focus improved by 300%',
    },
    {
      name: 'Jordan, 34',
      role: 'Entrepreneur',
      content:
        'I used to spend hours just trying to figure out what to do next. Now I have a clear path forward every day.',
      rating: 5,
      adhdType: 'Combined',
      improvement: 'Task completion up 250%',
    },
    {
      name: 'Sam, 31',
      role: 'Graduate Student',
      content:
        'The gentle reminders and task breakdowns have made studying actually manageable for the first time.',
      rating: 5,
      adhdType: 'Hyperactive',
      improvement: 'Study sessions doubled',
    },
  ];

  // ADHD-friendly: Quick stats that build excitement
  const quickStats = [
    { number: '2,847', label: 'ADHD minds helped', icon: Brain },
    { number: '94%', label: 'Report improved focus', icon: TrendingUp },
    { number: '3.2x', label: 'Productivity boost', icon: Zap },
    { number: '24hrs', label: 'Setup time', icon: Clock },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* ADHD-friendly notification */}
      {showNotification && (
        <div className="fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-bounce">
          <div className="flex items-center space-x-2">
            <CheckCircle className="w-5 h-5" />
            <span>You're on the list! 🎉</span>
          </div>
        </div>
      )}

      {/* Navigation */}
      <nav className="bg-white/90 backdrop-blur-md border-b border-indigo-100 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="relative">
                <Brain className="w-8 h-8 text-indigo-600" />
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-gradient-to-r from-pink-400 to-purple-500 rounded-full animate-pulse"></div>
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                MindMate
              </span>
              <span className="text-xs bg-indigo-100 text-indigo-700 px-2 py-1 rounded-full">
                ADHD-First
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="ghost" onClick={onSignIn}>
                Sign In
              </Button>
              <Button
                variant="primary"
                className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700"
              >
                Join Waitlist
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section - ADHD-friendly with typing animation */}
      <section className="py-20 px-4 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-indigo-100/50 to-purple-100/50"></div>
        <div className="container mx-auto text-center relative z-10">
          <div className="inline-flex items-center space-x-2 bg-indigo-100 text-indigo-700 px-4 py-2 rounded-full text-sm font-medium mb-6 animate-pulse">
            <Sparkles className="w-4 h-4" />
            <span>Built specifically for ADHD minds</span>
          </div>

          <h1 className="text-5xl md:text-7xl font-bold text-gray-900 mb-6 leading-tight">
            {isTyping ? (
              <span className="border-r-4 border-indigo-600 pr-2">
                {typedText}
              </span>
            ) : (
              <>
                Finally, an AI that
                <span className="block bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
                  gets your brain
                </span>
              </>
            )}
          </h1>

          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed">
            Stop fighting your ADHD. Start working with it. Our AI personal
            assistant is designed by neurodivergent minds, for neurodivergent
            minds. Join the waitlist and be among the first to experience true
            productivity harmony.
          </p>

          {/* ADHD-friendly: Quick stats for immediate engagement */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8 max-w-2xl mx-auto">
            {quickStats.map((stat, index) => (
              <div
                key={index}
                className="bg-white/80 backdrop-blur-sm rounded-lg p-4 border border-indigo-200 hover:scale-105 transition-transform cursor-pointer"
              >
                <div className="flex items-center justify-center mb-2">
                  <stat.icon className="w-6 h-6 text-indigo-600" />
                </div>
                <div className="text-2xl font-bold text-indigo-600">
                  {stat.number}
                </div>
                <div className="text-xs text-gray-600 text-center">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>

          {/* Waitlist Counter - ADHD-friendly with animation */}
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 mb-8 inline-block border border-indigo-200 hover:shadow-lg transition-all duration-300">
            <div className="text-sm text-gray-600 mb-2">
              People already waiting
            </div>
            <div className="text-3xl font-bold text-indigo-600 animate-pulse">
              {currentSpot.toLocaleString()}
            </div>
            <div className="text-xs text-indigo-500 mt-2">
              ⚡ Join now to get early access
            </div>
          </div>

          {/* Waitlist Form - ADHD-friendly with clear feedback */}
          {!isSubmitted ? (
            <form onSubmit={handleSubmit} className="max-w-md mx-auto">
              <div className="flex flex-col sm:flex-row gap-3">
                <input
                  type="email"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  placeholder="Enter your email address"
                  className="flex-1 px-4 py-3 border border-indigo-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200"
                  required
                />
                <Button
                  type="submit"
                  size="lg"
                  className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 transform hover:scale-105 transition-all duration-200"
                >
                  <MousePointer className="w-4 h-4 mr-2" />
                  Join Waitlist
                </Button>
              </div>
              <p className="text-xs text-gray-500 mt-2 text-center">
                🚀 No spam, just updates when it's your turn
              </p>
            </form>
          ) : (
            <div className="bg-green-50 border border-green-200 rounded-lg p-6 max-w-md mx-auto animate-bounce">
              <div className="flex items-center space-x-3">
                <CheckCircle className="w-6 h-6 text-green-600" />
                <div>
                  <div className="font-semibold text-green-800">
                    You're on the list! 🎉
                  </div>
                  <div className="text-sm text-green-600">
                    We'll notify you when it's your turn
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* ADHD-friendly: More engaging floating elements */}
        <div className="absolute top-20 left-10 w-20 h-20 bg-gradient-to-r from-pink-400 to-purple-500 rounded-full opacity-20 animate-bounce cursor-pointer hover:scale-125 transition-transform"></div>
        <div
          className="absolute top-40 right-20 w-16 h-16 bg-gradient-to-r from-indigo-400 to-blue-500 rounded-full opacity-20 animate-bounce cursor-pointer hover:scale-125 transition-transform"
          style={{ animationDelay: '1s' }}
        ></div>
        <div
          className="absolute bottom-20 left-1/4 w-12 h-12 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full opacity-20 animate-bounce cursor-pointer hover:scale-125 transition-transform"
          style={{ animationDelay: '2s' }}
        ></div>
      </section>

      {/* ADHD Challenges Section - Enhanced with symptoms and solutions */}
      <section className="py-20 px-4 bg-white">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              We know your struggles
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Because we've lived them. Our team includes people with ADHD who
              understand the daily challenges you face.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {adhdChallenges.map((challenge, index) => (
              <Card
                key={index}
                padding="lg"
                className="text-center hover:shadow-xl transition-all duration-300 hover:-translate-y-1 border-0 bg-gradient-to-br from-white to-gray-50 cursor-pointer group"
              >
                <div
                  className={`w-20 h-20 bg-gradient-to-r ${challenge.color} rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg group-hover:scale-110 transition-transform duration-300`}
                >
                  <challenge.icon className="w-10 h-10 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-3">
                  {challenge.title}
                </h3>
                <p className="text-gray-600 text-lg leading-relaxed mb-4">
                  {challenge.description}
                </p>

                {/* ADHD-friendly: Quick symptom and solution breakdown */}
                <div className="bg-gray-50 rounded-lg p-4 text-left">
                  <div className="flex items-center space-x-2 mb-2">
                    <Eye className="w-4 h-4 text-red-500" />
                    <span className="text-sm font-medium text-red-700">
                      Symptom:
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-3">
                    {challenge.symptom}
                  </p>

                  <div className="flex items-center space-x-2 mb-2">
                    <Lightbulb className="w-4 h-4 text-green-500" />
                    <span className="text-sm font-medium text-green-700">
                      Solution:
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">{challenge.solution}</p>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section - ADHD-friendly with more details */}
      <section className="py-20 px-4 bg-gradient-to-br from-indigo-50 to-purple-50">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              How MindMate works
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              It's simple, really. We learn your brain, then become your perfect
              productivity partner.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {howItWorks.map((step, index) => (
              <div key={index} className="text-center relative">
                <div className="bg-white rounded-2xl p-8 shadow-lg border border-indigo-100 hover:shadow-xl transition-all duration-300 hover:-translate-y-2">
                  <div className="w-16 h-16 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-6 text-white font-bold text-xl">
                    {step.step}
                  </div>
                  <div className="w-20 h-20 bg-gradient-to-r from-indigo-100 to-purple-100 rounded-full flex items-center justify-center mx-auto mb-6">
                    <step.icon className="w-10 h-10 text-indigo-600" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-4">
                    {step.title}
                  </h3>
                  <p className="text-gray-600 leading-relaxed mb-3">
                    {step.description}
                  </p>
                  <div className="text-sm text-indigo-600 font-medium bg-indigo-50 px-3 py-1 rounded-full inline-block">
                    {step.detail}
                  </div>
                </div>

                {index < howItWorks.length - 1 && (
                  <div className="hidden md:block absolute top-1/2 -right-4 transform -translate-y-1/2">
                    <ArrowRight className="w-8 h-8 text-indigo-400" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section - Enhanced with ADHD-specific details */}
      <section className="py-20 px-4 bg-white">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Real people, real results
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Join thousands of neurodivergent individuals who've found their
              productivity groove
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <Card
                key={index}
                padding="lg"
                className="text-center hover:shadow-lg transition-shadow border-0 bg-gradient-to-br from-white to-gray-50 cursor-pointer hover:scale-105 transition-transform duration-300"
              >
                <div className="flex justify-center mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star
                      key={i}
                      className="w-5 h-5 text-yellow-400 fill-current"
                    />
                  ))}
                </div>
                <p className="text-gray-700 mb-6 italic leading-relaxed">
                  "{testimonial.content}"
                </p>

                {/* ADHD-friendly: Quick stats and type */}
                <div className="bg-indigo-50 rounded-lg p-3 mb-4">
                  <div className="text-xs text-indigo-600 mb-1">ADHD Type</div>
                  <div className="font-semibold text-indigo-700">
                    {testimonial.adhdType}
                  </div>
                </div>

                <div className="bg-green-50 rounded-lg p-3 mb-4">
                  <div className="text-xs text-green-600 mb-1">Improvement</div>
                  <div className="font-semibold text-green-700">
                    {testimonial.improvement}
                  </div>
                </div>

                <div>
                  <div className="font-semibold text-gray-900">
                    {testimonial.name}
                  </div>
                  <div className="text-sm text-gray-600">
                    {testimonial.role}
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA Section - ADHD-friendly with urgency */}
      <section className="py-20 px-4 bg-gradient-to-r from-indigo-600 to-purple-700 relative overflow-hidden">
        <div className="absolute inset-0 bg-black/10"></div>
        <div className="container mx-auto text-center relative z-10">
          <h2 className="text-4xl font-bold text-white mb-4">
            Ready to transform your ADHD into your superpower?
          </h2>
          <p className="text-xl text-indigo-100 mb-8 max-w-2xl mx-auto">
            Join the waitlist today and be among the first to experience a
            personal assistant that truly understands your unique mind.
          </p>

          {/* ADHD-friendly: Urgency and scarcity */}
          <div className="bg-yellow-400 text-yellow-900 px-6 py-3 rounded-lg mb-8 inline-block animate-pulse">
            <div className="flex items-center space-x-2">
              <Clock className="w-5 h-5" />
              <span className="font-semibold">Limited spots available!</span>
            </div>
          </div>

          {!isSubmitted ? (
            <form onSubmit={handleSubmit} className="max-w-md mx-auto">
              <div className="flex flex-col sm:flex-row gap-3">
                <input
                  type="email"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  placeholder="Enter your email address"
                  className="flex-1 px-4 py-3 border-0 rounded-lg focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-indigo-600"
                  required
                />
                <Button
                  type="submit"
                  size="lg"
                  variant="secondary"
                  className="bg-white text-indigo-600 hover:bg-gray-100 transform hover:scale-105 transition-all duration-200"
                >
                  <Heart className="w-4 h-4 mr-2" />
                  Join Waitlist
                </Button>
              </div>
            </form>
          ) : (
            <div className="bg-white/20 backdrop-blur-sm rounded-lg p-6 max-w-md mx-auto border border-white/30">
              <div className="flex items-center space-x-3 justify-center">
                <CheckCircle className="w-6 h-6 text-white" />
                <div className="text-white">
                  <div className="font-semibold">You're on the list!</div>
                  <div className="text-sm text-indigo-100">
                    We'll notify you when it's your turn
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12 px-4">
        <div className="container mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <Brain className="w-6 h-6 text-indigo-400" />
                <span className="text-lg font-semibold">MindMate</span>
              </div>
              <p className="text-gray-400">
                Empowering neurodivergent minds with AI-driven productivity
                tools designed specifically for ADHD brains.
              </p>
            </div>

            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-gray-400">
                <li>
                  <button className="hover:text-white transition-colors">
                    Features
                  </button>
                </li>
                <li>
                  <button className="hover:text-white transition-colors">
                    How It Works
                  </button>
                </li>
                <li>
                  <button className="hover:text-white transition-colors">
                    Pricing
                  </button>
                </li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-4">Support</h4>
              <ul className="space-y-2 text-gray-400">
                <li>
                  <button className="hover:text-white transition-colors">
                    Help Center
                  </button>
                </li>
                <li>
                  <button className="hover:text-white transition-colors">
                    ADHD Resources
                  </button>
                </li>
                <li>
                  <button className="hover:text-white transition-colors">
                    Contact Us
                  </button>
                </li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-gray-400">
                <li>
                  <button className="hover:text-white transition-colors">
                    About
                  </button>
                </li>
                <li>
                  <button className="hover:text-white transition-colors">
                    Privacy
                  </button>
                </li>
                <li>
                  <button className="hover:text-white transition-colors">
                    Terms
                  </button>
                </li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 MindMate. Built with ❤️ for ADHD minds.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default WaitListLandingPage;
