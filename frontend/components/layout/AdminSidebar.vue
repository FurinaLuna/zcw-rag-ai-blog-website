<template>
  <aside class="fixed bottom-0 left-0 top-0 z-30 hidden w-[220px] border-r border-border-default bg-bg-surface lg:block">
    <div class="flex h-14 items-center border-b border-border-default px-4">
      <NuxtLink to="/admin" class="text-base font-semibold text-text-primary">
        运营后台
      </NuxtLink>
    </div>
    <nav class="p-3" aria-label="后台导航">
      <NuxtLink to="/admin" class="sidebar-item" active-class="sidebar-item-active">
        <span>概览</span>
      </NuxtLink>
      <NuxtLink to="/admin/articles" class="sidebar-item" active-class="sidebar-item-active">
        <span>文章管理</span>
      </NuxtLink>
      <NuxtLink to="/admin/monitor" class="sidebar-item" active-class="sidebar-item-active">
        <span>监控大盘</span>
      </NuxtLink>
      <NuxtLink to="/admin/knowledge" class="sidebar-item" active-class="sidebar-item-active">
        <span>知识库运维</span>
      </NuxtLink>
    </nav>
  </aside>
</template>

<style scoped>
.sidebar-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 2px;
  transition: background-color 0.15s, color 0.15s;
}
.sidebar-item:hover {
  background-color: #f3f4f6;
  color: var(--text-primary);
}
.sidebar-item-active {
  background-color: rgba(15, 118, 110, 0.08);
  color: var(--accent);
  font-weight: 500;
}
</style>
