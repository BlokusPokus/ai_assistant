import React from 'react';
import { cn } from '../../../utils/cn';

export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface SelectProps
  extends Omit<React.SelectHTMLAttributes<HTMLSelectElement>, 'onChange'> {
  label?: string;
  error?: string;
  options: SelectOption[];
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  onChange?: (value: string) => void;
  placeholder?: string;
}

const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
  ({ 
    className, 
    label, 
    error, 
    options, 
    leftIcon, 
    rightIcon, 
    onChange, 
    placeholder,
    disabled,
    ...props 
  }, ref) => {
    const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
      if (onChange) {
        onChange(e.target.value);
      }
    };

    return (
      <div className="space-y-3">
        {label && (
          <label className="block text-sm font-medium text-primary font-semibold">
            {label}
          </label>
        )}
        <div className="relative">
          {leftIcon && (
            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 z-10">
              {leftIcon}
            </div>
          )}
          <select
            className={cn(
              "flex h-12 w-full rounded-2xl border border-gray-300/50 bg-white/80 backdrop-blur-sm px-4 py-3 text-sm",
              "placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent/50",
              "disabled:cursor-not-allowed disabled:opacity-50 disabled:bg-gray-50/80",
              "transition-all duration-200 hover:border-gray-400/60",
              "shadow-sm hover:shadow-md appearance-none",
              leftIcon && "pl-12",
              rightIcon && "pr-12",
              error && "border-red-400 focus:ring-red-400/50 focus:border-red-400/50",
              className
            )}
            ref={ref}
            onChange={handleChange}
            disabled={disabled}
            {...props}
          >
            {placeholder && (
              <option value="" disabled>
                {placeholder}
              </option>
            )}
            {options.map((option) => (
              <option
                key={option.value}
                value={option.value}
                disabled={option.disabled}
                className="py-2"
              >
                {option.label}
              </option>
            ))}
          </select>
          {rightIcon && (
            <div className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 z-10">
              {rightIcon}
            </div>
          )}
          {/* Custom dropdown arrow */}
          <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none">
            <svg
              className="w-4 h-4 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </div>
        </div>
        {error && (
          <p className="text-sm text-red-600 px-1 font-medium">
            {error}
          </p>
        )}
      </div>
    );
  }
);

Select.displayName = "Select";

export { Select };
export default Select;
