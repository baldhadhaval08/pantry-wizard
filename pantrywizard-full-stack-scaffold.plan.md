<!-- 95687ce4-b438-4a39-8eb8-2028952aba88 3ca9f7e4-d596-4c35-b58d-76fca97b0e8d -->
# PantryWizard+ Implementation Plan

## Overview

Build a complete full-stack AI Health & Recipe Assistant that generates healthy recipes daily using ingredients users already have in their pantry, with FastAPI backend and Next.js frontend, supporting both local and API-based LLM integration.

## Phase A: Backend Scaffolding

### Core Infrastructure

- **backend/app/config.py**: Environment configuration reading from .env:
  - `DATABASE_URL` (default: `sqlite:///./pantry.db`)
  - `JWT_SECRET` for token signing
  - `LLM_MODE` (`local` or `api`)
  - `LLM_API_URL`, `LLM_API_KEY` for API mode
  - `LLM_MODEL_PATH` for local mode
  - `SD_MODEL_PATH` for Stable Diffusion
  - `IMAGE_MODE` (`placeholder|local_sd|api`)
  - `USE_CUDA` for GPU acceleration
- **backend/app/database.py**: SQLModel engine setup with SQLite default, session management
- **backend/app/models.py**: SQLModel models:
  - `User`: id, name, email, password_hash, height_cm, weight_kg, age, diet_type, allergies, goal, created_at
  - `PantryItem`: id, user_id, name, quantity, unit, created_at
  - `RecipeHistory`: id, user_id, recipe_name, recipe_json (full JSON), calories, created_at
  - `DailySuggestion`: id, user_id, recipe_id, suggested_at
- **backend/app/schemas.py**: Pydantic request/response schemas for all endpoints
- **backend/app/main.py**: FastAPI app initialization with CORS middleware, router registration, OpenAPI docs at `/docs`

### Authentication

- **backend/app/auth.py**: 
  - JWT token generation/validation functions
  - Password hashing with bcrypt
  - `get_current_user` dependency for protected routes
- **backend/app/routers/users.py**: 
  - `POST /api/auth/register`: Register with profile (name, email, password, height_cm, weight_kg, age, diet_type, allergies, goal)
  - `POST /api/auth/login`: Returns JWT token
  - `GET /api/users/profile`: Get current user profile

### Core Routers

- **backend/app/routers/pantry.py**: 
  - `GET /api/pantry`: List all pantry items for current user
  - `POST /api/pantry`: Add new pantry item (name, quantity, unit)
  - `PUT /api/pantry/{id}`: Update pantry item
  - `DELETE /api/pantry/{id}`: Delete pantry item
- **backend/app/routers/recipes.py**: 
  - `POST /api/recipes/generate`: Generate recipe from user's pantry ingredients + preferences
    - Body: `{use_pantry: true, extra_ingredients: [], preferences: {cuisine, spice_level}, avoid_repeats: true}`
    - Returns: JSON recipe + image URL
  - `GET /api/recipes/daily`: Fetch or generate daily unique recipe suggestion using current pantry items
    - Automatically uses all pantry items from user's pantry
    - Stores as DailySuggestion to track daily recommendations
    - Ensures non-repetitive recipes based on history
  - `POST /api/recipes/save`: Save recipe to history (mark as cooked)
    - Body: `{recipe_json: {...}, calories: number}`
- **backend/app/routers/history.py**: 
  - `GET /api/history`: List user recipe history with filters (week/month)
  - `GET /api/reports/weekly`: Generate weekly summary (calories sum, variety score, top ingredients)

### Utilities

- **backend/app/utils.py**: 
  - `calculate_bmi(height_cm, weight_kg)`: BMI calculation
  - `estimate_calories_from_ingredients(ingredients)`: Heuristic calorie estimation if AI doesn't return calories
- **backend/requirements.txt**: All Python dependencies (fastapi, uvicorn, sqlmodel, python-jose, passlib, transformers, torch, diffusers, etc.)

## Phase B: AI Integration

### LLM Integration

