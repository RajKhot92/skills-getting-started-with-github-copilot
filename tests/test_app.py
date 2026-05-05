from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    """Test that root path redirects to static index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Redirect
    assert "static/index.html" in response.headers.get("location", "")

def test_get_activities():
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "description" in data["Chess Club"]
    assert "participants" in data["Chess Club"]

def test_signup_success():
    """Test successful signup"""
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    result = response.json()
    assert "Signed up" in result["message"]
    
    # Verify the participant was added
    response2 = client.get("/activities")
    data = response2.json()
    assert email in data[activity]["participants"]

def test_signup_duplicate():
    """Test signing up twice fails"""
    email = "dupstudent@mergington.edu"
    activity = "Programming Class"
    # First signup
    client.post(f"/activities/{activity}/signup?email={email}")
    
    # Second signup should fail
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 400
    result = response.json()
    assert "already signed up" in result["detail"]

def test_signup_invalid_activity():
    """Test signup for non-existent activity"""
    response = client.post("/activities/Invalid Activity/signup?email=test@mergington.edu")
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]

def test_unregister_success():
    """Test successful unregister"""
    email = "removeme@mergington.edu"
    activity = "Gym Class"
    # First sign up
    client.post(f"/activities/{activity}/signup?email={email}")
    
    # Then unregister
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 200
    result = response.json()
    assert "Unregistered" in result["message"]
    
    # Verify removed
    response2 = client.get("/activities")
    data = response2.json()
    assert email not in data[activity]["participants"]

def test_unregister_not_signed_up():
    """Test unregistering someone not signed up"""
    response = client.delete("/activities/Chess Club/unregister?email=notsignedup@mergington.edu")
    assert response.status_code == 400
    result = response.json()
    assert "not signed up" in result["detail"]

def test_unregister_invalid_activity():
    """Test unregister from non-existent activity"""
    response = client.delete("/activities/Invalid Activity/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]