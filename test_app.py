import pytest
from .app import app
from unittest.mock import patch

# Use pytest's fixture for setting up the test client
@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Test that the home page loads successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Home" in response.data  # Adjust if there's a specific text on your home page

def test_list_users(client):
    """Test that the users list page loads successfully."""
    with patch('app.data_manager.get_all_users', return_value=[]):
        response = client.get('/users')
        assert response.status_code == 200
        assert b"No users found" in response.data  # Adjust according to your template

def test_user_profile_404(client):
    """Test that a non-existent user profile triggers a 404."""
    with patch('app.data_manager.get_user_by_id', return_value=None):
        response = client.get('/users/999')  # Using a non-existent user_id
        assert response.status_code == 404
        assert b"User not found" in response.data  # Adjust according to your 404 template

def test_custom_404_handler(client):
    """Test the custom 404 handler using a dedicated route."""
    response = client.get('/test-404')
    assert response.status_code == 404
    assert b"Page Not Found" in response.data  # Adjust according to your 404 template
