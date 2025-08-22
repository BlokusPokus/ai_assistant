# Personal Assistant TDAH - Frontend

This is the React frontend application for the Personal Assistant TDAH project.

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- npm 9+

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at [http://localhost:3000](http://localhost:3000).

## 📁 Project Structure

```
src/
├── components/ui/     # Basic UI components (Button, Input, Card, etc.)
├── types/            # TypeScript type definitions
├── utils/            # Utility functions
├── pages/            # Page components (to be implemented)
├── services/         # API services (to be implemented)
├── stores/           # State management (to be implemented)
└── styles/           # CSS and Tailwind configuration
```

## 🛠️ Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run build:check` - Type check without building
- `npm run lint` - Run ESLint
- `npm run lint:fix` - Fix ESLint issues automatically
- `npm run format` - Format code with Prettier
- `npm run format:check` - Check code formatting
- `npm run type-check` - Run TypeScript type checking
- `npm run preview` - Preview production build

## 🎨 UI Components

### Button

- Variants: primary, secondary, outline, ghost, destructive
- Sizes: sm, md, lg
- States: disabled, loading

### Input

- Types: text, email, password, number, tel, url
- Features: labels, validation, error states
- Accessibility: required field indicators

### Card

- Configurable padding (sm, md, lg)
- Optional title
- Flexible content

### Loading

- Multiple sizes (sm, md, lg)
- Optional loading text
- Animated spinner

### Error

- Error message display
- Optional retry functionality
- Consistent error styling

## 🎯 Technology Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Zustand (ready for implementation)
- **Forms**: React Hook Form (ready for implementation)
- **Routing**: React Router DOM (ready for implementation)
- **HTTP Client**: Axios (ready for implementation)
- **Icons**: Lucide React

## 🔧 Configuration

### TypeScript

- Strict mode enabled
- Path aliases configured for clean imports
- Modern ES2022 target

### Tailwind CSS

- Custom color palette (primary, secondary, success, warning, error)
- Custom animations and keyframes
- Responsive design utilities
- Component variants

### Vite

- Development server on port 3000
- API proxy to backend (port 8000)
- Path alias resolution
- Build optimization with code splitting

### ESLint & Prettier

- React and TypeScript rules
- Consistent code formatting
- Automatic fix capabilities

## 🌐 Development

### API Integration

The frontend is configured to proxy API requests to the backend:

- Development: `/api/*` → `http://localhost:8000/*`
- Production: Built assets served through Nginx

### Hot Reload

Vite provides fast hot module replacement for development.

### Type Safety

Full TypeScript support with strict type checking enabled.

## 🚀 Next Steps

This foundation is ready for:

1. **Task 039**: Authentication UI Implementation
2. **Routing**: React Router setup
3. **State Management**: Zustand store implementation
4. **API Services**: Axios-based service layer
5. **Forms**: React Hook Form integration

## 📚 Resources

- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

## 🤝 Contributing

1. Follow the established code style (ESLint + Prettier)
2. Write TypeScript interfaces for all component props
3. Use Tailwind CSS for styling
4. Test components before committing

---

**Task**: 038 - React Project Foundation Setup  
**Status**: ✅ Complete  
**Next**: Task 039 - Authentication UI Implementation
