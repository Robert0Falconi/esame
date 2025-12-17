<template>
  <div class="search-page">

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
          <h3>{{ book.title }}</h3>
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

    <!-- Modal per prenotazione -->
    <div v-if="selectedBook" class="modal" @click="closeModal">
      <div class="modal-content" @click.stop>
        <h2>Prenota Prestito</h2>
        <p><strong>{{ selectedBook.title }}</strong> di {{ selectedBook.author }}</p>

        <form @submit.prevent="createLoan">
          <div class="form-group">
            <label>Numero Tessera Biblioteca</label>
            <input v-model="loanForm.libraryCard" required placeholder="es. LIB001" />
          </div>
          <div class="form-group">
            <label>Data Restituzione Prevista</label>
            <input type="date" v-model="loanForm.returnDate" required :min="tomorrow" />
          </div>
          <div class="modal-actions">
            <button type="button" @click="closeModal" class="btn btn-secondary">Annulla</button>
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

export default {
  name: 'UserSearch',
  setup() {
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
      libraryCard: '',
      returnDate: ''
    })

    const tomorrow = computed(() => {
      const date = new Date()
      date.setDate(date.getDate() + 1)
      return date.toISOString().split('T')[0]
    })

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
      loanForm.returnDate = ''
      loanError.value = ''
      loanSuccess.value = ''
    }

    const createLoan = async () => {
      submitting.value = true
      loanError.value = ''
      loanSuccess.value = ''

      try {
        const user = await api.getUserByCard(loanForm.libraryCard)

        await api.createLoan({
          user_id: user.id,
          book_id: selectedBook.value.id,
          expected_return_date: loanForm.returnDate
        })

        loanSuccess.value = 'Prestito registrato con successo!'
        setTimeout(() => {
          closeModal()
          handleSearch() // Refresh disponibilità
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
      tomorrow
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
  color: #2c3e50;
  margin-bottom: 2rem;
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
  color: #34495e;
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
  border-color: #3498db;
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

.book-card h3 {
  color: #2c3e50;
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
  background: #3498db;
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
  color: #e74c3c;
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
  background: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2980b9;
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
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  max-width: 500px;
  width: 90%;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.modal-actions button {
  flex: 1;
}

.loading,
.error,
.no-results {
  text-align: center;
  padding: 2rem;
}

.error {
  color: #e74c3c;
}

.success {
  color: #27ae60;
  margin-top: 1rem;
}
</style>