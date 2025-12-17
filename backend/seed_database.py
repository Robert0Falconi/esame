"""
Script per popolare il database con dati degli ultimi 6 mesi
Eseguire: python -m backend.seed_database
"""
import sys
from datetime import date, timedelta
import random
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app import models

# Dati di esempio
BOOKS_DATA = [
    {"isbn": "9788804668527", "title": "Il Nome della Rosa", "author": "Umberto Eco", "genre": "Romanzo Storico", "total_copies": 3},
    {"isbn": "9788807881596", "title": "L'Ombra del Vento", "author": "Carlos Ruiz Zafón", "genre": "Romanzo Storico", "total_copies": 2},
    {"isbn": "9788806220044", "title": "Se questo è un uomo", "author": "Primo Levi", "genre": "Memorialistica", "total_copies": 4},
    {"isbn": "9788845292613", "title": "1984", "author": "George Orwell", "genre": "Distopia", "total_copies": 3},
    {"isbn": "9788807901737", "title": "Il Signore degli Anelli", "author": "J.R.R. Tolkien", "genre": "Fantasy", "total_copies": 5},
    {"isbn": "9788804668534", "title": "Harry Potter e la Pietra Filosofale", "author": "J.K. Rowling", "genre": "Fantasy", "total_copies": 4},
    {"isbn": "9788806220051", "title": "La Divina Commedia", "author": "Dante Alighieri", "genre": "Classici", "total_copies": 3},
    {"isbn": "9788845292620", "title": "Il Piccolo Principe", "author": "Antoine de Saint-Exupéry", "genre": "Narrativa", "total_copies": 2},
    {"isbn": "9788807901744", "title": "Cent'anni di solitudine", "author": "Gabriel García Márquez", "genre": "Realismo Magico", "total_copies": 3},
    {"isbn": "9788804668541", "title": "La solitudine dei numeri primi", "author": "Paolo Giordano", "genre": "Narrativa", "total_copies": 2},
    {"isbn": "9788806220068", "title": "Io non ho paura", "author": "Niccolò Ammaniti", "genre": "Thriller", "total_copies": 3},
    {"isbn": "9788845292637", "title": "Il Codice da Vinci", "author": "Dan Brown", "genre": "Thriller", "total_copies": 4},
    {"isbn": "9788807901751", "title": "Sapiens", "author": "Yuval Noah Harari", "genre": "Saggistica", "total_copies": 3},
    {"isbn": "9788804668558", "title": "Educated", "author": "Tara Westover", "genre": "Biografia", "total_copies": 2},
    {"isbn": "9788806220075", "title": "L'arte della guerra", "author": "Sun Tzu", "genre": "Saggistica", "total_copies": 2},
    {"isbn": "9788845292644", "title": "Il Gattopardo", "author": "Giuseppe Tomasi di Lampedusa", "genre": "Romanzo Storico", "total_copies": 3},
    {"isbn": "9788807901768", "title": "Le otto montagne", "author": "Paolo Cognetti", "genre": "Narrativa", "total_copies": 2},
    {"isbn": "9788804668565", "title": "La ragazza con l'orecchino di perla", "author": "Tracy Chevalier", "genre": "Romanzo Storico", "total_copies": 2},
    {"isbn": "9788806220082", "title": "Norwegian Wood", "author": "Haruki Murakami", "genre": "Narrativa", "total_copies": 3},
    {"isbn": "9788845292651", "title": "Il Processo", "author": "Franz Kafka", "genre": "Classici", "total_copies": 2},
]

USERS_DATA = [
    {"library_card": "LIB001", "first_name": "Marco", "last_name": "Di Pasquale", "email": "marco.di.pasquale@email.it", "is_staff": False},
    {"library_card": "LIB002", "first_name": "Eldar", "last_name": "Dedic", "email": "eldar.dedic@email.it", "is_staff": False},
    {"library_card": "LIB003", "first_name": "Francesco", "last_name": "Gallo", "email": "francesco.gallo@email.it", "is_staff": False},
    {"library_card": "LIB004", "first_name": "Andrea", "last_name": "Calabrò", "email": "andrea.calabro@email.it", "is_staff": False},
    {"library_card": "STAFF001", "first_name": "Roberto", "last_name": "Falconi", "email": "roberto.falconi@biblioteca.it", "is_staff": True},
    {"library_card": "STAFF002", "first_name": "Carlotta", "last_name": "Forlino", "email": "carlotta.forlino@biblioteca.it", "is_staff": True},
]

