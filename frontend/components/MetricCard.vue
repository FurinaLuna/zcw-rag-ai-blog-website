<template>
  <div class="rounded-lg border border-border-default bg-bg-surface p-5">
    <div class="mb-1 text-sm text-text-tertiary">{{ label }}</div>
    <div class="text-2xl font-semibold text-text-primary">{{ displayValue }}</div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  label: string;
  value: string | number | null;
}>();

const displayValue = computed(() => {
  if (props.value === null || props.value === undefined) return "--";
  return String(props.value);
});
</script>
