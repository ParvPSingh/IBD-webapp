<template>
    <NavBar />
  <div class="food-container">
    <h2>Daily Food Intake Entry</h2>
    <form v-if="!hasTodayEntry" @submit.prevent="submitFood" class="food-form">
      <div class="form-group">
        <label>Water (no. of glasses):</label>
        <input type="number" min="0" v-model.number="form.water" required />
      </div>
      <div class="form-group">
        <label>Stress Level (1-10):</label>
        <input type="number" min="1" max="10" v-model.number="form.stress" required />
      </div>
      <button type="submit" :disabled="loading">Submit</button>
      <div v-if="error" class="error">{{ error }}</div>
      <div v-if="success" class="success">{{ success }}</div>
    </form>
    <div v-else class="info">You have already submitted food intake for today.</div>
    <div style="text-align:center; margin: 1rem 0;">
  <button type="button" @click="openMealInputModal" :disabled="loading">Add Meals for Today</button>
</div>

    <h3>All Food Intake Entries</h3>
    <div v-if="foods.length === 0" class="info">No entries yet.</div>
    <table v-else class="food-table">
      <thead>
        <tr>
          <th>Date</th>
          <th>Water (no. of glasses)</th>
          <th>Stress Level</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="food in foods" :key="food.id">
          <td>{{ food.date.split('T')[0] }}</td>
          <td>{{ food.water }}</td>
          <td>{{ food.stress }}</td>
          <td>
            <button @click="startEdit(food)">Update</button>
            <button @click="deleteFood(food.id)">Delete</button>
            <button @click="openMeals(food)">Meals</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Edit Modal -->
    <div v-if="editing" class="modal">
      <div class="modal-content">
        <h3>Edit Food Intake</h3>
        <form @submit.prevent="submitEdit">
          <div class="form-group">
            <label>Water (no. of glasses):</label>
            <input type="number" min="0" v-model.number="editForm.water" required />
          </div>
          <div class="form-group">
            <label>Stress Level (1-10):</label>
            <input type="number" min="1" max="10" v-model.number="editForm.stress" required />
          </div>
          <button type="submit" :disabled="loading">Save</button>
          <button type="button" @click="editing = false">Cancel</button>
        </form>
      </div>
    </div>

    <!-- Meals Modal (for viewing/updating/deleting meals for a food intake) -->
    <div v-if="mealsModal" class="modal">
      <div class="modal-content">
        <h3>Meals for {{ mealsDate }}</h3>
        <table class="meals-table">
          <thead>
            <tr>
              <th>Meal Type</th>
              <th>Item</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="meal in meals" :key="meal.id">
              <td>
                <select v-model="meal.meal_type" @change="meal.changed=true">
                  <option>breakfast</option>
                  <option>lunch</option>
                  <option>dinner</option>
                  <option>snacks</option>
                </select>
              </td>
              <td>
                <input v-model="meal.item" @input="meal.changed=true" />
              </td>
              <td>
                <button @click="updateMeal(meal)" :disabled="!meal.changed">Update</button>
                <button @click="deleteMeal(meal.id)">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
        <button @click="mealsModal = false">Close</button>
      </div>
    </div>

    <!-- Meals Input Modal (for adding meals for today) -->
    <div v-if="mealInputModal" class="modal">
      <div class="modal-content">
        <h3>Add Meals for Today ({{ today }})</h3>
        <form @submit.prevent="addMealForToday" class="meal-form">
          <div class="form-group">
            <label>Meal Type:</label>
            <select v-model="mealInputForm.meal_type" required>
              <option disabled value="">Select type</option>
              <option>breakfast</option>
              <option>lunch</option>
              <option>dinner</option>
              <option>snacks</option>
            </select>
          </div>
          <div class="form-group">
            <label>Item:</label>
            <input v-model="mealInputForm.item" required placeholder="Meal item" />
          </div>
          <button type="submit" :disabled="loading">Add Meal</button>
          <button type="button" @click="mealInputModal = false" style="margin-left:1rem;">Close</button>
        </form>
        <div v-if="mealInputError" class="error">{{ mealInputError }}</div>
        <div v-if="mealInputSuccess" class="success">{{ mealInputSuccess }}</div>
        <div v-if="todayMeals.length" class="meals-list">
          <h4>Today's Meals</h4>
          <ul>
            <li v-for="meal in todayMeals" :key="meal.id">
              <b>{{ meal.meal_type }}:</b> {{ meal.item }}
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { watch } from 'vue'
import { useRoute } from 'vue-router'
import ChatBot from './ChatBot.vue'
import NavBar from './NavBar.vue'

const apiUrl = import.meta.env.VITE_API_URL;
const route = useRoute()
const userId = route.params.user_id
const foods = ref([])
const loading = ref(false)
const error = ref('')
const success = ref('')
const editing = ref(false)
const editId = ref(null)
const editForm = reactive({})
const today = new Date().toISOString().split('T')[0]

const form = reactive({
  water: '',
  stress: ''
})

const hasTodayEntry = computed(() =>
  foods.value.some(f => f.date.split('T')[0] === today)
)

