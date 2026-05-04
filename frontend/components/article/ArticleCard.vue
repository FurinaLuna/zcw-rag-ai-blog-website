<template>
  <NuxtLink
    :to="`/articles/${article.slug}`"
    class="group block rounded-lg border border-border-default bg-bg-surface p-5 transition-colors hover:border-accent"
  >
    <h3 class="mb-2 line-clamp-2 font-medium text-text-primary group-hover:text-accent transition-colors">
      {{ article.title }}
    </h3>
    <p v-if="article.summary" class="mb-3 line-clamp-3 text-sm text-text-secondary">
      {{ article.summary }}
    </p>
    <div class="flex flex-wrap items-center gap-2 text-xs text-text-tertiary">
      <span v-if="article.category" class="rounded bg-gray-100 px-2 py-0.5">
        {{ article.category.name }}
      </span>
      <span v-if="article.reading_time">{{ article.reading_time }} 分钟阅读</span>
      <span v-if="article.published_at">{{ formatDate(article.published_at) }}</span>
    </div>
  </NuxtLink>
</template>

<script setup lang="ts">
import dayjs from "dayjs";

const props = defineProps<{
  article: {
    id: number;
    title: string;
    summary?: string;
    slug: string;
    category?: { name: string };
    reading_time?: number;
    published_at?: string;
  };
}>();

function formatDate(date: string) {
  return dayjs(date).format("YYYY-MM-DD");
}
</script>
