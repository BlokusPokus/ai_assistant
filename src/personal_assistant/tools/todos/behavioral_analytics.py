"""
Behavioral Analytics Engine for Enhanced Todo Tool.

This module analyzes user behavior patterns and generates insights to help users
improve their productivity and task completion rates.
"""

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
        """
        Analyze user's task completion patterns.
        
        Args:
            user_id: ID of the user to analyze
            
        Returns:
            Dictionary with completion pattern analysis
        """
        try:
            # Get user's todos
            todos = await self.get_user_todos(user_id)
            
            patterns = {
                'completion_rate': self.calculate_completion_rate(todos),
                'missed_patterns': await self.analyze_missed_patterns(todos),
                'optimal_timing': await self.find_optimal_timing(todos),
                'category_performance': await self.analyze_category_performance(todos),
                'segmentation_effectiveness': await self.analyze_segmentation_effectiveness(todos),
                'productivity_trends': await self.analyze_productivity_trends(todos),
                'total_todos': len(todos),
                'analysis_date': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Completed behavioral analysis for user {user_id}")
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing completion patterns for user {user_id}: {e}")
            return {}
    
    async def get_user_todos(self, user_id: int) -> List[Todo]:
        """
        Get all todos for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of todos
        """
        try:
            query = select(Todo).where(Todo.user_id == user_id)
            result = await self.db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting todos for user {user_id}: {e}")
            return []
    
    def calculate_completion_rate(self, todos: List[Todo]) -> float:
        """
        Calculate overall completion rate.
        
        Args:
            todos: List of todos
            
        Returns:
            Completion rate as percentage
        """
        if not todos:
            return 0.0
        
        completed = len([t for t in todos if t.status == 'completed'])
        return (completed / len(todos)) * 100
    
    async def analyze_missed_patterns(self, todos: List[Todo]) -> Dict[str, Any]:
        """
        Analyze patterns in missed tasks.
        
        Args:
            todos: List of todos
            
        Returns:
            Dictionary with missed pattern analysis
        """
        try:
            missed_todos = [t for t in todos if t.missed_count > 0]
            
            if not missed_todos:
                return {
                    'total_missed': 0,
                    'average_missed_count': 0,
                    'categories_with_misses': [],
                    'high_miss_tasks': [],
                    'missed_trend': 'stable'
                }
            
            # Analyze categories with misses
            categories_with_misses = list(set(t.category for t in missed_todos if t.category))
            
            # Find high miss tasks
            high_miss_tasks = [t.title for t in missed_todos if t.missed_count >= 3]
            
            # Calculate average missed count
            average_missed_count = sum(t.missed_count for t in missed_todos) / len(missed_todos)
            
            # Analyze missed trend (simplified)
            recent_misses = [t for t in missed_todos if t.last_missed_at and 
                           t.last_missed_at > datetime.utcnow() - timedelta(days=7)]
            missed_trend = 'increasing' if len(recent_misses) > len(missed_todos) / 2 else 'stable'
            
            return {
                'total_missed': len(missed_todos),
                'average_missed_count': round(average_missed_count, 2),
                'categories_with_misses': categories_with_misses,
                'high_miss_tasks': high_miss_tasks,
                'missed_trend': missed_trend,
                'recent_misses_count': len(recent_misses)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing missed patterns: {e}")
            return {}
    
    async def find_optimal_timing(self, todos: List[Todo]) -> Dict[str, Any]:
        """
        Find optimal times for task completion.
        
        Args:
            todos: List of todos
            
        Returns:
            Dictionary with optimal timing analysis
        """
        try:
            completed_todos = [t for t in todos if t.status == 'completed' and t.done_date]
            
            if not completed_todos:
                return {
                    'optimal_hours': [],
                    'optimal_days': [],
                    'completion_distribution': {'hours': {}, 'days': {}}
                }
            
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
            
            # Get top 3 optimal hours and days
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
            
        except Exception as e:
            logger.error(f"Error finding optimal timing: {e}")
            return {}
    
    async def analyze_category_performance(self, todos: List[Todo]) -> Dict[str, Dict[str, Any]]:
        """
        Analyze performance by category.
        
        Args:
            todos: List of todos
            
        Returns:
            Dictionary with category performance analysis
        """
        try:
            categories = {}
            
            for todo in todos:
                category = todo.category or 'Uncategorized'
                
                if category not in categories:
                    categories[category] = {
                        'total': 0,
                        'completed': 0,
                        'missed': 0,
                        'missed_count': 0
                    }
                
                categories[category]['total'] += 1
                
                if todo.status == 'completed':
                    categories[category]['completed'] += 1
                
                if todo.missed_count > 0:
                    categories[category]['missed'] += 1
                    categories[category]['missed_count'] += todo.missed_count
            
            # Calculate performance metrics for each category
            for category, data in categories.items():
                if data['total'] > 0:
                    data['completion_rate'] = round((data['completed'] / data['total']) * 100, 2)
                    data['missed_rate'] = round((data['missed'] / data['total']) * 100, 2)
                    data['average_missed_count'] = round(data['missed_count'] / max(data['missed'], 1), 2)
                else:
                    data['completion_rate'] = 0
                    data['missed_rate'] = 0
                    data['average_missed_count'] = 0
            
            return categories
            
        except Exception as e:
            logger.error(f"Error analyzing category performance: {e}")
            return {}
    
    async def analyze_segmentation_effectiveness(self, todos: List[Todo]) -> Dict[str, Any]:
        """
        Analyze effectiveness of task segmentation.
        
        Args:
            todos: List of todos
            
        Returns:
            Dictionary with segmentation effectiveness analysis
        """
        try:
            segmented_todos = [t for t in todos if t.is_segmented]
            subtasks = [t for t in todos if t.parent_task_id is not None]
            
            if not segmented_todos:
                return {
                    'segmented_todos_count': 0,
                    'subtasks_count': 0,
                    'subtask_completion_rate': 0,
                    'segmentation_effectiveness': 'no_data'
                }
            
            # Calculate subtask completion rate
            completed_subtasks = len([t for t in subtasks if t.status == 'completed'])
            subtask_completion_rate = (completed_subtasks / len(subtasks)) * 100 if subtasks else 0
            
            # Determine effectiveness
            if subtask_completion_rate >= 80:
                effectiveness = 'high'
            elif subtask_completion_rate >= 60:
                effectiveness = 'medium'
            else:
                effectiveness = 'low'
            
            return {
                'segmented_todos_count': len(segmented_todos),
                'subtasks_count': len(subtasks),
                'subtask_completion_rate': round(subtask_completion_rate, 2),
                'segmentation_effectiveness': effectiveness
            }
            
        except Exception as e:
            logger.error(f"Error analyzing segmentation effectiveness: {e}")
            return {}
    
    async def analyze_productivity_trends(self, todos: List[Todo]) -> Dict[str, Any]:
        """
        Analyze productivity trends over time.
        
        Args:
            todos: List of todos
            
        Returns:
            Dictionary with productivity trend analysis
        """
        try:
            # Group todos by week
            weekly_data = {}
            
            for todo in todos:
                if todo.created_at:
                    week_start = todo.created_at - timedelta(days=todo.created_at.weekday())
                    week_key = week_start.strftime('%Y-%W')
                    
                    if week_key not in weekly_data:
                        weekly_data[week_key] = {
                            'created': 0,
                            'completed': 0,
                            'missed': 0
                        }
                    
                    weekly_data[week_key]['created'] += 1
                    
                    if todo.status == 'completed':
                        weekly_data[week_key]['completed'] += 1
                    
                    if todo.missed_count > 0:
                        weekly_data[week_key]['missed'] += 1
            
            # Calculate trends
            weeks = sorted(weekly_data.keys())
            if len(weeks) < 2:
                return {'trend': 'insufficient_data', 'weekly_data': weekly_data}
            
            recent_weeks = weeks[-2:]
            recent_completion_rate = sum(weekly_data[w]['completed'] for w in recent_weeks) / sum(weekly_data[w]['created'] for w in recent_weeks) * 100
            older_completion_rate = sum(weekly_data[w]['completed'] for w in weeks[:-2]) / sum(weekly_data[w]['created'] for w in weeks[:-2]) * 100 if len(weeks) > 2 else recent_completion_rate
            
            if recent_completion_rate > older_completion_rate + 5:
                trend = 'improving'
            elif recent_completion_rate < older_completion_rate - 5:
                trend = 'declining'
            else:
                trend = 'stable'
            
            return {
                'trend': trend,
                'recent_completion_rate': round(recent_completion_rate, 2),
                'weekly_data': weekly_data
            }
            
        except Exception as e:
            logger.error(f"Error analyzing productivity trends: {e}")
            return {}
    
    async def generate_insights(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Generate personalized insights and recommendations.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of insight dictionaries
        """
        try:
            patterns = await self.analyze_completion_patterns(user_id)
            insights = []
            
            # Completion rate insights
            completion_rate = patterns.get('completion_rate', 0)
            if completion_rate < 50:
                insights.append({
                    'type': 'completion_rate',
                    'title': 'Low Completion Rate',
                    'message': f"Your completion rate is {completion_rate:.1f}%. Consider breaking down larger tasks into smaller, more manageable pieces.",
                    'action': 'Try using the auto-segmentation feature for complex tasks.',
                    'priority': 'high'
                })
            elif completion_rate > 80:
                insights.append({
                    'type': 'completion_rate',
                    'title': 'Excellent Completion Rate',
                    'message': f"Great job! Your completion rate is {completion_rate:.1f}%. Keep up the good work!",
                    'action': 'Consider taking on more challenging tasks or helping others improve their productivity.',
                    'priority': 'low'
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
            
            # Category performance insights
            category_performance = patterns.get('category_performance', {})
            worst_category = None
            worst_rate = 100
            
            for category, data in category_performance.items():
                if data['completion_rate'] < worst_rate and data['total'] >= 3:
                    worst_rate = data['completion_rate']
                    worst_category = category
            
            if worst_category and worst_rate < 40:
                insights.append({
                    'type': 'category_performance',
                    'title': f'Challenging Category: {worst_category}',
                    'message': f"Your completion rate for {worst_category} tasks is only {worst_rate:.1f}%. This category might need special attention.",
                    'action': f'Consider breaking down {worst_category} tasks into smaller steps or seeking help.',
                    'priority': 'medium'
                })
            
            # Segmentation effectiveness insights
            segmentation_effectiveness = patterns.get('segmentation_effectiveness', {})
            if segmentation_effectiveness.get('segmentation_effectiveness') == 'high':
                insights.append({
                    'type': 'segmentation',
                    'title': 'Segmentation Working Well',
                    'message': f"Task segmentation is helping! Your subtask completion rate is {segmentation_effectiveness.get('subtask_completion_rate', 0):.1f}%.",
                    'action': 'Continue using auto-segmentation for complex tasks.',
                    'priority': 'low'
                })
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights for user {user_id}: {e}")
            return []
