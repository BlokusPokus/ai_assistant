import React from "react";
import type { CardProps } from "@/types";
import { cn } from "@/utils/cn";

const Card: React.FC<CardProps> = ({
  title,
  children,
  className,
  padding = "md",
}) => {
  const paddingClasses = {
    sm: "p-4",
    md: "p-6",
    lg: "p-8",
  };

  const classes = cn(
    "rounded-lg border border-gray-200 bg-white shadow-sm",
    paddingClasses[padding],
    className
  );

  return (
    <div className={classes}>
      {title && (
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        </div>
      )}
      {children}
    </div>
  );
};

export default Card;
