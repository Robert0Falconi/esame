<template>
  <div class="home">
    <div class="hero">
      <h1>Biblioteca Comunale</h1>
      <p class="subtitle">Sistema di Gestione Prestiti</p>
    </div>

    <div class="login-section">
      <div class="card">
        <h2>Accesso Utente</h2>
        <form @submit.prevent="handleUserLogin">
          <div class="form-group">
            <input 
              type="text" 
              id="library-card" 
              v-model="libraryCard" 
              placeholder="Numero tessera biblioteca (es. LIB001 o STAFF001)"
              required
            />
          </div>
          <button type="submit" class="btn btn-primary mt-3" :disabled="loading">
            {{ loading ? 'Caricamento...' : 'Accedi' }}
          </button>
          <p v-if="error" class="error">{{ error }}</p>
        </form>
        <p class="info-text">
          Inserisci il numero della tua tessera biblioteca per accedere. 
          Il personale può usare le credenziali staff.
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'
import { useAuthStore } from '../stores/authStore'

export default {
  name: 'Home',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const libraryCard = ref('')
    const loading = ref(false)
    const error = ref('')

    const isAuthenticated = computed(() => authStore.isAuthenticated.value)
    const isStaff = computed(() => authStore.isStaff())

    const handleUserLogin = async () => {
      if (!libraryCard.value.trim()) {
        error.value = 'Inserisci il numero della tessera'
        return
      }

      loading.value = true
      error.value = ''

      try {
        const user = await api.getUserByCard(libraryCard.value.trim())
        
        // Salva l'utente nello store
        authStore.login(user)
        
        // Redirect basato sul tipo di utente
        if (user.is_staff) {
          router.push('/staff')
        } else {
          router.push(`/my-loans/${user.id}`)
        }
      } catch (err) {
        error.value = err.message
      } finally {
        loading.value = false
      }
    }

    return {
      libraryCard,
      loading,
      error,
      handleUserLogin,
      isAuthenticated,
      isStaff
    }
  }
}
</script>

<style scoped>
.home {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.hero {
  text-align: center;
  margin-bottom: 3rem;
}

.hero h1 {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.subtitle {
  font-size: 1.2rem;
  color: #7f8c8d;
}

.login-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

.card {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.card h2 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
    display: block;
    margin-bottom: -8px;
    color: #34495e;
    text-align: left;
    padding-left: 0px;
    font-weight: 600;
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form-group input:focus {
  outline: none;
  border-color: #3498db;
}

.btn {
  width: 100%;
  padding: 0.75rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
  text-align: center;
  transition: background 0.3s;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2980b9;
}

.btn-primary:disabled {
  background: #95a5a6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #2ecc71;
  color: white;
}

.btn-secondary:hover {
  background: #27ae60;
}

.error {
  color: #e74c3c;
  margin-top: 1rem;
  font-size: 0.9rem;
}

.info-text {
  margin-top: 1rem;
  font-size: 0.9rem;
  color: #7f8c8d;
  text-align: center;
  padding-top: 1rem;
  border-top: 1px solid #ecf0f1;
}
</style>