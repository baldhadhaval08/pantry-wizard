"""Image generation for recipes using Stable Diffusion or placeholders."""
import os
from pathlib import Path
from typing import Optional
from app.config import settings

# Create images directory
IMAGES_DIR = Path(__file__).parent.parent / "static" / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def generate_food_image(dish_name: str, style_hint: Optional[str] = None) -> str:
    """
    Generate food image for a dish.
    
    Args:
        dish_name: Name of the dish
        style_hint: Optional style hint for image generation
    
    Returns:
        URL or path to the generated image
    """
    if settings.IMAGE_MODE == "placeholder":
        return _get_placeholder_image(dish_name)
    elif settings.IMAGE_MODE == "local_sd":
        return _generate_with_stable_diffusion(dish_name, style_hint)
    elif settings.IMAGE_MODE == "api":
        return _generate_with_api(dish_name, style_hint)
    else:
        return _get_placeholder_image(dish_name)


def _get_placeholder_image(dish_name: str) -> str:
    """Return placeholder image URL."""
    # Use a food placeholder service or local placeholder
    # For now, return a placeholder URL
    return f"/static/images/placeholder.jpg"


def _generate_with_stable_diffusion(dish_name: str, style_hint: Optional[str] = None) -> str:
    """Generate image using local Stable Diffusion."""
    try:
        from diffusers import StableDiffusionPipeline
        import torch
        from PIL import Image
        
        device = "cuda" if settings.USE_CUDA and torch.cuda.is_available() else "cpu"
        
        # Build prompt
        prompt = f"High quality professional food photography of {dish_name} presented on a clean plate. Style: realistic, vibrant colors, appetizing, close-up, natural light, slight bokeh, 4k detail."
        if style_hint:
            prompt += f" Optional style hint: {style_hint}"
        
        # Load pipeline
        model_path = settings.SD_MODEL_PATH or settings.SD_MODEL_NAME
        print(f"Loading Stable Diffusion model from {model_path}...")
        
        pipe = StableDiffusionPipeline.from_pretrained(
            model_path,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32
        )
        pipe = pipe.to(device)
        
        # Generate image
        print(f"Generating image for: {dish_name}")
        image = pipe(prompt, num_inference_steps=20, guidance_scale=7.5).images[0]
        
        # Save image
        safe_name = "".join(c for c in dish_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        image_filename = f"{safe_name.replace(' ', '_')}.jpg"
        image_path = IMAGES_DIR / image_filename
        image.save(image_path, "JPEG", quality=85)
        
        return f"/static/images/{image_filename}"
    except Exception as e:
        print(f"Error generating image with Stable Diffusion: {e}")
        print("Falling back to placeholder")
        return _get_placeholder_image(dish_name)


def _generate_with_api(dish_name: str, style_hint: Optional[str] = None) -> str:
    """Generate image using external API (placeholder for now)."""
    # This would call an external image generation API
    # For now, fall back to placeholder
    return _get_placeholder_image(dish_name)

