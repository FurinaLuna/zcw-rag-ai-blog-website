<template>
  <div>
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-2xl font-bold text-text-primary">知识库运维</h1>
      <button
        class="rounded-md bg-accent px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        :disabled="rebuilding"
        @click="rebuildAll"
      >
        {{ rebuilding ? "重建中..." : "全量重建" }}
      </button>
    </div>

    <div class="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
      <div class="rounded-lg border border-border-default p-4">
        <div class="text-xs text-text-tertiary">总文章</div>
        <div class="text-xl font-semibold text-text-primary">{{ status?.total_articles ?? "--" }}</div>
      </div>
      <div class="rounded-lg border border-border-default p-4">
        <div class="text-xs text-text-tertiary">已同步</div>
        <div class="text-xl font-semibold text-green-600">{{ status?.synced ?? "--" }}</div>
      </div>
      <div class="rounded-lg border border-border-default p-4">
        <div class="text-xs text-text-tertiary">同步中</div>
        <div class="text-xl font-semibold text-blue-600">{{ status?.syncing ?? "--" }}</div>
      </div>
      <div class="rounded-lg border border-border-default p-4">
        <div class="text-xs text-text-tertiary">待同步</div>
        <div class="text-xl font-semibold text-gray-500">{{ status?.pending ?? "--" }}</div>
      </div>
      <div class="rounded-lg border border-border-default p-4">
        <div class="text-xs text-text-tertiary">失败</div>
        <div class="text-xl font-semibold text-red-500">{{ status?.failed ?? "--" }}</div>
      </div>
    </div>

    <div v-if="articles.length > 0" class="overflow-x-auto rounded-lg border border-border-default">
      <table class="w-full text-sm">
        <thead class="border-b border-border-default bg-gray-50">
          <tr>
            <th class="px-4 py-3 text-left font-medium text-text-secondary">文章</th>
            <th class="px-4 py-3 text-left font-medium text-text-secondary">向量状态</th>
            <th class="px-4 py-3 text-right font-medium text-text-secondary">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="a in articles" :key="a.id" class="border-b border-border-default">
            <td class="px-4 py-3">{{ a.title }}</td>
            <td class="px-4 py-3">
              <span
                class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium"
                :class="vectorClass(a.vector_status)"
              >
                {{ vectorLabel(a.vector_status) }}
              </span>
            </td>
            <td class="px-4 py-3 text-right">
              <button
                class="text-xs text-accent hover:underline"
                :disabled="syncingId === a.id"
                @click="syncSingle(a.id)"
              >
                {{ syncingId === a.id ? "同步中..." : "同步" }}
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
const status = ref<any>(null);
const articles = ref<any[]>([]);
const rebuilding = ref(false);
const syncingId = ref<number | null>(null);

async function fetchStatus() {
  try {
    const [sRes, aRes] = await Promise.all([
      api.get<any>("/admin/knowledge/status"),
      api.get<any>("/admin/knowledge/articles", { page_size: 50 }),
    ]);
    if (sRes.success) status.value = sRes.data;
    if (aRes.success) articles.value = aRes.data.items;
  } catch {}
}

async function syncSingle(id: number) {
  syncingId.value = id;
  try {
    await api.post(`/admin/articles/${id}/sync-vector`);
    fetchStatus();
  } catch {} finally {
    syncingId.value = null;
  }
}

async function rebuildAll() {
  rebuilding.value = true;
  try {
    await api.post("/admin/knowledge/rebuild");
    fetchStatus();
  } catch {} finally {
    rebuilding.value = false;
  }
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

await fetchStatus();
</script>
