import React from 'react';
import { Link } from 'react-router-dom';
import { Button, Card } from '@/components/ui';

const LandingPage: React.FC = () => {
  const socialProof = [
    { number: '15,000+', label: 'Active Users' },
    { number: '98%', label: 'Satisfaction Rate' },
    { number: '3.2x', label: 'Productivity Boost' },
  ];

  const adhdChallenges = [
    {
      icon: '⏰',
      title: 'Time Blindness',
      description:
        'Lose track of time? Bloop keeps you on schedule with gentle, non-judgmental reminders.',
      stat: 'Save 2+ hours daily',
    },
    {
      icon: '🧠',
      title: 'Task Paralysis',
      description:
        'Overwhelmed by to-do lists? We break everything into ADHD-friendly micro-tasks.',
      stat: '3x more tasks completed',
    },
    {
      icon: '📱',
      title: 'Digital Distractions',
      description:
        'Constantly switching apps? Our focus mode keeps you locked in on what matters.',
      stat: '60% fewer distractions',
    },
    {
      icon: '💭',
      title: 'Memory Issues',
      description:
        "Forget important things? Bloop remembers everything so you don't have to.",
      stat: 'Never miss deadlines again',
    },
  ];

  const successStories = [
    {
      quote:
        'Bloop literally changed my life. I went from missing every deadline to being the most organized person in my team. My ADHD finally feels like a superpower!',
      author: 'Emma Chen',
      role: 'Marketing Director',
      improvement: 'Productivity increased by 400%',
    },
    {
      quote:
        "I've tried every productivity app out there. Nothing worked until Bloop. It's like it was built specifically for how my brain works.",
      author: 'Marcus Rodriguez',
      role: 'Software Engineer',
      improvement: 'Tasks completed: 5 → 25 per day',
    },
    {
      quote:
        'As someone with ADHD, I always felt like I was fighting against my tools. Bloop works WITH my brain, not against it. Game changer!',
      author: 'Sarah Kim',
      role: 'Entrepreneur',
      improvement: 'Business revenue up 200%',
    },
  ];

  const features = [
    {
      icon: '🎯',
      title: 'Smart Task Breakdown',
      description:
        'AI breaks overwhelming projects into bite-sized, achievable steps that match your attention span.',
      benefit: 'Reduce overwhelm by 80%',
    },
    {
      icon: '🔔',
      title: 'Gentle Reminders',
      description:
        'Non-intrusive notifications that respect your focus time and help you stay on track.',
      benefit: 'Never miss important tasks',
    },
    {
      icon: '📊',
      title: 'Progress Visualization',
      description:
        'See your progress in real-time with satisfying visual feedback that keeps you motivated.',
      benefit: 'Stay motivated longer',
    },
    {
      icon: '🔄',
      title: 'Adaptive Scheduling',
      description:
        "AI learns your energy patterns and schedules tasks when you're most likely to complete them.",
      benefit: 'Work with your natural rhythm',
    },
    {
      icon: '🎨',
      title: 'Customizable Interface',
      description:
        'Personalize everything from colors to layout to match your unique preferences and needs.',
      benefit: 'Create your perfect workspace',
    },
    {
      icon: '🚀',
      title: 'Focus Mode',
      description:
        'One-click distraction blocking that helps you maintain deep focus when you need it most.',
      benefit: 'Achieve flow state faster',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-blue-50 to-blue-100">
      {/* Navigation */}
      <nav className="container mx-auto px-6 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <img src="/orca3d.png" alt="Bloop Logo" className="w-10 h-10" />
            <span className="text-2xl font-bold text-primary font-nunito">
              Bloop
            </span>
          </div>
          <div className="flex items-center space-x-4">
            <Link
              to="/prototype"
              className="text-primary hover:text-accent transition-colors font-medium"
            >
              Prototype
            </Link>
            <Link
              to="/login"
              className="text-primary hover:text-accent transition-colors font-medium"
            >
              Sign In
            </Link>
            <Link to="/register">
              <Button variant="primary" size="sm">
                Get Started
              </Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="container mx-auto px-6 py-20 text-center">
        <div className="max-w-4xl mx-auto">
          {/* Social Proof Badge */}
          <div className="inline-flex items-center space-x-2 bg-green-100 text-green-800 px-4 py-2 rounded-full text-sm font-medium mb-6 animate-pulse">
            <span>⭐</span>
            <span>Trusted by 15,000+ ADHD users worldwide</span>
          </div>

          <h1 className="text-5xl font-bold text-primary mb-6 font-nunito leading-tight">
            Finally, an AI that{' '}
            <span className="text-transparent bg-gradient-to-r from-accent to-blue-400 bg-clip-text">
              gets your ADHD brain
            </span>
          </h1>
          <p className="text-xl text-gray-700 mb-8 leading-relaxed font-nunito max-w-2xl mx-auto">
            Stop fighting your ADHD. Start working with it. Bloop is the only AI
            assistant designed by neurodivergent minds, for neurodivergent
            minds.
          </p>

          {/* Social Proof Stats */}
          <div className="grid grid-cols-3 gap-6 mb-12 max-w-2xl mx-auto">
            {socialProof.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl font-bold text-accent mb-2 font-nunito">
                  {stat.number}
                </div>
                <div className="text-sm text-gray-600 font-nunito">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/register">
              <Button variant="primary" size="lg">
                Start Your Free Trial
              </Button>
            </Link>
            <Link to="/waitlist">
              <Button variant="secondary" size="lg">
                Join Waitlist
              </Button>
            </Link>
          </div>

          {/* Trust Indicators */}
          <p className="text-sm text-gray-500 mt-4 font-nunito">
            🚀 No credit card required • 14-day free trial • Cancel anytime
          </p>
        </div>
      </section>

      {/* ADHD Challenges Section */}
      <section className="container mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-primary mb-4 font-nunito">
            We Get It. We've Been There.
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto font-nunito">
            Traditional productivity tools weren't built for neurodivergent
            brains. We're changing that, one ADHD mind at a time.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {adhdChallenges.map((challenge, index) => (
            <Card key={index} className="text-center p-6 glass-effect">
              <div className="text-4xl mb-4">{challenge.icon}</div>
              <h3 className="text-xl font-bold text-primary mb-3 font-nunito">
                {challenge.title}
              </h3>
              <p className="text-gray-600 mb-4 font-nunito text-sm">
                {challenge.description}
              </p>
              <div className="text-accent font-semibold text-sm font-nunito">
                {challenge.stat}
              </div>
            </Card>
          ))}
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-primary mb-4 font-nunito">
            Built Specifically for ADHD Minds
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto font-nunito">
            Every feature is designed with neurodivergent thinking patterns in
            mind. No more fighting against your tools.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <Card key={index} className="p-6 glass-effect">
              <div className="text-3xl mb-4">{feature.icon}</div>
              <h3 className="text-xl font-bold text-primary mb-3 font-nunito">
                {feature.title}
              </h3>
              <p className="text-gray-600 mb-4 font-nunito text-sm leading-relaxed">
                {feature.description}
              </p>
              <div className="inline-block bg-accent/10 text-accent px-3 py-1 rounded-full text-sm font-semibold font-nunito">
                {feature.benefit}
              </div>
            </Card>
          ))}
        </div>
      </section>

      {/* Success Stories */}
      <section className="container mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-primary mb-4 font-nunito">
            Real Results from Real ADHD Users
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto font-nunito">
            Don't just take our word for it. Here's what our community is
            saying.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {successStories.map((story, index) => (
            <Card key={index} className="p-6 glass-effect">
              <div className="mb-4">
                <p className="text-gray-700 italic font-nunito text-sm leading-relaxed">
                  "{story.quote}"
                </p>
              </div>
              <div className="mb-3">
                <div className="font-semibold text-primary font-nunito">
                  {story.author}
                </div>
                <div className="text-gray-600 font-nunito text-sm">
                  {story.role}
                </div>
              </div>
              <div className="inline-block bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-semibold font-nunito">
                {story.improvement}
              </div>
            </Card>
          ))}
        </div>
      </section>

      {/* How It Works Section */}
      <section className="container mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-primary mb-4 font-nunito">
            Get Started in 3 Simple Steps
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto font-nunito">
            No complicated setup. No overwhelming options. Just simple steps to
            transform your productivity.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="w-20 h-20 bg-gradient-to-br from-accent to-blue-400 rounded-full flex items-center justify-center mx-auto mb-6 text-white text-2xl font-bold">
              1
            </div>
            <h3 className="text-xl font-bold text-primary mb-3 font-nunito">
              Connect Your Tools
            </h3>
            <p className="text-gray-600 font-nunito">
              Link your calendar, email, and favorite apps. Takes less than 2
              minutes.
            </p>
          </div>

          <div className="text-center">
            <div className="w-20 h-20 bg-gradient-to-br from-accent to-blue-400 rounded-full flex items-center justify-center mx-auto mb-6 text-white text-2xl font-bold">
              2
            </div>
            <h3 className="text-xl font-bold text-primary mb-3 font-nunito">
              AI Learns Your Style
            </h3>
            <p className="text-gray-600 font-nunito">
              Our AI adapts to your unique workflow in just a few days.
            </p>
          </div>

          <div className="text-center">
            <div className="w-20 h-20 bg-gradient-to-br from-accent to-blue-400 rounded-full flex items-center justify-center mx-auto mb-6 text-white text-2xl font-bold">
              3
            </div>
            <h3 className="text-xl font-bold text-primary mb-3 font-nunito">
              Stay Focused & Productive
            </h3>
            <p className="text-gray-600 font-nunito">
              Enjoy distraction-free productivity with intelligent reminders and
              task management.
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-6 py-20">
        <Card className="text-center p-12 glass-effect max-w-4xl mx-auto">
          <h2 className="text-4xl font-bold text-primary mb-6 font-nunito">
            Ready to Transform Your ADHD into a Superpower?
          </h2>
          <p className="text-lg text-gray-600 mb-8 font-nunito max-w-2xl mx-auto">
            Join 15,000+ users who have already discovered what it feels like to
            work WITH their brain, not against it.
          </p>

          {/* Urgency and Social Proof */}
          <div className="bg-accent/10 rounded-lg p-4 mb-8 max-w-md mx-auto">
            <p className="text-accent font-semibold font-nunito">
              🎉 Limited Time: First 100 new users get 50% off for life!
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/register">
              <Button variant="primary" size="lg">
                Start Free Trial Now
              </Button>
            </Link>
            <Link to="/waitlist">
              <Button variant="ghost" size="lg">
                Learn More
              </Button>
            </Link>
          </div>

          <p className="text-sm text-gray-500 mt-4 font-nunito">
            ⚡ 14-day free trial • No credit card required • Cancel anytime
          </p>
        </Card>
      </section>

      {/* Footer */}
      <footer className="container mx-auto px-6 py-12 border-t border-gray-200">
        <div className="flex flex-col md:flex-row items-center justify-between">
          <div className="flex items-center space-x-3 mb-4 md:mb-0">
            <img src="/orca3d.png" alt="Bloop Logo" className="w-8 h-8" />
            <span className="text-xl font-bold text-primary font-nunito">
              Bloop
            </span>
          </div>
          <div className="text-gray-600 text-sm font-nunito">
            © 2024 Bloop. Empowering ADHD minds worldwide.
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
