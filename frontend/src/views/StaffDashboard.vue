<template>
  <div class="staff-dashboard">
    <div class="header d-flex flex-column flex-md-row">
      <h1>Dashboard Staff</h1>
      <button @click="updateOverdueStatus" class="btn btn-secondary" :disabled="updating">
        {{ updating ? 'Aggiornamento...' : '🔄 Aggiorna Stato Prestiti' }}
      </button>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-value">{{ activeLoans.length }}</div>
        <div class="stat-label">Prestiti Attivi</div>
      </div>
      <div class="stat-card warning">
        <div class="stat-value">{{ overdueLoans.length }}</div>
        <div class="stat-label">Prestiti in Ritardo</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">€&nbsp;{{ totalPenalties }}</div>
        <div class="stat-label">Penali Potenziali</div>
      </div>
    </div>

    <div class="tabs">
      <button :class="['tab', { active: activeTab === 'overdue' }]" @click="activeTab = 'overdue'">
        Prestiti in Ritardo ({{ overdueLoans.length }})
      </button>
      <button :class="['tab', { active: activeTab === 'active' }]" @click="activeTab = 'active'">
        Tutti i Prestiti Attivi ({{ activeLoans.length }})
      </button>
    </div>

    <div v-if="loading" class="loading">Caricamento...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="content">
      <div v-show="activeTab === 'overdue'">
        <div v-if="overdueLoans.length === 0" class="no-data success-message">
          ✓ Nessun prestito in ritardo!
        </div>
        <div v-else class="loans-table">
          <table>
            <thead>
              <tr>
                <th>Utente</th>
                <th>Libro</th>
                <th>Data Inizio</th>
                <th>Scadenza</th>
                <th>Giorni Ritardo</th>
                <th>Penale Stimata</th>
                <th>Azioni</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="loan in overdueLoans" :key="loan.id" class="overdue-row">
                <td>{{ loan.user.first_name }} {{ loan.user.last_name }}</td>
                <td>{{ loan.book.title }}</td>
                <td>{{ formatDate(loan.start_date) }}</td>
                <td>{{ formatDate(loan.expected_return_date) }}</td>
                <td class="warning-text">{{ calculateDaysLate(loan.expected_return_date) }}</td>
                <td>€ {{ calculatePenalty(loan.expected_return_date) }}</td>
                <td>
                  <button @click="openReturnModal(loan)" class="btn-small btn-primary">
                    Registra Restituzione
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-show="activeTab === 'active'">
        <div v-if="activeLoans.length === 0" class="no-data">
          Nessun prestito attivo
        </div>
        <div v-else class="loans-table">
          <table>
            <thead>
              <tr>
                <th>Utente</th>
                <th>Libro</th>
                <th>Data Inizio</th>
                <th>Scadenza</th>
                <th>Stato</th>
                <th>Azioni</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="loan in activeLoans" :key="loan.id">
                <td>{{ loan.user.first_name }} {{ loan.user.last_name }}</td>
                <td>{{ loan.book.title }}</td>
                <td>{{ formatDate(loan.start_date) }}</td>
                <td>{{ formatDate(loan.expected_return_date) }}</td>
                <td>
                  <span :class="['status-badge', loan.status]">
                    {{ loan.status === 'in_corso' ? 'In Corso' : 'In Ritardo' }}
                  </span>
                </td>
                <td>
                  <button @click="openReturnModal(loan)" class="btn-small btn-primary">
                    Registra Restituzione
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div v-if="returnModal.show" class="modal" @click="closeReturnModal">
      <div class="modal-content" @click.stop>
        <h2>Registra Restituzione</h2>
        <div class="modal-info">
          <p><strong>Utente:</strong> {{ returnModal.loan?.user.first_name }} {{ returnModal.loan?.user.last_name }}</p>
          <p><strong>Libro:</strong> {{ returnModal.loan?.book.title }}</p>
          <p><strong>Scadenza:</strong> {{ formatDate(returnModal.loan?.expected_return_date) }}</p>
        </div>

        <form @submit.prevent="processReturn">
          <div class="form-group">
            <label style="position: relative !important;">Data Restituzione Effettiva</label>
            <input type="date" v-model="returnModal.returnDate" required :max="today" />
          </div>

          <div v-if="returnModal.penalty > 0" class="penalty-warning">
            ⚠️ Penale da applicare: <strong>€ {{ returnModal.penalty.toFixed(2) }}</strong>
          </div>

          <div class="modal-actions">
            <button type="button" @click="closeReturnModal" class="btn btn-secondary">
              Annulla
            </button>
            <button type="submit" class="btn btn-primary" :disabled="submitting">
              {{ submitting ? 'Elaborazione...' : 'Conferma Restituzione' }}
            </button>
          </div>

          <p v-if="returnModal.error" class="error">{{ returnModal.error }}</p>
          <p v-if="returnModal.success" class="success">{{ returnModal.success }}</p>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import api from '../services/api'

