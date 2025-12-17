from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional, List
from . import models, schemas
from .config import settings

# Book CRUD
def get_book(db: Session, book_id: int):
    return db.query(models.Book).filter(models.Book.id == book_id).first()

def get_book_by_isbn(db: Session, isbn: str):
    return db.query(models.Book).filter(models.Book.isbn == isbn).first()

def get_books(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Book).offset(skip).limit(limit).all()

def search_books(db: Session, search_params: schemas.BookSearch):
    query = db.query(models.Book)
    
    if search_params.genre:
        query = query.filter(models.Book.genre.ilike(f"%{search_params.genre}%"))
    if search_params.author:
        query = query.filter(models.Book.author.ilike(f"%{search_params.author}%"))
    if search_params.title:
        query = query.filter(models.Book.title.ilike(f"%{search_params.title}%"))
    if search_params.available_only:
        query = query.filter(models.Book.available_copies > 0)
    
    return query.all()

def create_book(db: Session, book: schemas.BookCreate):
    db_book = models.Book(
        **book.model_dump(),
        available_copies=book.total_copies
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

# User CRUD
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_library_card(db: Session, library_card: str):
    return db.query(models.User).filter(models.User.library_card == library_card).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Loan CRUD
def get_loan(db: Session, loan_id: int):
    return db.query(models.Loan).filter(models.Loan.id == loan_id).first()

def get_user_loans(db: Session, user_id: int):
    return db.query(models.Loan).filter(models.Loan.user_id == user_id).order_by(models.Loan.start_date.desc()).all()

def get_active_loans(db: Session):
    return db.query(models.Loan).filter(
        models.Loan.status.in_(["in_corso", "in_ritardo"])
    ).all()

def get_overdue_loans(db: Session):
    today = date.today()
    return db.query(models.Loan).filter(
        models.Loan.status == "in_ritardo"
    ).all()

def count_active_user_loans(db: Session, user_id: int) -> int:
    return db.query(models.Loan).filter(
        and_(
            models.Loan.user_id == user_id,
            models.Loan.status.in_(["in_corso", "in_ritardo"])
        )
    ).count()

def create_loan(db: Session, loan: schemas.LoanCreate):
    # Check if user has reached max loans
    active_loans = count_active_user_loans(db, loan.user_id)
    if active_loans >= settings.MAX_LOANS_PER_USER:
        raise ValueError(f"Utente ha raggiunto il limite di {settings.MAX_LOANS_PER_USER} prestiti attivi")
    
    # Check book availability
    book = get_book(db, loan.book_id)
    if not book or book.available_copies <= 0:
        raise ValueError("Libro non disponibile")
    
    # Create loan
    db_loan = models.Loan(**loan.model_dump())
    book.available_copies -= 1
    
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    return db_loan

def return_loan(db: Session, loan_id: int, return_date: date):
    loan = get_loan(db, loan_id)
    if not loan:
        raise ValueError("Prestito non trovato")
    
    if loan.status == "restituito":
        raise ValueError("Libro già restituito")
    
    # Calculate penalty
    penalty = Decimal("0.0")
    if return_date > loan.expected_return_date:
        days_late = (return_date - loan.expected_return_date).days
        penalty = Decimal(str(days_late * settings.PENALTY_PER_DAY))
    
    # Update loan
    loan.actual_return_date = return_date
    loan.status = "restituito"
    loan.penalty_amount = penalty
    
    # Update book availability
    book = get_book(db, loan.book_id)
    book.available_copies += 1
    
    db.commit()
    db.refresh(loan)
    return loan

def update_overdue_status(db: Session):
    """Update status of overdue loans"""
    today = date.today()
    overdue_loans = db.query(models.Loan).filter(
        and_(
            models.Loan.status == "in_corso",
            models.Loan.expected_return_date < today
        )
    ).all()
    
    for loan in overdue_loans:
        loan.status = "in_ritardo"
    
    db.commit()
    return len(overdue_loans)