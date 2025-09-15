import React, { useState, useEffect } from 'react';
import { Button, Card, Badge, Alert } from '@/components/ui';
import { Input } from '@/components/ui/Input/Input';
import {
  Phone,
  Plus,
  Edit,
  Trash2,
  Shield,
  CheckCircle,
  Send,
} from 'lucide-react';
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

interface PhoneManagementProps {
  className?: string;
}

const PhoneManagement: React.FC<PhoneManagementProps> = ({
  className = '',
}) => {
  const [phoneNumbers, setPhoneNumbers] = useState<PhoneNumber[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Add phone number state
  const [showAddForm, setShowAddForm] = useState(false);
  const [newPhoneNumber, setNewPhoneNumber] = useState('');
  const [isPrimary, setIsPrimary] = useState(false);

  // Edit phone number state
  const [editingPhone, setEditingPhone] = useState<PhoneNumber | null>(null);
  const [editPhoneNumber, setEditPhoneNumber] = useState('');
  const [editIsPrimary, setEditIsPrimary] = useState(false);

  // Verification state
  const [verifyingPhone, setVerifyingPhone] = useState<string | null>(null);
  const [verificationCode, setVerificationCode] = useState('');
  const [verificationSent, setVerificationSent] = useState<string | null>(null);

  useEffect(() => {
    fetchPhoneNumbers();
  }, []);

  const fetchPhoneNumbers = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await api.get('/users/me/phone-numbers');
      setPhoneNumbers(response.data.phone_numbers);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to fetch phone numbers'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddPhoneNumber = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    try {
      await api.post('/users/me/phone-numbers', {
        phone_number: newPhoneNumber,
        is_primary: isPrimary,
      });

      setSuccess('Phone number added successfully');
      setNewPhoneNumber('');
      setIsPrimary(false);
      setShowAddForm(false);
      fetchPhoneNumbers();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to add phone number'
      );
    }
  };

  const handleUpdatePhoneNumber = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingPhone) return;

    setError(null);
    setSuccess(null);

    try {
      await api.put(`/users/me/phone-numbers/${editingPhone.id}`, {
        phone_number: editPhoneNumber,
        is_primary: editIsPrimary,
      });

      setSuccess('Phone number updated successfully');
      setEditingPhone(null);
      setEditPhoneNumber('');
      setEditIsPrimary(false);
      fetchPhoneNumbers();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to update phone number'
      );
    }
  };

  const handleDeletePhoneNumber = async (phoneId: number | string) => {
    if (!confirm('Are you sure you want to delete this phone number?')) return;

    setError(null);
    setSuccess(null);

    try {
      await api.delete(`/users/me/phone-numbers/${phoneId}`);

      setSuccess('Phone number deleted successfully');
      fetchPhoneNumbers();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to delete phone number'
      );
    }
  };

  const handleSetPrimary = async (phoneId: number | string) => {
    setError(null);
    setSuccess(null);

    try {
      await api.post(`/users/me/phone-numbers/${phoneId}/set-primary`);

      setSuccess('Primary phone number updated successfully');
      fetchPhoneNumbers();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Failed to set primary phone number'
      );
    }
  };

  const handleSendVerification = async (phoneNumber: string) => {
    setError(null);
    setSuccess(null);

    try {
      await api.post('/users/me/phone-numbers/verify', {
        phone_number: phoneNumber,
      });

      setSuccess('Verification code sent successfully');
      setVerifyingPhone(phoneNumber);
      setVerificationSent(phoneNumber);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to send verification code'
      );
    }
  };

  const handleVerifyCode = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!verifyingPhone) return;

    setError(null);
    setSuccess(null);

    try {
      await api.post('/users/me/phone-numbers/verify-code', {
        phone_number: verifyingPhone,
        verification_code: verificationCode,
      });

      setSuccess('Phone number verified successfully');
      setVerifyingPhone(null);
      setVerificationCode('');
      setVerificationSent(null);
      fetchPhoneNumbers();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to verify code');
    }
  };

  const startEdit = (phone: PhoneNumber) => {
    setEditingPhone(phone);
    setEditPhoneNumber(phone.phone_number);
    setEditIsPrimary(phone.is_primary);
  };

  const cancelEdit = () => {
    setEditingPhone(null);
    setEditPhoneNumber('');
    setEditIsPrimary(false);
  };

  const formatPhoneNumber = (phone: string) => {
    // Simple formatting for display
    const cleaned = phone.replace(/\D/g, '');
    if (cleaned.length === 11 && cleaned.startsWith('1')) {
      return `+1 (${cleaned.slice(1, 4)}) ${cleaned.slice(4, 7)}-${cleaned.slice(7)}`;
    } else if (cleaned.length === 10) {
      return `+1 (${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
    }
    return phone;
  };

  if (isLoading && phoneNumbers.length === 0) {
    return (
      <Card padding="lg" className={className}>
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
          <div className="space-y-3">
            <div className="h-10 bg-gray-200 rounded"></div>
            <div className="h-10 bg-gray-200 rounded"></div>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card padding="lg" className={className}>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Phone Numbers</h2>
          <p className="text-gray-600 mt-1">
            Manage your phone numbers for SMS service and notifications
          </p>
        </div>
        <Button
          onClick={() => setShowAddForm(true)}
          variant="outline"
          size="sm"
          className="flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Add Phone
        </Button>
      </div>

      {/* Error and Success Messages */}
      {error && (
        <Alert variant="error" className="mb-4">
          {error}
        </Alert>
      )}
      {success && (
        <Alert variant="success" className="mb-4">
          {success}
        </Alert>
      )}

      {/* Add Phone Number Form */}
      {showAddForm && (
        <Card padding="md" className="mb-6 bg-gray-50">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Add New Phone Number
          </h3>
          <form onSubmit={handleAddPhoneNumber} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Phone Number
              </label>
              <Input
                type="tel"
                value={newPhoneNumber}
                onChange={e => setNewPhoneNumber(e.target.value)}
                placeholder="+1 (555) 123-4567"
                required
                className="w-full"
              />
              <p className="text-xs text-gray-500 mt-1">
                Enter phone number in international format (e.g., +1 for US)
              </p>
            </div>
            <div className="flex items-center">
              <input
                type="checkbox"
                id="isPrimary"
                checked={isPrimary}
                onChange={e => setIsPrimary(e.target.checked)}
                className="h-4 w-4 text-blue-600 rounded border-gray-300"
              />
              <label htmlFor="isPrimary" className="ml-2 text-sm text-gray-700">
                Set as primary phone number
              </label>
            </div>
            <div className="flex gap-2">
              <Button type="submit" size="sm">
                Add Phone Number
              </Button>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => setShowAddForm(false)}
              >
                Cancel
              </Button>
            </div>
          </form>
        </Card>
      )}

      {/* Phone Numbers List */}
      <div className="space-y-4">
        {phoneNumbers.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Phone className="w-12 h-12 mx-auto mb-3 text-gray-300" />
            <p>No phone numbers added yet</p>
            <p className="text-sm">
              Add a phone number to get started with SMS service
            </p>
          </div>
        ) : (
          phoneNumbers.map(phone => (
            <div key={phone.id} className="border rounded-lg p-4 bg-white">
              {editingPhone?.id === phone.id ? (
                // Edit Form
                <form onSubmit={handleUpdatePhoneNumber} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Phone Number
                    </label>
                    <Input
                      type="tel"
                      value={editPhoneNumber}
                      onChange={e => setEditPhoneNumber(e.target.value)}
                      required
                      className="w-full"
                    />
                  </div>
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id={`editIsPrimary-${phone.id}`}
                      checked={editIsPrimary}
                      onChange={e => setEditIsPrimary(e.target.checked)}
                      className="h-4 w-4 text-blue-600 rounded border-gray-300"
                    />
                    <label
                      htmlFor={`editIsPrimary-${phone.id}`}
                      className="ml-2 text-sm text-gray-700"
                    >
                      Set as primary phone number
                    </label>
                  </div>
                  <div className="flex gap-2">
                    <Button type="submit" size="sm">
                      Save Changes
                    </Button>
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={cancelEdit}
                    >
                      Cancel
                    </Button>
                  </div>
                </form>
              ) : (
                // Display Mode
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Phone className="w-5 h-5 text-gray-400" />
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-gray-900">
                          {formatPhoneNumber(phone.phone_number)}
                        </span>
                        {phone.is_primary && (
                          <Badge variant="primary" size="sm">
                            Primary
                          </Badge>
                        )}
                        {phone.is_verified ? (
                          <Badge
                            variant="success"
                            size="sm"
                            className="flex items-center gap-1"
                          >
                            <CheckCircle className="w-3 h-3" />
                            Verified
                          </Badge>
                        ) : (
                          <Badge
                            variant="warning"
                            size="sm"
                            className="flex items-center gap-1"
                          >
                            <Shield className="w-3 h-3" />
                            Unverified
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm text-gray-500">
                        Added {new Date(phone.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {!phone.is_verified && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() =>
                          handleSendVerification(phone.phone_number)
                        }
                        disabled={verificationSent === phone.phone_number}
                        className="flex items-center gap-1"
                      >
                        <Send className="w-3 h-3" />
                        {verificationSent === phone.phone_number
                          ? 'Sent'
                          : 'Verify'}
                      </Button>
                    )}
                    {!phone.is_primary && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleSetPrimary(phone.id)}
                        className="flex items-center gap-1"
                      >
                        <CheckCircle className="w-3 h-3" />
                        Set Primary
                      </Button>
                    )}
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => startEdit(phone)}
                      className="flex items-center gap-1"
                    >
                      <Edit className="w-3 h-3" />
                      Edit
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDeletePhoneNumber(phone.id)}
                      className="flex items-center gap-1 text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="w-3 h-3" />
                      Delete
                    </Button>
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Verification Code Input */}
      {verifyingPhone && (
        <Card padding="md" className="mt-6 bg-blue-50 border-blue-200">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Verify Phone Number
          </h3>
          <p className="text-sm text-gray-600 mb-4">
            Enter the 6-digit verification code sent to{' '}
            {formatPhoneNumber(verifyingPhone)}
          </p>
          <form onSubmit={handleVerifyCode} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Verification Code
              </label>
              <Input
                type="text"
                value={verificationCode}
                onChange={(value: string) => setVerificationCode(value)}
                placeholder="123456"
                required
                className="w-full"
              />
            </div>
            <div className="flex gap-2">
              <Button type="submit" size="sm">
                Verify Code
              </Button>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => {
                  setVerifyingPhone(null);
                  setVerificationCode('');
                  setVerificationSent(null);
                }}
              >
                Cancel
              </Button>
            </div>
          </form>
        </Card>
      )}
    </Card>
  );
};

export default PhoneManagement;
