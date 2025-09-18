# Task 089: Todo Tab Implementation - Onboarding

## Context

You are given the following context:

- **Task**: Add a tab for the todo tool in the frontend application
- **Requirements**: The tab should be able to add a todo, remove a todo, and show a list of todos
- **Style**: It needs to be in the same style as the other tabs
- **Location**: Frontend React application in `src/apps/frontend/`

## Current System Analysis

### Tab System Architecture

The application uses a sophisticated tab system with the following components:

1. **TabNavigation Component** (`src/apps/frontend/src/components/oauth-settings/components/TabNavigation.tsx`)

   - Defines tabs with icons, names, and role-based permissions
   - Handles tab switching and permission filtering
   - Uses consistent styling with Tailwind CSS

2. **Main Page Structure** (`src/apps/frontend/src/components/oauth-settings/OAuthSettingsPage.tsx`)

   - Manages active tab state
   - Renders tab content based on active tab
   - Handles permission checks before rendering

3. **Tab Content Components**
   - Each tab has its own component (e.g., `IntegrationsTab.tsx`)
   - Consistent styling with white backgrounds, shadows, and proper spacing
   - Uses loading states and error handling

### Current Tab Structure

The existing tabs follow this pattern:

```typescript
const allTabs = [
  { id: "integrations", name: "Integrations", icon: "🔗", requiredRole: null },
  { id: "analytics", name: "Analytics", icon: "📊", requiredRole: "premium" },
  {
    id: "audit",
    name: "Audit Logs",
    icon: "📋",
    requiredRole: "administrator",
  },
  { id: "settings", name: "Settings", icon: "⚙️", requiredRole: null },
];
```

### Todo Tool Backend Implementation

The todo tool is already fully implemented in the backend:

**Location**: `src/personal_assistant/tools/todos/todo_tool.py`

**Available Operations**:

- `create_todo()` - Create new todos with title, description, due date, priority, category
- `get_todos()` - Retrieve todos with filtering options
- `update_todo()` - Update existing todos
- `complete_todo()` - Mark todos as completed
- `delete_todo()` - Remove todos
- `get_overdue_todos()` - Get overdue todos
- `get_todo_stats()` - Get statistics and behavioral patterns
- `trigger_segmentation()` - Break down complex tasks
- `get_analytics()` - Get behavioral analytics

**Database Model**: `src/personal_assistant/database/models/todos.py`

- User isolation (each user sees only their todos)
- Support for subtasks, priorities, categories, due dates
- Status tracking (pending, in_progress, completed, cancelled)

### Frontend Architecture

**Main Dashboard Pages**:

- `src/apps/frontend/src/pages/dashboard/DashboardHome.tsx` - Main dashboard
- `src/apps/frontend/src/pages/dashboard/ChatPage.tsx` - Chat interface
- `src/apps/frontend/src/pages/dashboard/NotesPage.tsx` - Notes interface

**Styling Patterns**:

- Uses Tailwind CSS for consistent styling
- Card-based layouts with shadows and rounded corners
- Blue accent colors (`bg-blue-500`, `text-blue-600`)
- Consistent button styles and hover effects
- Loading states with spinners
- Error handling with colored alerts

## Implementation Requirements

### 1. Create Todo Tab Component

**File**: `src/apps/frontend/src/components/todos/TodoTab.tsx`

**Features Required**:

- Display list of todos in a clean, organized layout
- Add new todo functionality with form
- Remove/delete todo functionality
- Mark todos as complete
- Filter todos by status, priority, category
- Show todo details (title, description, due date, priority, category)

**Styling Requirements**:

- Follow the same pattern as `IntegrationsTab.tsx`
- Use white background with shadow (`bg-white shadow`)
- Consistent button styling with hover effects
- Loading states and error handling
- Responsive design

### 2. Integrate with Existing Tab System

**Options for Integration**:

**Option A: Add to OAuth Settings Page**

- Add todo tab to `TabNavigation.tsx`
- Update `OAuthSettingsPage.tsx` to handle todo tab
- Pros: Quick implementation, follows existing pattern
- Cons: Todos don't logically belong in OAuth settings

**Option B: Create New Dashboard Page**

- Create `src/apps/frontend/src/pages/dashboard/TodosPage.tsx`
- Add navigation link in dashboard
- Pros: Better logical organization
- Cons: More complex implementation

**Option C: Add to Main Dashboard**

- Integrate todo functionality into `DashboardHome.tsx`
- Add as a section or modal
- Pros: Centralized location
- Cons: May clutter main dashboard

### 3. Backend Integration

**API Endpoints Needed**:

- The todo tool is already registered in the tool registry
- Need to create API endpoints to expose todo functionality
- Should follow existing API patterns in the backend

**Authentication**:

- Ensure user isolation (users only see their own todos)
- Use existing authentication system

### 4. State Management

**Options**:

- Create new Zustand store for todos (`src/apps/frontend/src/stores/todoStore.ts`)
- Follow patterns from existing stores like `oauthSettingsStore.ts`
- Handle loading states, error states, and data caching

## Technical Considerations

### 1. Data Flow

```
User Action → Frontend Component → API Call → Backend Tool → Database
```

### 2. Error Handling

- Network errors
- Validation errors
- Permission errors
- Database errors

### 3. Performance

- Lazy loading of todos
- Pagination for large todo lists
- Optimistic updates for better UX

### 4. Accessibility

- Keyboard navigation
- Screen reader support
- Focus management

## Implementation Steps

1. **Analyze existing tab patterns** ✅
2. **Create TodoTab component** with basic CRUD operations
3. **Create todo store** for state management
4. **Create API endpoints** for todo operations
5. **Integrate with tab system** (choose integration approach)
6. **Add styling** to match existing design
7. **Test functionality** and error handling
8. **Add loading states** and user feedback
9. **Implement filtering and sorting**
10. **Add accessibility features**

## Questions to Consider

1. **Where should the todo tab be integrated?**

   - OAuth Settings page (quick but not logical)
   - New Todos page (better organization)
   - Main dashboard (centralized)

2. **What level of functionality should be included?**

   - Basic CRUD operations (add, remove, list)
   - Advanced features (filtering, sorting, categories)
   - Analytics and insights

3. **Should it integrate with existing todo tool features?**
   - Missed counter functionality
   - Task segmentation
   - Behavioral analytics

## Success Criteria

- [ ] Todo tab displays list of todos
- [ ] Users can add new todos
- [ ] Users can remove todos
- [ ] Styling matches existing tabs
- [ ] Proper error handling
- [ ] Loading states
- [ ] User isolation (security)
- [ ] Responsive design
- [ ] Accessibility compliance

## Next Steps

1. Choose integration approach (recommend Option B: New Todos Page)
2. Create basic TodoTab component
3. Implement CRUD operations
4. Add styling to match existing design
5. Test and refine functionality
