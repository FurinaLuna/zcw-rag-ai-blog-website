<template>
  <div class="flex min-h-screen items-center justify-center bg-bg-page px-4">
    <div class="text-center">
      <h1 class="mb-2 text-6xl font-bold text-text-tertiary">{{ error?.statusCode || 500 }}</h1>
      <p class="mb-8 text-lg text-text-secondary">
        {{ error?.statusCode === 404 ? '页面不存在' : '服务器异常' }}
      </p>
      <p v-if="error?.message && error.statusCode !== 404" class="mb-6 text-sm text-text-tertiary">
        {{ error.message }}
      </p>
      <div class="flex justify-center gap-3">
        <button
          class="rounded-md border border-border-default px-5 py-2 text-sm text-text-secondary transition-colors hover:border-accent hover:text-accent"
          @click="handleError"
        >
          重试
        </button>
        <NuxtLink to="/" class="rounded-md bg-accent px-5 py-2 text-sm text-white transition-opacity hover:opacity-90">
          返回首页
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  error?: {
    statusCode?: number;
    message?: string;
  };
}>();

function handleError() {
  clearError({ redirect: "/" });
}
</script>
