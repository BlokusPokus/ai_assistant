import React, { useState, useEffect } from 'react';
import { Button, Card, Badge, Alert } from '@/components/ui';
import {
  Phone,
  Plus,
  Edit,
  Shield,
  CheckCircle,
  AlertCircle,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import api from '@/services/api';

interface PhoneNumber {
  id: number | string;
  user_id: number;
  phone_number: string;
  is_primary: boolean;
  is_verified: boolean;
  verification_method: string;
  created_at: string;
  updated_at?: string;
}

interface PhoneNumberRegistrationWidgetProps {
  className?: string;
}

const PhoneNumberRegistrationWidget: React.FC<
  PhoneNumberRegistrationWidgetProps
> = ({ className = '' }) => {
  const navigate = useNavigate();
  const [phoneNumbers, setPhoneNumbers] = useState<PhoneNumber[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPhoneNumbers();
  }, []);

  const fetchPhoneNumbers = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await api.get('/users/me/phone-numbers');
      setPhoneNumbers(response.data.phone_numbers || []);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to fetch phone numbers'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const formatPhoneNumber = (phone: string) => {
    // Simple formatting for display
    const cleaned = phone.replace(/\D/g, '');
    if (cleaned.length === 10) {
      return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
    }
    return phone;
  };

  const getStatusIcon = (phone: PhoneNumber) => {
    if (phone.is_verified) {
      return <CheckCircle className="w-4 h-4 text-green-500" />;
    }
    return <AlertCircle className="w-4 h-4 text-yellow-500" />;
  };

  const getStatusText = (phone: PhoneNumber) => {
    if (phone.is_verified) {
      return 'Verified';
    }
    return 'Pending Verification';
  };

  const getStatusColor = (phone: PhoneNumber) => {
    if (phone.is_verified) {
      return 'bg-green-100 text-green-800';
    }
    return 'bg-yellow-100 text-yellow-800';
  };

  const handleManageClick = () => {
    navigate('/dashboard/phone-management');
  };

  const handleAddPhoneClick = () => {
    navigate('/dashboard/phone-management?action=add');
  };

  const handleVerifyClick = () => {
    navigate('/dashboard/phone-management?action=verify');
  };

  if (isLoading) {
    return (
      <Card className={`p-6 ${className}`}>
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent"></div>
        </div>
      </Card>
    );
  }

  return (
    <Card className={`p-6 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Phone className="w-5 h-5 text-accent" />
          <h3 className="text-lg font-semibold text-gray-900">Phone Number</h3>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={handleManageClick}
          className="text-accent hover:text-accent-light"
        >
          Manage →
        </Button>
      </div>

      {error && (
        <Alert variant="error" className="mb-4">
          {error}
        </Alert>
      )}

      {phoneNumbers.length === 0 ? (
        <div className="text-center py-6">
          <Phone className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500 text-sm mb-4">
            No phone number registered
          </p>
          <Button
            variant="primary"
            size="sm"
            onClick={handleAddPhoneClick}
            className="w-full"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Phone Number
          </Button>
        </div>
      ) : (
        <div className="space-y-3">
          {phoneNumbers.slice(0, 1).map(phone => (
            <div
              key={phone.id}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div className="flex items-center space-x-3">
                {getStatusIcon(phone)}
                <div>
                  <p className="font-medium text-gray-900">
                    {formatPhoneNumber(phone.phone_number)}
                  </p>
                  <Badge className={`text-xs ${getStatusColor(phone)}`}>
                    {getStatusText(phone)}
                  </Badge>
                </div>
              </div>
              <div className="flex space-x-2">
                {!phone.is_verified && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleVerifyClick}
                    className="text-xs"
                  >
                    <Shield className="w-3 h-3 mr-1" />
                    Verify
                  </Button>
                )}
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleManageClick}
                  className="text-xs"
                >
                  <Edit className="w-3 h-3 mr-1" />
                  Manage
                </Button>
              </div>
            </div>
          ))}

          {phoneNumbers.length > 1 && (
            <p className="text-xs text-gray-500 text-center">
              +{phoneNumbers.length - 1} more phone number
              {phoneNumbers.length > 2 ? 's' : ''}
            </p>
          )}
        </div>
      )}

      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleAddPhoneClick}
            className="flex-1"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Phone
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleManageClick}
            className="flex-1"
          >
            <Edit className="w-4 h-4 mr-2" />
            Manage
          </Button>
        </div>
      </div>
    </Card>
  );
};

export default PhoneNumberRegistrationWidget;
