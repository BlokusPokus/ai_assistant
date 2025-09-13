# Implementation Plan: Enhanced Todo Tool with Missed Counter & Auto-Segmentation

## 🎯 **Implementation Overview**

This document provides a detailed implementation plan for Task 068, building upon the existing todo list tool (Task 055) to add advanced behavioral tracking and intelligent task management features.

## 📋 **Implementation Phases**

### **Phase 1: Database & Missed Counter (Day 1)**

**Duration**: 1 day  
**Focus**: Foundation and missed counter logic

#### **Morning (4 hours)**

- [ ] **Database Schema Enhancement**

  - Create migration script for new fields
  - Add indexes for performance optimization
  - Test migration in development environment
  - Update SQLAlchemy models

- [ ] **Model Updates**
  - Enhance Todo model with new fields
  - Update Pydantic request/response models
  - Add validation rules for new fields
  - Test model serialization

#### **Afternoon (4 hours)**

- [ ] **Missed Counter Logic**

  - Implement `MissedCounterManager` class
  - Create background task for daily checks
  - Add threshold detection logic
  - Implement counter increment/reset methods

- [ ] **Testing & Validation**
  - Unit tests for missed counter logic
  - Integration tests with database
  - Performance testing for background tasks
  - Error handling validation

### **Phase 2: Auto-Segmentation Engine (Day 2)**

**Duration**: 1.5 days  
**Focus**: LLM integration and task breakdown

#### **Day 2 Morning (4 hours)**

- [ ] **Segmentation Engine Foundation**

  - Create `SegmentationEngine` class
  - Design LLM prompt templates
  - Implement response parsing logic
  - Add error handling for LLM failures

- [ ] **LLM Integration**
  - Integrate with Gemini API
  - Implement rate limiting and retry logic
  - Create prompt engineering for task breakdown
  - Test LLM response quality

#### **Day 2 Afternoon (4 hours)**

- [ ] **Subtask Management**

  - Implement subtask creation logic
  - Set up parent-child relationships
  - Add dependency management
  - Create subtask validation

- [ ] **Integration Testing**
  - Test complete segmentation workflow
  - Validate LLM integration
  - Test error scenarios
  - Performance optimization

#### **Day 3 Morning (4 hours)**

- [ ] **Advanced Segmentation Features**

  - Implement intelligent due date assignment
  - Add priority level distribution
  - Create segmentation suggestions
  - Add manual segmentation trigger

- [ ] **Testing & Refinement**
  - Comprehensive testing of segmentation
  - User feedback integration
  - Performance optimization
  - Documentation updates

### **Phase 3: Behavioral Analytics (Day 3)**

**Duration**: 1 day  
**Focus**: Analytics and insights generation

#### **Afternoon (4 hours)**

- [ ] **Analytics Engine**

  - Create `BehavioralAnalytics` class
  - Implement pattern analysis algorithms
  - Add completion rate calculations
  - Create trend analysis methods

- [ ] **Insights Generation**
  - Build recommendation engine
  - Create personalized suggestions
  - Implement data aggregation
  - Add export functionality

### **Phase 4: Frontend & Testing (Day 4)**

**Duration**: 1 day  
**Focus**: UI implementation and comprehensive testing

#### **Morning (4 hours)**

- [ ] **Frontend Components**

  - Create `MissedCounterIndicator` component
  - Build `SegmentationView` component
  - Implement `AnalyticsDashboard` component
  - Add `InsightsPanel` component

- [ ] **Enhanced Todo Components**
  - Update `TodoItem` with new features
  - Enhance `TodoForm` with analytics options
  - Add missed counter visualizations
  - Implement segmentation management UI

#### **Afternoon (4 hours)**

- [ ] **Integration & Testing**

  - Frontend-backend integration
  - End-to-end testing
  - User acceptance testing
  - Performance optimization

- [ ] **Documentation & Deployment**
  - Complete documentation
  - Prepare deployment scripts
  - Final testing and validation
  - Production readiness check

## 🏗️ **Detailed Implementation Steps**

### **Step 1: Database Schema Enhancement**

