from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional
from decimal import Decimal

# Book Schemas
class BookBase(BaseModel):
    isbn: str = Field(..., min_length=10, max_length=13)
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    genre: str = Field(..., min_length=1, max_length=100)
    total_copies: int = Field(..., ge=0)

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: int
    available_copies: int
    
    class Config:
        from_attributes = True

# User Schemas
class UserBase(BaseModel):
    library_card: str = Field(..., min_length=1, max_length=20)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr

class UserCreate(UserBase):
    is_staff: bool = False

class User(UserBase):
    id: int
    registration_date: date
    is_staff: bool
    
    class Config:
        from_attributes = True

# Loan Schemas
class LoanCreate(BaseModel):
    user_id: int
    book_id: int
    expected_return_date: date

class LoanReturn(BaseModel):
    actual_return_date: date

class Loan(BaseModel):
    id: int
    user_id: int
    book_id: int
    start_date: date
    expected_return_date: date
    actual_return_date: Optional[date] = None
    status: str
    penalty_amount: Decimal
    
    class Config:
        from_attributes = True

class LoanWithDetails(Loan):
    book: Book
    user: User
    
    class Config:
        from_attributes = True

# Search and Filter Schemas
class BookSearch(BaseModel):
    genre: Optional[str] = None
    author: Optional[str] = None
    title: Optional[str] = None
    available_only: bool = True