export default {
  name: 'StaffDashboard',
  setup() {
    const activeTab = ref('overdue')
    const activeLoans = ref([])
    const overdueLoans = ref([])
    const users = ref({})
    const books = ref({})
    const loading = ref(false)
    const updating = ref(false)
    const error = ref('')
    const submitting = ref(false)

    const returnModal = ref({
      show: false,
      loan: null,
      returnDate: '',
      penalty: 0,
      error: '',
      success: ''
    })

    const today = computed(() => new Date().toISOString().split('T')[0])

    const totalPenalties = computed(() => {
      const total = overdueLoans.value.reduce((sum, loan) => {
        const daysLate = calculateDaysLate(loan.expected_return_date)
        return sum + (daysLate * 0.50)
      }, 0)
      return total.toFixed(2)
    })

    const formatDate = (dateString) => {
      if (!dateString) return '-'
      return new Date(dateString).toLocaleDateString('it-IT')
    }

    const calculateDaysLate = (expectedDate) => {
      const expected = new Date(expectedDate)
      const today = new Date()
      return Math.max(0, Math.floor((today - expected) / (1000 * 60 * 60 * 24)))
    }

    const calculatePenalty = (expectedDate) => {
      const daysLate = calculateDaysLate(expectedDate)
      return (daysLate * 0.50).toFixed(2)
    }

    const getUserName = (userId) => {
      const user = users.value[userId]
      return user ? `${user.first_name} ${user.last_name}` : 'Caricamento...'
    }

    const getBookTitle = (bookId) => {
      return books.value[bookId]?.title || 'Caricamento...'
    }

    const loadData = async () => {
      loading.value = true
      error.value = ''
      try {
        // Prima aggiorna lo stato dei prestiti
        await api.updateOverdueStatus()

        const [active, overdue] = await Promise.all([
          api.getActiveLoans(),
          api.getOverdueLoans()
        ])

        activeLoans.value = active
        overdueLoans.value = overdue

        const loadData = async () => {
          loading.value = true
          error.value = ''
          try {
            await api.updateOverdueStatus()

            const [active, overdue] = await Promise.all([
              api.getActiveLoans(),
              api.getOverdueLoans()
            ])

            activeLoans.value = active
            overdueLoans.value = overdue
          } catch (err) {
            error.value = err.message
          } finally {
            loading.value = false
          }
        }

      } catch (err) {
        error.value = err.message
      } finally {
        loading.value = false
      }
    }

    const updateOverdueStatus = async () => {
      updating.value = true
      try {
        await api.updateOverdueStatus()
        await loadData()
      } catch (err) {
        error.value = err.message
      } finally {
        updating.value = false
      }
    }

    const openReturnModal = (loan) => {
      returnModal.value = {
        show: true,
        loan,
        returnDate: today.value,
        penalty: 0,
        error: '',
        success: ''
      }
    }

    const closeReturnModal = () => {
      returnModal.value = {
        show: false,
        loan: null,
        returnDate: '',
        penalty: 0,
        error: '',
        success: ''
      }
    }

    const processReturn = async () => {
      submitting.value = true
      returnModal.value.error = ''
      returnModal.value.success = ''

      try {
        await api.returnLoan(returnModal.value.loan.id, returnModal.value.returnDate)
        returnModal.value.success = 'Restituzione registrata con successo!'

        setTimeout(async () => {
          closeReturnModal()
          await loadData()
        }, 1500)
      } catch (err) {
        returnModal.value.error = err.message
      } finally {
        submitting.value = false
      }
    }

    watch(() => returnModal.value.returnDate, (newDate) => {
      if (newDate && returnModal.value.loan) {
        const returnDate = new Date(newDate)
        const expectedDate = new Date(returnModal.value.loan.expected_return_date)
        if (returnDate > expectedDate) {
          const daysLate = Math.floor((returnDate - expectedDate) / (1000 * 60 * 60 * 24))
          returnModal.value.penalty = daysLate * 0.50
        } else {
          returnModal.value.penalty = 0
        }
      }
    })

    onMounted(() => {
      loadData()
    })

    return {
      activeTab,
      activeLoans,
      overdueLoans,
      loading,
      updating,
      error,
      totalPenalties,
      formatDate,
      calculateDaysLate,
      calculatePenalty,
      getUserName,
      getBookTitle,
      updateOverdueStatus,
      returnModal,
      today,
      openReturnModal,
      closeReturnModal,
      processReturn,
      submitting
    }
  }
}
</script>

<style scoped>
.staff-dashboard {
  max-width: 1400px;
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.stat-card.warning {
  background: #fff3cd;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.stat-label {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid #dee2e6;
}

.tab {
  padding: 1rem 1.5rem;
  border: none;
  background: none;
  color: #7f8c8d;
  cursor: pointer;
  font-weight: 500;
  border-bottom: 3px solid transparent;
  transition: all 0.3s;
}

.tab.active {
  color: #3498db;
  border-bottom-color: #3498db;
}

.loans-table {
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

tr.overdue-row {
  background: #fff3cd;
}

.warning-text {
  color: #e74c3c;
  font-weight: 600;
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

.btn,
.btn-small {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-small {
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
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

.btn-secondary:hover:not(:disabled) {
  background: #7f8c8d;
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

.modal-info {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 4px;
  margin: 1rem 0;
}

.modal-info p {
  margin: 0.5rem 0;
}

.form-group {
  margin: 1rem 0;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  position: relative !important;
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  color: white !important;
}

.penalty-warning {
  background: #fff3cd;
  padding: 1rem;
  border-radius: 4px;
  margin: 1rem 0;
  color: #856404;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

.modal-actions button {
  flex: 1;
}

.no-data {
  text-align: center;
  padding: 3rem;
  color: #7f8c8d;
  background: white;
  border-radius: 8px;
}

.success-message {
  color: #27ae60;
  font-weight: 500;
  font-size: 1.1rem;
}

.loading,
.error {
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