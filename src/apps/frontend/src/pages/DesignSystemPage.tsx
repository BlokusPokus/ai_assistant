import React from 'react';
import { ResponsiveContainer } from '../components/ui';
import {
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Input,
} from '../components/ui';
import { useIsMobile } from '../hooks/useAnimation';

const DesignSystemPage: React.FC = () => {
  const isMobile = useIsMobile();

  return (
    <div className="min-h-screen py-8">
      <ResponsiveContainer>
        {/* Header */}
        <div className="text-center mb-12 animate-fade-in">
          <h1 className="text-5xl font-bold text-primary mb-4">
            Design System Showcase
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Explore our new UI components with frosted glass aesthetics, modern
            typography, and enhanced user experience.
          </p>
        </div>

        {/* Color Palette */}
        <Card className="mb-8 animate-slide-in-left">
          <CardHeader>
            <CardTitle>Color Palette</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="w-16 h-16 bg-primary rounded-lg mx-auto mb-2 shadow-md"></div>
                <p className="text-sm font-medium">Primary</p>
                <p className="text-xs text-gray-500">#000000</p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-secondary rounded-lg mx-auto mb-2 shadow-md border border-gray-200"></div>
                <p className="text-sm font-medium">Secondary</p>
                <p className="text-xs text-gray-500">#FFFFFF</p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-r from-accent to-accent-light rounded-lg mx-auto mb-2 shadow-md"></div>
                <p className="text-sm font-medium">Accent</p>
                <p className="text-xs text-gray-500">#3B82F6 → #60A5FA</p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-soft-highlight rounded-lg mx-auto mb-2 shadow-md"></div>
                <p className="text-sm font-medium">Soft Highlight</p>
                <p className="text-xs text-gray-500">#E0F2FE</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Typography */}
        <Card className="mb-8 animate-slide-in-right">
          <CardHeader>
            <CardTitle>Typography Scale</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h1 className="text-5xl font-bold text-primary">
                Heading 1 (5xl)
              </h1>
              <p className="text-sm text-gray-500">48px / 3rem</p>
            </div>
            <div>
              <h2 className="text-4xl font-bold text-primary">
                Heading 2 (4xl)
              </h2>
              <p className="text-sm text-gray-500">36px / 2.25rem</p>
            </div>
            <div>
              <h3 className="text-3xl font-semibold text-primary">
                Heading 3 (3xl)
              </h3>
              <p className="text-sm text-gray-500">30px / 1.875rem</p>
            </div>
            <div>
              <h4 className="text-2xl font-semibold text-primary">
                Heading 4 (2xl)
              </h4>
              <p className="text-sm text-gray-500">24px / 1.5rem</p>
            </div>
            <div>
              <p className="text-lg text-gray-700">Body Large (lg)</p>
              <p className="text-sm text-gray-500">18px / 1.125rem</p>
            </div>
            <div>
              <p className="text-base text-gray-700">Body Base (base)</p>
              <p className="text-sm text-gray-500">16px / 1rem</p>
            </div>
          </CardContent>
        </Card>

        {/* Button System */}
        <Card className="mb-8 animate-scale-in">
          <CardHeader>
            <CardTitle>Button System</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {/* Button Variants */}
              <div>
                <h4 className="text-lg font-semibold mb-3">Button Variants</h4>
                <div className="flex flex-wrap gap-3">
                  <Button>Primary</Button>
                  <Button variant="secondary">Secondary</Button>
                  <Button variant="ghost">Ghost</Button>
                  <Button variant="danger">Danger</Button>
                </div>
              </div>

              {/* Button Sizes */}
              <div>
                <h4 className="text-lg font-semibold mb-3">Button Sizes</h4>
                <div className="flex flex-wrap items-center gap-3">
                  <Button size="sm">Small</Button>
                  <Button size="md">Medium</Button>
                  <Button size="lg">Large</Button>
                  <Button size="xl">Extra Large</Button>
                </div>
              </div>

              {/* Button States */}
              <div>
                <h4 className="text-lg font-semibold mb-3">Button States</h4>
                <div className="flex flex-wrap gap-3">
                  <Button loading>Loading</Button>
                  <Button disabled>Disabled</Button>
                  <Button leftIcon={<span>🚀</span>}>With Icon</Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Form Components */}
        <Card className="mb-8 animate-fade-in">
          <CardHeader>
            <CardTitle>Form Components</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <Input label="Basic Input" placeholder="Enter your text here" />
                <Input
                  label="Input with Left Icon"
                  placeholder="Search..."
                  leftIcon={<span>🔍</span>}
                />
                <Input
                  label="Input with Error"
                  placeholder="This input has an error"
                  error="This field is required"
                />
              </div>
              <div className="space-y-4">
                <Input
                  label="Email Input"
                  type="email"
                  placeholder="Enter your email"
                  leftIcon={<span>📧</span>}
                />
                <Input
                  label="Password Input"
                  type="password"
                  placeholder="Enter your password"
                  leftIcon={<span>🔒</span>}
                />
                <Input
                  label="Disabled Input"
                  placeholder="This input is disabled"
                  disabled
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Responsive Design */}
        <Card className="mb-8 animate-slide-in-left">
          <CardHeader>
            <CardTitle>Responsive Design</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center">
              <p className="text-lg mb-4">
                Current breakpoint:{' '}
                <span className="font-semibold text-accent">
                  {isMobile ? 'Mobile' : 'Desktop'}
                </span>
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-white/20 rounded-lg backdrop-blur-sm">
                  <p className="font-medium">Mobile First</p>
                  <p className="text-sm text-gray-600">Responsive by default</p>
                </div>
                <div className="p-4 bg-white/20 rounded-lg backdrop-blur-sm">
                  <p className="font-medium">Touch Optimized</p>
                  <p className="text-sm text-gray-600">44px minimum targets</p>
                </div>
                <div className="p-4 bg-white/20 rounded-lg backdrop-blur-sm">
                  <p className="font-medium">Adaptive Layout</p>
                  <p className="text-sm text-gray-600">Flexible grids</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Animations */}
        <Card className="mb-8 animate-slide-in-right">
          <CardHeader>
            <CardTitle>Animation System</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <h4 className="text-lg font-semibold">Hover Effects</h4>
                <div className="space-y-3">
                  <Button className="hover-lift">Hover to Lift</Button>
                  <Button className="hover-scale">Hover to Scale</Button>
                </div>
              </div>
              <div className="space-y-4">
                <h4 className="text-lg font-semibold">Animation Classes</h4>
                <div className="space-y-3">
                  <div className="p-3 bg-white/20 rounded-lg animate-bounce">
                    Bouncing Element
                  </div>
                  <div className="p-3 bg-white/20 rounded-lg animate-pulse">
                    Pulsing Element
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Glass Morphism */}
        <Card className="mb-8 animate-fade-in">
          <CardHeader>
            <CardTitle>Glass Morphism Effects</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="glass p-6 rounded-2xl text-center">
                <h4 className="font-semibold mb-2">Frosted Glass</h4>
                <p className="text-sm text-gray-600">
                  Translucent with backdrop blur
                </p>
              </div>
              <div className="glass glass-hover p-6 rounded-2xl text-center transition-all duration-300">
                <h4 className="font-semibold mb-2">Interactive Glass</h4>
                <p className="text-sm text-gray-600">Hover to see the effect</p>
              </div>
              <div className="glass p-6 rounded-2xl text-center">
                <h4 className="font-semibold mb-2">Depth Effect</h4>
                <p className="text-sm text-gray-600">Layered with shadows</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center text-gray-600 animate-fade-in">
          <p className="text-lg">
            Design System v1.0 - Built with ❤️ and Tailwind CSS
          </p>
          <p className="text-sm mt-2">
            All components are fully responsive and accessible
          </p>
        </div>
      </ResponsiveContainer>
    </div>
  );
};

export default DesignSystemPage;