- **backend/app/recipe_ai.py**: 
  - `LLMClient` abstract base class with two implementations:
    - `LocalLLMClient`: Uses transformers library with local model (Mistral/LLAMA)
    - `APILLMClient`: Calls external API (OpenRouter/OpenAI/Anthropic)
  - `generate_recipe_for_user(user, pantry_items, preferences, history)`: 
    - Builds detailed prompt using template below
    - Calls appropriate LLM client based on `LLM_MODE` config
    - Validates response against Pydantic schema
    - Returns structured JSON: name, description, ingredients, steps, time_minutes, difficulty, calories, macros, health_justification
  - `ensure_non_repetitive(history, candidate)`: 
    - Fuzzy string similarity check against last N saved recipes
    - Prevents recipe repetition
  - **Prompt Template** (detailed):
    ```
    You are a health-focused chef AI. Output only valid JSON.
    
    User profile:
  - Name: {user.name}
  - Age: {user.age}
  - Height_cm: {user.height_cm}
  - Weight_kg: {user.weight_kg}
  - BMI: {bmi}
  - Diet: {user.diet_type}
  - Allergies: {user.allergies}
  - Health goal: {user.goal}
    
    Pantry ingredients available (list): {pantry_list}
    Recent cooked recipes (titles): {recent_titles}
    
    Task:
  - Using only the given pantry ingredients, generate ONE healthy recipe optimized for the user's health goal.
  - Avoid allergies and disliked items.
  - Ensure variety: do not repeat any recipe title that is similar to the recent titles.
  - If a required staple is missing (salt, oil, water), assume small amounts are available.
    
    Return JSON EXACTLY in this shape:
    {
      "name": "Dish name",
      "description": "Short description 1-2 sentences",
      "ingredients": [{"name":"onion", "amount":"1 medium"}, ...],
      "steps": ["Step 1 ...", ...],
      "time_minutes": 30,
      "difficulty": "easy|medium|hard",
      "calories": 420,
      "macros": {"protein_g":20, "carbs_g":50, "fat_g":10},
      "health_justification": "Brief sentence explaining why this suits the user's goals."
    }
    ```


### Image Generation

- **backend/app/image_gen.py**: 
  - `generate_food_image(dish_name, style_hint)`: 
    - If `IMAGE_MODE=local_sd`: Uses diffusers pipeline with Stable Diffusion v1.5
    - If `IMAGE_MODE=placeholder`: Returns placeholder image URL
    - If `IMAGE_MODE=api`: Calls external image API (optional)
  - Saves generated images to `backend/static/images/`
  - Returns image URL for frontend display
  - **Image Prompt Template**:
    ```
    High quality professional food photography of {dish_name} presented on a clean plate.
    Style: realistic, vibrant colors, appetizing, close-up, natural light, slight bokeh, 4k detail.
    Optional style hint: {style_hint}
    ```


## Phase C: Frontend Scaffolding

### Next.js Setup

- **frontend/package.json**: Dependencies (Next.js 14+, TypeScript, TailwindCSS, shadcn/ui, Framer Motion, Lucide icons, axios)
- **frontend/tailwind.config.js**: Custom color palette:
  - Primary: `#10B981` (emerald)
  - Accent: `#FBBF24` (amber)
  - Neutral backgrounds with dark mode support
  - Border radius: `rounded-2xl`, Shadows: `shadow-lg`
- **frontend/app/layout.tsx**: Root layout with providers, metadata
- **frontend/app/page.tsx**: Landing page with redirect to dashboard if authenticated

### Authentication Pages

- **frontend/app/login/page.tsx**: Login form with email/password, JWT storage in HttpOnly cookie or localStorage
- **frontend/app/register/page.tsx**: Multi-step registration form:
  - Step 1: Basic info (name, email, password)
  - Step 2: Profile (height_cm, weight_kg, age)
  - Step 3: Preferences (diet_type, allergies, goal)

### Core Pages

- **frontend/app/dashboard/page.tsx**: 
  - Welcome card with user name
  - Daily recipe suggestion card (prominent, calls `/api/recipes/daily`)
  - Quick stats: meals cooked this week, total calories, pantry size
  - Three-column grid on desktop, responsive on mobile
- **frontend/app/pantry/page.tsx**: 
  - Add ingredient modal (name, quantity, unit)
  - List of pantry items with search functionality
  - Quick add buttons for common ingredients
  - Delete/edit actions
- **frontend/app/generate/page.tsx**: 
  - Display current pantry items
  - Preferences selector (cuisine, spice level)
  - "Generate Recipe" button (calls `/api/recipes/generate`)
  - Display generated recipe as vibrant card with:
    - Recipe image
    - Name, description, calories, macros
    - Expandable steps
    - "Save Recipe" / "Mark as Cooked" / "Regenerate" buttons
- **frontend/app/history/page.tsx**: 
  - Chronological list of saved recipes
  - Filter by week/month
  - Recipe cards with date, nutrition info
- **frontend/app/reports/page.tsx**: 
  - Weekly report display:
    - Total calories consumed
    - Variety score calculation
    - Top ingredients used
    - Bar chart for calories over week
    - Pie chart for macro distribution
  - Simple recommendations based on data

### Components

