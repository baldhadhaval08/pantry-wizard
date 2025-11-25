"""SQLModel database models."""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    """User model with health profile."""
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)
    password_hash: str
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    age: Optional[int] = None
    diet_type: Optional[str] = None  # e.g., "vegetarian", "vegan", "keto", "omnivore"
    allergies: Optional[str] = None  # Comma-separated list
    goal: Optional[str] = None  # e.g., "weight_loss", "muscle_gain", "maintain"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PantryItem(SQLModel, table=True):
    """Pantry item model."""
    __tablename__ = "pantry_items"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    name: str
    quantity: float
    unit: str  # e.g., "cups", "grams", "pieces"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class RecipeHistory(SQLModel, table=True):
    """Recipe history model for saved/cooked recipes."""
    __tablename__ = "recipe_history"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    recipe_name: str
    recipe_json: str  # Full recipe JSON stored as string
    calories: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DailySuggestion(SQLModel, table=True):
    """Daily recipe suggestion tracking."""
    __tablename__ = "daily_suggestions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    recipe_id: Optional[int] = Field(default=None, foreign_key="recipe_history.id")
    recipe_json: str  # Full recipe JSON stored as string
    suggested_at: datetime = Field(default_factory=datetime.utcnow)

