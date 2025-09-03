"""
Unit tests for Base Model.

This module tests the core BaseModel functionality including
serialization, relationships, and common database operations.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from personal_assistant.database.models.base import Base, BaseModel
from tests.utils.test_helpers import TestHelper
from tests.utils.test_data_generators import DatabaseDataGenerator


class TestBaseModel:
    """Test cases for BaseModel class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create a test model class that inherits from BaseModel
        # Use extend_existing=True to avoid table redefinition errors
        class TestModel(BaseModel):
            __tablename__ = "test_models"
            __table_args__ = {'extend_existing': True}
            
            id = Column(Integer, primary_key=True)
            name = Column(String(100), nullable=False)
            description = Column(String(255), nullable=True)
            created_at = Column(DateTime, default=datetime.utcnow)
            updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
            
            def __repr__(self):
                return f"<TestModel(id={self.id}, name='{self.name}')>"
        
        self.TestModel = TestModel

    def test_base_model_initialization(self):
        """Test BaseModel initialization."""
        model = self.TestModel(name="Test Item", description="Test Description")
        
        assert model.name == "Test Item"
        assert model.description == "Test Description"
        assert model.id is None  # Not set until saved to database
        # Note: Default values are applied at database level, not object creation
        assert model.created_at is None  # Will be set by database
        assert model.updated_at is None  # Will be set by database

    def test_base_model_to_dict(self):
        """Test BaseModel to_dict method."""
        model = self.TestModel(name="Test Item", description="Test Description")
        
        # Set some attributes that would normally be set by the database
        model.id = 1
        model.created_at = datetime(2024, 1, 15, 10, 30, 0)
        model.updated_at = datetime(2024, 1, 15, 10, 30, 0)
        
        result = model.to_dict()
        
        assert isinstance(result, dict)
        assert result["id"] == 1
        assert result["name"] == "Test Item"
        assert result["description"] == "Test Description"
        assert result["created_at"] == datetime(2024, 1, 15, 10, 30, 0)
        assert result["updated_at"] == datetime(2024, 1, 15, 10, 30, 0)

    def test_base_model_to_dict_with_none_values(self):
        """Test BaseModel to_dict method with None values."""
        model = self.TestModel(name="Test Item")
        model.id = 1
        
        result = model.to_dict()
        
        assert result["name"] == "Test Item"
        assert result["description"] is None

    def test_base_model_repr(self):
        """Test BaseModel __repr__ method."""
        model = self.TestModel(name="Test Item")
        model.id = 1
        
        result = repr(model)
        
        assert "TestModel" in result
        assert "id=1" in result
        assert "name='Test Item'" in result

    def test_base_model_table_name(self):
        """Test that BaseModel has correct table name."""
        assert self.TestModel.__tablename__ == "test_models"

    def test_base_model_columns(self):
        """Test that BaseModel has expected columns."""
        columns = self.TestModel.__table__.columns
        
        assert "id" in columns
        assert "name" in columns
        assert "description" in columns
        assert "created_at" in columns
        assert "updated_at" in columns

    def test_base_model_column_types(self):
        """Test that BaseModel columns have correct types."""
        columns = self.TestModel.__table__.columns
        
        assert str(columns["id"].type) == "INTEGER"
        assert str(columns["name"].type) == "VARCHAR(100)"
        assert str(columns["description"].type) == "VARCHAR(255)"
        assert "DATETIME" in str(columns["created_at"].type)
        assert "DATETIME" in str(columns["updated_at"].type)

    def test_base_model_primary_key(self):
        """Test that BaseModel has correct primary key."""
        primary_key = self.TestModel.__table__.primary_key
        
        assert len(primary_key.columns) == 1
        assert "id" in primary_key.columns

    def test_base_model_nullable_constraints(self):
        """Test that BaseModel has correct nullable constraints."""
        columns = self.TestModel.__table__.columns
        
        assert columns["id"].nullable is False  # Primary key
        assert columns["name"].nullable is False
        assert columns["description"].nullable is True
        assert columns["created_at"].nullable is True  # Has default
        assert columns["updated_at"].nullable is True  # Has default

    def test_base_model_inheritance(self):
        """Test that BaseModel properly inherits from Base."""
        assert issubclass(self.TestModel, BaseModel)
        assert issubclass(BaseModel, Base)

    def test_base_model_with_relationships(self):
        """Test BaseModel with relationships."""
        # Create a related model
        class RelatedModel(BaseModel):
            __tablename__ = "related_models"
            
            id = Column(Integer, primary_key=True)
            test_model_id = Column(Integer, ForeignKey("test_models.id"))
            value = Column(String(100))
            
            test_model = relationship("TestModel", back_populates="related_items")
        
        # Add relationship to TestModel
        self.TestModel.related_items = relationship("RelatedModel", back_populates="test_model")
        
        # Test relationship
        test_model = self.TestModel(name="Test Item")
        related_item = RelatedModel(value="Related Value")
        
        test_model.related_items = [related_item]
        related_item.test_model = test_model
        
        assert test_model.related_items[0] == related_item
        assert related_item.test_model == test_model

    def test_base_model_serialization_with_datetime(self):
        """Test BaseModel serialization with datetime objects."""
        model = self.TestModel(name="Test Item")
        model.id = 1
        model.created_at = datetime(2024, 1, 15, 10, 30, 0)
        model.updated_at = datetime(2024, 1, 15, 11, 30, 0)
        
        result = model.to_dict()
        
        # Check that datetime objects are preserved
        assert isinstance(result["created_at"], datetime)
        assert isinstance(result["updated_at"], datetime)
        assert result["created_at"] == datetime(2024, 1, 15, 10, 30, 0)
        assert result["updated_at"] == datetime(2024, 1, 15, 11, 30, 0)

    def test_base_model_with_custom_attributes(self):
        """Test BaseModel with custom attributes not in database."""
        model = self.TestModel(name="Test Item")
        model.id = 1
        
        # Add custom attribute not in database
        model.custom_attr = "Custom Value"
        
        result = model.to_dict()
        
        # Custom attributes should not be in the result
        assert "custom_attr" not in result
        assert result["name"] == "Test Item"
        assert result["id"] == 1

    def test_base_model_empty_model(self):
        """Test BaseModel with minimal data."""
        model = self.TestModel()
        model.id = 1
        
        result = model.to_dict()
        
        assert result["id"] == 1
        assert result["name"] is None
        assert result["description"] is None

    def test_base_model_with_foreign_key(self):
        """Test BaseModel with foreign key relationships."""
        class ParentModel(BaseModel):
            __tablename__ = "parent_models"
            
            id = Column(Integer, primary_key=True)
            name = Column(String(100))
        
        class ChildModel(BaseModel):
            __tablename__ = "child_models"
            
            id = Column(Integer, primary_key=True)
            parent_id = Column(Integer, ForeignKey("parent_models.id"))
            name = Column(String(100))
            
            parent = relationship("ParentModel")
        
        parent = ParentModel(name="Parent")
        parent.id = 1
        
        child = ChildModel(name="Child", parent_id=1)
        child.id = 1
        child.parent = parent
        
        assert child.parent_id == 1
        assert child.parent == parent
        assert child.parent.name == "Parent"

    def test_base_model_table_metadata(self):
        """Test BaseModel table metadata."""
        table = self.TestModel.__table__
        
        assert table.name == "test_models"
        assert len(table.columns) == 5  # id, name, description, created_at, updated_at
        assert table.primary_key is not None

    def test_base_model_column_attributes(self):
        """Test BaseModel column attributes."""
        columns = self.TestModel.__table__.columns
        
        # Test that columns have expected attributes
        id_column = columns["id"]
        assert id_column.primary_key is True
        assert id_column.nullable is False
        
        name_column = columns["name"]
        assert name_column.nullable is False
        assert name_column.type.length == 100
        
        description_column = columns["description"]
        assert description_column.nullable is True
        assert description_column.type.length == 255

    def test_base_model_with_defaults(self):
        """Test BaseModel with default values."""
        model = self.TestModel(name="Test Item")
        
        # Default values are applied at database level, not object creation
        assert model.created_at is None  # Will be set by database
        assert model.updated_at is None  # Will be set by database

    def test_base_model_equality(self):
        """Test BaseModel equality comparison."""
        model1 = self.TestModel(name="Test Item")
        model1.id = 1
        
        model2 = self.TestModel(name="Test Item")
        model2.id = 1
        
        model3 = self.TestModel(name="Different Item")
        model3.id = 1
        
        # Models with same ID should be equal
        assert model1 == model2
        
        # Models with different attributes but same ID should be equal
        assert model1 == model3

    def test_base_model_inequality(self):
        """Test BaseModel inequality comparison."""
        model1 = self.TestModel(name="Test Item")
        model1.id = 1
        
        model2 = self.TestModel(name="Test Item")
        model2.id = 2
        
        # Models with different IDs should not be equal
        assert model1 != model2

    def test_base_model_hash(self):
        """Test BaseModel hash functionality."""
        model1 = self.TestModel(name="Test Item")
        model1.id = 1
        
        model2 = self.TestModel(name="Test Item")
        model2.id = 1
        
        # Models with same ID should have same hash
        assert hash(model1) == hash(model2)
        
        # Models should be usable in sets
        model_set = {model1, model2}
        assert len(model_set) == 1  # Should be deduplicated

    def test_base_model_with_complex_data(self):
        """Test BaseModel with complex data types."""
        model = self.TestModel(
            name="Complex Test Item",
            description="A very long description that contains special characters: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        )
        model.id = 999
        model.created_at = datetime(2024, 12, 31, 23, 59, 59)
        model.updated_at = datetime(2024, 12, 31, 23, 59, 59)
        
        result = model.to_dict()
        
        assert result["id"] == 999
        assert result["name"] == "Complex Test Item"
        assert "special characters" in result["description"]
        assert result["created_at"] == datetime(2024, 12, 31, 23, 59, 59)
        assert result["updated_at"] == datetime(2024, 12, 31, 23, 59, 59)