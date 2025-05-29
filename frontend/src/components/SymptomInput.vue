<template>
    <NavBar />
  <div class="symptom-container">
    <h2>Daily Symptom Entry</h2>
    <form v-if="!hasTodayEntry" @submit.prevent="submitSymptom" class="symptom-form">
      <div class="form-group">
        <button
          type="button"
          class="help-btn"
          @click="showChart = true"
          aria-label="Show Bristol Stool Chart"
        >?</button>
        <label>Stool Consistency: <b>{{ form.stool_consistency }}</b></label>
        <input
          type="range"
          min="1"
          max="7"
          v-model.number="form.stool_consistency"
          width="80px"
        />
        <div class="slider-labels">
          <span>1</span>
          <span>7</span>
        </div>
      </div>
      <div class="form-group">
        <label>Pain While Passing Stool:</label>
        <label class="switch">
          <input type="checkbox" v-model="form.pain_while_passing_stool" true-value="1" false-value="0" />
          <span class="slider-switch"></span>
        </label>
      </div>
      <div class="form-group">
        <label>Stool Colour:</label>
        <label><input type="radio" value="brown" v-model="form.stool_colour" /> Brown</label>
        <label><input type="radio" value="yellow" v-model="form.stool_colour" /> Yellow</label>
        <label><input type="radio" value="red" v-model="form.stool_colour" /> Red</label>
      </div>
      <div class="form-group">
        <label>Stool Frequency:</label>
        <input
          type="number"
          min="0"
          max="20"
          v-model.number="form.stool_frequency"
        />
      </div>
      <div class="form-group">
        <label>Mucous in Stool:</label>
        <label class="switch">
          <input type="checkbox" v-model="form.mucous_in_stool" true-value="1" false-value="0" />
          <span class="slider-switch"></span>
        </label>
      </div>
      <div class="form-group">
        <label>Blood in Stool:</label>
        <label class="switch">
          <input type="checkbox" v-model="form.blood_in_stool" true-value="1" false-value="0" />
          <span class="slider-switch"></span>
        </label>
      </div>
      <div class="form-group">
        <label>Pain Location:</label>
        <label><input type="radio" value="lower abdomen" v-model="form.pain_location" /> Lower Abdomen</label>
        <label><input type="radio" value="upper abdomen" v-model="form.pain_location" /> Upper Abdomen</label>
        <label><input type="radio" value="both" v-model="form.pain_location" /> Both</label>
      </div>
      <div class="form-group">
        <label>Fever:</label>
        <label class="switch">
          <input type="checkbox" v-model="form.fever" true-value="1" false-value="0" />
          <span class="slider-switch"></span>
        </label>
      </div>
      <div class="form-group">
        <label>Nausea:</label>
        <label class="switch">
          <input type="checkbox" v-model="form.nausea" true-value="1" false-value="0" />
          <span class="slider-switch"></span>
        </label>
      </div>
      <div class="form-group">
        <label>Flatulence:</label>
        <label class="switch">
          <input type="checkbox" v-model="form.flatulence" true-value="1" false-value="0" />
          <span class="slider-switch"></span>
        </label>
      </div>
      <button type="submit" :disabled="loading">Submit</button>
      <div v-if="error" class="error">{{ error }}</div>
      <div v-if="success" class="success">{{ success }}</div>
    </form>
    <div v-else class="info">You have already submitted symptoms for today.</div>
    <div v-if="showChart" class="modal" @click.self="showChart = false">
      <div class="modal-content chart-modal">
        <img src="../assets/chart.png" alt="Bristol Stool Chart" style="max-width:100%;max-height:60vh;" />
        <button @click="showChart = false" class="close-btn">Close</button>
      </div>
    </div>
