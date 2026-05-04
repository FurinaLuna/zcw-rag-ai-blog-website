<template>
  <div class="mx-auto max-w-home px-4 py-12">
    <form class="mb-8" @submit.prevent="doSearch">
      <div class="flex gap-3">
        <input
          v-model="query"
          type="search"
          class="flex-1 rounded-lg border border-border-default px-4 py-3 text-sm outline-none focus:border-accent"
          placeholder="搜索文章..."
          style="height: 44px"
        />
        <button type="submit" class="rounded-lg bg-accent px-6 py-3 text-sm font-medium text-white">
          搜索
        </button>
      </div>
    </form>

    <div v-if="loading">
      <Skeleton v-for="i in 3" :key="i" variant="card" />
    </div>

    <div v-else-if="searched && results.length === 0" class="py-24 text-center text-text-tertiary">
      未找到包含「{{ searchedQuery }}」的文章，请尝试其他关键词
    </div>

    <div v-else-if="results.length > 0">
      <p class="mb-4 text-sm text-text-tertiary">找到 {{ total }} 条结果</p>
      <ArticleCard v-for="article in results" :key="article.id" :article="article" class="mb-4" />
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ ssr: false });

const route = useRoute();
const api = useApi();

const query = ref((route.query.q as string) || "");
const results = ref<any[]>([]);
const total = ref(0);
const loading = ref(false);
const searched = ref(false);
const searchedQuery = ref("");

async function doSearch() {
  if (!query.value.trim()) return;
  loading.value = true;
  searched.value = true;
  searchedQuery.value = query.value;
  try {
    const res = await api.get<any>("/public/search", { q: query.value });
    if (res.success) {
      results.value = res.data.items;
      total.value = res.data.total;
    }
  } catch {} finally {
    loading.value = false;
  }
}

if (query.value) doSearch();

useSeoMeta({ title: "搜索 - 智能内容平台" });
</script>
