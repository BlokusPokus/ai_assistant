import React from 'react';
import { Card } from '@/components/ui';
import {
  Calendar,
  Clock,
  MapPin,
  Plus,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';

const CalendarPage: React.FC = () => {
  const mockEvents = [
    {
      id: 1,
      title: 'Team Meeting',
      time: '9:00 AM - 10:00 AM',
      location: 'Conference Room A',
      type: 'meeting',
    },
    {
      id: 2,
      title: 'Doctor Appointment',
      time: '2:00 PM - 2:30 PM',
      location: 'Medical Center',
      type: 'appointment',
    },
    {
      id: 3,
      title: 'Grocery Shopping',
      time: '6:00 PM - 7:00 PM',
      location: 'Local Market',
      type: 'task',
    },
  ];

  const eventTypeColors = {
    meeting: 'bg-blue-100 text-blue-800 border-blue-200',
    appointment: 'bg-green-100 text-green-800 border-green-200',
    task: 'bg-purple-100 text-purple-800 border-purple-200',
  };

  return (
    <div className="space-y-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Calendar</h1>
        <p className="text-gray-600">
          View and manage your schedule, appointments, and upcoming events.
        </p>
      </div>

      {/* Calendar Header */}
      <Card padding="lg">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-4">
            <button className="p-2 hover:bg-gray-100 rounded-md">
              <ChevronLeft className="w-5 h-5" />
            </button>
            <h2 className="text-xl font-semibold text-gray-900">
              December 2024
            </h2>
            <button className="p-2 hover:bg-gray-100 rounded-md">
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 flex items-center space-x-2">
            <Plus className="w-4 h-4" />
            <span>Add Event</span>
          </button>
        </div>

        {/* Calendar Grid Placeholder */}
        <div className="grid grid-cols-7 gap-1 mb-4">
          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
            <div
              key={day}
              className="p-2 text-center text-sm font-medium text-gray-500"
            >
              {day}
            </div>
          ))}
          {Array.from({ length: 35 }, (_, i) => (
            <div
              key={i}
              className="p-2 h-20 border border-gray-200 text-sm text-gray-600 hover:bg-gray-50 cursor-pointer"
            >
              {i + 1}
            </div>
          ))}
        </div>
      </Card>

      {/* Upcoming Events */}
      <Card title="Upcoming Events" padding="lg">
        <div className="space-y-4">
          {mockEvents.map(event => (
            <div
              key={event.id}
              className="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg"
            >
              <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
              <div className="flex-1">
                <h4 className="font-medium text-gray-900">{event.title}</h4>
                <div className="flex items-center space-x-4 text-sm text-gray-600 mt-1">
                  <div className="flex items-center space-x-1">
                    <Clock className="w-4 h-4" />
                    <span>{event.time}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <MapPin className="w-4 h-4" />
                    <span>{event.location}</span>
                  </div>
                </div>
              </div>
              <span
                className={`px-2 py-1 text-xs font-medium rounded-full border ${eventTypeColors[event.type as keyof typeof eventTypeColors]}`}
              >
                {event.type}
              </span>
            </div>
          ))}
        </div>
      </Card>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card
          padding="lg"
          className="text-center hover:shadow-md transition-shadow cursor-pointer"
        >
          <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
            <Plus className="w-6 h-6 text-blue-600" />
          </div>
          <h3 className="font-medium text-gray-900 mb-1">Add Event</h3>
          <p className="text-sm text-gray-600">Create a new calendar event</p>
        </Card>

        <Card
          padding="lg"
          className="text-center hover:shadow-md transition-shadow cursor-pointer"
        >
          <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
            <Calendar className="w-6 h-6 text-green-600" />
          </div>
          <h3 className="font-medium text-gray-900 mb-1">View Month</h3>
          <p className="text-sm text-gray-600">See your monthly overview</p>
        </Card>

        <Card
          padding="lg"
          className="text-center hover:shadow-md transition-shadow cursor-pointer"
        >
          <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
            <Clock className="w-6 h-6 text-purple-600" />
          </div>
          <h3 className="font-medium text-gray-900 mb-1">Today's Schedule</h3>
          <p className="text-sm text-gray-600">Focus on today's events</p>
        </Card>
      </div>

      {/* Coming Soon Features */}
      <Card
        padding="lg"
        className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200"
      >
        <div className="text-center">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            📅 Advanced Calendar Features Coming Soon!
          </h3>
          <p className="text-gray-600 mb-4">
            We're working on bringing you powerful calendar capabilities
            including:
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
            <div className="flex items-center space-x-2">
              <Calendar className="w-4 h-4 text-blue-600" />
              <span>Microsoft Graph integration</span>
            </div>
            <div className="flex items-center space-x-2">
              <Clock className="w-4 h-4 text-green-600" />
              <span>Smart scheduling</span>
            </div>
            <div className="flex items-center space-x-2">
              <MapPin className="w-4 h-4 text-purple-600" />
              <span>Location services</span>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default CalendarPage;
