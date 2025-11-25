"""AI recipe generation using local or API-based LLMs."""
import json
import re
from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod
from difflib import SequenceMatcher
import httpx
from app.config import settings
from app.models import User, PantryItem, RecipeHistory
from app.schemas import RecipeResponse
from app.utils import calculate_bmi


class LLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    def generate_recipe(self, prompt: str) -> str:
        """Generate recipe text from prompt."""
        pass


class OllamaLLMClient(LLMClient):
    """Local LLM client using Ollama (works with Python 3.13+)."""
    
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model_name = settings.OLLAMA_MODEL
        self._check_ollama()
    
    def _check_ollama(self):
        """Check if Ollama is running."""
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=5.0)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                if self.model_name not in model_names:
                    print(f"⚠️  Warning: Model '{self.model_name}' not found in Ollama.")
                    print(f"Available models: {', '.join(model_names) if model_names else 'None'}")
                    print(f"Install it with: ollama pull {self.model_name}")
                else:
                    print(f"✅ Ollama model '{self.model_name}' is available")
        except Exception as e:
            print(f"⚠️  Warning: Cannot connect to Ollama at {self.base_url}")
            print(f"Error: {e}")
            print("Make sure Ollama is installed and running:")
            print("  brew install ollama  # macOS")
            print("  ollama serve")
            print(f"  ollama pull {self.model_name}")
    
    def generate_recipe(self, prompt: str) -> str:
        """Generate recipe using Ollama."""
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                }
            }
            
            response = httpx.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=120.0
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract response text
            response_text = data.get("response", "")
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json_match.group(0)
            return response_text
        except Exception as e:
            print(f"Error generating with Ollama: {e}")
            return self._fallback_recipe()
    
    def _fallback_recipe(self) -> str:
        """Fallback recipe if Ollama fails."""
        return json.dumps({
            "name": "Simple Pantry Stir-Fry",
            "description": "A quick and healthy stir-fry using your available ingredients.",
            "ingredients": [{"name": "mixed vegetables", "amount": "2 cups"}],
            "steps": [
                "Heat oil in a pan",
                "Add vegetables and stir-fry for 5 minutes",
                "Season with salt and pepper",
                "Serve hot"
            ],
            "time_minutes": 15,
            "difficulty": "easy",
            "calories": 200,
            "macros": {"protein_g": 10, "carbs_g": 30, "fat_g": 5},
            "health_justification": "A balanced meal with vegetables providing essential nutrients."
        })


class LocalLLMClient(LLMClient):
    """Local LLM client using transformers (requires Python 3.8-3.12)."""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self._load_model()
    
    def _load_model(self):
        """Load local transformer model."""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
            
            device = "cuda" if settings.USE_CUDA and torch.cuda.is_available() else "cpu"
            model_path = settings.LLM_MODEL_PATH or settings.LLM_MODEL_NAME
            
            print(f"Loading local model from {model_path} on {device}...")
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                device_map="auto" if device == "cuda" else None
            )
            if device == "cpu":
                self.model = self.model.to(device)
            self.model.eval()
            print("Local model loaded successfully")
        except ImportError as e:
            print(f"⚠️  Transformers/PyTorch not available: {e}")
            print("💡 Tip: Use 'ollama' mode instead (works with Python 3.13+)")
            print("   Set LLM_MODE=ollama in your .env file")
            self.model = None
        except Exception as e:
            print(f"Error loading local model: {e}")
            print("Falling back to placeholder mode")
            self.model = None
    
    def generate_recipe(self, prompt: str) -> str:
        """Generate recipe using local model."""
        if self.model is None or self.tokenizer is None:
            return self._fallback_recipe()
        
        try:
            import torch
            
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
            device = next(self.model.parameters()).device
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=1024,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json_match.group(0)
            return response
        except Exception as e:
            print(f"Error generating with local model: {e}")
            return self._fallback_recipe()
    
    def _fallback_recipe(self) -> str:
        """Fallback recipe if model fails."""
        return json.dumps({
            "name": "Simple Pantry Stir-Fry",
            "description": "A quick and healthy stir-fry using your available ingredients.",
            "ingredients": [{"name": "mixed vegetables", "amount": "2 cups"}],
            "steps": [
                "Heat oil in a pan",
                "Add vegetables and stir-fry for 5 minutes",
                "Season with salt and pepper",
                "Serve hot"
            ],
            "time_minutes": 15,
            "difficulty": "easy",
            "calories": 200,
            "macros": {"protein_g": 10, "carbs_g": 30, "fat_g": 5},
            "health_justification": "A balanced meal with vegetables providing essential nutrients."
        })