async function fetchFoods() {
  loading.value = true
  error.value = ''
  try {
    const res = await fetch(`${apiUrl}/food/user/${userId}`)
    foods.value = await res.json()
  } catch (e) {
    error.value = 'Could not fetch food intakes'
  }
  loading.value = false
}

async function submitFood() {
  error.value = ''
  success.value = ''
  loading.value = true
  try {
    const todayFood = foods.value.find(f => f.date.split('T')[0] === today)
    if (todayFood) {
      // Update existing food intake for today
      await fetch(`${apiUrl}/food/${todayFood.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      })
    } else {
      // Create new food intake for today
      await fetch(`${apiUrl}/food/${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      })
    }
    success.value = 'Food intake submitted!'
    await fetchFoods()
  } catch (e) {
    error.value = 'Network error'
  }
  loading.value = false
}

function startEdit(food) {
  editing.value = true
  editId.value = food.id
  Object.assign(editForm, food)
}

async function submitEdit() {
  error.value = ''
  loading.value = true
  try {
    const res = await fetch(`${apiUrl}/food/${editId.value}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(editForm)
    })
    const data = await res.json()
    if (!res.ok) {
      error.value = data.error || 'Could not update food intake'
    } else {
      editing.value = false
      await fetchFoods()
    }
  } catch (e) {
    error.value = 'Network error'
  }
  loading.value = false
}

async function deleteFood(id) {
  if (!confirm('Delete this food intake entry?')) return
  loading.value = true
  error.value = ''
  try {
    const res = await fetch(`${apiUrl}/food/${id}`, {
      method: 'DELETE'
    })
    const data = await res.json()
    if (!res.ok) {
      error.value = data.error || 'Could not delete food intake'
    } else {
      await fetchFoods()
    }
  } catch (e) {
    error.value = 'Network error'
  }
  loading.value = false
}

// Meals logic for viewing/updating/deleting meals for a food intake
const mealsModal = ref(false)
const meals = ref([])
const mealsDate = ref('')
const mealsFoodId = ref(null)
const newMeal = reactive({ meal_type: '', item: '' })

async function openMeals(food) {
  mealsModal.value = true
  mealsDate.value = food.date.split('T')[0]
  mealsFoodId.value = food.id
  await fetchMeals(food.id)
}

async function fetchMeals(food_intake_id) {
  loading.value = true
  error.value = ''
  try {
    const res = await fetch(`${apiUrl}/meals/food/${food_intake_id}`)
    meals.value = (await res.json()).map(m => ({ ...m, changed: false }))
  } catch (e) {
    error.value = 'Could not fetch meals'
  }
  loading.value = false
}

async function updateMeal(meal) {
  loading.value = true
  error.value = ''
  try {
    const res = await fetch(`${apiUrl}/meals/${meal.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ meal_type: meal.meal_type, item: meal.item })
    })
    const data = await res.json()
    if (!res.ok) {
      error.value = data.error || 'Could not update meal'
    } else {
      meal.changed = false
      await fetchMeals(mealsFoodId.value)
    }
  } catch (e) {
    error.value = 'Network error'
  }
  loading.value = false
}

async function deleteMeal(id) {
  if (!confirm('Delete this meal?')) return
  loading.value = true
  error.value = ''
  try {
    const res = await fetch(`${apiUrl}/meals/${id}`, {
      method: 'DELETE'
    })
    const data = await res.json()
    if (!res.ok) {
      error.value = data.error || 'Could not delete meal'
    } else {
      await fetchMeals(mealsFoodId.value)
    }
  } catch (e) {
    error.value = 'Network error'
  }
  loading.value = false
}

// Meals Input Modal for adding meals for today
const mealInputModal = ref(false)
const mealInputForm = reactive({ meal_type: '', item: '' })
const mealInputError = ref('')
const mealInputSuccess = ref('')
const todayMeals = ref([])

function openMealInputModal() {
  mealInputModal.value = true
  mealInputForm.meal_type = ''
  mealInputForm.item = ''
  mealInputError.value = ''
  mealInputSuccess.value = ''
  fetchTodayMeals()
}

async function fetchTodayMeals() {
  // Find today's food intake id (if any)
  let todayFood = foods.value.find(f => f.date.split('T')[0] === today)
  if (!todayFood) {
    todayMeals.value = []
    return
  }
  try {
    const res = await fetch(`${apiUrl}/meals/food/${todayFood.id}`)
    todayMeals.value = await res.json()
  } catch (e) {
    todayMeals.value = []
  }
}

async function addMealForToday() {
  mealInputError.value = ''
  mealInputSuccess.value = ''
  loading.value = true
  try {
    // Always use the new backend logic: send user_id, meal_type, item
    const res = await fetch(`${apiUrl}/meals/${userId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        meal_type: mealInputForm.meal_type,
        item: mealInputForm.item
      })
    })
    const data = await res.json()
    if (!res.ok) {
      mealInputError.value = data.error || 'Could not add meal'
    } else {
      mealInputSuccess.value = 'Meal added!'
      mealInputForm.meal_type = ''
      mealInputForm.item = ''
      await fetchFoods()
      await fetchTodayMeals()
    }
  } catch (e) {
    mealInputError.value = 'Network error'
  }
  loading.value = false
}



onMounted(fetchFoods)
</script>