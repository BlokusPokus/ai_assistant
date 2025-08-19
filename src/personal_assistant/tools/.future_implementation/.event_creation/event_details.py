from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ValidationStatus(Enum):
    """Validation status for event details."""
    VALID = "valid"
    INVALID = "invalid"
    PARTIAL = "partial"


@dataclass
class EventDetails:
    """Data structure for parsed event details."""

    title: str
    start_time: datetime
    duration: int = 60  # minutes
    location: str = ""
    description: str = ""
    recurrence_pattern: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'title': self.title,
            'start_time': self.start_time.isoformat(),
            'duration': self.duration,
            'location': self.location,
            'description': self.description,
            'recurrence_pattern': self.recurrence_pattern
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EventDetails':
        """Create from dictionary."""
        return cls(
            title=data['title'],
            start_time=datetime.fromisoformat(data['start_time']),
            duration=data.get('duration', 60),
            location=data.get('location', ''),
            description=data.get('description', ''),
            recurrence_pattern=data.get('recurrence_pattern')
        )


@dataclass
class ValidationResult:
    """Result of event details validation."""

    status: ValidationStatus
    errors: List[str] = None
    warnings: List[str] = None
    suggestions: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.suggestions is None:
            self.suggestions = []

    @property
    def is_valid(self) -> bool:
        """Check if validation passed."""
        return self.status == ValidationStatus.VALID

    @property
    def has_errors(self) -> bool:
        """Check if there are validation errors."""
        return len(self.errors) > 0

    @property
    def has_warnings(self) -> bool:
        """Check if there are validation warnings."""
        return len(self.warnings) > 0


@dataclass
class RecurrencePattern:
    """Data structure for recurrence patterns."""

    frequency: str  # daily, weekly, monthly, yearly
    interval: int = 1  # every N days/weeks/months/years
    # for weekly patterns [0=Monday, 6=Sunday]
    weekdays: Optional[List[int]] = None
    end_date: Optional[datetime] = None  # when to stop recurring
    max_occurrences: Optional[int] = None  # max number of instances

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'frequency': self.frequency,
            'interval': self.interval,
            'weekdays': self.weekdays,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'max_occurrences': self.max_occurrences
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RecurrencePattern':
        """Create from dictionary."""
        return cls(
            frequency=data['frequency'],
            interval=data.get('interval', 1),
            weekdays=data.get('weekdays'),
            end_date=datetime.fromisoformat(
                data['end_date']) if data.get('end_date') else None,
            max_occurrences=data.get('max_occurrences')
        )

    def is_valid(self) -> bool:
        """Validate recurrence pattern."""
        if self.frequency not in ['daily', 'weekly', 'monthly', 'yearly']:
            return False
        if self.interval < 1:
            return False
        if self.frequency == 'weekly' and (self.weekdays is None or len(self.weekdays) == 0):
            return False
        if self.max_occurrences is not None and self.max_occurrences < 1:
            return False
        return True
