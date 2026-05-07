<template>
  <span
    class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium"
    :class="badgeClass"
  >
    {{ label }}
  </span>
</template>

<script setup lang="ts">
const props = defineProps<{
  status: string;
}>();

const labelMap: Record<string, string> = {
  draft: "草稿",
  published: "已发布",
  archived: "已归档",
};

const classMap: Record<string, string> = {
  draft: "bg-yellow-100 text-yellow-700",
  published: "bg-green-100 text-green-700",
  archived: "bg-gray-100 text-gray-600",
};

const label = computed(() => labelMap[props.status] || props.status);
const badgeClass = computed(() => classMap[props.status] || "bg-gray-100 text-gray-600");
</script>
