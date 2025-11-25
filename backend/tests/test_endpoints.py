"""Pytest tests for API endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from app.main import app
from app.database import get_session
from app.models import User
from app.auth import get_password_hash


# Test database
@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session
    
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    user = User(
        name="Test User",
        email="test@example.com",
        password_hash=get_password_hash("testpassword"),
        height_cm=170.0,
        weight_kg=70.0,
        age=30,
        diet_type="omnivore",
        allergies="peanuts",
        goal="weight_loss"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def test_register(client: TestClient):
    """Test user registration."""
    response = client.post(
        "/api/auth/register",
        json={
            "name": "New User",
            "email": "newuser@example.com",
            "password": "password123",
            "height_cm": 175.0,
            "weight_kg": 75.0,
            "age": 25,
            "diet_type": "vegetarian",
            "allergies": None,
            "goal": "maintain"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate_email(client: TestClient, test_user: User):
    """Test registration with duplicate email."""
    response = client.post(
        "/api/auth/register",
        json={
            "name": "Another User",
            "email": test_user.email,
            "password": "password123"
        }
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_login(client: TestClient, test_user: User):
    """Test user login."""
    response = client.post(
        "/api/auth/login",
        json={
            "email": test_user.email,
            "password": "testpassword"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_login_invalid_credentials(client: TestClient, test_user: User):
    """Test login with invalid credentials."""
    response = client.post(
        "/api/auth/login",
        json={
            "email": test_user.email,
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401


def test_get_profile(client: TestClient, test_user: User):
    """Test getting user profile."""
    # Login first
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": test_user.email,
            "password": "testpassword"
        }
    )
    token = login_response.json()["access_token"]
    
    # Get profile
    response = client.get(
        "/api/auth/profile",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["name"] == test_user.name


def test_add_pantry_item(client: TestClient, test_user: User):
    """Test adding pantry item."""
    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"email": test_user.email, "password": "testpassword"}
    )
    token = login_response.json()["access_token"]
    
    # Add pantry item
    response = client.post(
        "/api/pantry",
        json={"name": "Tomato", "quantity": 5.0, "unit": "pieces"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Tomato"
    assert data["quantity"] == 5.0


def test_list_pantry_items(client: TestClient, test_user: User):
    """Test listing pantry items."""
    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"email": test_user.email, "password": "testpassword"}
    )
    token = login_response.json()["access_token"]
    
    # Add item first
    client.post(
        "/api/pantry",
        json={"name": "Onion", "quantity": 2.0, "unit": "pieces"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # List items
    response = client.get(
        "/api/pantry",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_delete_pantry_item(client: TestClient, test_user: User):
    """Test deleting pantry item."""
    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"email": test_user.email, "password": "testpassword"}
    )
    token = login_response.json()["access_token"]
    
    # Add item
    add_response = client.post(
        "/api/pantry",
        json={"name": "Carrot", "quantity": 3.0, "unit": "pieces"},
        headers={"Authorization": f"Bearer {token}"}
    )
    item_id = add_response.json()["id"]
    
    # Delete item
    response = client.delete(
        f"/api/pantry/{item_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 204


def test_generate_recipe(client: TestClient, test_user: User):
    """Test recipe generation."""
    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"email": test_user.email, "password": "testpassword"}
    )
    token = login_response.json()["access_token"]
    
    # Add pantry items
    client.post(
        "/api/pantry",
        json={"name": "Chicken", "quantity": 500.0, "unit": "grams"},
        headers={"Authorization": f"Bearer {token}"}
    )
    client.post(
        "/api/pantry",
        json={"name": "Rice", "quantity": 200.0, "unit": "grams"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Generate recipe
    response = client.post(
        "/api/recipes/generate",
        json={
            "use_pantry": True,
            "preferences": {"cuisine": "any", "spice_level": "medium"},
            "avoid_repeats": True
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "recipe" in data
    assert "image_url" in data
    assert "name" in data["recipe"]


def test_get_daily_recipe(client: TestClient, test_user: User):
    """Test daily recipe generation."""
    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"email": test_user.email, "password": "testpassword"}
    )
    token = login_response.json()["access_token"]
    
    # Add pantry items
    client.post(
        "/api/pantry",
        json={"name": "Eggs", "quantity": 6.0, "unit": "pieces"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Get daily recipe
    response = client.get(
        "/api/recipes/daily",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "recipe" in data
    assert "image_url" in data


def test_save_recipe(client: TestClient, test_user: User):
    """Test saving recipe to history."""
    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"email": test_user.email, "password": "testpassword"}
    )
    token = login_response.json()["access_token"]
    
    # Save recipe
    recipe_data = {
        "name": "Test Recipe",
        "description": "A test recipe",
        "ingredients": [{"name": "test", "amount": "1 cup"}],
        "steps": ["Step 1", "Step 2"],
        "time_minutes": 30,
        "difficulty": "easy",
        "calories": 300,
        "macros": {"protein_g": 20, "carbs_g": 30, "fat_g": 10},
        "health_justification": "Test justification"
    }
    
    response = client.post(
        "/api/recipes/save",
        json={"recipe_json": recipe_data, "calories": 300},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["recipe_name"] == "Test Recipe"


def test_get_history(client: TestClient, test_user: User):
    """Test getting recipe history."""
    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"email": test_user.email, "password": "testpassword"}
    )
    token = login_response.json()["access_token"]
    
    # Save a recipe first
    recipe_data = {
        "name": "History Test Recipe",
        "description": "Test",
        "ingredients": [],
        "steps": [],
        "time_minutes": 20,
        "difficulty": "easy",
        "calories": 200,
        "macros": {"protein_g": 10, "carbs_g": 20, "fat_g": 5},
        "health_justification": "Test"
    }
    client.post(
        "/api/recipes/save",
        json={"recipe_json": recipe_data},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Get history
    response = client.get(
        "/api/history",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_weekly_report(client: TestClient, test_user: User):
    """Test getting weekly report."""
    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"email": test_user.email, "password": "testpassword"}
    )
    token = login_response.json()["access_token"]
    
    # Get report
    response = client.get(
        "/api/history/reports/weekly",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_calories" in data
    assert "variety_score" in data
    assert "meals_count" in data

