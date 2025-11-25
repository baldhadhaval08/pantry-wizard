"""Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr


# Auth Schemas
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    age: Optional[int] = None
    diet_type: Optional[str] = None
    allergies: Optional[str] = None
    goal: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserProfile(BaseModel):
    id: int
    name: str
    email: str
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    age: Optional[int] = None
    diet_type: Optional[str] = None
    allergies: Optional[str] = None
    goal: Optional[str] = None
    created_at: datetime


# Pantry Schemas
class PantryItemCreate(BaseModel):
    name: str
    quantity: float
    unit: str


class PantryItemUpdate(BaseModel):
    name: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None


class PantryItemResponse(BaseModel):
    id: int
    user_id: int
    name: str
    quantity: float
    unit: str
    created_at: datetime


# Recipe Schemas
class Ingredient(BaseModel):
    name: str
    amount: str


class Macros(BaseModel):
    protein_g: float
    carbs_g: float
    fat_g: float


class RecipeResponse(BaseModel):
    name: str
    description: str
    ingredients: List[Ingredient]
    steps: List[str]
    time_minutes: int
    difficulty: str
    calories: float
    macros: Macros
    health_justification: str


class RecipeGenerateRequest(BaseModel):
    use_pantry: bool = True
    extra_ingredients: List[str] = []
    preferences: Optional[Dict[str, str]] = None
    avoid_repeats: bool = True


class RecipeSaveRequest(BaseModel):
    recipe_json: Dict
    calories: Optional[float] = None


class RecipeHistoryResponse(BaseModel):
    id: int
    recipe_name: str
    recipe_json: Dict
    calories: Optional[float] = None
    created_at: datetime


# Report Schemas
class WeeklyReport(BaseModel):
    total_calories: float
    variety_score: float
    top_ingredients: List[Dict[str, Any]]
    meals_count: int
    avg_calories_per_meal: float