#### **Migration Script**

```python
# migrations/add_missed_counter_fields.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Add new fields to todos table
    op.add_column('todos', sa.Column('missed_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('todos', sa.Column('is_segmented', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('todos', sa.Column('parent_task_id', sa.Integer(), nullable=True))
    op.add_column('todos', sa.Column('segmentation_triggered_at', sa.DateTime(), nullable=True))
    op.add_column('todos', sa.Column('completion_patterns', postgresql.JSONB(), nullable=True))
    op.add_column('todos', sa.Column('user_insights', postgresql.JSONB(), nullable=True))
    op.add_column('todos', sa.Column('last_missed_at', sa.DateTime(), nullable=True))
    op.add_column('todos', sa.Column('segmentation_suggestions', postgresql.JSONB(), nullable=True))

    # Add foreign key constraint
    op.create_foreign_key('fk_todos_parent_task', 'todos', 'todos', ['parent_task_id'], ['id'])

    # Create indexes
    op.create_index('idx_todos_missed_count', 'todos', ['missed_count'])
    op.create_index('idx_todos_is_segmented', 'todos', ['is_segmented'])
    op.create_index('idx_todos_parent_task_id', 'todos', ['parent_task_id'])
    op.create_index('idx_todos_user_missed', 'todos', ['user_id', 'missed_count'])

def downgrade():
    # Remove indexes
    op.drop_index('idx_todos_user_missed', 'todos')
    op.drop_index('idx_todos_parent_task_id', 'todos')
    op.drop_index('idx_todos_is_segmented', 'todos')
    op.drop_index('idx_todos_missed_count', 'todos')

    # Remove foreign key constraint
    op.drop_constraint('fk_todos_parent_task', 'todos', type_='foreignkey')

    # Remove columns
    op.drop_column('todos', 'segmentation_suggestions')
    op.drop_column('todos', 'last_missed_at')
    op.drop_column('todos', 'user_insights')
    op.drop_column('todos', 'completion_patterns')
    op.drop_column('todos', 'segmentation_triggered_at')
    op.drop_column('todos', 'parent_task_id')
    op.drop_column('todos', 'is_segmented')
    op.drop_column('todos', 'missed_count')
```

#### **Model Updates**

```python
# src/personal_assistant/database/models/todos.py
from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import Base

class Todo(Base):
    __tablename__ = "todos"

    # Existing fields
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=True)
    done_date = Column(DateTime, nullable=True)
    priority = Column(String(20), default='medium')
    category = Column(String(50), nullable=True)
    status = Column(String(20), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # New missed counter fields
    missed_count = Column(Integer, default=0, nullable=False)
    last_missed_at = Column(DateTime, nullable=True)

    # Segmentation fields
    is_segmented = Column(Boolean, default=False, nullable=False)
    parent_task_id = Column(Integer, ForeignKey("todos.id"), nullable=True)
    segmentation_triggered_at = Column(DateTime, nullable=True)

    # Analytics fields
    completion_patterns = Column(JSON, nullable=True)
    user_insights = Column(JSON, nullable=True)
    segmentation_suggestions = Column(JSON, nullable=True)

    # Relationships
    parent_task = relationship("Todo", remote_side=[id], backref="subtasks")
    user = relationship("User", back_populates="todos")
```

### **Step 2: Missed Counter Implementation**

#### **MissedCounterManager Class**

