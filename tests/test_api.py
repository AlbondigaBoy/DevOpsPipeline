import pytest
from httpx import ASGITransport, AsyncClient

import app.routers.items as items_module
from app.main import app
from app.routers.items import items_db


@pytest.fixture(autouse=True)
def reset_db():
    """Reset the in-memory database before each test."""
    items_db.clear()
    items_module._id_counter = 0
    yield
    items_db.clear()

@pytest.fixture
async def client():
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_root(client):
    """Test root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    assert "DevOps Pipeline Lab API" in response.json()["message"]

@pytest.mark.asyncio
async def test_health_check(client):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data

@pytest.mark.asyncio
async def test_create_item(client):
    """Test item creation."""
    item_data = {
        "name": "Test Item",
        "description": "A test item",
        "price": 9.99,
        "quantity": 10,
    }
    response = await client.post("/items/", json=item_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == item_data["name"]
    assert data["price"] == item_data["price"]
    assert "id" in data

@pytest.mark.asyncio
async def test_list_items(client):
    """Test listing items."""
    # Create an item first
    await client.post("/items/", json={"name": "Item 1", "price": 5.0})

    response = await client.get("/items/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1

@pytest.mark.asyncio
async def test_get_item(client):
    """Test getting a specific item."""
    # Create an item first
    create_response = await client.post(
     "/items/", json={"name": "Item 1", "price": 5.0}
    )
    item_id = create_response.json()["id"]

    response = await client.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Item 1"

@pytest.mark.asyncio
async def test_get_item_not_found(client):
    """Test getting a non-existent item."""
    response = await client.get("/items/999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_item(client):
    """Test updating an item."""
    # Create an item first
    create_response = await client.post(
     "/items/", json={"name": "Original", "price": 10.0}
    )
    item_id = create_response.json()["id"]

    response = await client.put(f"/items/{item_id}", json={"name": "Updated"})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated"
    assert response.json()["price"] == 10.0 # Price unchanged

@pytest.mark.asyncio
async def test_delete_item(client):
    """Test deleting an item."""
    # Create an item first
    create_response = await client.post(
    "/items/", json={"name": "To Delete", "price": 5.0}
    )
    item_id = create_response.json()["id"]

    response = await client.delete(f"/items/{item_id}")
    assert response.status_code == 204

    # Verify it's deleted
    get_response = await client.get(f"/items/{item_id}")
    assert get_response.status_code == 404
@pytest.mark.asyncio
async def test_create_item_validation_error(client):
    """Test item creation with invalid data."""
    response = await client.post(
        "/items/",
        json={
            "name": "", # Empty name should fail
            "price": -5, # Negative price should fail
        },
    )
    assert response.status_code == 422