</div>
<div class="symptom-container2">
    <h3 class="centered-table">All Symptom Entries</h3>
    <div v-if="symptoms.length === 0" class="info">No entries yet.</div>
    <table v-else class="symptom-table centered-table">
      <thead>
        <tr>
          <th>Date</th>
          <th>Stool Consistency</th>
          <th>Pain Passing Stool</th>
          <th>Stool Colour</th>
          <th>Stool Frequency</th>
          <th>Mucous in Stool</th>
          <th>Blood in Stool</th>
          <th>Pain Location</th>
          <th>Fever</th>
          <th>Nausea</th>
          <th>Flatulence</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="symptom in symptoms" :key="symptom.id">
          <td>{{ symptom.date.split('T')[0] }}</td>
          <td>{{ symptom.stool_consistency }}</td>
          <td>{{ symptom.pain_while_passing_stool == 1 ? 'Yes' : 'No' }}</td>
          <td>{{ symptom.stool_colour }}</td>
          <td>{{ symptom.stool_frequency }}</td>
          <td>{{ symptom.mucous_in_stool == 1 ? 'Yes' : 'No' }}</td>
          <td>{{ symptom.blood_in_stool == 1 ? 'Yes' : 'No' }}</td>
          <td>{{ symptom.pain_location }}</td>
          <td>{{ symptom.fever == 1 ? 'Yes' : 'No' }}</td>
          <td>{{ symptom.nausea == 1 ? 'Yes' : 'No' }}</td>
          <td>{{ symptom.flatulence == 1 ? 'Yes' : 'No' }}</td>
          <td>
            <button @click="startEdit(symptom)">Update</button>
            <button @click="deleteSymptom(symptom.id)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Edit Modal -->
    <div v-if="editing" class="modal">
      <div class="modal-content">
        <h3>Edit Symptom Entry</h3>
        <form @submit.prevent="submitEdit">
          <div class="form-group">
            <label>Stool Consistency: <b>{{ editForm.stool_consistency }}</b></label>
            <input
              type="range"
              min="1"
              max="7"
              v-model.number="editForm.stool_consistency"
            />
            <div class="slider-labels">
              <span>1</span>
              <span>7</span>
            </div>
          </div>
          <div class="form-group">
            <label>Pain While Passing Stool:</label>
            <label class="switch">
              <input type="checkbox" v-model="editForm.pain_while_passing_stool" true-value="1" false-value="0" />
              <span class="slider-switch"></span>
            </label>
          </div>
          <div class="form-group">
            <label>Stool Colour:</label>
            <label><input type="radio" value="brown" v-model="editForm.stool_colour" /> Brown</label>
            <label><input type="radio" value="yellow" v-model="editForm.stool_colour" /> Yellow</label>
            <label><input type="radio" value="red" v-model="editForm.stool_colour" /> Red</label>
          </div>
          <div class="form-group">
            <label>Stool Frequency:</label>
            <input
              type="number"
              min="0"
              max="20"
              v-model.number="editForm.stool_frequency"
            />
          </div>
          <div class="form-group">
            <label>Mucous in Stool:</label>
            <label class="switch">
              <input type="checkbox" v-model="editForm.mucous_in_stool" true-value="1" false-value="0" />
              <span class="slider-switch"></span>
            </label>
          </div>
          <div class="form-group">
            <label>Blood in Stool:</label>
            <label class="switch">
              <input type="checkbox" v-model="editForm.blood_in_stool" true-value="1" false-value="0" />
              <span class="slider-switch"></span>
            </label>
          </div>
          <div class="form-group">
            <label>Pain Location:</label>
            <label><input type="radio" value="lower abdomen" v-model="editForm.pain_location" /> Lower Abdomen</label>
            <label><input type="radio" value="upper abdomen" v-model="editForm.pain_location" /> Upper Abdomen</label>
            <label><input type="radio" value="both" v-model="editForm.pain_location" /> Both</label>
          </div>
          <div class="form-group">
            <label>Fever:</label>
            <label class="switch">
              <input type="checkbox" v-model="editForm.fever" true-value="1" false-value="0" />
              <span class="slider-switch"></span>
            </label>
          </div>
          <div class="form-group">
            <label>Nausea:</label>
            <label class="switch">
              <input type="checkbox" v-model="editForm.nausea" true-value="1" false-value="0" />
              <span class="slider-switch"></span>
            </label>
          </div>
          <div class="form-group">
            <label>Flatulence:</label>
            <label class="switch">
              <input type="checkbox" v-model="editForm.flatulence" true-value="1" false-value="0" />
              <span class="slider-switch"></span>
            </label>
          </div>
          <button type="submit" :disabled="loading">Save</button>
          <button type="button" @click="editing = false">Cancel</button>
        </form>
      </div>
    </div>
  </div>
    <ChatBot />
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { watch } from 'vue'
import { useRoute } from 'vue-router'
import ChatBot from './ChatBot.vue'
import NavBar from './NavBar.vue'