```python
# src/personal_assistant/tools/todos/missed_counter.py
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from personal_assistant.database.models.todos import Todo
from personal_assistant.config.logging_config import get_logger

logger = get_logger("missed_counter")

class MissedCounterManager:
    """Manages missed task counting and threshold detection."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def check_overdue_tasks(self, user_id: int) -> List[Todo]:
        """Check for overdue tasks and increment missed counters."""
        try:
            # Get overdue tasks for user
            overdue_todos = await self.get_overdue_todos(user_id)

            for todo in overdue_todos:
                await self.increment_missed_count(todo)

                # Check if threshold reached
                if todo.missed_count >= 3:
                    await self.trigger_segmentation(todo)

            return overdue_todos

        except Exception as e:
            logger.error(f"Error checking overdue tasks: {e}")
            return []

    async def get_overdue_todos(self, user_id: int) -> List[Todo]:
        """Get todos that are overdue."""
        now = datetime.utcnow()
        query = select(Todo).where(
            and_(
                Todo.user_id == user_id,
                Todo.due_date < now,
                Todo.status.in_(['pending', 'in_progress'])
            )
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def increment_missed_count(self, todo: Todo):
        """Increment missed count and update last_missed_at."""
        try:
            todo.missed_count += 1
            todo.last_missed_at = datetime.utcnow()

            # Update completion patterns
            await self.update_completion_patterns(todo)

            await self.db.commit()
            logger.info(f"Incremented missed count for todo {todo.id}: {todo.missed_count}")

        except Exception as e:
            logger.error(f"Error incrementing missed count: {e}")
            await self.db.rollback()

    async def trigger_segmentation(self, todo: Todo):
        """Trigger automatic segmentation for tasks with 3+ missed attempts."""
        try:
            # Import here to avoid circular imports
            from .segmentation_engine import SegmentationEngine

            segmentation_engine = SegmentationEngine(self.db)
            await segmentation_engine.segment_task(todo)

            logger.info(f"Triggered segmentation for todo {todo.id}")

        except Exception as e:
            logger.error(f"Error triggering segmentation: {e}")

    async def update_completion_patterns(self, todo: Todo):
        """Update completion patterns for analytics."""
        if not todo.completion_patterns:
            todo.completion_patterns = {}

        patterns = todo.completion_patterns
        patterns['missed_dates'] = patterns.get('missed_dates', [])
        patterns['missed_dates'].append(datetime.utcnow().isoformat())
        patterns['total_missed'] = len(patterns['missed_dates'])

        todo.completion_patterns = patterns
```

### **Step 3: Auto-Segmentation Engine**

#### **SegmentationEngine Class**

```python
# src/personal_assistant/tools/todos/segmentation_engine.py
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from personal_assistant.llm.gemini_client import GeminiClient
from personal_assistant.database.models.todos import Todo
from personal_assistant.config.logging_config import get_logger

logger = get_logger("segmentation_engine")

class SegmentationEngine:
    """Intelligent task segmentation using LLM."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.llm_client = GeminiClient()

    async def segment_task(self, todo: Todo) -> List[Todo]:
        """Break down a complex task into manageable subtasks."""
        try:
            # Create segmentation prompt
            prompt = self.create_segmentation_prompt(todo)

            # Get LLM response
            llm_response = await self.llm_client.generate_content(prompt)

            # Parse response and create subtasks
            subtasks_data = self.parse_llm_response(llm_response)
            subtasks = await self.create_subtasks(todo, subtasks_data)

            # Mark original task as segmented
            todo.is_segmented = True
            todo.segmentation_triggered_at = datetime.utcnow()
            await self.db.commit()

            logger.info(f"Successfully segmented todo {todo.id} into {len(subtasks)} subtasks")
            return subtasks

        except Exception as e:
            logger.error(f"Error segmenting task {todo.id}: {e}")
            return []

    def create_segmentation_prompt(self, todo: Todo) -> str:
        """Create a prompt for LLM to segment the task."""
        return f"""
        You are an expert productivity coach specializing in helping people with ADHD break down overwhelming tasks.

        Task to segment:
        Title: {todo.title}
        Description: {todo.description or 'No description provided'}
        Due Date: {todo.due_date.strftime('%Y-%m-%d') if todo.due_date else 'No due date'}
        Priority: {todo.priority}
        Category: {todo.category or 'General'}

        Please break this task down into 3-5 manageable subtasks that are:
        1. Specific and actionable
        2. Small enough to complete in 1-2 hours each
        3. Ordered logically (some may depend on others)
        4. Clear and easy to understand

        Format your response as a JSON array with this structure:
        [
            {{
                "title": "Subtask title",
                "description": "Detailed description of what needs to be done",
                "estimated_duration": "1-2 hours",
                "priority": "high/medium/low",
                "order": 1
            }}
        ]

        Focus on making each subtask feel achievable and motivating for someone with ADHD.
        """

    def parse_llm_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response into subtask data."""
        try:
            import json
            # Extract JSON from response
            start = response.find('[')
            end = response.rfind(']') + 1
            json_str = response[start:end]
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return []

    async def create_subtasks(self, parent_todo: Todo, subtasks_data: List[Dict[str, Any]]) -> List[Todo]:
        """Create subtasks from parsed data."""
        subtasks = []

        for i, subtask_data in enumerate(subtasks_data):
            # Calculate due date for subtask
            due_date = self.calculate_subtask_due_date(parent_todo, i, len(subtasks_data))

            subtask = Todo(
                user_id=parent_todo.user_id,
                title=subtask_data.get('title', f'Subtask {i+1}'),
                description=subtask_data.get('description', ''),
                due_date=due_date,
                priority=subtask_data.get('priority', 'medium'),
                category=parent_todo.category,
                status='pending',
                parent_task_id=parent_todo.id,
                created_at=datetime.utcnow()
            )

            self.db.add(subtask)
            subtasks.append(subtask)

        await self.db.commit()
        return subtasks

    def calculate_subtask_due_date(self, parent_todo: Todo, subtask_index: int, total_subtasks: int) -> datetime:
        """Calculate appropriate due date for subtask."""
        if not parent_todo.due_date:
            return datetime.utcnow() + timedelta(days=1)

        # Distribute subtasks evenly across remaining time
        time_remaining = parent_todo.due_date - datetime.utcnow()
        if time_remaining.total_seconds() <= 0:
            return datetime.utcnow() + timedelta(hours=1)

        # Calculate time per subtask
        time_per_subtask = time_remaining / total_subtasks

        # Set due date for this subtask
        return datetime.utcnow() + (time_per_subtask * (subtask_index + 1))
```