def seed_database():
    # Prima crea le tabelle
    print("Creazione tabelle...")
    models.Base.metadata.create_all(bind=engine)
    print("✓ Tabelle create")
    
    db = SessionLocal()
    
    try:
        # Check if database is already populated
        if db.query(models.Book).count() > 0:
            print("Database già popolato. Eliminazione dati esistenti...")
            db.query(models.Loan).delete()
            db.query(models.Book).delete()
            db.query(models.User).delete()
            db.commit()
        
        print("Inserimento libri...")
        books = []
        for book_data in BOOKS_DATA:
            book = models.Book(**book_data, available_copies=book_data["total_copies"])
            db.add(book)
            books.append(book)
        db.commit()
        print(f"✓ {len(books)} libri inseriti")
        
        print("Inserimento utenti...")
        users = []
        for user_data in USERS_DATA:
            registration_days_ago = random.randint(180, 365)
            user = models.User(
                **user_data,
                registration_date=date.today() - timedelta(days=registration_days_ago)
            )
            db.add(user)
            users.append(user)
        db.commit()
        print(f"✓ {len(users)} utenti inseriti")
        
        print("Generazione prestiti ultimi 6 mesi...")
        # Refresh to get IDs
        db.refresh(books[0])
        db.refresh(users[0])
        
        loans_count = 0
        start_date = date.today() - timedelta(days=180)
        
        # Traccia i prestiti attivi per utente
        active_loans_per_user = {u.id: 0 for u in users if not u.is_staff}
        
        # Generate random loans
        attempts = 0
        max_attempts = 500  # Evita loop infiniti
        
        while loans_count < 150 and attempts < max_attempts:
            attempts += 1
            
            # Seleziona utente casuale (non staff)
            user = random.choice([u for u in users if not u.is_staff])
            book = random.choice(books)
            
            loan_start = start_date + timedelta(days=random.randint(0, 179))
            loan_duration = 30  # 1 mese
            expected_return = loan_start + timedelta(days=loan_duration)
            
            # 70% dei prestiti sono restituiti
            is_returned = random.random() < 0.7
            
            if is_returned:
                # Prestito restituito - non conta nel limite
                if random.random() < 0.8:
                    # Restituito in tempo
                    actual_return = expected_return - timedelta(days=random.randint(0, 3))
                else:
                    # Restituito in ritardo
                    actual_return = expected_return + timedelta(days=random.randint(1, 10))
                
                penalty = 0.0
                if actual_return > expected_return:
                    days_late = (actual_return - expected_return).days
                    penalty = days_late * 0.50
                
                loan = models.Loan(
                    user_id=user.id,
                    book_id=book.id,
                    start_date=loan_start,
                    expected_return_date=expected_return,
                    actual_return_date=actual_return,
                    status="restituito",
                    penalty_amount=penalty
                )
                db.add(loan)
                loans_count += 1
            else:
                # Prestito attivo - controlla il limite di 3
                if active_loans_per_user[user.id] >= 3:
                    continue  # Salta questo utente, ha già 3 prestiti attivi
                
                status = "in_corso"
                if expected_return < date.today():
                    status = "in_ritardo"
                
                loan = models.Loan(
                    user_id=user.id,
                    book_id=book.id,
                    start_date=loan_start,
                    expected_return_date=expected_return,
                    status=status
                )
                
                # Decrementa copie disponibili per prestiti attivi
                if book.available_copies > 0:
                    book.available_copies -= 1
                
                db.add(loan)
                loans_count += 1
                active_loans_per_user[user.id] += 1
        
        db.commit()
        print(f"✓ {loans_count} prestiti generati (rispettando limite di 3 prestiti attivi per utente)")
        
        # Statistics
        print("\n=== STATISTICHE DATABASE ===")
        print(f"Libri totali: {db.query(models.Book).count()}")
        print(f"Utenti totali: {db.query(models.User).count()}")
        print(f"Prestiti totali: {db.query(models.Loan).count()}")
        print(f"Prestiti attivi: {db.query(models.Loan).filter(models.Loan.status.in_(['in_corso', 'in_ritardo'])).count()}")
        print(f"Prestiti in ritardo: {db.query(models.Loan).filter(models.Loan.status == 'in_ritardo').count()}")
        print(f"Prestiti restituiti: {db.query(models.Loan).filter(models.Loan.status == 'restituito').count()}")
        
        print("\n✓ Database popolato con successo!")
        
    except Exception as e:
        print(f"Errore: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Popolamento database biblioteca...")
    seed_database()