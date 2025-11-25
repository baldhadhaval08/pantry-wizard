# PantryWizard+ — AI Health & Recipe Assistant

PantryWizard+ is a full-stack AI-powered health and recipe assistant that generates healthy, personalized recipes daily using ingredients you already have in your pantry. It helps you cook every day with what's available, tracks your nutrition, and provides weekly health reports.

## Features

- 🍳 **Daily AI Recipe Generation**: Get unique recipe suggestions every day based on your pantry ingredients
- 📦 **Pantry Management**: Track your available ingredients with easy CRUD operations
- 🎯 **Personalized Health Profiles**: Recipes tailored to your diet, allergies, and health goals
- 📊 **Weekly Health Reports**: Track calories, variety score, and get recommendations
- 🖼️ **Recipe Images**: AI-generated food images (with placeholder fallback)
- 🔄 **Non-Repetitive Recipes**: Smart algorithm ensures variety in daily suggestions
- 📱 **Responsive Design**: Beautiful UI that works on mobile, tablet, and desktop

## Prerequisites

Before starting, make sure you have:

- **Python 3.10+** (Python 3.13+ works great with Ollama!)
- **Node.js 18+** and npm (or pnpm/yarn)
- **Git** (to clone the repository)
- **Ollama** (for local AI - we'll install this in the setup)

---

## Complete Local Setup Guide

Follow these steps line by line to set up and run PantryWizard+ locally.

### Step 1: Clone and Navigate to Project

```bash
# If you haven't cloned yet, do:
# git clone <repository-url>
# cd pantry-wizard

# Navigate to project root
cd /usr/local/var/www/pantry-wizard
```

### Step 2: Install Ollama (For Local AI)

Ollama is required for local AI recipe generation. It works with any Python version including 3.13+.

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download and install from: https://ollama.com/download

**Verify installation:**
```bash
ollama --version
```

### Step 3: Start Ollama Server

Open a **new terminal window** and keep it running:

```bash
ollama serve
```

Leave this terminal open. Ollama will run on `http://localhost:11434`

### Step 4: Download an AI Model

In your **main terminal** (not the one running `ollama serve`), download a model:

```bash
# Recommended: Mistral (4.1GB, fast, good quality)
ollama pull mistral

# This will take a few minutes depending on your internet speed
# You'll see progress as it downloads
```

**Alternative models:**
```bash
ollama pull llama2        # Alternative (3.8GB)
ollama pull phi           # Smaller, faster (1.6GB)
ollama pull codellama     # Code-focused (3.8GB)
```

**Verify model is installed:**
```bash
ollama list
```

You should see `mistral` (or your chosen model) in the list.

### Step 5: Backend Setup

**5.1 Navigate to backend directory:**
```bash
cd backend
```

**5.2 Create Python virtual environment:**
```bash
python3 -m venv .venv
```

**5.3 Activate virtual environment:**

**macOS/Linux:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.venv\Scripts\activate
```

You should see `(.venv)` in your terminal prompt.

**5.4 Upgrade pip:**
```bash
python -m pip install --upgrade pip
```

**5.5 Install Python dependencies:**
```bash
pip install -r requirements.txt
```

This will install FastAPI, SQLModel, Pydantic, and other core dependencies.

**5.6 Install email validator (required):**
```bash
pip install email-validator
```

**5.7 Create environment file:**
```bash
# Copy the example file
cp ../.env.example .env

# Or create it manually
cat > .env << 'EOF'
DATABASE_URL=sqlite:///./pantry.db
JWT_SECRET=your-secret-key-change-in-production-$(openssl rand -hex 32)
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# LLM Configuration - Using Ollama for local AI
LLM_MODE=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral

# Image Generation
IMAGE_MODE=placeholder

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:3001"]
API_V1_PREFIX=/api
EOF
```

**5.8 Initialize the database:**
```bash
python -c "from app.database import init_db; init_db()"
```

You should see: `✅ Database initialized` or no errors.

**5.9 Start the backend server:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

**Keep this terminal running!** The backend is now available at:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Step 6: Frontend Setup

Open a **new terminal window** (keep backend and Ollama running).

**6.1 Navigate to frontend directory:**
```bash
cd /usr/local/var/www/pantry-wizard/frontend
```

**6.2 Install Node.js dependencies:**
```bash
npm install
```

This will install Next.js, React, TailwindCSS, and other frontend dependencies. It may take a few minutes.

**6.3 Create frontend environment file:**
```bash
cat > .env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_MOCK_MODE=false
EOF
```

**6.4 Start the frontend development server:**
```bash
npm run dev
```

You should see:
```
  ▲ Next.js 14.x.x
  - Local:        http://localhost:3000
  - ready started server on 0.0.0.0:3000
```

**Keep this terminal running!** The frontend is now available at http://localhost:3000

### Step 7: Verify Everything is Running

You should now have **3 terminals running**:

1. **Terminal 1**: Ollama server (`ollama serve`)
2. **Terminal 2**: Backend server (`uvicorn app.main:app ...`)
3. **Terminal 3**: Frontend server (`npm run dev`)

**Test the setup:**

**Backend health check:**
```bash
curl http://localhost:8000/health
```
Should return: `{"status":"healthy"}`

**Frontend check:**
Open your browser and go to: http://localhost:3000

You should see the PantryWizard+ login page.

**Ollama check:**
```bash
curl http://localhost:11434/api/tags
```
Should return a JSON list of available models.

---

## Using the Application

### First Time Setup

1. **Open the app**: Go to http://localhost:3000 in your browser

2. **Register a new account**:
   - Click "Sign up" or go to http://localhost:3000/register
   - Fill in your information:
     - Step 1: Name, Email, Password
     - Step 2: Height (cm), Weight (kg), Age
     - Step 3: Diet type, Allergies, Health goal
   - Click "Create Account"

3. **Add pantry items**:
   - After logging in, go to "Pantry" page
   - Click "Add Item"
   - Add ingredients you have (e.g., "Tomato", "5", "pieces")
   - Use "Quick Add" buttons for common items

4. **Get your first recipe**:
   - Go to "Dashboard" - you'll see today's recipe suggestion
   - Or go to "Generate" to create a custom recipe
   - Click "Generate Recipe" and wait for AI to create it

5. **Save and track**:
   - Click "Mark as Cooked" to save recipes to history
   - View "History" to see all your cooked recipes
   - Check "Reports" for weekly nutrition insights

---

## Configuration Options

### LLM Modes

**Ollama Mode (Recommended - Default):**
- Works with Python 3.13+
- No Python ML packages needed
- Fast and easy setup
- Configure in `.env`:
  ```env
  LLM_MODE=ollama
  OLLAMA_BASE_URL=http://localhost:11434
  OLLAMA_MODEL=mistral
  ```

**API Mode:**
- Works with any Python version
- Requires API key
- Configure in `.env`:
  ```env
  LLM_MODE=api
  LLM_API_URL=https://api.openai.com/v1/chat/completions
  LLM_API_KEY=your-api-key-here
  ```

**Local Transformers Mode (Python 3.8-3.12 only):**
- Requires PyTorch (not available for Python 3.13+)
- Uncomment ML packages in `requirements.txt`
- Configure in `.env`:
  ```env
  LLM_MODE=local
  LLM_MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.2
  ```

### Available Ollama Models

- `mistral` - Best balance (4.1GB) ⭐ Recommended
- `llama2` - Good alternative (3.8GB)
- `phi` - Smaller, faster (1.6GB)
- `codellama` - Code-focused (3.8GB)
- `neural-chat` - Conversational (4.1GB)

See all models: https://ollama.com/library

---

## Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn app.main:app --reload --port 8001
```

**Database errors:**
```bash
# Reset database
cd backend
rm pantry.db
python -c "from app.database import init_db; init_db()"
```

**Import errors:**
```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend Issues

**Port 3000 already in use:**
```bash
# Use a different port
npm run dev -- -p 3001
```

**Module not found:**
```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

**Node version too old:**
```bash
# Check your Node version
node --version

# Should be 18+ for Next.js 14
# If not, update Node.js or use nvm:
nvm install 18
nvm use 18
```

### Ollama Issues

**Ollama not found:**
```bash
# Check if installed
which ollama

# If not, reinstall:
# macOS: brew install ollama
# Linux: curl -fsSL https://ollama.com/install.sh | sh
```

**Model not found:**
```bash
# Check available models
ollama list

# Pull the model if missing
ollama pull mistral
```

**Connection refused:**
```bash
# Make sure Ollama server is running
ollama serve

# Test connection
curl http://localhost:11434/api/tags
```

**Slow recipe generation:**
- Use a smaller model: `ollama pull phi`
- Or use API mode with a faster service
- Check your system resources (CPU/RAM)

### General Issues

**CORS errors:**
- Make sure backend `.env` has: `CORS_ORIGINS=["http://localhost:3000"]`
- Restart backend after changing `.env`

**Authentication errors:**
- Clear browser localStorage
- Make sure JWT_SECRET is set in backend `.env`
- Try registering a new account

**Recipe generation fails:**
- Check Ollama is running: `curl http://localhost:11434/api/tags`
- Check backend logs for errors
- Try API mode as fallback

---

## Project Structure

```
pantrywizard/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI application
│   │   ├── config.py         # Configuration management
│   │   ├── database.py        # Database setup
│   │   ├── models.py          # SQLModel database models
│   │   ├── schemas.py         # Pydantic request/response schemas
│   │   ├── auth.py            # JWT authentication
│   │   ├── recipe_ai.py       # LLM integration (Ollama/API/Local)
│   │   ├── image_gen.py       # Image generation
│   │   ├── utils.py           # Utility functions
│   │   └── routers/           # API route handlers
│   │       ├── users.py        # Authentication routes
│   │       ├── pantry.py       # Pantry management routes
│   │       ├── recipes.py      # Recipe generation routes
│   │       └── history.py      # History and reports routes
│   ├── static/images/         # Generated recipe images
│   ├── tests/                 # Backend tests
│   ├── .env                   # Backend environment variables
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── app/                   # Next.js app directory
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Landing page
│   │   ├── login/             # Login page
│   │   ├── register/          # Registration page
│   │   ├── dashboard/         # Dashboard page
│   │   ├── pantry/            # Pantry management page
│   │   ├── generate/          # Recipe generation page
│   │   ├── history/           # Recipe history page
│   │   └── reports/           # Health reports page
│   ├── components/            # React components
│   │   ├── ui/                # shadcn/ui components
│   │   ├── RecipeCard.tsx     # Recipe display component
│   │   ├── PantryCard.tsx     # Pantry item component
│   │   ├── StatCard.tsx       # Statistics card component
│   │   └── Navbar.tsx         # Navigation component
│   ├── lib/                   # Utilities
│   │   ├── api.ts             # API client
│   │   ├── auth.ts            # Authentication utilities
│   │   └── utils.ts           # Helper functions
│   ├── .env.local             # Frontend environment variables
│   └── package.json           # Node.js dependencies
├── .env.example               # Environment variables template
└── README.md                  # This file
```

---

## API Documentation

Once the backend is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide interactive API documentation where you can test endpoints directly.

---

## Development Commands

### Backend

```bash
cd backend
source .venv/bin/activate

# Run server
uvicorn app.main:app --reload

# Run tests
pytest tests/test_endpoints.py -v

# Initialize database
python -c "from app.database import init_db; init_db()"
```

### Frontend

```bash
cd frontend

# Development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

---

## Quick Reference

**Start all services:**
1. Terminal 1: `ollama serve`
2. Terminal 2: `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload`
3. Terminal 3: `cd frontend && npm run dev`

**Access points:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Ollama: http://localhost:11434

**Stop services:**
- Press `Ctrl+C` in each terminal
- Or: `pkill -f "ollama serve"` and `pkill -f "uvicorn"` and `pkill -f "next dev"`

---

## License

MIT License - feel free to use and modify!

## Contributing

Contributions welcome! Please open issues or pull requests.

---

## Need Help?

- Check the Troubleshooting section above
- Review API docs at http://localhost:8000/docs
- Check backend logs in the terminal running uvicorn
- Check frontend logs in the terminal running npm
- Verify Ollama is running: `curl http://localhost:11434/api/tags`
