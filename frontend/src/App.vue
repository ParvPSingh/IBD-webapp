<script setup>
import ChatBot from './components/ChatBot.vue';

</script>

<template>
  <main>
    <router-view></router-view>
    <ChatBot />
    <!-- <button class="floating-chatbot-btn" @click="openChatbot">
      <img src="https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/svg/1f916.svg" alt="Chatbot" style="width: 32px; height: 32px;" />
    </button> -->
  </main>
</template>

<!-- <style scoped>
header {
  line-height: 1.5;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }
}
</style> -->
