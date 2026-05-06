<template>
  <div class="mx-auto max-w-home px-4 py-12">
    <h1 class="mb-2 text-2xl font-bold text-text-primary">文章列表</h1>
    <p class="mb-8 text-sm text-text-tertiary">技术内容沉淀与知识分发</p>

    <div class="mb-6 flex flex-wrap gap-3">
      <select v-model="categorySlug" class="rounded-md border border-border-default px-3 py-1.5 text-sm" @change="fetchArticles">
        <option value="">全部分类</option>
        <option v-for="cat in categories" :key="cat.slug" :value="cat.slug">{{ cat.name }}</option>
      </select>
      <select v-model="sortBy" class="rounded-md border border-border-default px-3 py-1.5 text-sm" @change="fetchArticles">
        <option value="published_at">最新发布</option>
        <option value="view_count">最多浏览</option>
      </select>
    </div>

    <div v-if="loading" class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      <Skeleton v-for="i in 6" :key="i" variant="card" />
    </div>

    <div v-else-if="articles.length === 0" class="py-24 text-center">
      <p class="text-text-tertiary">{{ categorySlug ? '该分类下暂无文章' : '暂无文章' }}</p>
      <NuxtLink v-if="categorySlug" to="/articles" class="mt-3 inline-block text-sm text-accent hover:underline">
        清除筛选
      </NuxtLink>
    </div>

    <div v-else class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      <ArticleCard v-for="article in articles" :key="article.id" :article="article" />
    </div>

    <Pagination
      v-if="totalPages > 1"
      class="mt-8"
      :current="page"
      :total-pages="totalPages"
      @change="goPage"
    />
  </div>
</template>

<script setup lang="ts">
const api = useApi();

const articles = ref<ArticleListResponse[]>([]);
const categories = ref<CategoryResponse[]>([]);
const loading = ref(true);
const page = ref(1);
const totalPages = ref(1);
const categorySlug = ref("");
const sortBy = ref("published_at");

async function fetchArticles() {
  loading.value = true;
  try {
    const [artRes, catRes] = await Promise.all([
      api.get<ApiResponse<PaginatedData<ArticleListResponse>>>("/public/articles", {
        page: page.value,
        page_size: 12,
        category_slug: categorySlug.value || undefined,
        sort_by: sortBy.value,
      }),
      api.get<ApiResponse<CategoryResponse[]>>("/public/categories"),
    ]);
    if (artRes.success) {
      articles.value = artRes.data.items;
      totalPages.value = artRes.data.total_pages;
    }
    if (catRes.success) {
      categories.value = catRes.data;
    }
  } catch {
    // Error state
  } finally {
    loading.value = false;
  }
}

function goPage(p: number) {
  page.value = p;
  fetchArticles();
}

await fetchArticles();

useSeoMeta({
  title: "文章列表 - 智能内容平台",
  description: "浏览所有技术文章",
});
</script>
