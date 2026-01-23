import os
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from api.main import app

# Add project root to path
sys.path.append(str(Path(__file__).parent))

client = TestClient(app)

def test_register_and_login():
    print("\n[TEST] Register new user...")
    fake_user = {
        "user_name": "testuser",
        "email": "test@example.com",
        "password": "secretpassword",
        "full_name": "Test User"
    }
    response = client.post("/auth/register", json=fake_user)
    
    # Handle case where user might already exist from previous run
    if response.status_code == 400 and "already registered" in response.text:
        print("User likely already exists, proceeding to login.")
    else:
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        print("✅ User registered successfully.")

    print("\n[TEST] Login...")
    login_data = {
        "username": "testuser",
        "password": "secretpassword"
    }
    response = client.post("/auth/token", data=login_data)
    assert response.status_code == 200
    token_data = response.json()
    access_token = token_data["access_token"]
    print("✅ Login successful. Token received.")
    
    print("\n[TEST] Access protected route...")
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["user_name"] == "testuser"
    assert "hashed_password" not in user_data  # Should not expose password
    assert user_data["id"] is not None
    assert isinstance(user_data["id"], int)
    print(f"✅ Protected route accessed. Hello {user_data['full_name']}! (User ID: {user_data['id']})")

if __name__ == "__main__":
    try:
        # Clean up database if needed, but for now we just run against it.
        if os.path.exists("checkmate.db"):
             os.remove("checkmate.db")
        
        # Explicitly create tables
        from api.database import create_db_and_tables
        import api.models # Ensure models are registered
        create_db_and_tables()
             
        test_register_and_login()
        print("\n🎉 API Verification Passed!")
    except Exception as e:
        print(f"\n❌ API Verification Failed: {e}")
        raise e
