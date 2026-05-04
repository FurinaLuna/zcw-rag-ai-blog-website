<template>
  <header class="site-header border-b border-border-default bg-bg-surface">
    <nav class="mx-auto flex max-w-home items-center justify-between px-4 h-14" aria-label="主导航">
      <NuxtLink to="/" class="text-lg font-semibold text-text-primary hover:text-accent transition-colors">
        智能内容平台
      </NuxtLink>

      <div class="hidden items-center gap-6 md:flex">
        <NuxtLink to="/" class="nav-link">首页</NuxtLink>
        <NuxtLink to="/articles" class="nav-link">文章</NuxtLink>
        <NuxtLink to="/topics" class="nav-link">专题</NuxtLink>
        <NuxtLink to="/ask" class="nav-link">AI 问答</NuxtLink>
        <NuxtLink to="/about" class="nav-link">关于</NuxtLink>
      </div>

      <button
        class="flex h-9 w-9 items-center justify-center rounded-md md:hidden hover:bg-gray-100"
        aria-label="打开菜单"
        @click="menuOpen = !menuOpen"
      >
        <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
          <path v-if="!menuOpen" fill-rule="evenodd" d="M3 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 15a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd" />
          <path v-else fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
        </svg>
      </button>
    </nav>

    <div v-if="menuOpen" class="border-t border-border-default bg-bg-surface px-4 pb-4 md:hidden">
      <NuxtLink to="/" class="block py-2" @click="menuOpen = false">首页</NuxtLink>
      <NuxtLink to="/articles" class="block py-2" @click="menuOpen = false">文章</NuxtLink>
      <NuxtLink to="/topics" class="block py-2" @click="menuOpen = false">专题</NuxtLink>
      <NuxtLink to="/ask" class="block py-2" @click="menuOpen = false">AI 问答</NuxtLink>
      <NuxtLink to="/about" class="block py-2" @click="menuOpen = false">关于</NuxtLink>
    </div>
  </header>
</template>

<script setup lang="ts">
const menuOpen = ref(false);

const route = useRoute();
watch(() => route.path, () => { menuOpen.value = false; });
</script>

<style scoped>
.nav-link {
  font-size: 14px;
  color: var(--text-secondary);
  transition: color 0.15s;
}
.nav-link:hover,
.nav-link.router-link-exact-active {
  color: var(--accent);
}
</style>
