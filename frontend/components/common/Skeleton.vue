<template>
  <div aria-hidden="true" class="animate-pulse">
    <!-- Avatar -->
    <div v-if="variant === 'avatar'" class="rounded-full bg-gray-200" :style="{ width: size, height: size }" />

    <!-- Text lines -->
    <div v-else-if="variant === 'text'" class="space-y-2">
      <div
        v-for="i in lines"
        :key="i"
        class="h-4 rounded bg-gray-200"
        :style="{ width: i === lines && lastLineWidth ? lastLineWidth : widths[i - 1] || '100%' }"
      />
    </div>

    <!-- Card with image + text -->
    <div v-else-if="variant === 'card'" class="rounded-lg border border-gray-100 p-5">
      <div class="mb-3 h-40 w-full rounded bg-gray-200" />
      <div class="mb-2 h-5 w-3/4 rounded bg-gray-200" />
      <div class="mb-2 h-4 w-5/6 rounded bg-gray-100" />
      <div class="h-4 w-2/3 rounded bg-gray-100" />
    </div>

    <!-- Block -->
    <div v-else class="rounded bg-gray-200" :style="{ width, height }" />
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    variant?: "block" | "text" | "avatar" | "card";
    width?: string;
    height?: string;
    size?: string;
    lines?: number;
    lastLineWidth?: string;
  }>(),
  {
    variant: "block",
    width: "100%",
    height: "1rem",
    size: "40px",
    lines: 3,
  }
);

const widths = ["92%", "100%", "85%", "70%", "90%", "65%", "80%", "95%", "75%", "60%"];
</script>
