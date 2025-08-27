import React from 'react';
import { cn } from '../../../utils/cn';

interface ResponsiveContainerProps {
  children: React.ReactNode;
  className?: string;
  mobile?: string;
  tablet?: string;
  desktop?: string;
}

const ResponsiveContainer: React.FC<ResponsiveContainerProps> = ({
  children,
  className,
  mobile = "px-4",
  tablet = "px-6",
  desktop = "px-8",
}) => {
  return (
    <div
      className={cn(
        "w-full mx-auto",
        mobile,
        `md:${tablet}`,
        `lg:${desktop}`,
        className
      )}
    >
      {children}
    </div>
  );
};

export { ResponsiveContainer };
export default ResponsiveContainer;
