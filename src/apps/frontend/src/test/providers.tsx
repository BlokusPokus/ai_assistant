import React from 'react';
import { BrowserRouter } from 'react-router-dom';

// Test providers wrapper
export const AllTheProviders = ({
  children,
}: {
  children: React.ReactNode;
}) => {
  return <BrowserRouter>{children}</BrowserRouter>;
};
