import React from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

interface BreadcrumbItem {
  label: string;
  href: string;
  icon?: LucideIcon;
}

interface BreadcrumbsProps {
  currentPath: string;
}

const Breadcrumbs: React.FC<BreadcrumbsProps> = ({ currentPath }) => {
  const generateBreadcrumbs = (pathname: string): BreadcrumbItem[] => {
    const pathSegments = pathname.split('/').filter(Boolean);
    const breadcrumbs: BreadcrumbItem[] = [
      { label: 'Home', href: '/dashboard', icon: Home },
    ];

    let currentPath = '/dashboard';
    pathSegments.forEach((segment, index) => {
      if (index === 0) return; // Skip 'dashboard' as it's already in the first breadcrumb

      currentPath += `/${segment}`;
      const label = segment.charAt(0).toUpperCase() + segment.slice(1);
      breadcrumbs.push({ label, href: currentPath });
    });

    return breadcrumbs;
  };

  const breadcrumbs = generateBreadcrumbs(currentPath);

  return (
    <nav className="flex items-center space-x-1 text-sm text-gray-500">
      {breadcrumbs.map((breadcrumb, index) => {
        const isLast = index === breadcrumbs.length - 1;
        const Icon = breadcrumb.icon;

        if (isLast) {
          return (
            <span key={breadcrumb.href} className="text-gray-900 font-medium">
              {Icon && <Icon className="inline h-4 w-4 mr-1" />}
              {breadcrumb.label}
            </span>
          );
        }

        return (
          <React.Fragment key={breadcrumb.href}>
            <Link
              to={breadcrumb.href}
              className="flex items-center hover:text-gray-700 transition-colors"
            >
              {Icon && <Icon className="h-4 w-4 mr-1" />}
              {breadcrumb.label}
            </Link>
            <ChevronRight className="h-4 w-4" />
          </React.Fragment>
        );
      })}
    </nav>
  );
};

export default Breadcrumbs;
