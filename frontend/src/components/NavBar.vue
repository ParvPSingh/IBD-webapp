<template>
  <nav class="navbar">
    <div class="navbar-left">
      <router-link :to="{name: 'HomePage', params: { user_id: this.user_id } }" class="logo-link">
        <img src="../assets/doctor.png" alt="Logo" class="logo" />
      </router-link>
    </div>
    <div class="navbar-center">
      <router-link :to="{name: 'AnalYtics', params: { user_id: this.user_id } }" class="nav-link">Analytics</router-link>
      <router-link :to="{name: 'FoodInput', params: { user_id: this.user_id } }" class="nav-link">Food Input</router-link>
      <router-link :to="{name: 'SymptomInput', params: { user_id: this.user_id } }" class="nav-link">Symptom Input</router-link>
      <router-link :to="{name: 'TriggerFoods', params: { user_id: this.user_id } }" class="nav-link">Trigger Foods</router-link>
    </div>
    <div class="navbar-right">
      <button @click="logout" class="logout-btn">Logout</button>
    </div>
  </nav>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

function logout() {
  // Clear auth tokens or user info here if needed
  localStorage.clear()
  router.push('/login')
}
</script>