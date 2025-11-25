"""Recipe generation and management routes."""
import json
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.auth import get_current_user
from app.models import User, PantryItem, RecipeHistory, DailySuggestion
from app.schemas import RecipeGenerateRequest, RecipeResponse, RecipeSaveRequest
from app.recipe_ai import generate_recipe_for_user
from app.image_gen import generate_food_image
from app.utils import estimate_calories_from_ingredients

router = APIRouter(prefix="/recipes", tags=["recipes"])


@router.post("/generate", response_model=dict)
async def generate_recipe(
    request: RecipeGenerateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Generate a recipe from user's pantry ingredients.
    
    Uses AI to generate a healthy recipe based on:
    - User's pantry items
    - User's health profile (diet, allergies, goals)
    - Preferences (cuisine, spice level)
    - Recent recipe history (to avoid repetition)
    
    Returns recipe JSON and image URL.
    """
    # Get pantry items
    statement = select(PantryItem).where(PantryItem.user_id == current_user.id)
    pantry_items = list(session.exec(statement).all())
    
    if not pantry_items and request.use_pantry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No pantry items found. Please add ingredients to your pantry first."
        )
    
    # Get recent recipe history for non-repetition
    history_statement = select(RecipeHistory).where(
        RecipeHistory.user_id == current_user.id
    ).order_by(RecipeHistory.created_at.desc()).limit(10)
    history = list(session.exec(history_statement).all())
    
    # Generate recipe
    recipe_data = await generate_recipe_for_user(
        user=current_user,
        pantry_items=pantry_items,
        preferences=request.preferences,
        history=history,
        avoid_repeats=request.avoid_repeats
    )
    
    # Generate image
    image_url = generate_food_image(recipe_data.get("name", "Recipe"), recipe_data.get("description"))
    
    return {
        "recipe": recipe_data,
        "image_url": image_url
    }


@router.get("/daily", response_model=dict)
async def get_daily_recipe(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get or generate daily unique recipe suggestion.
    
    Automatically uses all current pantry items to generate a recipe.
    Stores the suggestion to track daily recommendations.
    Ensures non-repetitive recipes based on history.
    """
    # Check if there's already a suggestion for today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    statement = select(DailySuggestion).where(
        DailySuggestion.user_id == current_user.id,
        DailySuggestion.suggested_at >= today_start,
        DailySuggestion.suggested_at < today_end
    )
    existing_suggestion = session.exec(statement).first()
    
    if existing_suggestion:
        # Return existing suggestion
        recipe_data = json.loads(existing_suggestion.recipe_json)
        return {
            "recipe": recipe_data,
            "image_url": generate_food_image(recipe_data.get("name", "Recipe")),
            "suggested_at": existing_suggestion.suggested_at.isoformat()
        }
    
    # Generate new daily suggestion
    # Get all pantry items
    pantry_statement = select(PantryItem).where(PantryItem.user_id == current_user.id)
    pantry_items = list(session.exec(pantry_statement).all())
    
    if not pantry_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No pantry items found. Please add ingredients to your pantry first."
        )
    
    # Get recent history
    history_statement = select(RecipeHistory).where(
        RecipeHistory.user_id == current_user.id
    ).order_by(RecipeHistory.created_at.desc()).limit(10)
    history = list(session.exec(history_statement).all())
    
    # Generate recipe
    recipe_data = await generate_recipe_for_user(
        user=current_user,
        pantry_items=pantry_items,
        preferences=None,
        history=history,
        avoid_repeats=True
    )
    
    # Generate image
    image_url = generate_food_image(recipe_data.get("name", "Recipe"), recipe_data.get("description"))
    
    # Save as daily suggestion
    suggestion = DailySuggestion(
        user_id=current_user.id,
        recipe_json=json.dumps(recipe_data),
        suggested_at=datetime.utcnow()
    )
    session.add(suggestion)
    session.commit()
    
    return {
        "recipe": recipe_data,
        "image_url": image_url,
        "suggested_at": suggestion.suggested_at.isoformat()
    }


@router.post("/save", response_model=dict, status_code=status.HTTP_201_CREATED)
async def save_recipe(
    request: RecipeSaveRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Save a recipe to history (mark as cooked).
    
    Stores the recipe in user's history with nutritional information.
    """
    recipe_json = request.recipe_json
    recipe_name = recipe_json.get("name", "Unknown Recipe")
    
    # Get calories from request or estimate
    calories = request.calories
    if not calories and "calories" in recipe_json:
        calories = recipe_json.get("calories")
    if not calories and "ingredients" in recipe_json:
        calories = estimate_calories_from_ingredients(recipe_json.get("ingredients", []))
    
    # Save to history
    history_item = RecipeHistory(
        user_id=current_user.id,
        recipe_name=recipe_name,
        recipe_json=json.dumps(recipe_json),
        calories=calories
    )
    session.add(history_item)
    session.commit()
    session.refresh(history_item)
    
    return {
        "id": history_item.id,
        "recipe_name": history_item.recipe_name,
        "calories": history_item.calories,
        "created_at": history_item.created_at.isoformat()
    }

