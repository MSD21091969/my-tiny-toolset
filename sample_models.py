"""
Sample models for testing the code analyzer
This file demonstrates various model types that the analyzer can detect
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from dataclasses import dataclass


# Pydantic Models for Request/Response


class UserCreateRequest(BaseModel):
    """Request model for creating a user"""

    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    age: Optional[int] = Field(None, ge=0, le=150)


class UserResponse(BaseModel):
    """Response model for user data"""

    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    age: Optional[int] = None
    created_at: datetime
    is_active: bool = True


class UserUpdateRequest(BaseModel):
    """Request model for updating user data"""

    email: Optional[str] = None
    full_name: Optional[str] = None
    age: Optional[int] = Field(None, ge=0, le=150)


class ProductRequest(BaseModel):
    """Request model for product"""

    name: str
    description: str
    price: float = Field(..., gt=0)
    quantity: int = Field(..., ge=0)
    category: str
    tags: List[str] = []


class ProductResponse(BaseModel):
    """Response model for product"""

    id: int
    name: str
    description: str
    price: float
    quantity: int
    category: str
    tags: List[str]
    created_at: datetime
    updated_at: datetime


# Dataclass Models


@dataclass
class Address:
    """Address dataclass"""

    street: str
    city: str
    state: str
    zip_code: str
    country: str = "USA"


@dataclass
class OrderItem:
    """Order item dataclass"""

    product_id: int
    quantity: int
    unit_price: float

    @property
    def total_price(self) -> float:
        return self.quantity * self.unit_price


# Regular Class


class DatabaseConnection:
    """Database connection manager"""

    def __init__(self, host: str, port: int, database: str):
        self.host = host
        self.port = port
        self.database = database
        self.connected = False

    def connect(self) -> bool:
        """Establish database connection"""
        # Connection logic here
        self.connected = True
        return self.connected

    def disconnect(self) -> None:
        """Close database connection"""
        self.connected = False

    async def execute_query(self, query: str) -> List[dict]:
        """Execute a database query asynchronously"""
        # Query execution logic
        return []


# API Handler Functions (simulating FastAPI/Flask patterns)


def create_user(request: UserCreateRequest) -> UserResponse:
    """
    Create a new user
    This simulates a POST endpoint
    """
    # Business logic here
    return UserResponse(
        id=1,
        username=request.username,
        email=request.email,
        full_name=request.full_name,
        age=request.age,
        created_at=datetime.now(),
        is_active=True,
    )


async def get_user(user_id: int) -> UserResponse:
    """
    Get user by ID
    This simulates a GET endpoint
    """
    # Fetch from database
    return UserResponse(
        id=user_id,
        username="john_doe",
        email="john@example.com",
        created_at=datetime.now(),
    )


async def update_user(user_id: int, request: UserUpdateRequest) -> UserResponse:
    """
    Update user information
    This simulates a PUT/PATCH endpoint
    """
    # Update logic here
    return UserResponse(
        id=user_id,
        username="john_doe",
        email=request.email or "john@example.com",
        full_name=request.full_name,
        age=request.age,
        created_at=datetime.now(),
    )


def create_product(request: ProductRequest) -> ProductResponse:
    """Create a new product"""
    return ProductResponse(
        id=1,
        name=request.name,
        description=request.description,
        price=request.price,
        quantity=request.quantity,
        category=request.category,
        tags=request.tags,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


# Utility functions


def validate_email(email: str) -> bool:
    """Validate email format"""
    import re

    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, email))


def calculate_discount(price: float, discount_percentage: float) -> float:
    """Calculate discounted price"""
    return price * (1 - discount_percentage / 100)


class ValidationError(Exception):
    """Custom validation error"""

    pass
