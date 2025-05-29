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
const userId = route.params.user_id
const foods = ref([])
const error = ref('')
const loading = ref(false)

async function fetchTriggerFoods() {
  error.value = ''
  foods.value = []
  loading.value = true
  try {
    const res = await fetch(`http://localhost:5000/trees_classifier/${userId}`, {
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

<!-- <style scoped>

h2 {
  text-align: center;
  color: #1976d2;
  margin-bottom: 1.5rem;
}

.fetch-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.7rem 1.2rem;
  background: #1976d2;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  font-size: 1.1rem;
  cursor: pointer;
  margin: 0 auto 1.5rem auto;
  min-width: 180px;
  transition: background 0.2s;
}

.fetch-btn:disabled {
  background: #90caf9;
  cursor: not-allowed;
}

.loader {
  border: 3px solid #f3f3f3;
  border-top: 3px solid #1976d2;
  border-radius: 50%;
  width: 22px;
  height: 22px;
  animation: spin 1s linear infinite;
  margin: 0 auto;
  display: inline-block;
}

@keyframes spin {
  0% { transform: rotate(0deg);}
  100% { transform: rotate(360deg);}
}

.food-list {
  margin-top: 1.5rem;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 0.5rem;
}

th, td {
  padding: 0.7rem 0.5rem;
  border-bottom: 1px solid #eee;
  text-align: left;
}

th {
  background: #f5f5f5;
  color: #1976d2;
}

.error {
  color: #d32f2f;
  background: #ffebee;
  border: 1px solid #ffcdd2;
  padding: 0.5rem;
  border-radius: 4px;
  text-align: center;
  margin-top: 1rem;
}

.info {
  text-align: center;
  color: #888;
  margin-top: 1.5rem;
}
</style> -->