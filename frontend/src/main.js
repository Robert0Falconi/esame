import { createApp } from 'vue'
import router from './router'

import 'bootstrap-italia/dist/css/bootstrap-italia.min.css'
import './style.css'

import App from './App.vue'

const app = createApp(App)
app.use(router)
app.mount('#app')