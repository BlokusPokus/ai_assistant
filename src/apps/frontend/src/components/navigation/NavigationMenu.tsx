import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import type { LucideIcon } from 'lucide-react';

export interface NavigationItem {
  label: string;
  href: string;
  icon: LucideIcon;
  exact?: boolean;
  children?: NavigationItem[];
}

interface NavigationMenuProps {
  items: NavigationItem[];
  isCollapsed?: boolean;
}

const NavigationMenu: React.FC<NavigationMenuProps> = ({
  items,
  isCollapsed = false,
}) => {
  const location = useLocation();

  const isActive = (item: NavigationItem) => {
    if (item.exact) {
      return location.pathname === item.href;
    }
    return location.pathname.startsWith(item.href);
  };

  const renderMenuItem = (item: NavigationItem) => {
    const active = isActive(item);
    const Icon = item.icon;

    if (isCollapsed) {
      return (
        <Link
          key={item.href}
          to={item.href}
          className={`
            group flex h-12 w-12 items-center justify-center rounded-lg mx-auto mb-2
            transition-colors duration-200
            ${
              active
                ? 'bg-blue-100 text-blue-600'
                : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
            }
          `}
          title={item.label}
        >
          <Icon className="h-5 w-5" />
        </Link>
      );
    }

    return (
      <Link
        key={item.href}
        to={item.href}
        className={`
          group flex items-center space-x-3 rounded-lg px-3 py-2 text-sm font-medium
          transition-colors duration-200
          ${
            active
              ? 'bg-blue-100 text-blue-600'
              : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
          }
        `}
      >
        <Icon className="h-5 w-5" />
        <span>{item.label}</span>
        {active && (
          <div className="ml-auto w-2 h-2 bg-blue-600 rounded-full"></div>
        )}
      </Link>
    );
  };

  return (
    <nav className="px-3 py-4">
      <div className="space-y-1">{items.map(renderMenuItem)}</div>
    </nav>
  );
};

export default NavigationMenu;
