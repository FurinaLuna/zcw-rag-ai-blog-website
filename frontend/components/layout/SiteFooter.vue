<template>
  <footer class="border-t border-border-default bg-bg-surface py-8 text-center text-sm text-text-tertiary">
    <p>&copy; {{ year }} 智能内容平台. Built with Nuxt3 + FastAPI.</p>
  </footer>
</template>

<script setup lang="ts">
const year = new Date().getFullYear();
</script>
