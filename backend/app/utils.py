"""Utility functions for calculations and helpers."""
from typing import List, Dict


def calculate_bmi(height_cm: float, weight_kg: float) -> float:
    """Calculate BMI from height (cm) and weight (kg)."""
    if height_cm <= 0 or weight_kg <= 0:
        return 0.0
    height_m = height_cm / 100.0
    return round(weight_kg / (height_m ** 2), 1)


def estimate_calories_from_ingredients(ingredients: List[Dict[str, str]]) -> float:
    """
    Heuristic calorie estimation from ingredients.
    This is a rough approximation - AI should provide accurate calories.
    """
    # Basic calorie estimates per common ingredient (per unit)
    calorie_map = {
        "chicken": 165,  # per 100g
        "beef": 250,
        "pork": 242,
        "fish": 206,
        "rice": 130,  # per 100g cooked
        "pasta": 131,
        "potato": 77,
        "onion": 40,
        "tomato": 18,
        "carrot": 41,
        "broccoli": 34,
        "spinach": 23,
        "egg": 70,  # per egg
        "cheese": 113,  # per 30g
        "milk": 42,  # per 100ml
        "oil": 884,  # per 100ml
        "butter": 717,
    }
    
    total_calories = 0.0
    
    for ingredient in ingredients:
        name = ingredient.get("name", "").lower()
        amount_str = ingredient.get("amount", "").lower()
        
        # Try to find matching ingredient
        for key, calories_per_unit in calorie_map.items():
            if key in name:
                # Very rough estimation - assume 100g or 1 unit
                # In reality, this should parse the amount string properly
                total_calories += calories_per_unit * 0.5  # Conservative estimate
                break
    
    # If no matches found, use a default estimate
    if total_calories == 0:
        total_calories = len(ingredients) * 50  # Rough estimate
    
    return round(total_calories, 0)