### **Step 4: Behavioral Analytics**

#### **BehavioralAnalytics Class**

```python
# src/personal_assistant/tools/todos/behavioral_analytics.py
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from personal_assistant.database.models.todos import Todo
from personal_assistant.config.logging_config import get_logger

logger = get_logger("behavioral_analytics")

class BehavioralAnalytics:
    """Analyze user behavior patterns and generate insights."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def analyze_completion_patterns(self, user_id: int) -> Dict[str, Any]:
        """Analyze user's task completion patterns."""
        try:
            # Get user's todos
            todos = await self.get_user_todos(user_id)

            patterns = {
                'completion_rate': self.calculate_completion_rate(todos),
                'missed_patterns': await self.analyze_missed_patterns(todos),
                'optimal_timing': await self.find_optimal_timing(todos),
                'category_performance': await self.analyze_category_performance(todos),
                'segmentation_effectiveness': await self.analyze_segmentation_effectiveness(todos),
                'productivity_trends': await self.analyze_productivity_trends(todos)
            }

            return patterns

        except Exception as e:
            logger.error(f"Error analyzing completion patterns: {e}")
            return {}

    async def get_user_todos(self, user_id: int) -> List[Todo]:
        """Get all todos for a user."""
        query = select(Todo).where(Todo.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    def calculate_completion_rate(self, todos: List[Todo]) -> float:
        """Calculate overall completion rate."""
        if not todos:
            return 0.0

        completed = len([t for t in todos if t.status == 'completed'])
        return (completed / len(todos)) * 100

    async def analyze_missed_patterns(self, todos: List[Todo]) -> Dict[str, Any]:
        """Analyze patterns in missed tasks."""
        missed_todos = [t for t in todos if t.missed_count > 0]

        if not missed_todos:
            return {'total_missed': 0, 'patterns': []}

        patterns = {
            'total_missed': len(missed_todos),
            'average_missed_count': sum(t.missed_count for t in missed_todos) / len(missed_todos),
            'categories_with_misses': list(set(t.category for t in missed_todos if t.category)),
            'high_miss_tasks': [t.title for t in missed_todos if t.missed_count >= 3]
        }

        return patterns

    async def find_optimal_timing(self, todos: List[Todo]) -> Dict[str, Any]:
        """Find optimal times for task completion."""
        completed_todos = [t for t in todos if t.status == 'completed' and t.done_date]

        if not completed_todos:
            return {'optimal_hours': [], 'optimal_days': []}

        # Analyze completion times
        completion_hours = [t.done_date.hour for t in completed_todos]
        completion_days = [t.done_date.weekday() for t in completed_todos]

        # Find most common completion times
        hour_counts = {}
        for hour in completion_hours:
            hour_counts[hour] = hour_counts.get(hour, 0) + 1

        day_counts = {}
        for day in completion_days:
            day_counts[day] = day_counts.get(day, 0) + 1

        optimal_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        optimal_days = sorted(day_counts.items(), key=lambda x: x[1], reverse=True)[:3]

        return {
            'optimal_hours': [h[0] for h in optimal_hours],
            'optimal_days': [d[0] for d in optimal_days],
            'completion_distribution': {
                'hours': hour_counts,
                'days': day_counts
            }
        }

    async def generate_insights(self, user_id: int) -> List[Dict[str, Any]]:
        """Generate personalized insights and recommendations."""
        patterns = await self.analyze_completion_patterns(user_id)
        insights = []

        # Completion rate insights
        if patterns.get('completion_rate', 0) < 50:
            insights.append({
                'type': 'completion_rate',
                'title': 'Low Completion Rate',
                'message': f"Your completion rate is {patterns['completion_rate']:.1f}%. Consider breaking down larger tasks into smaller, more manageable pieces.",
                'action': 'Try using the auto-segmentation feature for complex tasks.',
                'priority': 'high'
            })

        # Missed pattern insights
        missed_patterns = patterns.get('missed_patterns', {})
        if missed_patterns.get('total_missed', 0) > 5:
            insights.append({
                'type': 'missed_patterns',
                'title': 'Frequent Missed Deadlines',
                'message': f"You have {missed_patterns['total_missed']} tasks with missed deadlines. Consider setting more realistic due dates.",
                'action': 'Review your task planning and consider adding buffer time.',
                'priority': 'medium'
            })

        # Timing insights
        optimal_timing = patterns.get('optimal_timing', {})
        if optimal_timing.get('optimal_hours'):
            best_hours = optimal_timing['optimal_hours'][:2]
            insights.append({
                'type': 'timing',
                'title': 'Optimal Work Times',
                'message': f"You tend to complete tasks most successfully around {best_hours[0]}:00 and {best_hours[1]}:00.",
                'action': 'Schedule your most important tasks during these peak hours.',
                'priority': 'low'
            })

        return insights
```

