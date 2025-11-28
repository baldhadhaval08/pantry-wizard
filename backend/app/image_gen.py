"""Image generation for recipes using Ollama (Python 3.13+ compatible)."""
import base64
import re
from pathlib import Path
from typing import Optional
import httpx
from app.config import settings

# Create images directory
IMAGES_DIR = Path(__file__).parent.parent / "static" / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def generate_food_image(dish_name: str, style_hint: Optional[str] = None) -> str:
    """
    Generate food image for a dish using Ollama.
    
    Args:
        dish_name: Name of the dish
        style_hint: Optional style hint for image generation
    
    Returns:
        URL or path to the generated image
    """
    if settings.IMAGE_MODE == "ollama":
        return _generate_with_ollama(dish_name, style_hint)
    else:
        return _get_placeholder_image(dish_name)


def _get_placeholder_image(dish_name: str) -> str:
    """Return placeholder image URL."""
    return f"/static/images/placeholder.jpg"


def _generate_with_ollama(dish_name: str, style_hint: Optional[str] = None) -> str:
    """
    Generate image using Ollama with image generation model (Python 3.13+ compatible).
    
    Supported models:
    - abedalswaity7/flux-prompt:latest (prompt enhancement model)
    - Other Flux/Stable Diffusion models if available
    
    Install with: ollama pull abedalswaity7/flux-prompt:latest
    """
    try:
        # Build prompt
        prompt = f"High quality professional food photography of {dish_name} presented on a clean plate. Style: realistic, vibrant colors, appetizing, close-up, natural light, slight bokeh, 4k detail."
        if style_hint:
            prompt += f" Optional style hint: {style_hint}"
        
        # Try Ollama's image generation endpoint
        payload = {
            "model": settings.OLLAMA_IMAGE_MODEL,
            "prompt": prompt,
            "stream": False,
        }
        
        response = httpx.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=180.0
        )
        response.raise_for_status()
        data = response.json()
        
        # Check if response contains image data
        if "response" in data:
            response_text = data.get("response", "")
            
            # Check if this is a prompt enhancement model (returns text, not images)
            # flux-prompt models return enhanced prompts, not images
            if "flux-prompt" in settings.OLLAMA_IMAGE_MODEL.lower():
                print(f"⚠️  Note: '{settings.OLLAMA_IMAGE_MODEL}' is a prompt enhancement model, not an image generator.")
                print(f"   It returns enhanced prompts, not images. Using placeholder for now.")
                print(f"   For actual image generation, you may need a different model.")
                return _get_placeholder_image(dish_name)
            
            # Try to extract base64 image data
            if "data:image" in response_text or len(response_text) > 1000:
                try:
                    # Try to decode if it's base64
                    base64_match = re.search(r'data:image/[^;]+;base64,([A-Za-z0-9+/=]+)', response_text)
                    if base64_match:
                        image_data = base64_match.group(1)
                        image_bytes = base64.b64decode(image_data)
                    else:
                        # Try direct base64 decode
                        image_bytes = base64.b64decode(response_text)
                except:
                    print(f"⚠️  Ollama model '{settings.OLLAMA_IMAGE_MODEL}' may not be an image generation model.")
                    print(f"   Response was text, not an image. Using placeholder.")
                    return _get_placeholder_image(dish_name)
            else:
                print(f"⚠️  Ollama model '{settings.OLLAMA_IMAGE_MODEL}' returned text instead of an image.")
                print(f"   This model may be for prompt enhancement, not image generation.")
                return _get_placeholder_image(dish_name)
        elif "image" in data:
            # Direct image field
            image_data = data["image"]
            image_bytes = base64.b64decode(image_data)
        else:
            # Try alternative endpoint
            return _try_ollama_image_endpoint(dish_name, prompt)
        
        # Save image
        safe_name = "".join(c for c in dish_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        image_filename = f"{safe_name.replace(' ', '_')}.jpg"
        image_path = IMAGES_DIR / image_filename
        
        with open(image_path, "wb") as f:
            f.write(image_bytes)
        
        print(f"✅ Generated image: {image_filename}")
        return f"/static/images/{image_filename}"
            
    except httpx.HTTPError as e:
        print(f"Error calling Ollama for image: {e}")
        print(f"Make sure Ollama is running and you have the model installed:")
        print(f"  ollama pull {settings.OLLAMA_IMAGE_MODEL}")
        print(f"Note: Some models like 'flux-prompt' are for prompt enhancement, not image generation.")
        return _get_placeholder_image(dish_name)
    except Exception as e:
        print(f"Error generating image with Ollama: {e}")
        return _get_placeholder_image(dish_name)


def _try_ollama_image_endpoint(dish_name: str, prompt: str) -> str:
    """Try alternative Ollama image generation endpoints."""
    try:
        # Some Ollama setups might have /api/image endpoint
        payload = {
            "model": settings.OLLAMA_IMAGE_MODEL,
            "prompt": prompt,
        }
        
        response = httpx.post(
            f"{settings.OLLAMA_BASE_URL}/api/image",
            json=payload,
            timeout=180.0
        )
        response.raise_for_status()
        
        # Save image
        safe_name = "".join(c for c in dish_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        image_filename = f"{safe_name.replace(' ', '_')}.jpg"
        image_path = IMAGES_DIR / image_filename
        
        with open(image_path, "wb") as f:
            f.write(response.content)
        
        return f"/static/images/{image_filename}"
    except Exception:
        return _get_placeholder_image(dish_name)
