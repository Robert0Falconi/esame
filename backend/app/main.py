from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import date, timedelta

from . import models, schemas, crud
from .database import engine, get_db
from .config import settings

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Books Endpoints
@app.post("/api/v1/books/", response_model=schemas.Book)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    db_book = crud.get_book_by_isbn(db, isbn=book.isbn)
    if db_book:
        raise HTTPException(status_code=400, detail="ISBN già esistente")
    return crud.create_book(db=db, book=book)

@app.get("/api/v1/books/", response_model=List[schemas.Book])
def list_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    books = crud.get_books(db, skip=skip, limit=limit)
    return books

@app.get("/api/v1/books/search/", response_model=List[schemas.Book])
def search_books(
    genre: str = Query(None),
    author: str = Query(None),
    title: str = Query(None),
    available_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    search_params = schemas.BookSearch(
        genre=genre,
        author=author,
        title=title,
        available_only=available_only
    )
    return crud.search_books(db, search_params)

@app.get("/api/v1/books/{book_id}", response_model=schemas.Book)
def get_book(book_id: int, db: Session = Depends(get_db)):
    db_book = crud.get_book(db, book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Libro non trovato")
    return db_book

# Users Endpoints
@app.post("/api/v1/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email già registrata")
    db_user = crud.get_user_by_library_card(db, library_card=user.library_card)
    if db_user:
        raise HTTPException(status_code=400, detail="Tessera biblioteca già esistente")
    return crud.create_user(db=db, user=user)

@app.get("/api/v1/users/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Utente non trovato.")
    return db_user

@app.get("/api/v1/users/card/{library_card}", response_model=schemas.User)
def get_user_by_card(library_card: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_library_card(db, library_card=library_card)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    return db_user

# Loans Endpoints
@app.post("/api/v1/loans/", response_model=schemas.Loan)
def create_loan(loan: schemas.LoanCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_loan(db=db, loan=loan)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/loans/{loan_id}/return", response_model=schemas.Loan)
def return_loan(
    loan_id: int,
    return_data: schemas.LoanReturn,
    db: Session = Depends(get_db)
):
    try:
        return crud.return_loan(db, loan_id, return_data.actual_return_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/loans/user/{user_id}", response_model=List[schemas.Loan])
def get_user_loans(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user_loans(db, user_id)

@app.get("/api/v1/loans/active/", response_model=List[schemas.LoanWithDetails])
def get_active_loans(db: Session = Depends(get_db)):
    return crud.get_active_loans(db)

@app.get("/api/v1/loans/overdue/", response_model=List[schemas.LoanWithDetails])
def get_overdue_loans(db: Session = Depends(get_db)):
    return crud.get_overdue_loans(db)

@app.post("/api/v1/loans/update-overdue/")
def update_overdue_status(db: Session = Depends(get_db)):
    count = crud.update_overdue_status(db)
    return {"message": f"{count} prestiti aggiornati a 'in_ritardo'"}

# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy"}