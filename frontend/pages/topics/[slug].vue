<template>
  <div class="mx-auto max-w-home px-4 py-12">
    <div v-if="topic">
      <h1 class="mb-2 text-2xl font-bold text-text-primary">{{ topic.name }}</h1>
      <p class="mb-8 text-sm text-text-secondary">{{ topic.description }}</p>
    </div>

    <div v-if="loading" class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      <Skeleton v-for="i in 3" :key="i" variant="card" />
    </div>

    <div v-else-if="articles.length === 0" class="py-24 text-center text-text-tertiary">
      该专题下暂无文章
    </div>

    <div v-else class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      <ArticleCard v-for="article in articles" :key="article.id" :article="article" />
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute();
const slug = route.params.slug as string;
const api = useApi();

const topic = ref<CategoryResponse | null>(null);
const articles = ref<ArticleListResponse[]>([]);
const loading = ref(true);

try {
  const [topicRes, artRes] = await Promise.all([
    api.get<ApiResponse<CategoryResponse>>(`/public/topics/${slug}`),
    api.get<ApiResponse<PaginatedData<ArticleListResponse>>>("/public/articles", { topic_slug: slug, page_size: 20 }),
  ]);
  if (topicRes.success) topic.value = topicRes.data;
  if (artRes.success) articles.value = artRes.data.items;
} catch {
} finally {
  loading.value = false;
}

useSeoMeta({
  title: topic.value ? `${topic.value.name} - 智能内容平台` : "专题详情",
  description: topic.value?.description || "",
});
</script>
