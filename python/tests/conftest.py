import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
import sys
import tempfile

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, Base, get_db
from auth import User, hash_password

# Create a test database
@pytest.fixture(scope="session")
def test_db():
    # Create a temporary SQLite database
    fd, path = tempfile.mkstemp()
    os.close(fd)
    
    # Create the database engine
    engine = create_engine(
        f"sqlite:///{path}",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create a session factory
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create a test database session
    db = TestingSessionLocal()
    
    # Create test data
    test_user = User(
        email="test@example.com",
        password=hash_password("Test123!"),
        full_name="Test User",
        is_active=True,
        is_verified=True
    )
    db.add(test_user)
    db.commit()
    
    yield db
    
    # Clean up
    db.close()
    os.unlink(path)

# Override the get_db dependency
@pytest.fixture(scope="function")
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.rollback()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

# Test user data
@pytest.fixture
def test_user_data():
    return {
        "email": "test@example.com",
        "password": "Test123!",
        "full_name": "Test User"
    }

# Test user credentials
@pytest.fixture
def test_user_credentials():
    return {
        "username": "test@example.com",
        "password": "Test123!"
    }

# Test account data
@pytest.fixture
def test_account_data():
    return {
        "number": "1234567890",
        "name": "Test Account",
        "address": "Test Address",
        "status": "active"
    } 