import pytest
from httpx import AsyncClient
from main import app  # Import your FastAPI app

@pytest.mark.asyncio
async def test_create_pizza():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/pizza/create", json={"name": "Margherita", "price": 10.99})
    assert response.status_code == 200
    assert response.json() == {"name": "Margherita", "price": 10.99}

@pytest.mark.asyncio
async def test_get_pizza():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/pizza/1")  # Assuming the pizza with ID 1 exists
    assert response.status_code == 200
    assert response.json()["name"] == "Margherita"
