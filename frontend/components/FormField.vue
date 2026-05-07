<template>
  <div class="form-field">
    <label v-if="label" :for="id" class="mb-1.5 block text-sm font-medium text-text-primary">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>
    <slot />
    <p v-if="helper && !error" class="mt-1 text-xs text-text-tertiary">{{ helper }}</p>
    <p v-if="error" class="mt-1 text-xs text-red-500" role="alert">{{ error }}</p>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    label?: string;
    error?: string;
    helper?: string;
    required?: boolean;
    id?: string;
  }>(),
  { required: false }
);
</script>
