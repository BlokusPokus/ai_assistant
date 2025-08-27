# UI Components - Design System

This directory contains our enhanced UI components built with a modern design system featuring frosted glass aesthetics, improved typography, and enhanced user experience.

## 🎨 Design Philosophy

Our design system is built around these core principles:
- **Friendly & Modern**: Clean, minimal design with playful accents
- **Glass Morphism**: Frosted glass effects with backdrop blur
- **Responsive First**: Mobile-first approach with progressive enhancement
- **Accessibility**: WCAG 2.1 AA compliance built-in
- **Performance**: Optimized animations and smooth interactions

## 🧩 Components

### Button
Enhanced button component with multiple variants, sizes, and states.

```tsx
import { Button } from '../components/ui';

// Basic usage
<Button>Click me</Button>

// With variants
<Button variant="secondary">Secondary</Button>
<Button variant="ghost">Ghost</Button>
<Button variant="danger">Danger</Button>

// With sizes
<Button size="sm">Small</Button>
<Button size="lg">Large</Button>

// With states
<Button loading>Loading...</Button>
<Button disabled>Disabled</Button>

// With icons
<Button leftIcon={<span>🚀</span>}>Launch</Button>
```

**Props:**
- `variant`: 'primary' | 'secondary' | 'ghost' | 'danger'
- `size`: 'sm' | 'md' | 'lg' | 'xl'
- `loading`: boolean
- `leftIcon`: ReactNode
- `rightIcon`: ReactNode

### Card
Frosted glass card component with backdrop blur and hover effects.

```tsx
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '../components/ui';

<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
  </CardHeader>
  <CardContent>
    <p>Card content goes here</p>
  </CardContent>
  <CardFooter>
    <Button>Action</Button>
  </CardFooter>
</Card>
```

**Features:**
- Frosted glass background with backdrop blur
- Smooth hover animations
- Consistent spacing and typography
- Responsive design

### Input
Enhanced input component with labels, icons, and validation states.

```tsx
import { Input } from '../components/ui';

// Basic input
<Input label="Username" placeholder="Enter username" />

// With icons
<Input 
  label="Search"
  leftIcon={<span>🔍</span>}
  placeholder="Search..."
/>

// With error state
<Input 
  label="Email"
  type="email"
  error="Please enter a valid email"
/>
```

**Props:**
- `label`: string
- `error`: string
- `leftIcon`: ReactNode
- `rightIcon`: ReactNode
- All standard HTML input props

### ResponsiveContainer
Utility component for consistent responsive spacing.

```tsx
import { ResponsiveContainer } from '../components/ui';

<ResponsiveContainer>
  <p>Content with responsive padding</p>
</ResponsiveContainer>

// Custom spacing
<ResponsiveContainer 
  mobile="px-2" 
  tablet="px-4" 
  desktop="px-8"
>
  <p>Custom responsive spacing</p>
</ResponsiveContainer>
```

## 🎭 Animation System

### CSS Classes
- `.animate-fade-in`: Fade in animation
- `.animate-slide-in-left`: Slide in from left
- `.animate-slide-in-right`: Slide in from right
- `.animate-scale-in`: Scale in animation
- `.animate-bounce`: Bouncing animation

### Hover Effects
- `.hover-lift`: Lift effect on hover
- `.hover-scale`: Scale effect on hover
- `.glass-hover`: Enhanced glass effect on hover

### Transitions
- `.transition-all`: All properties transition
- `.transition-transform`: Transform transitions
- `.transition-colors`: Color transitions

## 🎨 Design Tokens

### Colors
- `--color-primary`: #000000 (Black)
- `--color-secondary`: #ffffff (White)
- `--color-accent`: #3b82f6 (Blue)
- `--color-accent-light`: #60a5fa (Light Blue)
- `--color-soft-highlight`: #e0f2fe (Soft Blue)

### Typography
- `--font-family-primary`: "Nunito", sans-serif
- Font sizes from `--font-size-xs` (12px) to `--font-size-5xl` (48px)

### Spacing
- Consistent spacing scale from `--spacing-1` (4px) to `--spacing-20` (80px)

### Shadows
- Shadow system from `--shadow-sm` to `--shadow-2xl`

## 📱 Responsive Design

### Breakpoints
- **xs**: 320px - 480px (Mobile Small)
- **sm**: 481px - 768px (Mobile Medium)
- **md**: 769px - 1024px (Tablet)
- **lg**: 1025px - 1440px (Desktop Small)
- **xl**: 1441px - 1920px (Desktop Large)
- **2xl**: 1921px+ (Desktop Extra Large)

### Hooks
```tsx
import { useBreakpoint, useIsMobile, useIsTablet, useIsDesktop } from '../hooks/useBreakpoint';

const breakpoint = useBreakpoint();
const isMobile = useIsMobile();
const isTablet = useIsTablet();
const isDesktop = useIsDesktop();
```

## ♿ Accessibility

All components are built with accessibility in mind:
- Proper ARIA labels and roles
- Keyboard navigation support
- Focus management
- Screen reader compatibility
- WCAG 2.1 AA compliance

## 🚀 Usage Examples

### Complete Form Example
```tsx
import { Card, CardHeader, CardTitle, CardContent, Input, Button } from '../components/ui';

<Card>
  <CardHeader>
    <CardTitle>User Registration</CardTitle>
  </CardHeader>
  <CardContent className="space-y-4">
    <Input 
      label="Full Name"
      placeholder="Enter your full name"
      leftIcon={<span>👤</span>}
    />
    <Input 
      label="Email"
      type="email"
      placeholder="Enter your email"
      leftIcon={<span>📧</span>}
    />
    <Input 
      label="Password"
      type="password"
      placeholder="Enter your password"
      leftIcon={<span>🔒</span>}
    />
    <Button className="w-full">Register</Button>
  </CardContent>
</Card>
```

### Dashboard Layout
```tsx
import { ResponsiveContainer, Card, CardHeader, CardTitle, CardContent } from '../components/ui';

<ResponsiveContainer>
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <Card>
      <CardHeader>
        <CardTitle>Statistics</CardTitle>
      </CardHeader>
      <CardContent>
        <p>Your content here</p>
      </CardContent>
    </Card>
    {/* More cards... */}
  </div>
</ResponsiveContainer>
```

## 🔧 Customization

### Extending Components
All components accept a `className` prop for custom styling:

```tsx
<Button className="bg-purple-500 hover:bg-purple-600">
  Custom Styled Button
</Button>
```

### Design Token Overrides
Customize design tokens in `src/styles/design-tokens.css`:

```css
:root {
  --color-accent: #8b5cf6; /* Custom purple accent */
  --font-family-primary: 'Inter', sans-serif; /* Custom font */
}
```

## 📚 Resources

- **Tailwind CSS**: https://tailwindcss.com/docs
- **CSS Backdrop Filter**: MDN documentation
- **Accessibility Guidelines**: WCAG 2.1 documentation
- **Design System Best Practices**: Industry standards and examples

---

**Version**: 1.0  
**Last Updated**: December 2024  
**Status**: 🚀 Ready for Production
