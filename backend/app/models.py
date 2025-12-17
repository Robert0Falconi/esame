from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Boolean, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Book(Base):
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    isbn = Column(String(13), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False, index=True)
    author = Column(String(255), nullable=False, index=True)
    genre = Column(String(100), nullable=False, index=True)
    available_copies = Column(Integer, default=0, nullable=False)
    total_copies = Column(Integer, default=0, nullable=False)
    
    loans = relationship("Loan", back_populates="book")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    library_card = Column(String(20), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    registration_date = Column(Date, nullable=False, default=datetime.utcnow().date)
    is_staff = Column(Boolean, default=False)
    
    loans = relationship("Loan", back_populates="user")

class Loan(Base):
    __tablename__ = "loans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    start_date = Column(Date, nullable=False, default=datetime.utcnow().date)
    expected_return_date = Column(Date, nullable=False)
    actual_return_date = Column(Date, nullable=True)
    status = Column(String(20), nullable=False, default="in_corso")  # in_corso, restituito, in_ritardo
    penalty_amount = Column(Numeric(10, 2), default=0.0)
    
    user = relationship("User", back_populates="loans")
    book = relationship("Book", back_populates="loans")