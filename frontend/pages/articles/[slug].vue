<template>
  <div>
    <ArticleProgress />

    <div class="mx-auto max-w-home px-4 py-12">
      <div v-if="loading" class="space-y-4">
        <Skeleton width="66%" height="2rem" />
        <Skeleton width="33%" height="1rem" />
        <div class="mt-8 space-y-2">
          <Skeleton v-for="i in 10" :key="i" variant="text" :lines="1" />
        </div>
      </div>

      <article v-else-if="article" class="lg:grid lg:grid-cols-[1fr_220px] lg:gap-10">
        <div class="min-w-0">
          <header class="mb-8">
            <h1 class="mb-3 text-3xl font-bold text-text-primary">{{ article.title }}</h1>
            <div class="flex flex-wrap items-center gap-3 text-sm text-text-tertiary">
              <span v-if="article.category" class="rounded bg-gray-100 px-2 py-0.5">{{ article.category.name }}</span>
              <span>{{ article.reading_time }} 分钟阅读</span>
              <span>{{ article.view_count }} 次浏览</span>
              <span v-if="article.published_at">{{ formatDate(article.published_at) }}</span>
            </div>
          </header>

          <!-- Mobile TOC -->
          <details class="mb-6 rounded-lg border border-border-default lg:hidden">
            <summary class="cursor-pointer px-4 py-3 text-sm font-medium text-text-secondary">
              目录
            </summary>
            <div class="border-t border-border-default px-4 pb-3 pt-2">
              <ArticleToc />
            </div>
          </details>

          <div class="prose" v-html="renderedContent" />

          <div class="mt-12 border-t border-border-default pt-6">
            <NuxtLink :to="`/ask?q=关于《${article.title}》的更多信息`" class="text-sm text-accent hover:underline">
              基于本文向 AI 提问 →
            </NuxtLink>
          </div>

          <RelatedArticles :articles="relatedArticles" />
          <CommentSection :article-slug="slug" />
        </div>

        <aside class="hidden lg:block">
          <div class="sticky top-20">
            <ArticleToc />
          </div>
        </aside>
      </article>

      <div v-else class="py-24 text-center">
        <h2 class="mb-4 text-xl font-semibold text-text-primary">文章不存在</h2>
        <NuxtLink to="/articles" class="text-accent hover:underline">返回文章列表</NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type MarkdownIt from "markdown-it";
import markdownit from "markdown-it";
import dayjs from "dayjs";
import "highlight.js/styles/github-dark.css";
import hljs from "highlight.js";

const route = useRoute();
const slug = route.params.slug as string;

const api = useApi();
const article = ref<ArticleDetailResponse | null>(null);
const loading = ref(true);
const relatedArticles = ref<ArticleListResponse[]>([]);

let md: MarkdownIt;

function createMarkdown(): MarkdownIt {
  const instance = markdownit({
    html: true,
    linkify: true,
    highlight(str: string, lang: string): string {
      try {
        if (lang && hljs.getLanguage(lang)) {
          return `<pre class="group relative"><code class="hljs ${lang}">${hljs.highlight(str, { language: lang }).value}</code><button class="copy-btn" onclick="navigator.clipboard.writeText(this.previousElementSibling.textContent);this.textContent='已复制';setTimeout(()=>this.textContent='复制',2000)" aria-label="复制代码">复制</button></pre>`;
        }
      } catch {}
      return `<pre class="group relative"><code>${instance.utils.escapeHtml(str)}</code><button class="copy-btn" onclick="navigator.clipboard.writeText(this.previousElementSibling.textContent);this.textContent='已复制';setTimeout(()=>this.textContent='复制',2000)" aria-label="复制代码">复制</button></pre>`;
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
  const res = await api.get<ApiResponse<ArticleDetailResponse>>(`/public/articles/${slug}`);
  if (res.success) {
    article.value = res.data;

    api.post(`/public/articles/${slug}/view`).catch(() => {});

    useSeoMeta({
      title: article.value.seo_title || article.value.title,
      description: article.value.seo_description || article.value.summary,
    });

    // JSON-LD structured data
    useHead({
      script: [
        {
          type: "application/ld+json",
          innerHTML: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "Article",
            headline: article.value.title,
            description: article.value.summary || "",
            datePublished: article.value.published_at,
            dateModified: article.value.updated_at,
            author: { "@type": "Organization", name: "智能内容平台" },
            publisher: { "@type": "Organization", name: "智能内容平台" },
          }),
        },
      ],
    });

    relatedArticles.value = res.data.related_articles || [];
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

<style scoped>
:deep(.copy-btn) {
  position: absolute;
  top: 8px;
  right: 8px;
  background: #374151;
  color: #d1d5db;
  border: none;
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 12px;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.15s;
}
:deep(pre:hover .copy-btn) {
  opacity: 1;
}
:deep(.copy-btn:hover) {
  background: #4b5563;
}
</style>
