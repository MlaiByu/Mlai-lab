import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Home from '../views/Home.vue'
import Vulnerabilities from '../views/Vulnerabilities.vue'
import Users from '../views/Users.vue'
import Progress from '../views/Progress.vue'
import Learning from '../views/Learning.vue'

const routes = [
  {
    path: '/',
    name: 'Login',
    component: Login
  },
  {
    path: '/login',
    name: 'LoginPage',
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/home',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true }
  },
  {
    path: '/vulnerabilities',
    name: 'Vulnerabilities',
    component: Vulnerabilities,
    meta: { requiresAuth: true }
  },
  {
    path: '/learning',
    name: 'Learning',
    component: Learning,
    meta: { requiresAuth: true }
  },
  {
    path: '/users',
    name: 'Users',
    component: Users,
    meta: { requiresAuth: true }
  },
  {
    path: '/progress',
    name: 'Progress',
    component: Progress,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const user = JSON.parse(localStorage.getItem('user') || 'null')

  if (to.meta.requiresAuth && !user) {
    next('/login')
  } else if ((to.path === '/' || to.path === '/login' || to.path === '/register') && user) {
    next('/home')
  } else {
    next()
  }
})

export default router
