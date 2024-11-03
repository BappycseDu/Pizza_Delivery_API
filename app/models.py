from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from passlib.context import CryptContext
from pydantic import BaseModel  

Base = declarative_base()  # Create a declarative base class
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  # Password hashing context

# Function to verify password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Admin model
class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=True)  # Flag to check if the user is an admin

# User model
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    def verify_password(self, plain_password: str) -> bool:
        return pwd_context.verify(plain_password, self.hashed_password)

# Pydantic models for request validation
class UserCreate(BaseModel):
    username: str
    password: str

class AdminCreate(BaseModel):
    username: str
    password: str

class AdminResponse(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True  # Enable ORM mode for Pydantic model

# Pizza model
class Pizza(Base):
    __tablename__ = "pizzas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    price = Column(Float)

# Pydantic models for pizza
class PizzaCreate(BaseModel):
    name: str
    description: str
    price: float

class PizzaResponse(PizzaCreate):
    id: int

    class Config:
        orm_mode = True  # Enable ORM mode for Pydantic model
