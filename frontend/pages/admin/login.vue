<template>
  <div class="flex min-h-screen items-center justify-center bg-bg-page px-4">
    <div class="w-full max-w-sm">
      <h1 class="mb-8 text-center text-xl font-bold text-text-primary">管理员登录</h1>

      <form class="rounded-lg border border-border-default bg-bg-surface p-6" @submit.prevent="handleLogin">
        <FormField id="username" label="账号" :error="error" class="mb-4">
          <input
            id="username"
            v-model="username"
            type="text"
            class="w-full rounded-md border border-border-default px-3 py-2 text-sm outline-none focus:border-accent"
            placeholder="请输入账号"
            :disabled="loading"
            style="height: 40px"
          />
        </FormField>
        <FormField id="password" label="密码" class="mb-4">
          <input
            id="password"
            v-model="password"
            type="password"
            class="w-full rounded-md border border-border-default px-3 py-2 text-sm outline-none focus:border-accent"
            placeholder="请输入密码"
            :disabled="loading"
            style="height: 40px"
          />
        </FormField>
        <BaseButton type="submit" variant="primary" size="md" block :loading="loading" :disabled="!username || !password || loading">
          {{ loading ? "登录中..." : "登录" }}
        </BaseButton>
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
  } catch (e: unknown) {
    const err = e as { data?: { message?: string } } | undefined;
    error.value = err?.data?.message || "登录失败，请检查账号密码";
  } finally {
    loading.value = false;
  }
}

useSeoMeta({ title: "管理员登录" });
</script>