- **frontend/components/ui/**: shadcn/ui components setup (Button, Card, Dialog, Input, Select, etc.)
- **frontend/components/RecipeCard.tsx**: 
  - Displays recipe with image, title, description
  - Calories and macros display
  - Expandable steps section
  - Action buttons (Save, Cooked, Regenerate)
  - Framer Motion hover animations
- **frontend/components/PantryCard.tsx**: 
  - Pantry item display with name, quantity, unit
  - Edit/delete actions
- **frontend/components/StatCard.tsx**: 
  - Small stat card with icon (Lucide)
  - Displays number and label
- **frontend/components/Navbar.tsx**: 
  - Navigation with auth state
  - Links to all pages
  - Logout functionality

### API Integration

- **frontend/lib/api.ts**: 
  - Axios instance with base URL
  - JWT token injection from storage
  - API wrapper functions for all endpoints
  - Error handling and retry logic
  - Mock mode fallback if backend unreachable
- **frontend/lib/auth.ts**: 
  - Token storage/retrieval utilities
  - Auth state management
  - Protected route helpers

## Phase D: Integration & Polish

### Testing

- **backend/tests/test_endpoints.py**: Pytest tests covering:
  - Auth: register, login, JWT validation
  - Pantry: CRUD operations
  - Recipes: generation, daily suggestion, save
  - History: retrieval, weekly reports
- Basic test coverage for core flows

### Documentation

- **README.md**: Comprehensive documentation including:
  - Project description
  - Local dev setup for backend (venv, pip install, uvicorn)
  - Local dev setup for frontend (pnpm install, pnpm dev)
  - Environment variables explanation
  - How to switch between local LLM and API LLM
  - Troubleshooting tips (GPU issues, model download, memory)
  - Quick demo flow walkthrough
- **.env.example**: All required environment variables with comments:
  - Database configuration
  - JWT secret
  - LLM mode and API keys
  - Image generation settings
  - Optional Docker settings
- **docker-compose.yml** (optional): Docker setup for easy dev environment

### Polish & Responsive Design

- Responsive breakpoints: 320px (mobile), 768px (tablet), 1280px (desktop)
- Mobile: Single column, large touch targets, bottom navigation
- Tablet: Two-column layouts
- Desktop: Three-column grid for dashboard
- Framer Motion animations:
  - Page transitions
  - Card hover effects
  - Loading states
- Accessibility:
  - Form labels for all inputs
  - ARIA labels where necessary
  - Keyboard navigation support
  - Color contrast compliance
- Error handling:
  - User-friendly error messages
  - Loading states for async operations
  - Network error fallbacks

## File Structure

```
pantrywizard/
├─ backend/
│  ├─ app/
│  │  ├─ main.py
│  │  ├─ config.py
│  │  ├─ database.py
│  │  ├─ models.py
│  │  ├─ schemas.py
│  │  ├─ auth.py
│  │  ├─ recipe_ai.py
│  │  ├─ image_gen.py
│  │  ├─ utils.py
│  │  └─ routers/
│  │     ├─ users.py
│  │     ├─ pantry.py
│  │     ├─ recipes.py
│  │     └─ history.py
│  ├─ static/
│  │  └─ images/
│  ├─ tests/
│  │  └─ test_endpoints.py
│  └─ requirements.txt
├─ frontend/
│  ├─ app/
│  │  ├─ layout.tsx
│  │  ├─ page.tsx
│  │  ├─ login/
│  │  │  └─ page.tsx
│  │  ├─ register/
│  │  │  └─ page.tsx
│  │  ├─ dashboard/
│  │  │  └─ page.tsx
│  │  ├─ pantry/
│  │  │  └─ page.tsx
│  │  ├─ generate/
│  │  │  └─ page.tsx
│  │  ├─ history/
│  │  │  └─ page.tsx
│  │  └─ reports/
│  │     └─ page.tsx
│  ├─ components/
│  │  ├─ ui/
│  │  ├─ RecipeCard.tsx
│  │  ├─ PantryCard.tsx
│  │  ├─ StatCard.tsx
│  │  └─ Navbar.tsx
│  ├─ lib/
│  │  ├─ api.ts
│  │  └─ auth.ts
│  ├─ styles/
│  ├─ package.json
│  └─ tailwind.config.js
├─ .env.example
├─ README.md
└─ docker-compose.yml (optional)
```

## Key Implementation Details

1. **Daily Recipe Generation**: The `/api/recipes/daily` endpoint automatically fetches user's current pantry items and generates a unique recipe daily. This is the core feature that helps users cook every day using ingredients they already have.

2. **LLM Modularity**: Abstract `LLMClient` class allows seamless switching between local transformers (Mistral/LLAMA) and API calls (OpenRouter/OpenAI/Anthropic) via `LLM_MODE` config.

3. **JSON Validation**: Strict Pydantic models for LLM responses prevent crashes from malformed AI output.

4. **Image Fallback**: Placeholder mode for environments without GPU/Stable Diffusion support.

5. **Recipe Caching**: Cache generated recipes to avoid rapid re-generation of same prompts.

6. **Non-Repetitive Logic**: Fuzzy string matching ensures daily suggestions don't repeat recent recipes.

7. **Security**: JWT in HttpOnly cookies (preferred) or localStorage, password hashing with bcrypt.

8. **Responsive Design**: Mobile-first approach with breakpoints, touch-friendly targets.

9. **Color Theme**: Emerald (#10B981) primary, Amber (#FBBF24) accent, rounded-2xl borders, shadow-lg.

10. **Pantry-First Approach**: All recipe generation uses pantry items as the primary ingredient source, ensuring users can actually cook with what they have.

## Acceptance Criteria

- ✅ Auth: Register + login returns JWT token
- ✅ Pantry: Add/list/update/delete items works for authenticated users
- ✅ Recipe generation: `/api/recipes/generate` returns valid JSON recipe + image URL
- ✅ Daily recipe: `/api/recipes/daily` generates unique recipe from current pantry items
- ✅ History: Saved recipes display with date and nutrition info
- ✅ Reports: `/api/reports/weekly` returns summary with calories and variety score
- ✅ UI: Fully responsive at 320px, 768px, 1280px breakpoints
- ✅ Accessibility: Forms have labels, ARIA where necessary
- ✅ Animations: Framer Motion transitions and hover effects working
- ✅ Error handling: User-friendly messages and loading states

### To-dos

- [ ] Create backend core infrastructure: config.py (env vars), database.py (SQLModel engine), models.py (User, PantryItem, RecipeHistory, DailySuggestion), schemas.py (Pydantic schemas), main.py (FastAPI app with CORS)
- [ ] Implement authentication: auth.py (JWT, password hashing, get_current_user), users.py router (register, login, profile endpoints)
- [ ] Create pantry router: pantry.py with GET (list), POST (add), PUT (update), DELETE (delete) endpoints for pantry items
- [ ] Create recipes router: recipes.py with POST /generate (from pantry), GET /daily (daily unique recipe from pantry), POST /save (to history)
- [ ] Create history router: history.py with GET /history (filtered list), GET /reports/weekly (weekly summary with calories, variety score)
- [ ] Implement AI integration: recipe_ai.py with LLMClient abstraction (LocalLLMClient, APILLMClient), generate_recipe_for_user() with detailed prompt template, ensure_non_repetitive() logic
- [ ] Implement image generation: image_gen.py with diffusers pipeline for local SD, placeholder fallback, image saving to static/images/
- [ ] Create utility functions: utils.py with calculate_bmi(), estimate_calories_from_ingredients() helpers
- [ ] Create requirements.txt with all Python dependencies (fastapi, uvicorn, sqlmodel, transformers, torch, diffusers, etc.)
- [ ] Write pytest tests: test_endpoints.py covering auth, pantry CRUD, recipe generation, daily suggestions, history, reports
- [ ] Setup Next.js frontend: package.json (dependencies), tailwind.config.js (color palette), app/layout.tsx, TypeScript config
- [ ] Create authentication pages: login/page.tsx and register/page.tsx with multi-step form (basic info, profile, preferences)
- [ ] Create API integration layer: lib/api.ts (Axios instance, API wrappers, mock mode) and lib/auth.ts (JWT handling, auth state)
- [ ] Build UI components: RecipeCard.tsx, PantryCard.tsx, StatCard.tsx, Navbar.tsx, setup shadcn/ui components directory
- [ ] Create dashboard page: dashboard/page.tsx with welcome card, daily recipe suggestion card (prominent), quick stats (meals, calories, pantry size)
- [ ] Create pantry page: pantry/page.tsx with add modal, list with search, quick add buttons, edit/delete actions
- [ ] Create generate page: generate/page.tsx with pantry display, preferences selector, Generate button, recipe card with Save/Cooked/Regenerate
- [ ] Create history page: history/page.tsx with chronological recipe cards, week/month filters
- [ ] Create reports page: reports/page.tsx with weekly report, variety score, bar chart (calories), pie chart (macros), recommendations
- [ ] Add Framer Motion animations: page transitions, card hover effects, loading states across all pages
- [ ] Implement responsive design: mobile (320px single column), tablet (768px two columns), desktop (1280px three columns), touch-friendly targets
- [ ] Add accessibility features: form labels, ARIA labels, keyboard navigation, color contrast compliance
- [ ] Connect frontend to backend: wire up all API calls, handle errors with user-friendly messages, add loading states, implement mock mode fallback
- [ ] Create documentation: README.md (setup instructions, env vars, LLM switching, troubleshooting), .env.example (all variables with comments)
- [ ] Create optional docker-compose.yml for easy dev environment setup with backend and frontend services