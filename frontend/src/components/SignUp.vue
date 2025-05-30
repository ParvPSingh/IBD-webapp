<template>
  <div class="signup-container">
    <h1 style="text-align: center; margin-bottom: 1.5rem; color: #6366f1;">IBD Journal</h1>
    <form class="signup-form" @submit.prevent="signup">
      <h2>Create Account</h2>
      <div class="form-group">
        <label>Username</label>
        <input v-model="name" required placeholder="Enter username" />
      </div>
      <div class="form-group">
        <label>Email</label>
        <input v-model="email" type="email" required placeholder="Enter email" />
      </div>
      <div class="form-group">
        <label>Password</label>
        <input v-model="password" type="password" required minlength="8" placeholder="At least 8 characters" />
      </div>
      <button type="submit" :disabled="loading">
        <span v-if="loading">Signing Up...</span>
        <span v-else>Sign Up</span>
      </button>
      <div v-if="error" class="error">{{ error }}</div>
      <div v-if="success" class="success">{{ success }}</div>
    </form>
    <div class="login-link" style="margin-top: 1rem; text-align: center;">
      Already have an account?
      <router-link to="/login" style="color: #6366f1; text-decoration: underline; margin-left: 0.3em;">
        Log In!
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const apiUrl = import.meta.env.VITE_API_URL;
const router = useRouter()
const name = ref('')
const email = ref('')
const password = ref('')
const error = ref('')
const success = ref('')
const loading = ref(false)

async function signup() {
  error.value = ''
  success.value = ''
  loading.value = true
  try {
    const res = await fetch(`${apiUrl}/users`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: name.value, email: email.value, password: password.value })
    })
    const data = await res.json()
    if (!res.ok) {
      error.value = data.error_message || data.error || 'Signup failed'
    } else {
      success.value = 'Signup successful! Redirecting to login...'
      name.value = ''
      email.value = ''
      password.value = ''
      setTimeout(() => {
        router.push('/login')
      }, 1200)
    }
  } catch (e) {
    error.value = 'Network error'
  }
  loading.value = false
}
</script>