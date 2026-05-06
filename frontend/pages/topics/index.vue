<template>
  <div class="mx-auto max-w-home px-4 py-12">
    <h1 class="mb-2 text-2xl font-bold text-text-primary">知识专题</h1>
    <p class="mb-8 text-sm text-text-tertiary">系统化知识体系，深度探索技术主题</p>

    <div v-if="topics.length === 0" class="py-24 text-center text-text-tertiary">
      暂无专题
    </div>
    <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <NuxtLink
        v-for="topic in topics"
        :key="topic.id"
        :to="`/topics/${topic.slug}`"
        class="rounded-lg border border-border-default bg-bg-surface p-6 transition-colors hover:border-accent"
      >
        <h3 class="mb-2 text-lg font-medium text-text-primary">{{ topic.name }}</h3>
        <p class="mb-3 text-sm text-text-secondary">{{ topic.description }}</p>
        <span class="text-xs text-text-tertiary">{{ topic.article_count || 0 }} 篇文章</span>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
const api = useApi();
const topics = ref<CategoryResponse[]>([]);

try {
  const res = await api.get<ApiResponse<CategoryResponse[]>>("/public/topics");
  if (res.success) topics.value = res.data;
} catch {}

useSeoMeta({ title: "知识专题 - 智能内容平台", description: "系统化知识体系" });
</script>
