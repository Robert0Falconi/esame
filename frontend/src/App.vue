<template>
  <div id="app">
    <nav class="navbar">
      <div class="navbar-content">
        <router-link to="/" class="logo pe-0 pe-md-5">
          Biblioteca
        </router-link>
        <div class="nav-links pt-1 d-flex flex-column flex-md-row">
          <div class="d-flex gap-4">
            <router-link to="/">Home</router-link>
            <router-link to="/search">Cerca Libri</router-link>
            <router-link v-if="isStaff" to="/staff">Staff</router-link>
          </div>
          <div class="d-flex gap-2">
            <div v-if="isAuthenticated" class="user-menu">
              <span class="user-name">👤 {{ currentUser?.first_name }} {{ currentUser?.last_name }}</span>
              <button @click="handleLogout" class="btn-logout">Logout</button>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <main class="main-content">
      <router-view />
    </main>

    <footer class="footer">
      <!-- Anno dinamico -->
      <p>&copy; {{ new Date().getFullYear() }} Sistema Gestione Biblioteca - Tutti i diritti riservati</p>
    </footer>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from './stores/authStore'

export default {
  name: 'App',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()

    // Ripristina la sessione all'avvio
    authStore.restoreSession()

    const isAuthenticated = computed(() => authStore.isAuthenticated.value)
    const currentUser = computed(() => authStore.currentUser.value)
    const isStaff = computed(() => authStore.isStaff())

    const handleLogout = () => {
      authStore.logout()
      router.push('/')
    }

    return {
      isAuthenticated,
      currentUser,
      isStaff,
      handleLogout
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: #f5f6fa;
  color: #2c3e50;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  background: #2c3e50;
  color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.navbar-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 1.5rem;
  font-weight: bold;
  color: white;
  text-decoration: none;
}

.nav-links {
  display: flex;
  gap: 2rem;
  align-items: center;
}

.nav-links a {
  color: white;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s;
}

.nav-links a:hover,
.nav-links a.router-link-active {
  color: #3498db;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-left: 1rem;
  padding-left: 1rem;
  border-left: 1px solid rgba(255, 255, 255, 0.3);
}

.user-name {
  color: white;
  font-size: 0.9rem;
}

.btn-logout {
  padding: 0.5rem 1rem;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.3s;
}

.btn-logout:hover {
  background: #c0392b;
}

.main-content {
  flex: 1;
  padding: 2rem 0;
}

.footer {
  background: #34495e;
  color: #ecf0f1;
  text-align: center;
  padding: 2rem;
  margin-top: auto;
}

.footer p {
  font-size: 0.9rem;
}

/* Responsive */
@media (max-width: 768px) {
  .navbar-content {
    flex-direction: column;
    gap: 1rem;
  }

  .nav-links {
    gap: 1rem;
  }

  .user-menu {
    margin-left: 0rem !important;
    padding-left: 0rem !important;
    border-left: 0px solid rgba(255, 255, 255, 0) !important;
  }
}
</style>