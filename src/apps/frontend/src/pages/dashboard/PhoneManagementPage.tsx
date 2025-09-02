import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Button } from '@/components/ui';
import { ArrowLeft, Phone } from 'lucide-react';
import PhoneManagement from '@/components/profile/PhoneManagement';

const PhoneManagementPage: React.FC = () => {
  const navigate = useNavigate();

  const breadcrumbs = [
    { label: 'Dashboard', href: '/dashboard' },
    { label: 'Phone Number', href: '/dashboard/phone-management' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-4 mb-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate('/dashboard')}
              className="flex items-center space-x-2"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back to Dashboard</span>
            </Button>
          </div>

          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-teal-100 rounded-lg flex items-center justify-center">
              <Phone className="w-5 h-5 text-teal-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Phone Number Management
              </h1>
              <p className="text-gray-600">
                Manage your phone number and SMS verification settings
              </p>
            </div>
          </div>
        </div>

        {/* Breadcrumb Navigation */}
        <nav className="mb-6">
          <ol className="flex items-center space-x-2 text-sm text-gray-500">
            {breadcrumbs.map((crumb, index) => (
              <li key={index} className="flex items-center">
                {index > 0 && <span className="mx-2">/</span>}
                {index === breadcrumbs.length - 1 ? (
                  <span className="text-gray-900 font-medium">
                    {crumb.label}
                  </span>
                ) : (
                  <button
                    onClick={() => navigate(crumb.href)}
                    className="hover:text-gray-700 underline"
                  >
                    {crumb.label}
                  </button>
                )}
              </li>
            ))}
          </ol>
        </nav>

        {/* Phone Number Overview */}
        <div className="mb-8">
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">
                Phone Number Overview
              </h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <h3 className="font-medium text-gray-900">Current Status</h3>
                <p className="text-sm text-gray-600">
                  Manage your primary phone number for SMS notifications and
                  verification.
                </p>
              </div>
              <div className="space-y-2">
                <h3 className="font-medium text-gray-900">Features</h3>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• SMS verification codes</li>
                  <li>• Phone number validation</li>
                  <li>• Secure phone number management</li>
                </ul>
              </div>
            </div>
          </Card>
        </div>

        {/* Phone Management Component */}
        <div className="mb-8">
          <Card className="p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-6">
              Phone Number Management
            </h2>
            <PhoneManagement />
          </Card>
        </div>

        {/* Help Section */}
        <div className="mb-8">
          <Card className="p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Need Help?
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-medium text-gray-900 mb-2">
                  Phone Number Verification
                </h3>
                <p className="text-sm text-gray-600 mb-3">
                  We'll send a verification code to your phone number to confirm
                  it's working correctly.
                </p>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Enter your phone number with country code</li>
                  <li>• Check your phone for the verification code</li>
                  <li>• Enter the code to complete verification</li>
                </ul>
              </div>
              <div>
                <h3 className="font-medium text-gray-900 mb-2">
                  SMS Notifications
                </h3>
                <p className="text-sm text-gray-600 mb-3">
                  Your verified phone number will be used for important
                  notifications and alerts.
                </p>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Security alerts and login notifications</li>
                  <li>• Important system updates</li>
                  <li>• Two-factor authentication codes</li>
                </ul>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default PhoneManagementPage;
