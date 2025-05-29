<template>
  <NavBar />
  <div class="dashboard-container">
    <h2>User Analytics Dashboard</h2>
    <div v-if="loading" class="loader"></div>
    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="graphs" class="graphs-grid">
      <div v-for="(src, key) in graphs" :key="key" class="graph-card">
        <h3>{{ graphTitles[key] || key }}</h3>
        <img :src="toPublicPath(src)" :alt="key" />
      </div>
    </div>
  </div>
    <ChatBot />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import ChatBot from './ChatBot.vue'
import NavBar from './NavBar.vue'

const route = useRoute()
const userId = route.params.user_id
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

function toPublicPath(path) {
  const idx = path.indexOf('/graphs/')
  return idx !== -1 ? path.slice(idx) : path
}

async function fetchGraphs() {
  error.value = ''
  graphs.value = null
  loading.value = true
  try {
    const res = await fetch(`http://localhost:5000/user_visualizations/${userId}`, {
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