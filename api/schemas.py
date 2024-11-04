from pydantic import BaseModel,ConfigDict

class UserCreate(BaseModel):
    """Pydantic model for creating a new user."""
    username: str
    password: str

class AdminCreate(BaseModel):
    """Pydantic model for creating a new admin."""
    username: str
    password: str

class AdminResponse(BaseModel):
    """Pydantic model for responding with admin details."""
    id: int
    username: str

    class ConfigDict:
        orm_mode = True

class PizzaCreate(BaseModel):
    """Pydantic model for creating a new pizza."""
    name: str
    description: str
    price: float

class PizzaResponse(PizzaCreate):
    """Pydantic model for responding with pizza details."""
    id: int

    class ConfigDict:
        orm_mode = True
