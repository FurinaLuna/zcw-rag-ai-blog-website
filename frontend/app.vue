<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>

<script setup lang="ts">
const authStore = useAuthStore();
onMounted(() => {
  authStore.initFromStorage();
});

useHead({
  htmlAttrs: { lang: "zh-CN" },
  link: [
    {
      rel: "stylesheet",
      href: "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&display=swap",
    },
  ],
});
</script>
