# Sistema di Gestione Biblioteca

Sistema completo per la gestione dei prestiti di libri in una biblioteca, sviluppato seguendo le best practice con architettura moderna.

## 🏗️ Architettura

- **Backend**: FastAPI (Python) con PostgreSQL
- **Frontend**: Vue.js 3 con Composition API
- **Database**: PostgreSQL 15
- **Containerizzazione**: Docker & Docker Compose

## 📋 Funzionalità

### Per gli Utenti
- 🔍 Ricerca libri per titolo, autore, genere
- 📚 Prenotazione prestiti online
- 📊 Visualizzazione storico prestiti personale
- ⏰ Notifiche scadenze e ritardi

### Per lo Staff
- 📈 Dashboard con statistiche prestiti
- ⚠️ Monitoraggio prestiti in ritardo
- 💰 Calcolo automatico penali
- ✅ Gestione rientri libri

## 🚀 Avvio Rapido

### Prerequisiti
- Docker e Docker Compose installati
- Porte 5432, 8000, 5173 disponibili

### Installazione

1. **Clone del repository** (se applicabile)
```bash
cd Biblioteca
```

2. **Avvio con Docker Compose**
```bash
docker-compose up -d
```

Questo comando avvierà:
- PostgreSQL su porta 5432
- Backend FastAPI su porta 8000
- Frontend Vue.js su porta 5173

3. **Popolamento Database**
```bash
# Attendere che i container siano attivi (circa 30 secondi)
docker-compose exec backend python -m seed_database
```

Questo script popolerà il database con:
- 20 libri di diversi generi
- 12 utenti (10 normali + 2 staff)
- 150 prestiti degli ultimi 6 mesi

## 📱 Accesso all'Applicazione

### Frontend Utente
URL: `http://localhost:5173`

**Credenziali Test:**
- Tessera: `LIB001` (Mario Rossi)
- Tessera: `LIB002` (Laura Bianchi)
- Tessera: `LIB003` (Giuseppe Verdi)

### Dashboard Staff
URL: `http://localhost:5173/staff`

**Credenziali Staff:**
- Tessera: `STAFF001` (Roberto Conti)
- Tessera: `STAFF002` (Elena Barbieri)

### API Backend
URL: `http://localhost:8000`
Documentazione Swagger: `http://localhost:8000/docs`

## 🗄️ Struttura Database

### Tabella `books`
- `id`: Identificativo unico
- `isbn`: Codice ISBN (univoco)
- `title`: Titolo del libro
- `author`: Autore
- `genre`: Genere letterario
- `available_copies`: Copie disponibili
- `total_copies`: Copie totali

### Tabella `users`
- `id`: Identificativo unico
- `library_card`: Tessera biblioteca (univoca)
- `first_name`: Nome
- `last_name`: Cognome
- `email`: Email (univoca)
- `registration_date`: Data iscrizione
- `is_staff`: Flag personale biblioteca

### Tabella `loans`
- `id`: Identificativo unico
- `user_id`: Riferimento utente
- `book_id`: Riferimento libro
- `start_date`: Data inizio prestito
- `expected_return_date`: Data prevista restituzione
- `actual_return_date`: Data effettiva restituzione
- `status`: Stato (in_corso, restituito, in_ritardo)
- `penalty_amount`: Importo penale

## 🔧 API Endpoints

### Books
- `GET /api/v1/books/` - Lista tutti i libri
- `GET /api/v1/books/{id}` - Dettaglio libro
- `GET /api/v1/books/search/` - Ricerca libri
- `POST /api/v1/books/` - Crea nuovo libro

### Users
- `GET /api/v1/users/{id}` - Dettaglio utente
- `GET /api/v1/users/card/{library_card}` - Cerca per tessera
- `POST /api/v1/users/` - Registra nuovo utente

