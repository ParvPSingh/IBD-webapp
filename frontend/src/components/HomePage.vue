<template>
  <NavBar />
  <div class="homepage">
    <div class="welcome">
      <img src="../assets/doctor.png" alt="Logo" class="main-logo" />
      <h1>Welcome to IBD Journal</h1>
      <p class="subtitle">Track, analyze, and understand your IBD journey.</p>
    </div>
    <div class="card-grid">
      <div class="feature-card">
        <img src="https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/svg/1f4ca.svg" alt="Analytics" class="card-img" />
        <h2>Analytics Dashboard</h2>
        <p>Visualize your symptoms, meals, and trends with interactive graphs and insights.</p>
        <router-link :to="{ name: 'AnalYtics', params: { user_id: userId } }" class="card-link">Go to Analytics</router-link>
      </div>
      <div class="feature-card">
        <img src="https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/svg/1f372.svg" alt="Food Input" class="card-img" />
        <h2>Food Input</h2>
        <p>Log your daily water intake, stress, and meals to keep track of your diet and hydration.</p>
        <router-link :to="{ name: 'FoodInput', params: { user_id: userId } }" class="card-link">Log Food Intake</router-link>
      </div>
      <div class="feature-card">
        <img src="https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/svg/1fa7a.svg" alt="Symptom Input" class="card-img" />
        <h2>Symptom Input</h2>
        <p>Record your daily symptoms and monitor your health over time.</p>
        <router-link :to="{ name: 'SymptomInput', params: { user_id: userId } }" class="card-link">Log Symptoms</router-link>
      </div>
      <div class="feature-card">
        <img src="https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/svg/1f336.svg" alt="Trigger Foods" class="card-img" />
        <h2>Trigger Foods</h2>
        <p>Identify foods that may trigger your symptoms and learn to avoid them.</p>
        <router-link :to="{ name: 'TriggerFoods', params: { user_id: userId } }" class="card-link">See Trigger Foods</router-link>
      </div>
      <div class="feature-card">
        <img src="https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/svg/1f916.svg" alt="Chatbot" class="card-img" />
        <h2>Ask the IBD Bot</h2>
        <p>Get personalized answers about your IBD data and management from our AI chatbot.</p>
        <button @click="openChatbot" class="card-link">Open Chatbot</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { onMounted } from 'vue'         // <-- Correct import!
import NavBar from './NavBar.vue'
const apiUrl = import.meta.env.VITE_API_URL;

const route = useRoute()
const userId = route.params.user_id

function openChatbot() {
  window.dispatchEvent(new CustomEvent('open-rag-chatbot'))
}

// Call the vector_db endpoint when the page loads
onMounted(async () => {
  if (userId) {
    try {
      await fetch(`${apiUrl}/vector_db/${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
      // Optionally handle the response here
    } catch (e) {
      // Optionally handle errors here
      console.error('Failed to initialize vector DB:', e)
    }
  }
})
</script>