class APILLMClient(LLMClient):
    """API-based LLM client (OpenAI/OpenRouter/Anthropic)."""
    
    def generate_recipe(self, prompt: str) -> str:
        """Generate recipe using API."""
        if not settings.LLM_API_URL or not settings.LLM_API_KEY:
            return self._fallback_recipe()
        
        try:
            # Try OpenAI-compatible API
            headers = {
                "Authorization": f"Bearer {settings.LLM_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Determine API format
            if "openai" in settings.LLM_API_URL.lower() or "openrouter" in settings.LLM_API_URL.lower():
                payload = {
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": "You are a health-focused chef AI. Output only valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1024
                }
            else:
                # Generic API format
                payload = {
                    "prompt": prompt,
                    "max_tokens": 1024,
                    "temperature": 0.7
                }
            
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    settings.LLM_API_URL,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                
                # Extract content from response
                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0].get("message", {}).get("content", "")
                elif "text" in data:
                    content = data["text"]
                elif "content" in data:
                    content = data["content"]
                else:
                    content = str(data)
                
                # Extract JSON from content
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json_match.group(0)
                return content
        except Exception as e:
            print(f"Error calling API: {e}")
            return self._fallback_recipe()
    
    def _fallback_recipe(self) -> str:
        """Fallback recipe if API fails."""
        return json.dumps({
            "name": "Healthy Pantry Bowl",
            "description": "A nutritious bowl made from your available ingredients.",
            "ingredients": [{"name": "available ingredients", "amount": "as needed"}],
            "steps": [
                "Prepare your ingredients",
                "Combine in a bowl",
                "Season to taste",
                "Enjoy!"
            ],
            "time_minutes": 20,
            "difficulty": "easy",
            "calories": 250,
            "macros": {"protein_g": 15, "carbs_g": 35, "fat_g": 8},
            "health_justification": "A balanced meal using fresh ingredients from your pantry."
        })


def get_llm_client() -> LLMClient:
    """Get appropriate LLM client based on configuration."""
    if settings.LLM_MODE == "ollama":
        return OllamaLLMClient()
    elif settings.LLM_MODE == "local":
        return LocalLLMClient()
    else:
        return APILLMClient()


def build_recipe_prompt(
    user: User,
    pantry_items: List[PantryItem],
    preferences: Optional[Dict[str, str]] = None,
    recent_titles: Optional[List[str]] = None
) -> str:
    """Build detailed recipe generation prompt."""
    # Calculate BMI
    bmi = 0.0
    if user.height_cm and user.weight_kg:
        bmi = calculate_bmi(user.height_cm, user.weight_kg)
    
    # Build pantry list
    pantry_list = ", ".join([f"{item.name} ({item.quantity} {item.unit})" for item in pantry_items])
    if not pantry_list:
        pantry_list = "No specific ingredients listed (use common pantry staples)"
    
    # Recent recipe titles
    recent_titles_str = ", ".join(recent_titles) if recent_titles else "None"
    
    # Preferences
    cuisine = preferences.get("cuisine", "any") if preferences else "any"
    spice_level = preferences.get("spice_level", "medium") if preferences else "medium"
    
    prompt = f"""You are a health-focused chef AI. Output only valid JSON.

User profile:
- Name: {user.name}
- Age: {user.age or 'Not specified'}
- Height_cm: {user.height_cm or 'Not specified'}
- Weight_kg: {user.weight_kg or 'Not specified'}
- BMI: {bmi}
- Diet: {user.diet_type or 'No restrictions'}
- Allergies: {user.allergies or 'None'}
- Health goal: {user.goal or 'General health'}

Pantry ingredients available (list): {pantry_list}
Recent cooked recipes (titles): {recent_titles_str}
Preferred cuisine: {cuisine}
Spice level: {spice_level}

Task:
- Using only the given pantry ingredients, generate ONE healthy recipe optimized for the user's health goal.
- Avoid allergies and disliked items.
- Ensure variety: do not repeat any recipe title that is similar to the recent titles.
- If a required staple is missing (salt, oil, water), assume small amounts are available.
- Make the recipe practical and easy to follow.

Return JSON EXACTLY in this shape:
{{
  "name": "Dish name",
  "description": "Short description 1-2 sentences",
  "ingredients": [
    {{"name":"onion", "amount":"1 medium"}},
    ...
  ],
  "steps": [
    "Step 1 ...",
    ...
  ],
  "time_minutes": 30,
  "difficulty": "easy|medium|hard",
  "calories": 420,
  "macros": {{"protein_g":20, "carbs_g":50, "fat_g":10}},
  "health_justification": "Brief sentence explaining why this suits the user's goals."
}}"""
    
    return prompt