### **Step 5: API Endpoints**

#### **Enhanced Todo Endpoints**

```python
# src/apps/fastapi_app/routes/todos.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from apps.fastapi_app.middleware.auth import get_current_user
from personal_assistant.database.session import AsyncSessionLocal
from personal_assistant.tools.todos.missed_counter import MissedCounterManager
from personal_assistant.tools.todos.segmentation_engine import SegmentationEngine
from personal_assistant.tools.todos.behavioral_analytics import BehavioralAnalytics

router = APIRouter(prefix="/api/v1/todos", tags=["todos"])

@router.get("/missed")
async def get_missed_todos(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(AsyncSessionLocal)
):
    """Get todos with missed attempts."""
    try:
        missed_manager = MissedCounterManager(db)
        overdue_todos = await missed_manager.get_overdue_todos(current_user.id)

        return {
            "overdue_todos": [
                {
                    "id": todo.id,
                    "title": todo.title,
                    "missed_count": todo.missed_count,
                    "last_missed_at": todo.last_missed_at,
                    "due_date": todo.due_date
                }
                for todo in overdue_todos
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{todo_id}/segment")
async def trigger_segmentation(
    todo_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(AsyncSessionLocal)
):
    """Manually trigger segmentation for a task."""
    try:
        # Get the todo
        todo = await db.get(Todo, todo_id)
        if not todo or todo.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Todo not found")

        # Trigger segmentation
        segmentation_engine = SegmentationEngine(db)
        subtasks = await segmentation_engine.segment_task(todo)

        return {
            "message": "Task segmented successfully",
            "subtasks_created": len(subtasks),
            "subtasks": [
                {
                    "id": subtask.id,
                    "title": subtask.title,
                    "description": subtask.description,
                    "due_date": subtask.due_date
                }
                for subtask in subtasks
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics")
async def get_analytics(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(AsyncSessionLocal)
):
    """Get behavioral analytics for the user."""
    try:
        analytics = BehavioralAnalytics(db)
        patterns = await analytics.analyze_completion_patterns(current_user.id)
        insights = await analytics.generate_insights(current_user.id)

        return {
            "patterns": patterns,
            "insights": insights,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### **Step 6: Frontend Components**

#### **MissedCounterIndicator Component**

```typescript
// src/apps/frontend/src/components/todos/MissedCounterIndicator.tsx
import React from "react";
import { AlertTriangle, Clock } from "lucide-react";

