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

    <div class="mb-8">
      <h2 class="mb-4 text-lg font-semibold text-text-primary">Web Vitals 状态</h2>
      <div class="grid gap-4 sm:grid-cols-3">
        <div class="rounded-lg border border-border-default p-4">
          <div class="text-xs text-text-tertiary">LCP</div>
          <div class="mt-1 text-xl font-semibold" :class="vitalsClass(vitals.lcp)">{{ vitals.lcp || '--' }}ms</div>
        </div>
        <div class="rounded-lg border border-border-default p-4">
          <div class="text-xs text-text-tertiary">CLS</div>
          <div class="mt-1 text-xl font-semibold" :class="vitalsClass(vitals.cls)">{{ vitals.cls || '--' }}</div>
        </div>
        <div class="rounded-lg border border-border-default p-4">
          <div class="text-xs text-text-tertiary">INP</div>
          <div class="mt-1 text-xl font-semibold" :class="vitalsClass(vitals.inp)">{{ vitals.inp || '--' }}ms</div>
        </div>
      </div>
    </div>

    <div class="mb-8">
      <h2 class="mb-4 text-lg font-semibold text-text-primary">最近错误</h2>
      <div v-if="recentErrors.length === 0" class="rounded-lg border border-border-default p-8 text-center text-sm text-text-tertiary">
        暂无错误记录
      </div>
      <div v-else class="overflow-x-auto rounded-lg border border-border-default">
        <table class="w-full text-sm">
          <thead class="border-b border-border-default bg-gray-50">
            <tr>
              <th class="px-4 py-2 text-left font-medium text-text-secondary">类型</th>
              <th class="px-4 py-2 text-left font-medium text-text-secondary">消息</th>
              <th class="px-4 py-2 text-left font-medium text-text-secondary">时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="err in recentErrors" :key="err.id" class="border-b border-border-default">
              <td class="px-4 py-2">
                <span class="rounded bg-red-100 px-2 py-0.5 text-xs font-medium text-red-600">{{ err.event_type }}</span>
              </td>
              <td class="max-w-[400px] truncate px-4 py-2 text-text-secondary">
                {{ err.event_data?.message || err.event_data?.error_type || '-' }}
              </td>
              <td class="px-4 py-2 text-text-tertiary">{{ formatTime(err.created_at) }}</td>
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

import dayjs from "dayjs";

const api = useApi();
const overview = ref<TodayOverview>({ pv: 0, uv: 0, rag_questions: 0, error_count: 0 });
const popular = ref<HotArticle[]>([]);
const knowledge = ref<KnowledgeStatus | null>(null);
const trends = ref<TrendItem[]>([]);
const recentErrors = ref<MonitorLogResponse[]>([]);
const vitals = ref({ lcp: 0, cls: 0, inp: 0 });

try {
  const [overRes, popRes, knowRes, trendRes, errRes, vitalsRes] = await Promise.all([
    api.get<ApiResponse<TodayOverview>>("/admin/dashboard/overview"),
    api.get<ApiResponse<HotArticle[]>>("/admin/dashboard/popular-articles", { limit: 10 }),
    api.get<ApiResponse<KnowledgeStatus>>("/admin/knowledge/status"),
    api.get<ApiResponse<TrendItem[]>>("/admin/dashboard/trends", { days: 7 }),
    api.get<ApiResponse<PaginatedData<MonitorLogResponse>>>("/monitor/stats", { event_type: "error", page_size: 10 }),
    api.get<ApiResponse<PaginatedData<MonitorLogResponse>>>("/monitor/stats", { event_type: "web_vital", page_size: 200 }),
  ]);
  if (overRes.success) overview.value = overRes.data;
  if (popRes.success) popular.value = popRes.data;
  if (knowRes.success) knowledge.value = knowRes.data;
  if (trendRes.success) trends.value = trendRes.data;
  if (errRes.success) recentErrors.value = errRes.data.items;
  if (vitalsRes.success) {
    const items = vitalsRes.data.items;
    const metrics: Record<string, number[]> = {};
    for (const item of items) {
      const m = item.event_data?.metric;
      const v = item.event_data?.value;
      if (m && typeof v === "number") {
        (metrics[m as string] ||= []).push(v);
      }
    }
    vitals.value = {
      lcp: metrics.LCP?.length ? Math.round(metrics.LCP.reduce((a, b) => a + b) / metrics.LCP.length) : 0,
      cls: metrics.CLS?.length ? Math.round(metrics.CLS.reduce((a, b) => a + b) / metrics.CLS.length * 100) / 100 : 0,
      inp: metrics.INP?.length ? Math.round(metrics.INP.reduce((a, b) => a + b) / metrics.INP.length) : 0,
    };
  }
} catch {}

function vitalsClass(val: number | string) {
  if (val === 0 || val === "--") return "text-text-tertiary";
  return +val > 2500 ? "text-red-500" : "text-green-600";
}

function formatTime(d: string) {
  return dayjs(d).format("MM-DD HH:mm");
}
</script>