def ensure_non_repetitive(history: List[RecipeHistory], candidate: Dict[str, Any]) -> bool:
    """Check if candidate recipe is too similar to recent recipes."""
    if not history:
        return True
    
    candidate_name = candidate.get("name", "").lower()
    
    # Check last 10 recipes
    recent_recipes = history[-10:]
    
    for recipe in recent_recipes:
        recipe_name = recipe.recipe_name.lower()
        similarity = SequenceMatcher(None, candidate_name, recipe_name).ratio()
        
        # If similarity > 0.7, consider it a repeat
        if similarity > 0.7:
            return False
    
    return True


def parse_recipe_response(response_text: str) -> Dict[str, Any]:
    """Parse and validate LLM response."""
    try:
        # Try to extract JSON
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            recipe_data = json.loads(json_match.group(0))
        else:
            recipe_data = json.loads(response_text)
        
        # Validate required fields
        required_fields = ["name", "description", "ingredients", "steps", "time_minutes", "difficulty", "calories", "macros"]
        for field in required_fields:
            if field not in recipe_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Ensure macros structure
        if "macros" not in recipe_data or not isinstance(recipe_data["macros"], dict):
            recipe_data["macros"] = {"protein_g": 0, "carbs_g": 0, "fat_g": 0}
        
        return recipe_data
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        raise ValueError(f"Invalid JSON response: {e}")
    except Exception as e:
        print(f"Error parsing recipe: {e}")
        raise


async def generate_recipe_for_user(
    user: User,
    pantry_items: List[PantryItem],
    preferences: Optional[Dict[str, str]] = None,
    history: Optional[List[RecipeHistory]] = None,
    avoid_repeats: bool = True
) -> Dict[str, Any]:
    """
    Generate a recipe for a user based on their pantry and profile.
    
    Args:
        user: User model with profile information
        pantry_items: List of available pantry items
        preferences: Optional preferences (cuisine, spice_level)
        history: Optional recipe history for non-repetition check
        avoid_repeats: Whether to check for recipe repetition
    
    Returns:
        Dictionary with recipe data
    """
    # Get recent recipe titles
    recent_titles = []
    if history:
        recent_titles = [r.recipe_name for r in history[-10:]]
    
    # Build prompt
    prompt = build_recipe_prompt(user, pantry_items, preferences, recent_titles)
    
    # Get LLM client
    client = get_llm_client()
    
    # Generate recipe (with retry for non-repetitive)
    max_attempts = 3
    for attempt in range(max_attempts):
        response_text = client.generate_recipe(prompt)
        recipe_data = parse_recipe_response(response_text)
        
        # Check for repetition if needed
        if not avoid_repeats or not history or ensure_non_repetitive(history, recipe_data):
            return recipe_data
        
        # If repetitive, try again with modified prompt
        if attempt < max_attempts - 1:
            prompt += "\n\nIMPORTANT: Generate a DIFFERENT recipe that is not similar to the recent recipes listed above."
    
    # Return last attempt even if repetitive
    return recipe_data