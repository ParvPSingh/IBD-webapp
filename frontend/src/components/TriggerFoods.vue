<template>
  <NavBar />
  <div class="trigger-foods-container">
    <h2>Trigger Foods & Probabilities</h2>
    <div class="center-btn">
      <button @click="fetchTriggerFoods" :disabled="loading" class="fetch-btn">
        <span v-if="loading" class="loader"></span>
        <span v-else>Find Probabilities</span>
      </button>
    </div>
    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="foods.length" class="food-list">
      <table>
        <thead>
          <tr>
            <th>Food</th>
            <th>Trigger Probability</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="food in foods" :key="food.Feature">
            <td>{{ food.Feature }}</td>
            <td>{{ (food.Importance * 100).toFixed(2) }}%</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else-if="!loading && !error" class="info">No data to display.</div>
  </div>
  <ChatBot />
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import ChatBot from './ChatBot.vue'
import NavBar from './NavBar.vue'

const route = useRoute()
const apiUrl = import.meta.env.VITE_API_URL;
const userId = route.params.user_id
const foods = ref([])
const error = ref('')
const loading = ref(false)

async function fetchTriggerFoods() {
  error.value = ''
  foods.value = []
  loading.value = true
  try {
    const res = await fetch(`${apiUrl}/trees_classifier/${userId}`, {
      method: 'POST'
    })
    const data = await res.json()
    if (!res.ok) {
      error.value = data.error || 'Could not fetch trigger foods'
    } else if (!data.Food_trigger_score || !data.Food_trigger_score.length) {
      error.value = 'No trigger food data found.'
    } else {
      foods.value = data.Food_trigger_score
    }
  } catch (e) {
    error.value = 'Not enough data to find trigger foods.'
  }
  loading.value = false
}
</script>