<template>
  <div>
    <div v-if="loading" class="flex items-center justify-center py-16">
      <Skeleton variant="text" :lines="5" />
    </div>

    <div v-else-if="error" class="rounded-lg border border-red-200 bg-red-50 px-4 py-8 text-center">
      <p class="text-sm text-red-600">{{ error }}</p>
      <BaseButton v-if="onRetry" variant="ghost" size="sm" class="mt-2" @click="onRetry">重试</BaseButton>
    </div>

    <div v-else-if="empty" class="rounded-lg border border-border-default px-4 py-16 text-center">
      <p class="text-sm text-text-tertiary">{{ emptyText }}</p>
    </div>

    <div v-else class="overflow-x-auto rounded-lg border border-border-default">
      <table class="w-full" :class="dense ? 'text-xs' : 'text-sm'">
        <thead class="border-b border-border-default bg-gray-50">
          <tr>
            <th
              v-for="col in columns"
              :key="col.key"
              class="px-4 py-3 font-medium text-text-secondary"
              :class="col.align === 'right' ? 'text-right' : 'text-left'"
            >
              {{ col.label }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, i) in rows" :key="i" class="border-b border-border-default last:border-b-0">
            <td
              v-for="col in columns"
              :key="col.key"
              class="px-4 py-3"
              :class="col.align === 'right' ? 'text-right' : ''"
            >
              <slot :name="`cell-${col.key}`" :row="row" :value="row[col.key]">
                {{ row[col.key] }}
              </slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  columns: Array<{ key: string; label: string; align?: "left" | "right" }>;
  rows: Array<Record<string, any>>;
  loading?: boolean;
  error?: string;
  empty?: boolean;
  emptyText?: string;
  dense?: boolean;
  onRetry?: () => void;
}>();
</script>
