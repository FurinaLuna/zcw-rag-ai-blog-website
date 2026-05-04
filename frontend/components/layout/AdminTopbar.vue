<template>
  <header class="flex h-14 items-center justify-between border-b border-border-default bg-bg-surface px-6">
    <div class="flex items-center gap-3">
      <NuxtLink to="/" class="text-sm text-accent hover:underline" target="_blank">查看前台</NuxtLink>
    </div>
    <div class="flex items-center gap-3">
      <span v-if="authStore.admin" class="text-sm text-text-secondary">
        {{ authStore.admin.username }}
      </span>
      <button class="text-sm text-text-tertiary hover:text-text-primary" @click="handleLogout">
        退出
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
const authStore = useAuthStore();

function handleLogout() {
  authStore.logout();
  navigateTo("/admin/login");
}
</script>
