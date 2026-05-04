<template>
  <div class="article-progress fixed left-0 right-0 top-0 z-40" role="progressbar" :aria-valuenow="percent" aria-valuemin="0" aria-valuemax="100" aria-label="阅读进度">
    <div class="h-0.5 bg-accent transition-all duration-150" :style="{ width: percent + '%' }" />
  </div>
</template>

<script setup lang="ts">
const percent = ref(0);

function onScroll() {
  const scrollTop = window.scrollY;
  const docHeight = document.documentElement.scrollHeight - window.innerHeight;
  percent.value = docHeight > 0 ? Math.min(100, Math.round((scrollTop / docHeight) * 100)) : 0;
}

onMounted(() => window.addEventListener("scroll", onScroll, { passive: true }));
onUnmounted(() => window.removeEventListener("scroll", onScroll));
</script>
