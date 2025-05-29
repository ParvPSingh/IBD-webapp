<template>
  <div>
    <button class="chatbot-fab" @click="showModal = true" title="Ask IBD Bot">
      <img src="https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/svg/1f916.svg" alt="Chatbot" style="width: 32px; height: 32px;" />
    </button>
    <div v-if="showModal" class="chatbot-modal">
      <div class="chatbot-modal-content">
        <button class="close-btn" @click="showModal = false">&times;</button>
        <h3>Ask IBD Chatbot</h3>
        <div class="chat-history">
          <div v-for="(msg, i) in messages" :key="i" :class="msg.role">
            <b v-if="msg.role==='user'">You</b>
            <b v-else><</b>
            <span v-if="msg.role==='user'">{{ msg.text }}</span>
              <VueMarkdownIt v-else :source="msg.text" />
          </div>
        </div>
        <form @submit.prevent="askBot">
          <input v-model="question" :disabled="loading" placeholder="Type your question..." required />
          <button type="submit" :disabled="loading || !question">Send</button>
        </form>
        <div v-if="loading" class="loading">Thinking...</div>
        <div v-if="error" class="error">{{ error }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import VueMarkdownIt from 'vue3-markdown-it'

const showModal = ref(false)
const question = ref('')
const loading = ref(false)
const error = ref('')
const messages = ref([])

let userId = null;
const user = localStorage.getItem('user');
if (user) {
  try {
    userId = JSON.parse(user).user_id;
  } catch (e) {
    userId = null;
  }
}

async function askBot() {
  if (!question.value) return
  error.value = ''
  loading.value = true
  messages.value.push({ role: 'user', text: question.value })
  try {
    const res = await fetch(`http://localhost:5000/process_data/${userId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, question: question.value })
    })
    const data = await res.json()
    if (!res.ok) {
      error.value = data.error || 'Could not get answer'
      messages.value.push({ role: 'bot', text: error.value })
    } else {
      messages.value.push({ role: 'bot', text: data.answer })
    }
  } catch (e) {
    error.value = 'Network error'
    messages.value.push({ role: 'bot', text: error.value })
  }
  question.value = ''
  loading.value = false
}
</script>

<style scoped>
.chatbot-fab {
  position: fixed;
  bottom: 32px;
  right: 32px;
  z-index: 1200;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(90deg, #a78bfa 0%, #6366f1 100%);
  box-shadow: 0 6px 32px #a78bfa44, 0 2px 8px rgba(0,0,0,0.16);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.18s, box-shadow 0.18s, transform 0.13s;
  outline: none;
  padding: 0;
}
.chatbot-fab:hover, .chatbot-fab:focus {
  background: linear-gradient(90deg, #6366f1 0%, #a78bfa 100%);
  box-shadow: 0 12px 32px #a78bfa66, 0 4px 16px rgba(0,0,0,0.20);
  transform: translateY(-2px) scale(1.07);
}
.chatbot-fab svg {
  width: 32px;
  height: 32px;
  display: block;
}

.chatbot-modal {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(24, 26, 32, 0.58);
  z-index: 1300;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(8px);
}

.chatbot-modal-content {
  background: rgba(32, 34, 42, 0.98);
  border-radius: 16px;
  box-shadow: 0 8px 32px 0 #a78bfa33, 0 2px 8px 0 rgba(0,0,0,0.15);
  padding: 2.2rem 1.4rem 1.2rem 1.4rem;
  min-width: 340px;
  max-width: 96vw;
  width: 100%;
  max-width: 400px;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: stretch;
}

.close-btn {
  position: absolute;
  top: 16px;
  right: 18px;
  background: none;
  border: none;
  color: #b1bbc9;
  font-size: 2rem;
  cursor: pointer;
  transition: color 0.2s;
  z-index: 2;
}
.close-btn:hover {
  color: #a78bfa;
}

.chatbot-modal-content h3 {
  color: #a78bfa;
  text-align: center;
  margin-bottom: 1.1rem;
  font-weight: 700;
  font-size: 1.18rem;
}

.chat-history {
  flex: 1 1 auto;
  min-height: 120px;
  max-height: 220px;
  overflow-y: auto;
  margin-bottom: 1rem;
  padding-right: 0.2rem;
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
}
.chat-history .user, .chat-history .bot {
  display: flex;
  align-items: flex-start;
  gap: 0.5em;
  font-size: 1.01rem;
  word-break: break-word;
  line-height: 1.5;
}
.chat-history .user {
  justify-content: flex-end;
  text-align: right;
}
.chat-history .bot {
  justify-content: flex-start;
  text-align: left;
}
.chat-history b {
  color: #a78bfa;
  margin-right: 0.2em;
  font-weight: 600;
}

form {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.2rem;
}
form input {
  flex: 1 1 auto;
  background: #23242b;
  color: #f6f7f9;
  border: none;
  border-radius: 8px;
  padding: 0.7rem 1rem;
  font-size: 1.04rem;
  outline: none;
  box-shadow: 0 1px 4px rgba(80,80,120,0.04);
  transition: box-shadow 0.2s, background 0.2s;
}
form input:focus {
  background: #23272f;
  box-shadow: 0 0 0 2px #a78bfa55;
}
form button {
  background: linear-gradient(90deg, #a78bfa 0%, #6366f1 100%);
  color: #181a20;
  font-weight: 700;
  border: none;
  border-radius: 8px;
  padding: 0.7rem 1.2rem;
  font-size: 1.04rem;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(139, 92, 246, 0.09);
  transition: background 0.18s, color 0.15s, transform 0.14s;
}
form button:disabled {
  background: #23272f;
  color: #b1bbc9;
  cursor: not-allowed;
}
form button:hover:not(:disabled) {
  background: linear-gradient(90deg, #6366f1 0%, #a78bfa 100%);
  color: #fff;
  transform: translateY(-2px) scale(1.03);
}

.loading {
  color: #a78bfa;
  text-align: center;
  margin-top: 0.7rem;
}

.error {
  color: #f87171;
  background: rgba(248, 113, 113, 0.08);
  border: 1.5px solid #f87171;
  padding: 0.5rem 0.7rem;
  border-radius: 8px;
  text-align: center;
  margin-top: 0.7rem;
  font-weight: 500;
}

@media (max-width: 600px) {
  .chatbot-fab {
    right: 16px;
    bottom: 16px;
    width: 48px;
    height: 48px;
  }
  .chatbot-fab svg {
    width: 24px;
    height: 24px;
  }
  .chatbot-modal-content {
    min-width: 0;
    width: 95vw;
    max-width: 98vw;
    padding: 1.1rem 0.4rem 0.6rem 0.4rem;
  }
}


</style>