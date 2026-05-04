<template>
  <div class="mx-auto max-w-content px-4 py-12">
    <div v-if="loading" class="animate-pulse">
      <div class="mb-4 h-8 w-2/3 rounded bg-gray-200" />
      <div class="mb-2 h-4 w-1/3 rounded bg-gray-100" />
      <div class="mt-8 space-y-2">
        <div v-for="i in 10" :key="i" class="h-4 rounded bg-gray-100" :style="{ width: `${100 - i * 5}%` }" />
      </div>
    </div>

    <article v-else-if="article">
      <header class="mb-8">
        <h1 class="mb-3 text-3xl font-bold text-text-primary">{{ article.title }}</h1>
        <div class="flex flex-wrap items-center gap-3 text-sm text-text-tertiary">
          <span v-if="article.category" class="rounded bg-gray-100 px-2 py-0.5">{{ article.category.name }}</span>
          <span>{{ article.reading_time }} 分钟阅读</span>
          <span>{{ article.view_count }} 次浏览</span>
          <span v-if="article.published_at">{{ formatDate(article.published_at) }}</span>
        </div>
      </header>

      <div class="prose" v-html="renderedContent" />

      <div class="mt-12 border-t border-border-default pt-6">
        <NuxtLink :to="`/ask?q=关于《${article.title}》的更多信息`" class="text-sm text-accent hover:underline">
          基于本文向 AI 提问 →
        </NuxtLink>
      </div>

      <CommentSection :article-slug="slug" />
    </article>

    <div v-else class="py-24 text-center">
      <h2 class="mb-4 text-xl font-semibold text-text-primary">文章不存在</h2>
      <NuxtLink to="/articles" class="text-accent hover:underline">返回文章列表</NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import type MarkdownIt from "markdown-it";
import markdownit from "markdown-it";
import dayjs from "dayjs";
import "highlight.js/styles/github-dark.css";

const route = useRoute();
const slug = route.params.slug as string;

const api = useApi();
const article = ref<any>(null);
const loading = ref(true);

let md: MarkdownIt;

function createMarkdown(): MarkdownIt {
  const instance = markdownit({
    html: true,
    linkify: true,
    highlight(str: string, lang: string): string {
      try {
        const hljs = require("highlight.js");
        if (lang && hljs.getLanguage(lang)) {
          return `<pre><code class="hljs ${lang}">${hljs.highlight(str, { language: lang }).value}</code></pre>`;
        }
      } catch {}
      return `<pre><code>${instance.utils.escapeHtml(str)}</code></pre>`;
    },
  });
  return instance;
}

md = createMarkdown();

const renderedContent = computed(() => {
  if (!article.value?.content_md) return "";
  return md.render(article.value.content_md);
});

try {
  const res = await api.get<any>(`/public/articles/${slug}`);
  if (res.success) {
    article.value = res.data;

    api.post(`/public/articles/${slug}/view`).catch(() => {});

    useSeoMeta({
      title: article.value.seo_title || article.value.title,
      description: article.value.seo_description || article.value.summary,
    });
  }
} catch {
  article.value = null;
} finally {
  loading.value = false;
}

function formatDate(date: string) {
  return dayjs(date).format("YYYY-MM-DD");
}
</script>
