<template>
  <nav class="navbar">
    <div class="navbar-left">
      <router-link :to="{name: 'HomePage', params: { user_id: userId } }" class="logo-link">
        <img src="../assets/doctor.png" alt="Logo" class="logo" />
      </router-link>
    </div>
    <div class="navbar-center">
      <router-link :to="{name: 'AnalYtics', params: { user_id: userId } }" class="nav-link">Analytics</router-link>
      <router-link :to="{name: 'FoodInput', params: { user_id: userId } }" class="nav-link">Food Input</router-link>
      <router-link :to="{name: 'SymptomInput', params: { user_id: userId } }" class="nav-link">Symptom Input</router-link>
      <router-link :to="{name: 'TriggerFoods', params: { user_id: userId } }" class="nav-link">Trigger Foods</router-link>
    </div>
    <div class="navbar-right">
      <button @click="logout" class="logout-btn">Logout</button>
    </div>
  </nav>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
const userId = localStorage.getItem('user_id') || route.params.user_id;
const apiUrl = import.meta.env.VITE_API_URL;

function logout() {
  // Clear auth tokens or user info here if needed
  localStorage.clear()
  router.push('/login')
}
</script>