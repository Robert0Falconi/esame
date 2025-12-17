import { ref } from 'vue'

const currentUser = ref(null)
const isAuthenticated = ref(false)

export function useAuthStore() {
  const login = (user) => {
    currentUser.value = user
    isAuthenticated.value = true
    // Salva in sessionStorage per persistenza durante la sessione
    sessionStorage.setItem('currentUser', JSON.stringify(user))
  }

  const logout = () => {
    currentUser.value = null
    isAuthenticated.value = false
    sessionStorage.removeItem('currentUser')
  }

  const isStaff = () => {
    return currentUser.value?.is_staff === true
  }

  const getCurrentUser = () => {
    return currentUser.value
  }

  // Recupera utente da sessionStorage all'avvio
  const restoreSession = () => {
    const savedUser = sessionStorage.getItem('currentUser')
    if (savedUser) {
      try {
        const user = JSON.parse(savedUser)
        currentUser.value = user
        isAuthenticated.value = true
      } catch (e) {
        sessionStorage.removeItem('currentUser')
      }
    }
  }

  return {
    currentUser,
    isAuthenticated,
    login,
    logout,
    isStaff,
    getCurrentUser,
    restoreSession
  }
}