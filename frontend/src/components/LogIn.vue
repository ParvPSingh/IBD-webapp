<template>
  <div class="login-container">
    <form class="login-form" @submit.prevent="login">
      <h2>Login</h2>
      <div class="form-group">
        <label>Email</label>
        <input v-model="email" type="email" required placeholder="Enter email" />
      </div>
      <div class="form-group">
        <label>Password</label>
        <input v-model="password" type="password" required placeholder="Enter password" />
      </div>
      <button type="submit" :disabled="loading">
        <span v-if="loading">Logging In...</span>
        <span v-else>Login</span>
      </button>
      <div v-if="error" class="error">{{ error }}</div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function login() {
  error.value = ''
  loading.value = true
  try {
    const res = await fetch('http://localhost:5000/login_user', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.value, password: password.value })
    })
    const data = await res.json()
    if (!res.ok) {
      error.value = data.error_message || data.error || 'Login failed'
    } else {
      // Store token and user info as needed
      localStorage.setItem('token', data.token)
      localStorage.setItem('user', JSON.stringify(data))
      localStorage.setItem('user_id', data.user_id)
      // Redirect to /user_id
      router.push(`/${data.user_id}`)
    }
  } catch (e) {
    error.value = 'Network error'
  }
  loading.value = false
}
</script>