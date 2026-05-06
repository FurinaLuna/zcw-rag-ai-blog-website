<template>
  <div class="home-page">
    <!-- Hero Section -->
    <section class="mx-auto max-w-home px-4 pb-12 pt-16">
      <div class="grid gap-8 lg:grid-cols-7 lg:gap-12">
        <div class="lg:col-span-5">
          <h1 class="mb-4 text-3xl font-bold tracking-tight text-text-primary lg:text-4xl">
            技术内容沉淀与智能检索
          </h1>
          <p class="mb-6 text-lg text-text-secondary leading-relaxed">
            基于 Nuxt3 混合渲染与 PgVector 向量检索的智能内容平台。在这里，内容高效分发，AI 精准作答。
          </p>
          <div class="flex gap-3">
            <NuxtLink to="/articles" class="inline-flex items-center rounded-lg bg-accent px-5 py-2.5 text-sm font-medium text-white transition-opacity hover:opacity-90">
              浏览文章
            </NuxtLink>
            <NuxtLink to="/ask" class="inline-flex items-center rounded-lg border border-border-default px-5 py-2.5 text-sm font-medium text-text-secondary transition-colors hover:border-accent hover:text-accent">
              AI 问答
            </NuxtLink>
          </div>
        </div>
        <div class="lg:col-span-2">
          <div class="rounded-lg border border-border-default bg-bg-surface p-4">
            <h3 class="mb-3 text-sm font-medium text-text-primary">快速提问</h3>
            <div class="space-y-2">
              <button
                v-for="q in quickQuestions"
                :key="q"
                class="w-full rounded-md border border-border-default px-3 py-2 text-left text-sm text-text-secondary transition-colors hover:border-accent hover:text-accent"
                @click="navigateTo(`/ask?q=${encodeURIComponent(q)}`)"
              >
                {{ q }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Featured Articles -->
    <section class="border-t border-border-default bg-bg-surface py-12">
      <div class="mx-auto max-w-home px-4">
        <h2 class="mb-8 text-2xl font-bold text-text-primary">精选文章</h2>
        <div v-if="loading" class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <Skeleton v-for="i in 3" :key="i" variant="card" />
        </div>
        <div v-else-if="articles.length === 0" class="py-16 text-center text-text-tertiary">
          暂无文章
        </div>
        <div v-else class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <ArticleCard v-for="article in articles" :key="article.id" :article="article" />
        </div>
      </div>
    </section>

    <!-- Topics Section -->
    <section class="py-12">
      <div class="mx-auto max-w-home px-4">
        <h2 class="mb-8 text-2xl font-bold text-text-primary">知识专题</h2>
        <div v-if="topics.length === 0" class="py-12 text-center text-text-tertiary">
          暂无专题
        </div>
        <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <NuxtLink
            v-for="topic in topics"
            :key="topic.id"
            :to="`/topics/${topic.slug}`"
            class="rounded-lg border border-border-default bg-bg-surface p-5 transition-colors hover:border-accent"
          >
            <h3 class="mb-1 font-medium text-text-primary">{{ topic.name }}</h3>
            <p class="text-sm text-text-tertiary">{{ topic.description || `${topic.article_count || 0} 篇文章` }}</p>
          </NuxtLink>
        </div>
      </div>
    </section>

    <!-- Metrics Section -->
    <section class="border-t border-border-default bg-bg-surface py-12">
      <div class="mx-auto max-w-home px-4">
        <h2 class="mb-8 text-2xl font-bold text-text-primary">系统能力</h2>
        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard label="文章总数" :value="totalArticles" />
          <MetricCard label="知识分片" :value="totalChunks" />
          <MetricCard label="混合渲染" value="SSG/SSR/CSR" />
          <MetricCard label="向量检索" value="PgVector" />
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "default" });

const api = useApi();

const articles = ref<ArticleListResponse[]>([]);
const topics = ref<CategoryResponse[]>([]);
const totalArticles = ref(0);
const totalChunks = ref(0);
const loading = ref(true);

const quickQuestions = [
  "Nuxt3 有哪些核心特性？",
  "什么是 RAG 技术？",
  "如何优化前端性能？",
];

try {
  const res = await api.get<ApiResponse<HomeData>>("/public/home");
  if (res.success) {
    articles.value = res.data.featured_articles || [];
    topics.value = res.data.topics || [];
    totalArticles.value = res.data.metrics?.total_articles || 0;
    totalChunks.value = res.data.metrics?.total_chunks || 0;
  }
} catch {
  // Use empty state
} finally {
  loading.value = false;
}

useSeoMeta({
  title: "智能内容平台 - 技术内容沉淀与智能检索",
  description: "基于 Nuxt3 混合渲染与 PgVector 向量检索的智能内容服务平台。",
});

useHead({
  script: [
    {
      type: "application/ld+json",
      innerHTML: JSON.stringify({
        "@context": "https://schema.org",
        "@type": "WebSite",
        name: "智能内容平台",
        description: "基于 Nuxt3 混合渲染与 PgVector 向量检索的智能内容服务平台",
        url: "http://localhost:3000",
        potentialAction: {
          "@type": "SearchAction",
          target: "http://localhost:3000/search?q={search_term_string}",
          "query-input": "required name=search_term_string",
        },
      }),
    } as any,
  ],
});
</script>
