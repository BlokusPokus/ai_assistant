import React, { useState } from 'react';
import { Button, Card, Input } from '@/components/ui';

const WaitListLandingPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;

    try {
      // TODO: Implement actual waitlist submission
      console.log('Submitting email:', email);
      setIsSubmitted(true);
      setEmail('');
    } catch (error) {
      console.error('Failed to submit:', error);
    }
  };

  const quickStats = [
    { number: '2,500+', label: 'Waitlist Members' },
    { number: '15+', label: 'Beta Testers' },
    { number: '98%', label: 'Satisfaction Rate' },
  ];

  const urgencyStats = [
    { number: '47', label: 'Spots Left' },
    { number: 'Q1 2025', label: 'Launch Date' },
    { number: 'Free', label: 'Beta Access' },
  ];

  const adhdStruggles = [
    {
      icon: '😰',
      title: 'Overwhelmed by Life',
      description:
        'Too many things to remember, too many deadlines to track, too many apps to manage.',
      impact: 'Causes daily stress and anxiety',
    },
    {
      icon: '😤',
      title: 'Fighting Your Tools',
      description:
        'Productivity apps that make you feel stupid for forgetting things or getting distracted.',
      impact: 'Creates negative self-talk',
    },
    {
      icon: '😵',
      title: 'Information Overload',
      description:
        'Important emails get buried, crucial tasks get forgotten, and nothing feels organized.',
      impact: 'Leads to decision paralysis',
    },
    {
      icon: '😔',
      title: 'Feeling Like a Failure',
      description:
        "When you can't keep up with neurotypical productivity standards, it's easy to feel inadequate.",
      impact: 'Damages self-confidence',
    },
  ];

  const bloopSolutions = [
    {
      icon: '🎯',
      title: 'One Place for Everything',
      description:
        'All your tasks, emails, and reminders in one intelligent interface that adapts to you.',
      benefit: 'No more app switching',
    },
    {
      icon: '🧠',
      title: 'AI That Gets You',
      description:
        'Our AI understands ADHD thinking patterns and works with your brain, not against it.',
      benefit: 'Finally feel understood',
    },
    {
      icon: '⚡',
      title: 'Smart Automation',
      description:
        'Let AI handle the boring stuff while you focus on what you do best.',
      benefit: 'Save 3+ hours daily',
    },
    {
      icon: '🎨',
      title: 'Your Way, Always',
      description:
        'Customize everything to match your unique preferences and workflow.',
      benefit: 'Create your perfect system',
    },
  ];

  const exclusiveBenefits = [
    {
      icon: '🏆',
      title: 'Lifetime Discount',
      description:
        '50% off forever for early adopters who believe in our mission.',
      value: 'Save $300+ annually',
    },
    {
      icon: '🚀',
      title: 'Early Access',
      description:
        'Be among the first to experience the future of ADHD-friendly productivity.',
      value: 'Exclusive beta features',
    },
    {
      icon: '💬',
      title: 'Direct Input',
      description:
        "Help shape Bloop's features and make it perfect for your needs.",
      value: 'Influence product roadmap',
    },
    {
      icon: '🎁',
      title: 'Bonus Features',
      description:
        "Access to premium features that won't be available to regular users.",
      value: '$200+ value',
    },
  ];

  const testimonials = [
    {
      quote:
        "I've been on the waitlist for 3 months and the updates alone have given me hope. Finally, someone who understands that my brain works differently!",
      author: 'Alex Thompson',
      role: 'ADHD Coach',
      waitlistTime: '3 months',
    },
    {
      quote:
        'The beta access I got from the waitlist changed everything. I went from chaos to calm in just 2 weeks. Worth every day of waiting!',
      author: 'Maria Santos',
      role: 'Graphic Designer',
      waitlistTime: '6 months',
    },
    {
      quote:
        'Being on the waitlist made me feel part of something special. When I finally got access, it was like Christmas morning for my productivity!',
      author: 'David Chen',
      role: 'Startup Founder',
      waitlistTime: '4 months',
    },
  ];

  const faqs = [
    {
      question: 'How long is the waitlist?',
      answer:
        "Currently about 2-3 months, but we're onboarding new users every week. The sooner you join, the sooner you get access!",
    },
    {
      question: "What if I don't like it?",
      answer:
        'No worries! You can cancel anytime during your free trial. We want you to love Bloop, not feel stuck with it.',
    },
    {
      question: 'Is it really free?',
      answer:
        "Yes! Beta access is completely free, and you'll get 14 days of full access when you're invited. No hidden fees.",
    },
    {
      question: 'What makes Bloop different?',
      answer:
        "We're the only AI productivity tool built specifically for ADHD minds. Every feature is designed with neurodivergent thinking in mind.",
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
            <a
              href="/"
              className="text-primary hover:text-accent transition-colors font-medium"
            >
              Home
            </a>
            <a
              href="/login"
              className="text-primary hover:text-accent transition-colors font-medium"
            >
              Sign In
            </a>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="container mx-auto px-6 py-20 text-center">
        <div className="max-w-4xl mx-auto">
          {/* Urgency Badge */}
          <div className="inline-flex items-center space-x-2 bg-red-100 text-red-800 px-4 py-2 rounded-full text-sm font-medium mb-6 animate-pulse">
            <span>🔥</span>
            <span>Only 47 spots left for early access!</span>
          </div>

          <h1 className="text-5xl font-bold text-primary mb-6 font-nunito leading-tight">
            Join the{' '}
            <span className="text-transparent bg-gradient-to-r from-accent to-blue-400 bg-clip-text">
              ADHD Productivity Revolution
            </span>
          </h1>
          <p className="text-xl text-gray-700 mb-8 leading-relaxed font-nunito max-w-2xl mx-auto">
            Be among the first 100 people to experience Bloop. Get exclusive
            early access, lifetime discounts, and help shape the future of
            ADHD-friendly productivity.
          </p>

          {/* Quick Stats */}
          <div className="grid grid-cols-3 gap-6 mb-12 max-w-2xl mx-auto">
            {quickStats.map((stat, index) => (
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

          {/* Urgency Stats */}
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-8 max-w-2xl mx-auto">
            <h3 className="text-lg font-semibold text-red-800 mb-4 font-nunito">
              ⏰ Limited Time Opportunity
            </h3>
            <div className="grid grid-cols-3 gap-4">
              {urgencyStats.map((stat, index) => (
                <div key={index} className="text-center">
                  <div className="text-2xl font-bold text-red-600 mb-1 font-nunito">
                    {stat.number}
                  </div>
                  <div className="text-sm text-red-700 font-nunito">
                    {stat.label}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Waitlist Form */}
          {!isSubmitted ? (
            <Card className="max-w-md mx-auto p-8 glass-effect">
              <h3 className="text-2xl font-bold text-primary mb-4 font-nunito">
                Join the Waitlist
              </h3>
              <p className="text-gray-600 mb-6 font-nunito">
                Get notified when it's your turn and receive exclusive early
                access benefits.
              </p>
              <form onSubmit={handleSubmit} className="space-y-4">
                <Input
                  type="email"
                  placeholder="Enter your email address"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  required
                  className="w-full"
                />
                <Button type="submit" variant="primary" className="w-full">
                  Join Waitlist
                </Button>
              </form>
              <p className="text-xs text-gray-500 mt-3 text-center font-nunito">
                🚀 No spam • Unsubscribe anytime • Join 2,500+ others
              </p>
            </Card>
          ) : (
            <Card className="max-w-md mx-auto p-8 glass-effect">
              <div className="text-center">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">✅</span>
                </div>
                <h3 className="text-2xl font-bold text-primary mb-2 font-nunito">
                  You're on the list!
                </h3>
                <p className="text-gray-600 font-nunito">
                  We'll notify you as soon as it's your turn. Thanks for joining
                  the revolution!
                </p>
              </div>
            </Card>
          )}
        </div>
      </section>

      {/* ADHD Struggles Section */}
      <section className="container mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-primary mb-4 font-nunito">
            We Know Your Struggles
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto font-nunito">
            Because we've lived them too. Traditional productivity tools weren't
            built for ADHD minds.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {adhdStruggles.map((struggle, index) => (
            <Card key={index} className="p-6 glass-effect">
              <div className="flex items-start space-x-4">
                <div className="text-3xl">{struggle.icon}</div>
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-primary mb-2 font-nunito">
                    {struggle.title}
                  </h3>
                  <p className="text-gray-600 mb-3 font-nunito text-sm leading-relaxed">
                    {struggle.description}
                  </p>
                  <div className="text-red-600 font-semibold text-sm font-nunito">
                    {struggle.impact}
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </section>

      {/* Bloop Solutions Section */}
      <section className="container mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-primary mb-4 font-nunito">
            Bloop Changes Everything
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto font-nunito">
            Finally, a productivity tool that works WITH your ADHD, not against
            it.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {bloopSolutions.map((solution, index) => (
            <Card key={index} className="p-6 glass-effect">
              <div className="flex items-start space-x-4">
                <div className="text-3xl">{solution.icon}</div>
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-primary mb-2 font-nunito">
                    {solution.title}
                  </h3>
                  <p className="text-gray-600 mb-3 font-nunito text-sm leading-relaxed">
                    {solution.description}
                  </p>
                  <div className="text-green-600 font-semibold text-sm font-nunito">
                    {solution.benefit}
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </section>

      {/* Exclusive Benefits Section */}
      <section className="container mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-primary mb-4 font-nunito">
            Exclusive Waitlist Benefits
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto font-nunito">
            Join now and get perks that won't be available to regular users.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {exclusiveBenefits.map((benefit, index) => (
            <Card key={index} className="text-center p-6 glass-effect">
              <div className="text-3xl mb-4">{benefit.icon}</div>
              <h3 className="text-lg font-bold text-primary mb-3 font-nunito">
                {benefit.title}
              </h3>
              <p className="text-gray-600 mb-4 font-nunito text-sm leading-relaxed">
                {benefit.description}
              </p>
              <div className="inline-block bg-accent/10 text-accent px-3 py-1 rounded-full text-sm font-semibold font-nunito">
                {benefit.value}
              </div>
            </Card>
          ))}
        </div>
      </section>

      {/* Testimonials */}
      <section className="container mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-primary mb-4 font-nunito">
            What Waitlist Members Say
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto font-nunito">
            Hear from people who are already experiencing the Bloop difference.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {testimonials.map((testimonial, index) => (
            <Card key={index} className="p-6 glass-effect">
              <div className="mb-4">
                <p className="text-gray-700 italic font-nunito text-sm leading-relaxed">
                  "{testimonial.quote}"
                </p>
              </div>
              <div className="mb-3">
                <div className="font-semibold text-primary font-nunito">
                  {testimonial.author}
                </div>
                <div className="text-gray-600 font-nunito text-sm">
                  {testimonial.role}
                </div>
              </div>
              <div className="inline-block bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-semibold font-nunito">
                Waitlist: {testimonial.waitlistTime}
              </div>
            </Card>
          ))}
        </div>
      </section>

      {/* FAQ Section */}
      <section className="container mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-primary mb-4 font-nunito">
            Frequently Asked Questions
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto font-nunito">
            Everything you need to know about joining the Bloop waitlist.
          </p>
        </div>

        <div className="max-w-3xl mx-auto space-y-6">
          {faqs.map((faq, index) => (
            <Card key={index} className="p-6 glass-effect">
              <h3 className="text-lg font-bold text-primary mb-3 font-nunito">
                {faq.question}
              </h3>
              <p className="text-gray-600 font-nunito leading-relaxed">
                {faq.answer}
              </p>
            </Card>
          ))}
        </div>
      </section>

      {/* Final CTA */}
      <section className="container mx-auto px-6 py-20">
        <Card className="text-center p-12 glass-effect max-w-4xl mx-auto">
          <h2 className="text-4xl font-bold text-primary mb-6 font-nunito">
            Don't Wait to Transform Your Productivity
          </h2>
          <p className="text-lg text-gray-600 mb-8 font-nunito max-w-2xl mx-auto">
            Every day you wait is another day of fighting against tools that
            don't understand you. Join the waitlist today and be among the first
            to experience true productivity harmony.
          </p>

          {/* Urgency and Social Proof */}
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-8 max-w-md mx-auto">
            <p className="text-red-800 font-semibold font-nunito mb-2">
              ⏰ Limited Time: Only 47 spots remaining!
            </p>
            <p className="text-red-700 text-sm font-nunito">
              Join now to secure your exclusive benefits and early access.
            </p>
          </div>

          <Button
            variant="primary"
            size="lg"
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
            className="mb-4"
          >
            Join Waitlist Now
          </Button>

          <p className="text-sm text-gray-500 font-nunito">
            🚀 Free to join • No credit card required • Unsubscribe anytime
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

export default WaitListLandingPage;
