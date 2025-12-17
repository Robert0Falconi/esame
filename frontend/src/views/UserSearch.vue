<template>
  <div class="search-page">
    <div class="info-banner">
      <span class="info-icon">ℹ️</span>
      <span>Puoi avere massimo <strong>3 prestiti simultanei</strong>. Restituisci un libro prima di prenotarne altri.</span>
    </div>

    <div class="search-form card px-5">
      <div class="form-row d-flex flex-column">
        <h1 class="mb-0">Cerca Libri</h1>
        <div class="row">
          <div class="form-group col-12 col-lg-4 pb-2 pb-lg-0">
            <label>Titolo</label>
            <input v-model="searchParams.title" @input="handleSearch" placeholder="Cerca per titolo..." />
          </div>
          <div class="form-group col-12 col-lg-4 pb-2 pb-lg-0">
            <label>Autore</label>
            <input v-model="searchParams.author" @input="handleSearch" placeholder="Cerca per autore..." />
          </div>
          <div class="form-group col-12 col-lg-4">
            <label>Genere</label>
            <select v-model="searchParams.genre" @change="handleSearch">
              <option value="">Tutti i generi</option>
              <option v-for="genre in genres" :key="genre" :value="genre">
                {{ genre }}
              </option>
            </select>
          </div>
        </div>
      </div>
      <div class="checkbox-group">
        <label>
          <input type="checkbox" v-model="searchParams.available_only" @change="handleSearch" />
          Solo libri disponibili
        </label>
      </div>
    </div>

    <div v-if="loading" class="loading">Caricamento...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="books.length === 0" class="no-results">
      Nessun libro trovato. Prova a modificare i filtri di ricerca.
    </div>
    <div v-else class="books-grid">
      <div v-for="book in books" :key="book.id" class="book-card">
        <div class="book-info">
          <h4>{{ book.title }}</h4>
          <p class="author">di {{ book.author }}</p>
          <p class="genre">
            <span class="badge">{{ book.genre }}</span>
          </p>
          <p class="isbn">ISBN: {{ book.isbn }}</p>
          <div class="availability">
            <span :class="['status', book.available_copies > 0 ? 'available' : 'unavailable']">
              {{ book.available_copies > 0 ? '✓ Disponibile' : '✗ Non disponibile' }}
            </span>
            <span class="copies">{{ book.available_copies }}/{{ book.total_copies }} copie</span>
          </div>
        </div>
        <button v-if="book.available_copies > 0" @click="selectBook(book)" class="btn btn-primary">
          Prenota
        </button>
      </div>
    </div>

    <!-- MODAL SENZA CALENDARIO -->
    <div v-if="selectedBook" class="modal" @click="closeModal">
      <div class="modal-content" @click.stop>
        <h2>Prenota Prestito</h2>
        
        <div class="book-title">
          <strong>{{ selectedBook.title }}</strong>
          <p class="author">di {{ selectedBook.author }}</p>
        </div>
        
        <div class="loan-info-box">
          <div class="info-row">
            <span class="info-icon">⏱️</span>
            <div>
              <strong>Durata prestito:</strong>
              <p>30 giorni (1 mese) dalla data di prenotazione</p>
            </div>
          </div>
          
          <div class="info-row">
            <span class="info-icon">📅</span>
            <div>
              <strong>Data restituzione prevista:</strong>
              <p>{{ returnDate }}</p>
            </div>
          </div>
          
          <div class="info-row warning">
            <span class="info-icon">⚠️</span>
            <div>
              <strong>Attenzione:</strong>
              <p>Penale di €0.50 al giorno per ogni giorno di ritardo</p>
            </div>
          </div>
        </div>

        <form @submit.prevent="createLoan">
          <div v-if="!isAuthenticated" class="form-group">
            <label>Numero Tessera Biblioteca</label>
            <input 
              v-model="loanForm.libraryCard" 
              required 
              placeholder="es. LIB001"
              autocomplete="off"
            />
          </div>
          
          <div v-else class="user-logged-info">
            <p>📋 Prenotazione per: <strong>{{ currentUser.first_name }} {{ currentUser.last_name }}</strong></p>
            <p class="library-card">Tessera: {{ currentUser.library_card }}</p>
          </div>
          
          <div class="modal-actions">
            <button type="button" @click="closeModal" class="btn btn-secondary">
              Annulla
            </button>
            <button type="submit" class="btn btn-primary" :disabled="submitting">
              {{ submitting ? 'Prenotazione...' : 'Conferma Prestito' }}
            </button>
          </div>
          
          <p v-if="loanError" class="error">{{ loanError }}</p>
          <p v-if="loanSuccess" class="success">{{ loanSuccess }}</p>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import api from '../services/api'
import { useAuthStore } from '../stores/authStore'

