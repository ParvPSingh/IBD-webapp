<template>
  <NavBar />
  <div class="dashboard-container">
    <h2>User Analytics Dashboard</h2>
    <div v-if="loading" class="loader"></div>
    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="graphs" class="graphs-grid">
      <div v-for="(src, key) in graphs" :key="key" class="graph-card">
        <h3>{{ graphTitles[key] || key }}</h3>
        <img :src="fullGraphUrl(src)" :alt="key" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import NavBar from './NavBar.vue'

const apiUrl = import.meta.env.VITE_API_URL;
const route = useRoute()

// Always extract user_id from the user object in localStorage if present
let userId = null;
const user = localStorage.getItem('user');
if (user) {
  try {
    userId = JSON.parse(user).user_id;
  } catch (e) {
    userId = null;
  }
}
if (!userId) {
  userId = route.params.user_id;
}

const graphs = ref(null)
const error = ref('')
const loading = ref(true)

const graphTitles = {
  stoolbar: 'Distribution of Stool Colors',
  stoolline: 'Stool Consistency Over Time',
  mealpie: 'Proportion of Different Food Items',
  stressscater: 'Scatter: Stress vs Water',
  bloodbar: 'Distribution of Blood in Stool',
  corr: 'Correlation Matrix for Symptom Data',
  freqbar: 'Stool Frequency Over Time',
  stressline: 'Stress Over Time'
}

// Convert backend file path to public URL
function fullGraphUrl(path) {
  // If path contains '/static/graphs/', use that part
  const idx = path.indexOf('/static/graphs/');
  const urlPath = idx !== -1 ? path.slice(idx) : path;
  return apiUrl + urlPath;
}

async function fetchGraphs() {
  error.value = ''
  graphs.value = null
  loading.value = true
  if (!userId) {
    error.value = 'User not found. Please log in again.'
    loading.value = false
    return
  }
  try {
    const res = await fetch(`${apiUrl}/user_visualizations/${userId}`, {
      method: 'POST'
    })
    const data = await res.json()
    if (!res.ok) {
      error.value = data.error || 'Could not fetch analytics'
    } else {
      graphs.value = data
    }
  } catch (e) {
    error.value = 'Network error'
  }
  loading.value = false
}

onMounted(fetchGraphs)
</script>
<style scoped>
.graph-card img {
  display: block;
  margin: 0 auto;
  width: 100%;
  max-width: 820px;
  height: 420px;
  max-height: 60vh;
  object-fit: contain;
  border-radius: 10px;
  background: #222;
  border: 1.5px solid #23272f;
  box-shadow: 0 1px 8px #a78bfa22;
}
</style>