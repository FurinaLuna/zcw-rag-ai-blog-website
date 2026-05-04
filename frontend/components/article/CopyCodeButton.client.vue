<template>
  <button
    v-if="copied"
    class="absolute right-2 top-2 rounded bg-green-600 px-2 py-1 text-xs text-white"
  >
    已复制
  </button>
  <button
    v-else
    class="absolute right-2 top-2 rounded bg-gray-700 px-2 py-1 text-xs text-gray-300 opacity-0 transition-opacity group-hover:opacity-100 hover:bg-gray-600"
    aria-label="复制代码"
    @click="copyCode"
  >
    复制
  </button>
</template>

<script setup lang="ts">
const copied = ref(false);

function copyCode() {
  const pre = (getCurrentInstance()?.vnode.el as HTMLElement)?.closest("pre");
  if (!pre) return;
  const code = pre.querySelector("code");
  if (!code) return;
  navigator.clipboard.writeText(code.textContent || "").then(() => {
    copied.value = true;
    setTimeout(() => { copied.value = false; }, 2000);
  });
}
</script>
