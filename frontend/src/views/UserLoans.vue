<template>
  <div class="user-loans">
    <div class="header">
      <h1>I Miei Prestiti</h1>
      <router-link to="/search" class="btn btn-primary">
        📚 Cerca Nuovi Libri
      </router-link>
    </div>

    <div v-if="loading" class="loading">Caricamento...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <!-- Prestiti Attivi -->
      <div class="section">
        <h2>Prestiti Attivi</h2>
        <div v-if="activeLoans.length === 0" class="no-data">
          Nessun prestito attivo
        </div>
        <div v-else class="loans-grid">
          <div v-for="loan in activeLoans" :key="loan.id" class="loan-card">
            <div class="loan-header">
              <span :class="['status-badge', loan.status]">
                {{ loan.status === 'in_corso' ? 'In Corso' : 'In Ritardo' }}
              </span>
              <span v-if="loan.status === 'in_ritardo'" class="warning">⚠️</span>
            </div>
            <h3>{{ getBookTitle(loan.book_id) }}</h3>
            <div class="loan-details">
              <p><strong>Data inizio:</strong> {{ formatDate(loan.start_date) }}</p>
              <p><strong>Restituzione prevista:</strong> {{ formatDate(loan.expected_return_date) }}</p>
              <p v-if="loan.status === 'in_ritardo'" class="warning-text">
                <strong>Giorni di ritardo:</strong> {{ calculateDaysLate(loan.expected_return_date) }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Storico Prestiti -->
      <div class="section">
        <h2>Storico Prestiti</h2>
        <div v-if="returnedLoans.length === 0" class="no-data">
          Nessun prestito completato
        </div>
        <div v-else class="history-table">
          <table>
            <thead>
              <tr>
                <th>Libro</th>
                <th>Data Inizio</th>
                <th>Data Restituzione</th>
                <th>Stato</th>
                <th>Penale</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="loan in returnedLoans" :key="loan.id">
                <td>{{ getBookTitle(loan.book_id) }}</td>
                <td>{{ formatDate(loan.start_date) }}</td>
                <td>{{ formatDate(loan.actual_return_date) }}</td>
                <td>
                  <span :class="['status-badge', wasLate(loan) ? 'late' : 'on-time']">
                    {{ wasLate(loan) ? 'In Ritardo' : 'In Tempo' }}
                  </span>
                </td>
                <td>{{ formatPenalty(loan.penalty_amount) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../services/api'

export default {
  name: 'UserLoans',
  setup() {
    const route = useRoute()
    const loans = ref([])
    const books = ref({})
    const loading = ref(false)
    const error = ref('')

    const userId = computed(() => parseInt(route.params.userId))

    const activeLoans = computed(() => 
      loans.value.filter(loan => loan.status !== 'restituito')
    )

    const returnedLoans = computed(() => 
      loans.value.filter(loan => loan.status === 'restituito')
    )

    const formatDate = (dateString) => {
      if (!dateString) return '-'
      const date = new Date(dateString)
      return date.toLocaleDateString('it-IT')
    }

    const formatPenalty = (amount) => {
      const value = parseFloat(amount)
      return value > 0 ? `€ ${value.toFixed(2)}` : '-'
    }

    const calculateDaysLate = (expectedDate) => {
      const expected = new Date(expectedDate)
      const today = new Date()
      const diff = Math.floor((today - expected) / (1000 * 60 * 60 * 24))
      return diff > 0 ? diff : 0
    }

    const wasLate = (loan) => {
      if (!loan.actual_return_date) return false
      return new Date(loan.actual_return_date) > new Date(loan.expected_return_date)
    }

    const getBookTitle = (bookId) => {
      return books.value[bookId]?.title || 'Caricamento...'
    }

    const loadLoans = async () => {
      loading.value = true
      error.value = ''
      try {
        loans.value = await api.getUserLoans(userId.value)
        
        // Load book details
        const bookIds = [...new Set(loans.value.map(loan => loan.book_id))]
        for (const bookId of bookIds) {
          if (!books.value[bookId]) {
            try {
              const book = await api.getBook(bookId)
              books.value[bookId] = book
            } catch (err) {
              console.error(`Error loading book ${bookId}:`, err)
            }
          }
        }
      } catch (err) {
        error.value = err.message
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      loadLoans()
    })

    return {
      loans,
      activeLoans,
      returnedLoans,
      loading,
      error,
      formatDate,
      formatPenalty,
      calculateDaysLate,
      wasLate,
      getBookTitle
    }
  }
}
</script>

<style scoped>
.user-loans {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

h1 {
  color: #2c3e50;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover {
  background: #2980b9;
}

.section {
  margin-bottom: 3rem;
}

.section h2 {
  color: #2c3e50;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #3498db;
}

.loans-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.loan-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.loan-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 500;
}

.status-badge.in_corso {
  background: #d4edda;
  color: #155724;
}

.status-badge.in_ritardo {
  background: #f8d7da;
  color: #721c24;
}

.status-badge.on-time {
  background: #d4edda;
  color: #155724;
}

.status-badge.late {
  background: #fff3cd;
  color: #856404;
}

.warning {
  font-size: 1.2rem;
}

.loan-card h3 {
  color: #2c3e50;
  margin-bottom: 1rem;
}

.loan-details p {
  margin: 0.5rem 0;
  color: #34495e;
}

.warning-text {
  color: #e74c3c;
  font-weight: 500;
}

.history-table {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th {
  background: #f8f9fa;
  padding: 1rem;
  text-align: center;
  font-weight: 600;
  color: #2c3e50;
  border-bottom: 2px solid #dee2e6;
}

td {
  padding: 1rem;
  border-bottom: 1px solid #dee2e6;
  color: #34495e;
}

tr:last-child td {
  border-bottom: none;
}

.no-data {
  text-align: center;
  padding: 2rem;
  color: #7f8c8d;
  background: white;
  border-radius: 8px;
}

.loading,
.error {
  text-align: center;
  padding: 2rem;
}

.error {
  color: #e74c3c;
}
</style>