import React, { useState } from 'react';
import { Card } from '@/components/ui';
import {
  FileText,
  Plus,
  Search,
  Tag,
  Calendar,
  Edit,
  Trash2,
} from 'lucide-react';

const NotesPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  const mockNotes = [
    {
      id: 1,
      title: 'Meeting Notes - Project Planning',
      content:
        'Discussed timeline for Q1 deliverables. Team agreed on March 15th deadline.',
      category: 'work',
      tags: ['meeting', 'project', 'planning'],
      created_at: '2024-12-20',
      updated_at: '2024-12-20',
    },
    {
      id: 2,
      title: 'Shopping List',
      content: 'Milk, bread, eggs, vegetables, chicken breast',
      category: 'personal',
      tags: ['shopping', 'groceries'],
      created_at: '2024-12-19',
      updated_at: '2024-12-19',
    },
    {
      id: 3,
      title: 'Ideas for Weekend Trip',
      content:
        'Hiking trail recommendations, restaurant suggestions, packing list',
      category: 'personal',
      tags: ['travel', 'weekend', 'ideas'],
      created_at: '2024-12-18',
      updated_at: '2024-12-18',
    },
  ];

  const categories = [
    { value: 'all', label: 'All Notes', count: mockNotes.length },
    {
      value: 'work',
      label: 'Work',
      count: mockNotes.filter(note => note.category === 'work').length,
    },
    {
      value: 'personal',
      label: 'Personal',
      count: mockNotes.filter(note => note.category === 'personal').length,
    },
  ];

  const filteredNotes = mockNotes.filter(note => {
    const matchesSearch =
      note.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      note.content.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory =
      selectedCategory === 'all' || note.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="space-y-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Notes</h1>
        <p className="text-gray-600">
          Create, organize, and manage your notes and ideas in one place.
        </p>
      </div>

      {/* Search and Filters */}
      <Card>
        <div className="flex flex-col md:flex-row md:items-center space-y-4 md:space-y-0 md:space-x-4">
          {/* Search */}
          <div className="flex-1 relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Search notes..."
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            />
          </div>

          {/* Category Filter */}
          <div className="flex space-x-2">
            {categories.map(category => (
              <button
                key={category.value}
                onClick={() => setSelectedCategory(category.value)}
                className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  selectedCategory === category.value
                    ? 'bg-blue-100 text-blue-700 border border-blue-200'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {category.label} ({category.count})
              </button>
            ))}
          </div>

          {/* Add Note Button */}
          <button className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 flex items-center space-x-2">
            <Plus className="w-4 h-4" />
            <span>Add Note</span>
          </button>
        </div>
      </Card>

      {/* Notes Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredNotes.map(note => (
          <Card key={note.id} className="hover:shadow-md transition-shadow">
            <div className="space-y-3">
              {/* Note Header */}
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 text-lg mb-1">
                    {note.title}
                  </h3>
                  <div className="flex items-center space-x-2 text-sm text-gray-500">
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${
                        note.category === 'work'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-green-100 text-green-800'
                      }`}
                    >
                      {note.category}
                    </span>
                    <span>•</span>
                    <span>{note.updated_at}</span>
                  </div>
                </div>
                <div className="flex space-x-1">
                  <button className="p-1 hover:bg-gray-100 rounded text-gray-400 hover:text-gray-600">
                    <Edit className="w-4 h-4" />
                  </button>
                  <button className="p-1 hover:bg-gray-100 rounded text-gray-400 hover:text-red-600">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Note Content */}
              <p className="text-gray-600 text-sm line-clamp-3">
                {note.content}
              </p>

              {/* Tags */}
              <div className="flex flex-wrap gap-1">
                {note.tags.map(tag => (
                  <span
                    key={tag}
                    className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
                  >
                    <Tag className="w-3 h-3 mr-1" />
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Empty State */}
      {filteredNotes.length === 0 && (
        <Card className="text-center py-12">
          <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No notes found
          </h3>
          <p className="text-gray-600 mb-4">
            {searchTerm || selectedCategory !== 'all'
              ? 'Try adjusting your search or filters'
              : 'Create your first note to get started'}
          </p>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 flex items-center space-x-2 mx-auto">
            <Plus className="w-4 h-4" />
            <span>Create Note</span>
          </button>
        </Card>
      )}

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="text-center hover:shadow-md transition-shadow cursor-pointer">
          <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
            <Plus className="w-6 h-6 text-blue-600" />
          </div>
          <h3 className="font-medium text-gray-900 mb-1">Quick Note</h3>
          <p className="text-sm text-gray-600">Create a note in seconds</p>
        </Card>

        <Card className="text-center hover:shadow-md transition-shadow cursor-pointer">
          <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
            <Tag className="w-6 h-6 text-green-600" />
          </div>
          <h3 className="font-medium text-gray-900 mb-1">Organize</h3>
          <p className="text-sm text-gray-600">Tag and categorize notes</p>
        </Card>

        <Card className="text-center hover:shadow-md transition-shadow cursor-pointer">
          <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
            <Search className="w-6 h-6 text-purple-600" />
          </div>
          <h3 className="font-medium text-gray-900 mb-1">Search</h3>
          <p className="text-sm text-gray-600">Find notes quickly</p>
        </Card>
      </div>

      {/* Coming Soon Features */}
      <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
        <div className="text-center">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            📝 Advanced Notes Features Coming Soon!
          </h3>
          <p className="text-gray-600 mb-4">
            We're working on bringing you powerful note-taking capabilities
            including:
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
            <div className="flex items-center space-x-2">
              <FileText className="w-4 h-4 text-blue-600" />
              <span>Rich text editing</span>
            </div>
            <div className="flex items-center space-x-2">
              <Tag className="w-4 h-4 text-green-600" />
              <span>Smart organization</span>
            </div>
            <div className="flex items-center space-x-2">
              <Calendar className="w-4 h-4 text-purple-600" />
              <span>Note reminders</span>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default NotesPage;
