<template>
  <nav v-if="totalPages > 1" class="flex items-center justify-center gap-1" aria-label="分页">
    <button
      class="rounded px-3 py-1.5 text-sm text-text-secondary hover:bg-gray-100 disabled:opacity-30"
      :disabled="current <= 1"
      @click="$emit('change', current - 1)"
      aria-label="上一页"
    >
      ‹
    </button>
    <button
      v-for="p in visiblePages"
      :key="p"
      class="rounded px-3 py-1.5 text-sm font-medium transition-colors"
      :class="p === current ? 'bg-accent text-white' : 'text-text-secondary hover:bg-gray-100'"
      :aria-current="p === current ? 'page' : undefined"
      @click="$emit('change', p)"
    >
      {{ p }}
    </button>
    <button
      class="rounded px-3 py-1.5 text-sm text-text-secondary hover:bg-gray-100 disabled:opacity-30"
      :disabled="current >= totalPages"
      @click="$emit('change', current + 1)"
      aria-label="下一页"
    >
      ›
    </button>
  </nav>
</template>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    current: number;
    totalPages: number;
    maxVisible?: number;
  }>(),
  { maxVisible: 7 }
);

defineEmits<{
  change: [page: number];
}>();

const visiblePages = computed(() => {
  const pages: number[] = [];
  const max = props.maxVisible;
  const total = props.totalPages;
  const cur = props.current;
  if (total <= max) {
    for (let i = 1; i <= total; i++) pages.push(i);
    return pages;
  }
  const half = Math.floor(max / 2);
  let start = Math.max(1, cur - half);
  let end = Math.min(total, start + max - 1);
  if (end - start + 1 < max) start = Math.max(1, end - max + 1);
  for (let i = start; i <= end; i++) pages.push(i);
  return pages;
});
</script>
