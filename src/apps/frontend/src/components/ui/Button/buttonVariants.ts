import { cva, type VariantProps } from 'class-variance-authority';

export const buttonVariants = cva(
  // Base styles
  'inline-flex items-center justify-center rounded-full font-semibold transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none',
  {
    variants: {
      variant: {
        primary:
          'bg-gradient-to-r from-accent to-accent-light text-white shadow-lg hover:shadow-xl hover:scale-105 focus:ring-accent',
        secondary:
          'bg-white text-primary border border-gray-300 shadow-md hover:shadow-lg hover:scale-105 focus:ring-gray-400',
        ghost:
          'bg-transparent text-primary hover:bg-gray-100 focus:ring-gray-400',
        danger:
          'bg-red-600 text-white shadow-lg hover:shadow-xl hover:scale-105 focus:ring-red-500',
      },
      size: {
        sm: 'h-8 px-3 text-sm',
        md: 'h-10 px-4 text-base',
        lg: 'h-12 px-6 text-lg',
        xl: 'h-14 px-8 text-xl',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  }
);

export type ButtonVariants = VariantProps<typeof buttonVariants>;
