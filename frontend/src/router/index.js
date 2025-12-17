import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/authStore'
import Home from '../views/Home.vue'
import UserSearch from '../views/UserSearch.vue'
import UserLoans from '../views/UserLoans.vue'
import StaffDashboard from '../views/StaffDashboard.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/search',
      name: 'search',
      component: UserSearch
    },
    {
      path: '/my-loans/:userId',
      name: 'my-loans',
      component: UserLoans,
      props: true,
      meta: { requiresAuth: true }
    },
    {
      path: '/staff',
      name: 'staff',
      component: StaffDashboard,
      meta: { requiresAuth: true, requiresStaff: true }
    }
  ]
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  authStore.restoreSession()

  // Controlla se la rotta richiede autenticazione
  if (to.meta.requiresAuth && !authStore.isAuthenticated.value) {
    // Redirect al login
    next({ name: 'home' })
    return
  }

  // Controlla se la rotta richiede permessi staff
  if (to.meta.requiresStaff && !authStore.isStaff()) {
    // Accesso negato, redirect alla home
    alert('Accesso negato: questa sezione è riservata allo staff')
    next({ name: 'home' })
    return
  }

  next()
})

export default router