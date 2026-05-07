<template>
  <div class="mx-auto max-w-home px-4 py-12">
    <!-- Search mode toggle -->
    <div class="mb-6 flex items-center justify-center gap-2">
      <button
        class="rounded-full px-4 py-1.5 text-sm font-medium transition-colors"
        :class="mode === 'keyword' ? 'bg-accent text-white' : 'bg-gray-100 text-text-secondary hover:bg-gray-200'"
        @click="mode = 'keyword'"
      >关键词搜索</button>
      <button
        class="rounded-full px-4 py-1.5 text-sm font-medium transition-colors"
        :class="mode === 'semantic' ? 'bg-accent text-white' : 'bg-gray-100 text-text-secondary hover:bg-gray-200'"
        @click="mode = 'semantic'"
      >语义搜索</button>
    </div>

    <!-- Search form -->
    <form class="mb-8" @submit.prevent="doSearch(1)">
      <div class="flex gap-3">
        <input
          v-model="query"
          type="search"
          class="flex-1 rounded-lg border border-border-default px-4 py-3 text-sm outline-none focus:border-accent"
          placeholder="搜索文章..."
          style="height: 44px"
          :disabled="loading"
        />
        <button type="submit" class="rounded-lg bg-accent px-6 py-3 text-sm font-medium text-white" :disabled="loading">
          {{ loading ? "搜索中..." : "搜索" }}
        </button>
      </div>
      <p v-if="mode === 'semantic'" class="mt-2 text-xs text-text-tertiary">
        语义搜索根据含义匹配，无需精确关键词，支持自然语言描述
      </p>
    </form>

    <!-- Loading -->
    <div v-if="loading">
      <Skeleton v-for="i in 3" :key="i" variant="card" />
    </div>

    <!-- Empty result -->
    <div v-else-if="searched && results.length === 0" class="py-24 text-center">
      <p class="text-lg text-text-secondary">未找到与「{{ searchedQuery }}」相关的文章</p>
      <p class="mt-2 text-sm text-text-tertiary">{{ mode === 'semantic' ? '请尝试换一种描述方式' : '请尝试其他关键词' }}</p>
    </div>

    <!-- Results -->
    <div v-else-if="results.length > 0">
      <p class="mb-4 text-sm text-text-tertiary">
        找到 {{ total }} 条结果
        <span v-if="mode === 'semantic'" class="ml-1">（按相关度排序）</span>
      </p>

      <div v-for="item in results" :key="item.id" class="mb-4">
        <ArticleCard :article="item" class="hover:shadow-md transition-shadow" />
        <!-- Relevance + snippet for semantic search -->
        <div v-if="mode === 'semantic' && item.relevance != null" class="-mt-3 mb-2 px-1">
          <span class="text-xs text-accent">相关度 {{ (item.relevance * 100).toFixed(0) }}%</span>
          <p class="mt-1 text-xs text-text-tertiary line-clamp-2">{{ item.snippet }}</p>
        </div>
      </div>

      <!-- Pagination -->
      <div class="mt-8">
        <Pagination :current="page" :total-pages="totalPages" @change="doSearch" />
      </div>
    </div>

    <!-- Initial empty state -->
    <div v-else class="py-24 text-center text-text-tertiary">
      <p>输入关键词开始搜索</p>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ ssr: false });

const route = useRoute();
const api = useApi();

const q = route.query.q;
const query = ref((Array.isArray(q) ? q[0] : q) || "");
const mode = ref<"keyword" | "semantic">("keyword");
const results = ref<ArticleListResponse[]>([]);
const total = ref(0);
const page = ref(1);
const totalPages = ref(1);
const loading = ref(false);
const searched = ref(false);
const searchedQuery = ref("");

async function doSearch(p: number = 1) {
  if (!query.value.trim()) return;
  loading.value = true;
  searched.value = true;
  searchedQuery.value = query.value;
  page.value = p;
  try {
    if (mode.value === "semantic") {
      const res = await api.post<ApiResponse<PaginatedData<ArticleListResponse>>>("/public/search/semantic", {
        q: query.value,
        page: p,
        page_size: 20,
        threshold: 0.3,
      });
      if (res.success) {
        results.value = res.data.items;
        total.value = res.data.total;
        totalPages.value = res.data.total_pages;
      }
    } else {
      const res = await api.get<ApiResponse<PaginatedData<ArticleListResponse>>>("/public/search", {
        q: query.value,
        page: p,
        page_size: 20,
      });
      if (res.success) {
        results.value = res.data.items;
        total.value = res.data.total;
        totalPages.value = res.data.total_pages;
      }
    }
  } catch {} finally {
    loading.value = false;
  }
}

// Sync page param to URL
watch(page, (p) => {
  if (p > 1) navigateTo({ query: { q: query.value, page: p } }, { replace: true });
});

if (query.value) doSearch();

useSeoMeta({ title: "搜索 - 智能内容平台" });
</script>
