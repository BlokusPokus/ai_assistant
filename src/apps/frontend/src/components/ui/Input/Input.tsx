import React from 'react';
import { cn } from '../../../utils/cn';

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, label, error, leftIcon, rightIcon, ...props }, ref) => {
    return (
      <div className="space-y-3 w-full">
        {label && (
          <label className="block text-sm font-medium text-primary font-semibold">
            {label}
          </label>
        )}
        <div className="relative w-full">
          {leftIcon && (
            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 z-10">
              {leftIcon}
            </div>
          )}
          <input
            type={type}
            className={cn(
              'flex h-12 w-full rounded-2xl border border-gray-300/50 bg-white/80 backdrop-blur-sm px-4 py-3 text-sm',
              'placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent/50',
              'disabled:cursor-not-allowed disabled:opacity-50 disabled:bg-gray-50/80',
              'transition-all duration-200 hover:border-gray-400/60',
              'shadow-sm hover:shadow-md',
              leftIcon && 'pl-12',
              rightIcon && 'pr-12',
              error &&
                'border-red-400 focus:ring-red-400/50 focus:border-red-400/50',
              className
            )}
            ref={ref}
            {...props}
            value={props.value || ''}
          />
          {rightIcon && (
            <div className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 z-10">
              {rightIcon}
            </div>
          )}
        </div>
        {error && (
          <p className="text-sm text-red-600 px-1 font-medium">{error}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export { Input };
export default Input;