interface MissedCounterIndicatorProps {
  missedCount: number;
  threshold: number;
  onReset?: () => void;
}

export const MissedCounterIndicator: React.FC<MissedCounterIndicatorProps> = ({
  missedCount,
  threshold,
  onReset,
}) => {
  const isApproachingThreshold = missedCount >= threshold - 1;
  const isAtThreshold = missedCount >= threshold;

  const getIndicatorColor = () => {
    if (isAtThreshold) return "text-red-600 bg-red-100";
    if (isApproachingThreshold) return "text-yellow-600 bg-yellow-100";
    return "text-gray-600 bg-gray-100";
  };

  const getIcon = () => {
    if (isAtThreshold) return <AlertTriangle className="w-4 h-4" />;
    return <Clock className="w-4 h-4" />;
  };

  return (
    <div
      className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getIndicatorColor()}`}
    >
      {getIcon()}
      <span className="ml-1">{missedCount} missed</span>
      {isAtThreshold && (
        <button
          onClick={onReset}
          className="ml-2 text-xs underline hover:no-underline"
        >
          Reset
        </button>
      )}
    </div>
  );
};
```

#### **AnalyticsDashboard Component**

```typescript
// src/apps/frontend/src/components/todos/AnalyticsDashboard.tsx
import React, { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface AnalyticsData {
  patterns: {
    completion_rate: number;
    missed_patterns: {
      total_missed: number;
      average_missed_count: number;
    };
    optimal_timing: {
      optimal_hours: number[];
      optimal_days: number[];
    };
  };
  insights: Array<{
    type: string;
    title: string;
    message: string;
    action: string;
    priority: string;
  }>;
}

export const AnalyticsDashboard: React.FC = () => {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const response = await fetch("/api/v1/todos/analytics");
      const data = await response.json();
      setAnalytics(data);
    } catch (error) {
      console.error("Error fetching analytics:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="animate-pulse">Loading analytics...</div>;
  }

  if (!analytics) {
    return <div>No analytics data available</div>;
  }

  return (
    <div className="space-y-6">
      {/* Completion Rate */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Completion Rate</h3>
        <div className="text-3xl font-bold text-blue-600">
          {analytics.patterns.completion_rate.toFixed(1)}%
        </div>
        <div className="text-sm text-gray-600 mt-2">
          Tasks completed successfully
        </div>
      </div>

      {/* Missed Tasks */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Missed Tasks</h3>
        <div className="text-2xl font-bold text-red-600">
          {analytics.patterns.missed_patterns.total_missed}
        </div>
        <div className="text-sm text-gray-600 mt-2">
          Tasks with missed deadlines
        </div>
      </div>

      {/* Insights */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">
          Insights & Recommendations
        </h3>
        <div className="space-y-4">
          {analytics.insights.map((insight, index) => (
            <div
              key={index}
              className={`p-4 rounded-lg border-l-4 ${
                insight.priority === "high"
                  ? "border-red-500 bg-red-50"
                  : insight.priority === "medium"
                  ? "border-yellow-500 bg-yellow-50"
                  : "border-blue-500 bg-blue-50"
              }`}
            >
              <h4 className="font-semibold text-gray-900">{insight.title}</h4>
              <p className="text-gray-700 mt-1">{insight.message}</p>
              <p className="text-sm text-gray-600 mt-2">
                <strong>Action:</strong> {insight.action}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
```

## 🧪 **Testing Strategy**

### **Unit Tests**

```python
# tests/unit/test_missed_counter.py
import pytest
from datetime import datetime, timedelta
from personal_assistant.tools.todos.missed_counter import MissedCounterManager

@pytest.mark.asyncio
async def test_increment_missed_count():
    """Test missed counter increment functionality."""
    # Setup test data
    todo = Todo(
        id=1,
        user_id=1,
        title="Test Task",
        due_date=datetime.utcnow() - timedelta(days=1),
        status="pending",
        missed_count=0
    )

    # Test increment
    manager = MissedCounterManager(mock_db_session)
    await manager.increment_missed_count(todo)

    assert todo.missed_count == 1
    assert todo.last_missed_at is not None

@pytest.mark.asyncio
async def test_threshold_detection():
    """Test threshold detection for segmentation."""
    todo = Todo(
        id=1,
        user_id=1,
        title="Test Task",
        missed_count=3
    )

    manager = MissedCounterManager(mock_db_session)
    # Mock segmentation trigger
    with patch.object(manager, 'trigger_segmentation') as mock_trigger:
        await manager.check_overdue_tasks(1)
        mock_trigger.assert_called_once_with(todo)
```

### **Integration Tests**

```python
# tests/integration/test_todo_analytics.py
import pytest
from fastapi.testclient import TestClient
from apps.fastapi_app.main import app

client = TestClient(app)

def test_get_analytics_endpoint():
    """Test analytics endpoint integration."""
    response = client.get("/api/v1/todos/analytics")
    assert response.status_code == 200

    data = response.json()
    assert "patterns" in data
    assert "insights" in data
    assert "generated_at" in data

def test_segmentation_endpoint():
    """Test segmentation endpoint integration."""
    # Create a test todo
    todo_data = {
        "title": "Complex Task",
        "description": "This is a complex task that needs segmentation",
        "due_date": "2024-12-31T23:59:59"
    }

    create_response = client.post("/api/v1/todos", json=todo_data)
    todo_id = create_response.json()["id"]

    # Trigger segmentation
    response = client.post(f"/api/v1/todos/{todo_id}/segment")
    assert response.status_code == 200

    data = response.json()
    assert "subtasks_created" in data
    assert data["subtasks_created"] > 0
```

## 📊 **Performance Considerations**

### **Database Optimization**

- Indexes on frequently queried fields
- JSONB fields for flexible analytics data
- Background processing for heavy analytics
- Caching for frequently accessed data

### **LLM Integration**

- Rate limiting to prevent API overuse
- Caching for similar segmentation requests
- Fallback strategies for LLM failures
- Batch processing for multiple tasks

### **Frontend Performance**

- Lazy loading for analytics components
- Virtual scrolling for large todo lists
- Debounced search and filtering
- Optimistic updates for better UX

## 🚀 **Deployment Checklist**

### **Pre-Deployment**

- [ ] All tests passing (95%+ coverage)
- [ ] Database migration tested in staging
- [ ] Performance benchmarks met
- [ ] Security review completed
- [ ] Documentation updated

### **Deployment Steps**

- [ ] Run database migration
- [ ] Deploy backend changes
- [ ] Deploy frontend changes
- [ ] Verify all endpoints working
- [ ] Monitor system performance

### **Post-Deployment**

- [ ] Monitor error rates
- [ ] Check analytics generation
- [ ] Verify user feedback
- [ ] Performance monitoring
- [ ] Bug fixes and optimizations

---

**Implementation Status**: 🚀 **READY TO START**  
**Estimated Completion**: 4 days  
**Next Review**: After Phase 1 completion  
**Assigned To**: [Developer Name]  
**Reviewer**: [Reviewer Name]
