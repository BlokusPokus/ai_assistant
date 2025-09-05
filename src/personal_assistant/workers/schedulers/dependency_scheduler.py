"""
Dependency Scheduler for Complex Task Patterns

Handles task dependencies, conditional execution, and
complex scheduling patterns beyond simple cron schedules.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class DependencyType(Enum):
    """Types of task dependencies."""

    REQUIRES = "requires"  # Task must complete successfully
    REQUIRES_ANY = "requires_any"  # At least one dependency must complete
    OPTIONAL = "optional"  # Task can run even if dependency fails
    CONDITIONAL = "conditional"  # Task runs based on condition


@dataclass
class TaskDependency:
    """Represents a task dependency relationship."""

    task_id: str
    depends_on: List[str] | None
    dependency_type: DependencyType = DependencyType.REQUIRES
    condition: Optional[str] = None
    timeout: Optional[timedelta] = None
    retry_on_failure: bool = False
    max_retries: int = 3


@dataclass
class TaskExecution:
    """Represents a task execution instance."""

    task_id: str
    task_name: str
    status: TaskStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error: Optional[str] = None
    retry_count: int = 0
    dependencies_met: bool = False


class DependencyScheduler:
    """Manages complex task dependencies and execution order."""

    def __init__(self):
        self.dependencies: Dict[str, TaskDependency] = {}
        self.execution_graph: Dict[str, Set[str]] = {}
        self.task_executions: Dict[str, TaskExecution] = {}
        self.execution_history: List[TaskExecution] = []
        self.logger = logging.getLogger(__name__)

    def add_dependency(self, dependency: TaskDependency) -> bool:
        """Add a task dependency."""
        try:
            # Validate dependency
            if not dependency.task_id or not dependency.task_id.strip():
                self.logger.error("Invalid dependency: task_id cannot be empty")
                return False

            # Allow empty depends_on for tasks with no dependencies
            if dependency.depends_on is None:
                dependency.depends_on = []

            # Check for circular dependencies
            if self._would_create_circle(dependency):
                self.logger.error(
                    f"Circular dependency detected for task: {dependency.task_id}"
                )
                return False

            # Add dependency
            self.dependencies[dependency.task_id] = dependency

            # Add dependent tasks to dependencies if they don't exist
            for dep_task_id in dependency.depends_on:
                if dep_task_id not in self.dependencies:
                    # Create a dependency entry for the dependent task
                    dep_dependency = TaskDependency(
                        task_id=dep_task_id, depends_on=[]  # No dependencies
                    )
                    self.dependencies[dep_task_id] = dep_dependency
                    self.logger.debug(f"Auto-added dependency for task: {dep_task_id}")

            self.logger.info(f"Added dependency for task {dependency.task_id}")

            # Update execution graph
            self._update_execution_graph()

            return True

        except Exception as e:
            self.logger.error(f"Error adding dependency: {e}")
            return False

    def remove_dependency(self, task_id: str) -> bool:
        """Remove a task dependency."""
        try:
            if task_id in self.dependencies:
                del self.dependencies[task_id]
                self._update_execution_graph()
                self.logger.info(f"Removed dependency for task: {task_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error removing dependency: {e}")
            return False

    def get_execution_order(self) -> List[str]:
        """Get the optimal execution order for dependent tasks using topological sorting."""
        try:
            if not self.execution_graph:
                return []

            # Kahn's algorithm for topological sorting
            in_degree = {task: 0 for task in self.execution_graph}
            for task, deps in self.execution_graph.items():
                for dep in deps:
                    if dep in in_degree:
                        in_degree[dep] += 1

            # Find tasks with no incoming edges
            queue = [task for task, degree in in_degree.items() if degree == 0]
            execution_order = []

            while queue:
                current_task = queue.pop(0)
                execution_order.append(current_task)

                # Reduce in-degree for dependent tasks
                if current_task in self.execution_graph:
                    for dependent_task in self.execution_graph[current_task]:
                        if dependent_task in in_degree:
                            in_degree[dependent_task] -= 1
                            if in_degree[dependent_task] == 0:
                                queue.append(dependent_task)

            # Check for cycles
            if len(execution_order) != len(self.execution_graph):
                self.logger.warning("Circular dependency detected in execution graph")
                return []

            return execution_order

        except Exception as e:
            self.logger.error(f"Error calculating execution order: {e}")
            return []

    def check_dependencies_met(self, task_id: str) -> bool:
        """Check if all dependencies for a task are satisfied."""
        try:
            if task_id not in self.dependencies:
                return True  # No dependencies

            dependency = self.dependencies[task_id]

            if not dependency.depends_on:
                return True

            # Check each dependency
            for dep_task_id in dependency.depends_on:
                if not self._is_dependency_satisfied(
                    dep_task_id, dependency.dependency_type
                ):
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Error checking dependencies for {task_id}: {e}")
            return False

    def can_execute_task(self, task_id: str) -> bool:
        """Check if a task can be executed based on dependencies and conditions."""
        try:
            # Check if dependencies are met
            if not self.check_dependencies_met(task_id):
                return False

            # Check if task is already running or completed
            if task_id in self.task_executions:
                execution = self.task_executions[task_id]
                if execution.status in [TaskStatus.RUNNING, TaskStatus.COMPLETED]:
                    return False

            # Check conditional execution
            if task_id in self.dependencies:
                dependency = self.dependencies[task_id]
                if dependency.condition and not self._evaluate_condition(
                    dependency.condition
                ):
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Error checking if task can execute {task_id}: {e}")
            return False

    def start_task_execution(self, task_id: str, task_name: str) -> bool:
        """Start tracking a task execution."""
        try:
            if not self.can_execute_task(task_id):
                return False

            execution = TaskExecution(
                task_id=task_id,
                task_name=task_name,
                status=TaskStatus.RUNNING,
                start_time=datetime.utcnow(),
                dependencies_met=True,
            )

            self.task_executions[task_id] = execution
            self.logger.info(f"Started task execution: {task_id} ({task_name})")
            return True

        except Exception as e:
            self.logger.error(f"Error starting task execution {task_id}: {e}")
            return False

    def complete_task_execution(
        self, task_id: str, success: bool = True, error: Optional[str] = None
    ) -> bool:
        """Complete a task execution."""
        try:
            if task_id not in self.task_executions:
                return False

            execution = self.task_executions[task_id]
            execution.end_time = datetime.utcnow()
            execution.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
            execution.error = error

            # Move to history
            self.execution_history.append(execution)
            del self.task_executions[task_id]

            self.logger.info(
                f"Completed task execution: {task_id} - {execution.status}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error completing task execution {task_id}: {e}")
            return False

    def get_ready_tasks(self) -> List[str]:
        """Get list of tasks that are ready to execute."""
        try:
            ready_tasks = []

            # Add tasks that are currently running or completed
            for task_id in self.task_executions:
                ready_tasks.append(task_id)

            # Add completed tasks from history
            for execution in self.execution_history:
                if execution.task_id not in ready_tasks:
                    ready_tasks.append(execution.task_id)

            # Add tasks that can execute (dependencies met)
            for task_id in self.dependencies:
                if task_id not in ready_tasks and self.can_execute_task(task_id):
                    ready_tasks.append(task_id)

            return ready_tasks

        except Exception as e:
            self.logger.error(f"Error getting ready tasks: {e}")
            return []

    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get the current status of a task."""
        try:
            if task_id in self.task_executions:
                return self.task_executions[task_id].status

            # Check history
            for execution in reversed(self.execution_history):
                if execution.task_id == task_id:
                    return execution.status

            return None

        except Exception as e:
            self.logger.error(f"Error getting task status for {task_id}: {e}")
            return None

    def get_execution_summary(self) -> Dict[str, Any]:
        """Get a summary of all task executions."""
        try:
            summary = {
                "total_tasks": len(self.dependencies),
                "running_tasks": len(
                    [
                        t
                        for t in self.task_executions.values()
                        if t.status == TaskStatus.RUNNING
                    ]
                ),
                "completed_tasks": len(
                    [
                        t
                        for t in self.execution_history
                        if t.status == TaskStatus.COMPLETED
                    ]
                ),
                "failed_tasks": len(
                    [t for t in self.execution_history if t.status == TaskStatus.FAILED]
                ),
                "ready_tasks": len(self.get_ready_tasks()),
                "execution_order": self.get_execution_order(),
            }
            return summary

        except Exception as e:
            self.logger.error(f"Error getting execution summary: {e}")
            return {}

    def _update_execution_graph(self):
        """Update the execution graph based on current dependencies."""
        try:
            self.execution_graph = {}

            for task_id, dependency in self.dependencies.items():
                if task_id not in self.execution_graph:
                    self.execution_graph[task_id] = set()

                for dep_task_id in dependency.depends_on:
                    if dep_task_id not in self.execution_graph:
                        self.execution_graph[dep_task_id] = set()

                    # Add edge: dep_task_id -> task_id (dependency points to dependent)
                    self.execution_graph[dep_task_id].add(task_id)

        except Exception as e:
            self.logger.error(f"Error updating execution graph: {e}")

    def _would_create_circle(self, dependency: TaskDependency) -> bool:
        """Check if adding this dependency would create a circular dependency."""
        try:
            # Temporarily add the dependency
            temp_deps = self.dependencies.copy()
            temp_deps[dependency.task_id] = dependency

            # Create temporary graph
            temp_graph: Dict[str, Set[str]] = {}
            for task_id, dep in temp_deps.items():
                if task_id not in temp_graph:
                    temp_graph[task_id] = set()
                for dep_task_id in dep.depends_on or []:
                    if dep_task_id not in temp_graph:
                        temp_graph[dep_task_id] = set()
                    temp_graph[dep_task_id].add(task_id)

            # Check for cycles using DFS
            visited = set()
            rec_stack = set()

            def has_cycle(node):
                visited.add(node)
                rec_stack.add(node)

                for neighbor in temp_graph.get(node, set()):
                    if neighbor not in visited:
                        if has_cycle(neighbor):
                            return True
                    elif neighbor in rec_stack:
                        return True

                rec_stack.remove(node)
                return False

            for node in temp_graph:
                if node not in visited:
                    if has_cycle(node):
                        return True

            return False

        except Exception as e:
            self.logger.error(f"Error checking for circular dependency: {e}")
            return True  # Assume circular to be safe

    def _is_dependency_satisfied(
        self, dep_task_id: str, dependency_type: DependencyType
    ) -> bool:
        """Check if a specific dependency is satisfied."""
        try:
            dep_status = self.get_task_status(dep_task_id)

            if dependency_type == DependencyType.REQUIRES:
                return dep_status == TaskStatus.COMPLETED

            elif dependency_type == DependencyType.OPTIONAL:
                return dep_status in [
                    TaskStatus.COMPLETED,
                    TaskStatus.FAILED,
                    TaskStatus.SKIPPED,
                ]

            elif dependency_type == DependencyType.REQUIRES_ANY:
                # This would need to be handled at the task level
                return dep_status == TaskStatus.COMPLETED

            elif dependency_type == DependencyType.CONDITIONAL:
                return dep_status == TaskStatus.COMPLETED

            # All DependencyType enum values are handled above

        except Exception as e:
            self.logger.error(f"Error checking dependency satisfaction: {e}")
            return False

    def _evaluate_condition(self, condition: str) -> bool:
        """Evaluate a conditional expression for task execution."""
        try:
            # Simple condition evaluation - can be extended for complex logic
            # For now, support basic comparisons and boolean operations

            # Example conditions:
            # "time.hour < 12" - only run before noon
            # "day_of_week in [0, 6]" - only run on weekends
            # "system.load < 0.8" - only run when system load is low

            # This is a placeholder - implement based on your needs
            self.logger.info(f"Evaluating condition: {condition}")

            # For now, return True to allow execution
            # TODO: Implement proper condition evaluation
            return True

        except Exception as e:
            self.logger.error(f"Error evaluating condition '{condition}': {e}")
            return False  # Fail safe - don't execute if condition evaluation fails

    def cleanup_old_executions(self, max_age_hours: int = 24):
        """Clean up old execution history."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            original_count = len(self.execution_history)

            self.execution_history = [
                execution
                for execution in self.execution_history
                if execution.end_time and execution.end_time > cutoff_time
            ]

            cleaned_count = original_count - len(self.execution_history)
            if cleaned_count > 0:
                self.logger.info(f"Cleaned up {cleaned_count} old execution records")

        except Exception as e:
            self.logger.error(f"Error cleaning up old executions: {e}")

    def reset(self):
        """Reset the scheduler state."""
        try:
            self.dependencies.clear()
            self.execution_graph.clear()
            self.task_executions.clear()
            self.execution_history.clear()
            self.logger.info("Dependency scheduler reset")

        except Exception as e:
            self.logger.error(f"Error resetting scheduler: {e}")
