const API_BASE_URL = 'http://localhost:8000/api/v1';

class ApiService {
  // Books
  async searchBooks(params = {}) {
    const query = new URLSearchParams();
    if (params.genre) query.append('genre', params.genre);
    if (params.author) query.append('author', params.author);
    if (params.title) query.append('title', params.title);
    if (params.available_only !== undefined) query.append('available_only', params.available_only);
    
    const response = await fetch(`${API_BASE_URL}/books/search/?${query}`);
    if (!response.ok) throw new Error('Errore nella ricerca dei libri');
    return response.json();
  }

  async getBook(bookId) {
    const response = await fetch(`${API_BASE_URL}/books/${bookId}`);
    if (!response.ok) throw new Error('Libro non trovato');
    return response.json();
  }

  async createBook(bookData) {
    const response = await fetch(`${API_BASE_URL}/books/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(bookData)
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Errore nella creazione del libro');
    }
    return response.json();
  }

  // Users
  async getUserByCard(libraryCard) {
    const response = await fetch(`${API_BASE_URL}/users/card/${libraryCard}`);
    if (!response.ok) throw new Error('Utente non trovato. Non hai la tessera? Fila in Biblioteca.');
    return response.json();
  }

  async createUser(userData) {
    const response = await fetch(`${API_BASE_URL}/users/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData)
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Errore nella registrazione utente');
    }
    return response.json();
  }

  // Loans
  async getUserLoans(userId) {
    const response = await fetch(`${API_BASE_URL}/loans/user/${userId}`);
    if (!response.ok) throw new Error('Errore nel recupero prestiti utente');
    return response.json();
  }

  async createLoan(loanData) {
    const response = await fetch(`${API_BASE_URL}/loans/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(loanData)
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Errore nella creazione del prestito');
    }
    return response.json();
  }

  async returnLoan(loanId, returnDate) {
    const response = await fetch(`${API_BASE_URL}/loans/${loanId}/return`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ actual_return_date: returnDate })
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Errore nella restituzione');
    }
    return response.json();
  }

  async getActiveLoans() {
    const response = await fetch(`${API_BASE_URL}/loans/active/`);
    if (!response.ok) throw new Error('Errore nel recupero prestiti attivi');
    return response.json();
  }

  async getOverdueLoans() {
    const response = await fetch(`${API_BASE_URL}/loans/overdue/`);
    if (!response.ok) throw new Error('Errore nel recupero prestiti in ritardo');
    return response.json();
  }

  async updateOverdueStatus() {
    const response = await fetch(`${API_BASE_URL}/loans/update-overdue/`, {
      method: 'POST'
    });
    if (!response.ok) throw new Error('Errore nell\'aggiornamento stato prestiti');
    return response.json();
  }
}

export default new ApiService();