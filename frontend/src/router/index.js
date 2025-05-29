import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../components/HomePage.vue'
import SignUp from '../components/SignUp.vue'
import LogIn from '../components/LogIn.vue'
import TriggerFoods from '../components/TriggerFoods.vue'
import AnalYtics from '../components/AnalYtics.vue'
import SymptomInput from '../components/SymptomInput.vue'
import FoodInput from '../components/FoodInput.vue'
import ChatBot from '../components/ChatBot.vue'

const routes = [
  { path: '/:user_id', name: 'HomePage', component: HomePage },
  { path: '/signup', name: 'SignUp', component: SignUp },
  { path: '/login', name: 'LogIn', component: LogIn },
  { path: '/trigger_foods/:user_id', name: 'TriggerFoods', component: TriggerFoods },
  { path: '/analytics/:user_id', name: 'AnalYtics', component: AnalYtics },
  { path: '/symptom_input/:user_id', name: 'SymptomInput', component: SymptomInput },
  { path: '/food_input/:user_id', name: 'FoodInput', component: FoodInput },
  { path: '/chatbot/:user_id', name: 'ChatBot', component: ChatBot },
  // Add more routes here
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach((to, from, next) => {
  // List of routes that do NOT require auth
  const publicPages = ['/login', '/signup']
  const authRequired = !publicPages.includes(to.path)
  const loggedIn = !!localStorage.getItem('token')

  if (authRequired && !loggedIn) {
    return next('/login')
  }
  next()
})

export default router
