<template>
  <div class="flex min-h-screen items-center justify-center bg-bg-page px-4">
    <div class="w-full max-w-sm">
      <h1 class="mb-8 text-center text-xl font-bold text-text-primary">管理员登录</h1>

      <form class="rounded-lg border border-border-default bg-bg-surface p-6" @submit.prevent="handleLogin">
        <div class="mb-4">
          <label class="mb-1.5 block text-sm font-medium text-text-primary" for="username">账号</label>
          <input
            id="username"
            v-model="username"
            type="text"
            class="w-full rounded-md border border-border-default px-3 py-2 text-sm outline-none focus:border-accent"
            placeholder="请输入账号"
            :disabled="loading"
            style="height: 40px"
          />
        </div>
        <div class="mb-6">
          <label class="mb-1.5 block text-sm font-medium text-text-primary" for="password">密码</label>
          <input
            id="password"
            v-model="password"
            type="password"
            class="w-full rounded-md border border-border-default px-3 py-2 text-sm outline-none focus:border-accent"
            placeholder="请输入密码"
            :disabled="loading"
            style="height: 40px"
          />
        </div>
        <p v-if="error" class="mb-4 text-sm text-red-500">{{ error }}</p>
        <button
          type="submit"
          class="w-full rounded-md bg-accent py-2.5 text-sm font-medium text-white transition-opacity hover:opacity-90 disabled:opacity-50"
          :disabled="!username || !password || loading"
          style="height: 40px"
        >
          {{ loading ? "登录中..." : "登录" }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false, ssr: false });

const username = ref("");
const password = ref("");
const loading = ref(false);
const error = ref("");
const authStore = useAuthStore();

async function handleLogin() {
  if (!username.value || !password.value) return;
  loading.value = true;
  error.value = "";
  try {
    await authStore.login(username.value, password.value);
    navigateTo("/admin");
  } catch (e: any) {
    error.value = e?.data?.message || "登录失败，请检查账号密码";
  } finally {
    loading.value = false;
  }
}

useSeoMeta({ title: "管理员登录" });
</script>
