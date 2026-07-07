// Entry point for the Vue application.
// This file bootstraps the app by creating the Vue instance, registering
// global plugins (Pinia for state management, Vue Router for navigation),
// and mounting the root component onto the #app div in index.html.

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

const app = createApp(App)

// Pinia is the state management library — it replaces Vuex in Vue 3.
// All stores (grades, professor, compare, myCourses, etc.) are registered here.
app.use(createPinia())

// Vue Router handles navigation between the four pages:
// /, /professor, /compare, /compare-professor, /my-courses
app.use(router)

// Mount the app onto the <div id="app"> element in public/index.html
app.mount('#app')
