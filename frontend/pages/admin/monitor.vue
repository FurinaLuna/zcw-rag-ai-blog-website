<template>
  <div>
    <h1 class="mb-8 text-2xl font-bold text-text-primary">监控大盘</h1>

    <div class="mb-6">
      <label class="mb-1 block text-sm font-medium text-text-primary">事件类型</label>
      <select v-model="eventType" class="rounded-md border border-border-default px-3 py-1.5 text-sm" @change="fetchLogs">
        <option value="">全部</option>
        <option value="pv">PV</option>
        <option value="web_vital">Web Vital</option>
        <option value="error">JS 错误</option>
        <option value="api_error">API 错误</option>
        <option value="resource_error">资源错误</option>
        <option value="exposure">曝光</option>
      </select>
    </div>

    <div v-if="loading" class="py-24 text-center text-sm text-text-tertiary">加载中...</div>

    <div v-else-if="logs.length === 0" class="py-24 text-center text-sm text-text-tertiary">
      暂无监控数据，请确保监控 SDK 已集成
    </div>

    <div v-else class="overflow-x-auto rounded-lg border border-border-default">
      <table class="w-full text-sm">
        <thead class="border-b border-border-default bg-gray-50">
          <tr>
            <th class="px-4 py-3 text-left font-medium text-text-secondary">类型</th>
            <th class="px-4 py-3 text-left font-medium text-text-secondary">页面</th>
            <th class="px-4 py-3 text-left font-medium text-text-secondary">数据</th>
            <th class="px-4 py-3 text-left font-medium text-text-secondary">时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in logs" :key="log.id" class="border-b border-border-default">
            <td class="px-4 py-3">
              <span class="rounded bg-gray-100 px-2 py-0.5 text-xs font-medium">{{ log.event_type }}</span>
            </td>
            <td class="px-4 py-3 max-w-[300px] truncate text-text-secondary">{{ log.page_url }}</td>
            <td class="px-4 py-3 max-w-[300px] truncate text-text-tertiary">{{ JSON.stringify(log.event_data).slice(0, 100) }}</td>
            <td class="px-4 py-3 text-text-tertiary">{{ formatDate(log.created_at) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "admin", middleware: "auth", ssr: false });

const api = useApi();
const logs = ref<any[]>([]);
const loading = ref(true);
const eventType = ref("");

async function fetchLogs() {
  loading.value = true;
  try {
    const res = await api.get<any>("/monitor/stats", {
      event_type: eventType.value || undefined,
      page_size: 50,
    });
    if (res.success) logs.value = res.data.items;
  } catch {} finally {
    loading.value = false;
  }
}

function formatDate(d: string) {
  return dayjs(d).format("MM-DD HH:mm:ss");
}

await fetchLogs();
</script>
