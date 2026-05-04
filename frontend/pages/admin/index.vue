<template>
  <div>
    <h1 class="mb-8 text-2xl font-bold text-text-primary">运营概览</h1>

    <div class="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <MetricCard label="今日 PV" :value="overview.pv" />
      <MetricCard label="今日 UV" :value="overview.uv" />
      <MetricCard label="RAG 问答" :value="overview.rag_questions" />
      <MetricCard label="今日异常" :value="overview.error_count" />
    </div>

    <div class="mb-8">
      <h2 class="mb-4 text-lg font-semibold text-text-primary">访问趋势 (近7天)</h2>
      <ClientOnly>
        <TrendChart v-if="trends.length > 0" :data="trends" />
        <div v-else class="flex h-[320px] items-center justify-center rounded-lg border border-border-default text-sm text-text-tertiary">
          暂无趋势数据
        </div>
      </ClientOnly>
    </div>

    <div class="mb-8">
      <h2 class="mb-4 text-lg font-semibold text-text-primary">热门文章</h2>
      <div v-if="popular.length === 0" class="py-8 text-center text-sm text-text-tertiary">
        暂无数据
      </div>
      <div v-else class="overflow-x-auto rounded-lg border border-border-default">
        <table class="w-full text-sm">
          <thead class="border-b border-border-default bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left font-medium text-text-secondary">标题</th>
              <th class="px-4 py-3 text-right font-medium text-text-secondary">浏览量</th>
              <th class="px-4 py-3 text-right font-medium text-text-secondary">评论数</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="article in popular" :key="article.id" class="border-b border-border-default">
              <td class="px-4 py-3">
                <NuxtLink :to="`/articles/${article.slug}`" class="text-accent hover:underline">
                  {{ article.title }}
                </NuxtLink>
              </td>
              <td class="px-4 py-3 text-right text-text-secondary">{{ article.view_count }}</td>
              <td class="px-4 py-3 text-right text-text-secondary">{{ article.comment_count }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div>
      <h2 class="mb-4 text-lg font-semibold text-text-primary">知识库状态</h2>
      <div v-if="knowledge" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard label="总文章数" :value="knowledge.total_articles" />
        <MetricCard label="已同步" :value="knowledge.synced" />
        <MetricCard label="待同步" :value="knowledge.pending" />
        <MetricCard label="同步失败" :value="knowledge.failed" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "admin", middleware: "auth", ssr: false });

const api = useApi();
const overview = ref({ pv: 0, uv: 0, rag_questions: 0, error_count: 0 });
const popular = ref<any[]>([]);
const knowledge = ref<any>(null);
const trends = ref<any[]>([]);

try {
  const [overRes, popRes, knowRes, trendRes] = await Promise.all([
    api.get<any>("/admin/dashboard/overview"),
    api.get<any>("/admin/dashboard/popular-articles", { limit: 10 }),
    api.get<any>("/admin/knowledge/status"),
    api.get<any>("/admin/dashboard/trends", { days: 7 }),
  ]);
  if (overRes.success) overview.value = overRes.data;
  if (popRes.success) popular.value = popRes.data;
  if (knowRes.success) knowledge.value = knowRes.data;
  if (trendRes.success) trends.value = trendRes.data;
} catch {}
</script>
