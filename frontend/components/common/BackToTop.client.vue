<template>
  <button
    v-show="visible"
    class="fixed bottom-6 right-6 z-50 flex h-10 w-10 items-center justify-center rounded-full bg-accent/90 text-white shadow-lg transition-all hover:bg-accent hover:scale-110"
    aria-label="回到顶部"
    @click="scrollTop"
  >
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
      <path d="M18 15l-6-6-6 6" />
    </svg>
  </button>
</template>

<script setup lang="ts">
const visible = ref(false);

function onScroll() {
  visible.value = window.scrollY > 400;
}

function scrollTop() {
  window.scrollTo({ top: 0, behavior: "smooth" });
}

onMounted(() => window.addEventListener("scroll", onScroll, { passive: true }));
onUnmounted(() => window.removeEventListener("scroll", onScroll));
</script>