export default {
  name: 'UserSearch',
  setup() {
    const authStore = useAuthStore()
    const books = ref([])
    const genres = ref([])
    const loading = ref(false)
    const error = ref('')
    const selectedBook = ref(null)
    const submitting = ref(false)
    const loanError = ref('')
    const loanSuccess = ref('')

    const searchParams = reactive({
      title: '',
      author: '',
      genre: '',
      available_only: true
    })

    const loanForm = reactive({
      libraryCard: ''
    })

    const isAuthenticated = computed(() => authStore.isAuthenticated.value)
    const currentUser = computed(() => authStore.currentUser.value)

    const returnDate = computed(() => {
      const date = new Date()
      date.setDate(date.getDate() + 30)
      return date.toLocaleDateString('it-IT', { 
        day: '2-digit', 
        month: 'long', 
        year: 'numeric' 
      })
    })

    const getReturnDateISO = () => {
      const date = new Date()
      date.setDate(date.getDate() + 30)
      return date.toISOString().split('T')[0]
    }

    const loadGenres = async () => {
      try {
        const allBooks = await api.searchBooks({ available_only: false })
        const uniqueGenres = [...new Set(allBooks.map(book => book.genre))].sort()
        genres.value = uniqueGenres
      } catch (err) {
        console.error('Error loading genres:', err)
      }
    }

    const handleSearch = async () => {
      loading.value = true
      error.value = ''
      try {
        books.value = await api.searchBooks(searchParams)
      } catch (err) {
        error.value = err.message
      } finally {
        loading.value = false
      }
    }

    const selectBook = (book) => {
      selectedBook.value = book
      loanError.value = ''
      loanSuccess.value = ''
    }

    const closeModal = () => {
      selectedBook.value = null
      loanForm.libraryCard = ''
      loanError.value = ''
      loanSuccess.value = ''
    }

    const createLoan = async () => {
      submitting.value = true
      loanError.value = ''
      loanSuccess.value = ''

      try {
        let userId
        
        // Se l'utente è loggato, usa il suo ID
        if (isAuthenticated.value && currentUser.value) {
          userId = currentUser.value.id
        } else {
          // Altrimenti, cerca per tessera
          const user = await api.getUserByCard(loanForm.libraryCard)
          userId = user.id
        }

        await api.createLoan({
          user_id: userId,
          book_id: selectedBook.value.id,
          expected_return_date: getReturnDateISO()
        })

        loanSuccess.value = 'Prestito registrato con successo!'
        setTimeout(() => {
          closeModal()
          handleSearch()
        }, 2000)
      } catch (err) {
        loanError.value = err.message
      } finally {
        submitting.value = false
      }
    }

    onMounted(() => {
      loadGenres()
      handleSearch()
    })

    return {
      books,
      genres,
      loading,
      error,
      searchParams,
      handleSearch,
      selectedBook,
      selectBook,
      closeModal,
      loanForm,
      createLoan,
      submitting,
      loanError,
      loanSuccess,
      returnDate,
      isAuthenticated,
      currentUser
    }
  }
}
</script>

<style scoped>
.search-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

h1 {
  color: #1d1d1d;
  margin-bottom: 2rem;
}

.info-banner {
  background: #e8f5e9;
  border-left: 4px solid #009688;
  padding: 1rem 1.5rem;
  margin-bottom: 1.5rem;
  border-radius: 4px;
  color: #00695c;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.info-icon {
  font-size: 1.2rem;
  flex-shrink: 0;
}

.info-banner strong {
  font-weight: 600;
  color: #004d40;
}

.card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: -8px;
  color: #1d1d1d;
  text-align: left;
  padding-left: 0px;
  font-weight: 600;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #009688;
}

.checkbox-group label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.books-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.book-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.book-info {
  flex: 1;
}

.book-card h4 {
  color: #1d1d1d;
  margin-bottom: 0.5rem;
}

.author {
  color: #7f8c8d;
  font-style: italic;
  margin-bottom: 0.5rem;
}

.genre {
  margin-bottom: 0.5rem;
}

.badge {
  display: inline-block;
  background: #009688;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.85rem;
}

.isbn {
  font-size: 0.9rem;
  color: #95a5a6;
  margin-bottom: 1rem;
}

.availability {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.status {
  font-weight: 500;
}

.status.available {
  color: #27ae60;
}

.status.unavailable {
  color: #ff5722;
}

.copies {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.btn {
  padding: 0.75rem;
  border: none;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-primary {
  background: #009688;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #00796b;
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  max-width: 550px;
  width: 90%;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.modal-content h2 {
  color: #1d1d1d;
  margin-bottom: 1.5rem;
  font-size: 1.8rem;
}

.book-title {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #ecf0f1;
}

.book-title strong {
  font-size: 1.2rem;
  color: #1d1d1d;
  display: block;
  margin-bottom: 0.5rem;
}

.book-title .author {
  color: #7f8c8d;
  font-style: italic;
  margin: 0;
}

.loan-info-box {
  background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%);
  border-left: 5px solid #009688;
  padding: 1.5rem;
  margin: 1.5rem 0;
  border-radius: 8px;
}

.info-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  align-items: flex-start;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-row.warning {
  background: #fff3cd;
  padding: 1rem;
  border-radius: 6px;
  border-left: 3px solid #ffc107;
  margin-top: 1rem;
}

.info-row .info-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.info-row strong {
  color: #004d40;
  font-weight: 600;
  display: block;
  margin-bottom: 0.25rem;
}

.info-row p {
  color: #00695c;
  margin: 0;
  font-size: 0.95rem;
}

.info-row.warning strong,
.info-row.warning p {
  color: #856404;
}

.user-logged-info {
  background: #e3f2fd;
  border-left: 4px solid #2196f3;
  padding: 1rem 1.5rem;
  margin: 1.5rem 0;
  border-radius: 6px;
}

.user-logged-info p {
  margin: 0.5rem 0;
  color: #1565c0;
  font-size: 0.95rem;
}

.user-logged-info p:first-child {
  font-size: 1rem;
}

.user-logged-info strong {
  color: #0d47a1;
  font-weight: 600;
}

.library-card {
  font-size: 0.9rem !important;
  color: #42a5f5 !important;
  font-family: monospace;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

.modal-actions button {
  flex: 1;
  padding: 0.875rem;
  border-radius: 6px;
  font-weight: 600;
}

.loading,
.error,
.no-results {
  text-align: center;
  padding: 2rem;
}

.error {
  color: #ff5722;
  margin-top: 1rem;
  padding: 0.75rem;
  background: #fadbd8;
  border-radius: 6px;
}

.success {
  color: #27ae60;
  margin-top: 1rem;
  padding: 0.75rem;
  background: #d5f4e6;
  border-radius: 6px;
}
</style>