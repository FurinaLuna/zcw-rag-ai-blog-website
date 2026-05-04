<template>
  <div v-if="articles.length > 0" class="related-articles mt-12 border-t border-border-default pt-8">
    <h2 class="mb-6 text-lg font-semibold text-text-primary">相关文章</h2>
    <div class="grid gap-4 sm:grid-cols-2">
      <NuxtLink
        v-for="article in articles"
        :key="article.id"
        :to="`/articles/${article.slug}`"
        class="rounded-lg border border-border-default p-4 transition-colors hover:border-accent"
      >
        <h3 class="mb-1 line-clamp-2 text-sm font-medium text-text-primary group-hover:text-accent">
          {{ article.title }}
        </h3>
        <p v-if="article.summary" class="line-clamp-2 text-xs text-text-tertiary">
          {{ article.summary }}
        </p>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  articles: Array<{
    id: number;
    title: string;
    summary?: string;
    slug: string;
  }>;
}>();
</script>