### Loans
- `POST /api/v1/loans/` - Crea nuovo prestito
- `POST /api/v1/loans/{id}/return` - Registra restituzione
- `GET /api/v1/loans/user/{user_id}` - Storico utente
- `GET /api/v1/loans/active/` - Prestiti attivi
- `GET /api/v1/loans/overdue/` - Prestiti in ritardo
- `POST /api/v1/loans/update-overdue/` - Aggiorna stato ritardi

## ⚙️ Configurazione

### Regole di Business (backend/app/config.py)
```python
DEFAULT_LOAN_DAYS = 14          # Durata prestito standard
PENALTY_PER_DAY = 0.50          # Penale giornaliera (€)
MAX_LOANS_PER_USER = 5          # Prestiti max per utente
```

### Variabili Ambiente
Creare file `.env` in root:
```env
DATABASE_URL=postgresql://biblioteca:biblioteca123@db:5432/biblioteca
```

## 📊 Dati di Test

Il database viene popolato con:

**Libri:** 20 titoli tra cui:
- Il Nome della Rosa (Umberto Eco)
- 1984 (George Orwell)
- Il Signore degli Anelli (J.R.R. Tolkien)
- Harry Potter (J.K. Rowling)
- Sapiens (Yuval Noah Harari)

**Utenti:** 10 utenti normali + 2 staff

**Prestiti:** 150 prestiti generati negli ultimi 6 mesi con:
- 70% restituiti (80% in tempo, 20% in ritardo)
- 30% ancora attivi (alcuni in ritardo)

## 🛠️ Sviluppo

### Struttura Progetto
```
Biblioteca/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # API FastAPI
│   │   ├── models.py        # Modelli SQLAlchemy
│   │   ├── schemas.py       # Schemi Pydantic
│   │   ├── crud.py          # Operazioni database
│   │   ├── database.py      # Configurazione DB
│   │   └── config.py        # Configurazioni
│   ├── requirements.txt
│   └── seed_database.py     # Popolamento DB
├── frontend/
│   ├── src/
│   │   ├── views/           # Pagine Vue
│   │   ├── services/        # API service
│   │   └── router/          # Vue Router
│   └── package.json
├── docker-compose.yml
├── Dockerfile
└── README.md
```

### Comandi Utili

**Backend:**
```bash
# Logs backend
docker-compose logs -f backend

# Accesso shell backend
docker-compose exec backend bash

# Riavvio backend
docker-compose restart backend
```

**Frontend:**
```bash
# Logs frontend
docker-compose logs -f frontend

# Accesso shell frontend
docker-compose exec frontend sh

# Rebuild frontend
docker-compose restart frontend
```

**Database:**
```bash
# Accesso PostgreSQL
docker-compose exec db psql -U biblioteca -d biblioteca

# Backup database
docker-compose exec db pg_dump -U biblioteca biblioteca > backup.sql

# Reset database
docker-compose down -v
docker-compose up -d
docker-compose exec backend python -m seed_database
```

## 🔒 Sicurezza

- Password database cambiate in produzione
- CORS configurato per domini specifici
- Validazione input con Pydantic
- Parametrized queries (SQLAlchemy ORM)

## 📈 Miglioramenti Futuri

- [ ] Autenticazione JWT per utenti
- [ ] Sistema di prenotazioni per libri non disponibili
- [ ] Notifiche email scadenze
- [ ] Export report Excel/PDF
- [ ] Sistema di recensioni libri
- [ ] API pubblica con rate limiting
- [ ] Integrazione sistemi di pagamento penali

## 🐛 Troubleshooting

**Problema:** Container non si avvia
```bash
# Verifica logs
docker-compose logs

# Riavvia tutto
docker-compose down
docker-compose up -d
```

**Problema:** Database non popolato
```bash
# Ripopola database
docker-compose exec backend python -m seed_database
```

**Problema:** Frontend non raggiungibile
```bash
# Verifica se Vite è in ascolto
docker-compose logs frontend

# Riavvia frontend
docker-compose restart frontend
```

## 📝 Licenza

Questo progetto è stato sviluppato per scopi educativi/dimostrativi.

## 👥 Contatti

Per domande o supporto, aprire un issue nel repository.