<template>
  <div>
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-2xl font-bold text-text-primary">文章管理</h1>
      <NuxtLink to="/admin/articles/new" class="rounded-md bg-accent px-4 py-2 text-sm font-medium text-white">
        新建文章
      </NuxtLink>
    </div>

    <div class="mb-4 flex gap-3">
      <input
        v-model="keyword"
        type="text"
        class="rounded-md border border-border-default px-3 py-1.5 text-sm outline-none focus:border-accent"
        placeholder="搜索文章..."
        style="height: 36px"
        @input="debouncedSearch"
      />
      <select v-model="statusFilter" class="rounded-md border border-border-default px-3 py-1.5 text-sm" @change="fetchArticles">
        <option value="">全部状态</option>
        <option value="draft">草稿</option>
        <option value="published">已发布</option>
        <option value="archived">已归档</option>
      </select>
    </div>

    <div v-if="loading" class="py-24 text-center text-sm text-text-tertiary">加载中...</div>

    <div v-else-if="articles.length === 0" class="py-24 text-center text-sm text-text-tertiary">
      暂无文章
    </div>

    <div v-else class="overflow-x-auto rounded-lg border border-border-default">
      <table class="w-full text-sm">
        <thead class="border-b border-border-default bg-gray-50">
          <tr>
            <th class="px-4 py-3 text-left font-medium text-text-secondary">标题</th>
            <th class="px-4 py-3 text-left font-medium text-text-secondary">状态</th>
            <th class="px-4 py-3 text-left font-medium text-text-secondary">向量</th>
            <th class="px-4 py-3 text-right font-medium text-text-secondary">浏览</th>
            <th class="px-4 py-3 text-left font-medium text-text-secondary">更新</th>
            <th class="px-4 py-3 text-right font-medium text-text-secondary">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="article in articles" :key="article.id" class="border-b border-border-default">
            <td class="px-4 py-3 max-w-[300px] truncate">
              <NuxtLink :to="`/admin/articles/${article.id}`" class="text-accent hover:underline">
                {{ article.title }}
              </NuxtLink>
            </td>
            <td class="px-4 py-3">
              <StatusBadge :status="article.status" />
            </td>
            <td class="px-4 py-3">
              <span
                class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium"
                :class="vectorClass(article.vector_status)"
              >
                {{ vectorLabel(article.vector_status) }}
              </span>
            </td>
            <td class="px-4 py-3 text-right text-text-secondary">{{ article.view_count }}</td>
            <td class="px-4 py-3 text-text-tertiary">{{ formatDate(article.updated_at) }}</td>
            <td class="px-4 py-3 text-right">
              <button
                v-if="article.status !== 'published'"
                class="mr-2 text-xs text-accent hover:underline"
                @click="publishArticle(article.id)"
              >
                发布
              </button>
              <button class="mr-2 text-xs text-red-500 hover:underline" @click="deleteArticle(article.id)">
                删除
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "admin", middleware: "auth", ssr: false });

const api = useApi();
const articles = ref<any[]>([]);
const loading = ref(true);
const keyword = ref("");
const statusFilter = ref("");

let timer: ReturnType<typeof setTimeout>;
function debouncedSearch() {
  clearTimeout(timer);
  timer = setTimeout(fetchArticles, 300);
}

async function fetchArticles() {
  loading.value = true;
  try {
    const res = await api.get<any>("/admin/articles", {
      page_size: 50,
      keyword: keyword.value || undefined,
      status: statusFilter.value || undefined,
    });
    if (res.success) articles.value = res.data.items;
  } catch {} finally {
    loading.value = false;
  }
}

async function publishArticle(id: number) {
  try {
    await api.post(`/admin/articles/${id}/publish`);
    fetchArticles();
  } catch {}
}

async function deleteArticle(id: number) {
  if (!confirm("确定删除该文章？")) return;
  try {
    await api.delete(`/admin/articles/${id}`);
    fetchArticles();
  } catch {}
}

function vectorLabel(s: string) {
  const map: Record<string, string> = { synced: "已同步", syncing: "同步中", pending: "待同步", failed: "失败" };
  return map[s] || s;
}

function vectorClass(s: string) {
  const map: Record<string, string> = {
    synced: "bg-green-100 text-green-700",
    syncing: "bg-blue-100 text-blue-700",
    pending: "bg-gray-100 text-gray-600",
    failed: "bg-red-100 text-red-700",
  };
  return map[s] || "";
}

function formatDate(d: string) {
  return dayjs(d).format("MM-DD HH:mm");
}

await fetchArticles();
</script>
