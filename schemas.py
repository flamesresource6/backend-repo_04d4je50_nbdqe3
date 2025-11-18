"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")
    image: Optional[str] = Field(None, description="Primary image URL")
    rating: Optional[float] = Field(4.5, ge=0, le=5, description="Average rating")
    specs: Optional[List[str]] = Field(default_factory=list, description="Key specifications")

class OrderItem(BaseModel):
    product_id: str = Field(..., description="ID of the purchased product")
    title: str = Field(..., description="Product title at time of purchase")
    price: float = Field(..., ge=0, description="Unit price at time of purchase")
    quantity: int = Field(..., ge=1, description="Quantity purchased")
    image: Optional[str] = Field(None, description="Image URL")

class Order(BaseModel):
    """
    Orders collection schema
    Collection name: "order" (lowercase of class name)
    """
    customer_name: str = Field(..., description="Customer full name")
    customer_email: str = Field(..., description="Customer email")
    customer_phone: Optional[str] = Field(None, description="Phone number")
    shipping_address: str = Field(..., description="Shipping address")
    items: List[OrderItem] = Field(..., description="List of purchased items")
    subtotal: float = Field(..., ge=0, description="Items subtotal")
    shipping: float = Field(0, ge=0, description="Shipping cost")
    total: float = Field(..., ge=0, description="Order total")
    status: str = Field("pending", description="Order status")
