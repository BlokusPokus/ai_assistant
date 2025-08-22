import React from 'react';
import { Button, Card } from '@/components/ui';
import {
  Brain,
  Shield,
  Zap,
  Users,
  MessageSquare,
  Calendar,
} from 'lucide-react';

interface LandingPageProps {
  onGetStarted?: () => void;
  onSignIn?: () => void;
}

const LandingPage: React.FC<LandingPageProps> = ({
  onGetStarted,
  onSignIn,
}) => {
  const features = [
    {
      icon: Brain,
      title: 'AI-Powered Assistance',
      description:
        'Intelligent conversation and task management powered by advanced language models',
    },
    {
      icon: Shield,
      title: 'Secure & Private',
      description:
        'Enterprise-grade security with end-to-end encryption and MFA protection',
    },
    {
      icon: Zap,
      title: 'Lightning Fast',
      description:
        'Optimized performance with sub-second response times and real-time updates',
    },
    {
      icon: Users,
      title: 'Multi-User Support',
      description:
        'Scalable architecture supporting individual users and enterprise teams',
    },
    {
      icon: MessageSquare,
      title: 'SMS Integration',
      description:
        'Access your assistant anywhere via SMS with Twilio integration',
    },
    {
      icon: Calendar,
      title: 'Smart Planning',
      description:
        'Intelligent scheduling and reminder systems for better productivity',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Brain className="w-8 h-8 text-blue-600" />
              <span className="text-xl font-bold text-gray-900">
                Personal Assistant TDAH
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="ghost" onClick={onSignIn}>
                Sign In
              </Button>
              <Button variant="primary" onClick={onGetStarted}>
                Get Started
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            Your Personal AI
            <span className="text-blue-600 block">Assistant</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Experience the future of personal productivity with our AI-powered
            assistant. Get help with tasks, planning, and organization through
            natural conversation.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" variant="primary" onClick={onGetStarted}>
              Start Free Trial
            </Button>
            <Button size="lg" variant="outline" onClick={onSignIn}>
              Sign In
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 bg-white">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Powerful Features for Modern Life
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Everything you need to stay organized, productive, and focused in
              today's busy world
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <Card
                key={index}
                padding="lg"
                className="text-center hover:shadow-lg transition-shadow"
              >
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <feature.icon className="w-8 h-8 text-blue-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600">{feature.description}</p>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-blue-600">
        <div className="container mx-auto text-center">
          <h2 className="text-4xl font-bold text-white mb-4">
            Ready to Get Started?
          </h2>
          <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
            Join thousands of users who have transformed their productivity with
            our AI assistant
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" variant="secondary" onClick={onGetStarted}>
              Create Free Account
            </Button>
            <Button size="lg" variant="outline" onClick={onSignIn}>
              Sign In to Existing Account
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12 px-4">
        <div className="container mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <Brain className="w-6 h-6 text-blue-400" />
                <span className="text-lg font-semibold">
                  Personal Assistant TDAH
                </span>
              </div>
              <p className="text-gray-400">
                Empowering individuals with AI-driven productivity tools for a
                better, more organized life.
              </p>
            </div>

            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-gray-400">
                <li>
                  <button className="hover:text-white">Features</button>
                </li>
                <li>
                  <button className="hover:text-white">Pricing</button>
                </li>
                <li>
                  <button className="hover:text-white">API</button>
                </li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-4">Support</h4>
              <ul className="space-y-2 text-gray-400">
                <li>
                  <button className="hover:text-white">Documentation</button>
                </li>
                <li>
                  <button className="hover:text-white">Help Center</button>
                </li>
                <li>
                  <button className="hover:text-white">Contact Us</button>
                </li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-gray-400">
                <li>
                  <button className="hover:text-white">About</button>
                </li>
                <li>
                  <button className="hover:text-white">Privacy</button>
                </li>
                <li>
                  <button className="hover:text-white">Terms</button>
                </li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 Personal Assistant TDAH. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