const apiUrl = import.meta.env.VITE_API_URL;
const showChart = ref(false)
const route = useRoute()
const userId = route.params.user_id
const symptoms = ref([])
const loading = ref(false)
const error = ref('')
const success = ref('')
const editing = ref(false)
const editId = ref(null)
const editForm = reactive({})
const today = new Date().toISOString().split('T')[0]

const form = reactive({
  stool_consistency: 4,
  pain_while_passing_stool: 0,
  stool_colour: 'brown',
  stool_frequency: 1,
  mucous_in_stool: 0,
  blood_in_stool: 0,
  pain_location: 'lower abdomen',
  fever: 0,
  nausea: 0,
  flatulence: 0
})

const hasTodayEntry = computed(() =>
  symptoms.value.some(s => s.date.split('T')[0] === today)
)

async function fetchSymptoms() {
  loading.value = true
  error.value = ''
  try {
    const res = await fetch(`${apiUrl}/symptoms/user/${userId}`)
    symptoms.value = await res.json()
  } catch (e) {
    error.value = 'Could not fetch symptoms'
  }
  loading.value = false
}

async function submitSymptom() {
  error.value = ''
  success.value = ''
  loading.value = true
  try {
    const res = await fetch(`${apiUrl}/symptoms/${userId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form)
    })
    const data = await res.json()
    if (!res.ok) {
      error.value = data.error || 'Could not submit symptom'
    } else {
      success.value = 'Symptom submitted!'
      await fetchSymptoms()
    }
  } catch (e) {
    error.value = 'Network error'
  }
  loading.value = false
}

function startEdit(symptom) {
  editing.value = true
  editId.value = symptom.id
  // Deep copy and ensure correct types for checkboxes
  Object.assign(editForm, JSON.parse(JSON.stringify(symptom)))
  // Ensure boolean fields are numbers (for checkboxes)
  const boolFields = [
    'pain_while_passing_stool', 'mucous_in_stool', 'blood_in_stool',
    'fever', 'nausea', 'flatulence'
  ]
  for (const field of boolFields) {
    if (field in editForm) {
      editForm[field] = Number(editForm[field])
    }
  }
}

async function submitEdit() {
  error.value = ''
  loading.value = true
  try {
    const res = await fetch(`${apiUrl}/symptoms/${editId.value}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(editForm)
    })
    const data = await res.json()
    if (!res.ok) {
      error.value = data.error || 'Could not update symptom'
    } else {
      editing.value = false
      await fetchSymptoms()
    }
  } catch (e) {
    error.value = 'Network error'
  }
  loading.value = false
}

async function deleteSymptom(id) {
  if (!confirm('Delete this symptom entry?')) return
  loading.value = true
  error.value = ''
  try {
    const res = await fetch(`${apiUrl}/symptoms/${id}`, {
      method: 'DELETE'
    })
    const data = await res.json()
    if (!res.ok) {
      error.value = data.error || 'Could not delete symptom'
    } else {
      await fetchSymptoms()
    }
  } catch (e) {
    error.value = 'Network error'
  }
  loading.value = false
}


onMounted(fetchSymptoms)
</script>