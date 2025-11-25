"""Recipe history and reports routes."""
import json
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, func
from app.database import get_session
from app.auth import get_current_user
from app.models import User, RecipeHistory
from app.schemas import RecipeHistoryResponse, WeeklyReport

router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=List[RecipeHistoryResponse])
async def get_history(
    period: Optional[str] = Query(None, description="Filter by period: 'week' or 'month'"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get user's recipe history.
    
    Returns list of saved/cooked recipes with optional filtering by period.
    """
    statement = select(RecipeHistory).where(RecipeHistory.user_id == current_user.id)
    
    # Apply period filter
    if period == "week":
        week_ago = datetime.utcnow() - timedelta(days=7)
        statement = statement.where(RecipeHistory.created_at >= week_ago)
    elif period == "month":
        month_ago = datetime.utcnow() - timedelta(days=30)
        statement = statement.where(RecipeHistory.created_at >= month_ago)
    
    statement = statement.order_by(RecipeHistory.created_at.desc())
    history_items = session.exec(statement).all()
    
    result = []
    for item in history_items:
        try:
            recipe_json = json.loads(item.recipe_json) if isinstance(item.recipe_json, str) else item.recipe_json
        except:
            recipe_json = {}
        
        result.append(RecipeHistoryResponse(
            id=item.id,
            recipe_name=item.recipe_name,
            recipe_json=recipe_json,
            calories=item.calories,
            created_at=item.created_at
        ))
    
    return result


@router.get("/reports/weekly", response_model=WeeklyReport)
async def get_weekly_report(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Generate weekly health report.
    
    Returns summary including:
    - Total calories consumed
    - Variety score (based on unique recipes)
    - Top ingredients used
    - Meals count
    - Average calories per meal
    """
    # Get recipes from last week
    week_ago = datetime.utcnow() - timedelta(days=7)
    statement = select(RecipeHistory).where(
        RecipeHistory.user_id == current_user.id,
        RecipeHistory.created_at >= week_ago
    )
    history_items = list(session.exec(statement).all())
    
    # Calculate total calories
    total_calories = sum(item.calories or 0 for item in history_items)
    
    # Count meals
    meals_count = len(history_items)
    
    # Calculate average calories per meal
    avg_calories = total_calories / meals_count if meals_count > 0 else 0
    
    # Calculate variety score (unique recipes / total recipes)
    unique_recipes = len(set(item.recipe_name for item in history_items))
    variety_score = (unique_recipes / meals_count * 100) if meals_count > 0 else 0
    
    # Extract top ingredients from recipe JSONs
    ingredient_counts = {}
    for item in history_items:
        try:
            recipe_json = json.loads(item.recipe_json) if isinstance(item.recipe_json, str) else item.recipe_json
            ingredients = recipe_json.get("ingredients", [])
            for ing in ingredients:
                ing_name = ing.get("name", "").lower()
                if ing_name:
                    ingredient_counts[ing_name] = ingredient_counts.get(ing_name, 0) + 1
        except:
            continue
    
    # Get top 5 ingredients
    top_ingredients = sorted(
        ingredient_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]
    top_ingredients_list = [{"name": name, "count": count} for name, count in top_ingredients]
    
    return WeeklyReport(
        total_calories=round(total_calories, 1),
        variety_score=round(variety_score, 1),
        top_ingredients=top_ingredients_list,
        meals_count=meals_count,
        avg_calories_per_meal=round(avg_calories, 1)
    )

