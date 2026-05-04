<template>
  <div class="mx-auto max-w-ask px-4 py-12">
    <h1 class="mb-8 text-2xl font-bold text-text-primary">站内智能问答</h1>

    <div v-if="!messages.length" class="mb-6">
      <p class="mb-4 text-sm text-text-tertiary">试试这些问题：</p>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="q in suggestions"
          :key="q"
          class="rounded-full border border-border-default px-4 py-1.5 text-sm text-text-secondary transition-colors hover:border-accent hover:text-accent"
          @click="askQuestion(q)"
        >
          {{ q }}
        </button>
      </div>
    </div>

    <div class="mb-6 space-y-4">
      <div v-for="(msg, i) in messages" :key="i">
        <div class="mb-1 text-xs font-medium text-text-tertiary">
          {{ msg.role === "user" ? "你" : "AI 助手" }}
        </div>
        <div
          :class="msg.role === 'user'
            ? 'rounded-lg bg-gray-100 p-4 text-sm text-text-primary'
            : 'rounded-lg border border-border-default p-4'"
        >
          <div v-if="msg.role === 'assistant'" class="text-sm text-text-primary" v-text="msg.content" />
          <div v-else class="text-sm" v-text="msg.content" />

          <div v-if="msg.sources?.length" class="mt-3 border-t border-border-default pt-3">
            <p class="mb-2 text-xs font-medium text-text-tertiary">参考来源：</p>
            <ul class="space-y-1">
              <li v-for="(src, j) in msg.sources" :key="j">
                <NuxtLink
                  :to="`/articles/${src.article_slug}`"
                  class="text-xs text-accent hover:underline"
                >
                  {{ src.article_title }} (相关度: {{ (src.similarity * 100).toFixed(0) }}%)
                </NuxtLink>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <form class="flex gap-3" @submit.prevent="send">
      <input
        v-model="question"
        type="text"
        class="flex-1 rounded-lg border border-border-default px-4 py-3 text-sm outline-none focus:border-accent"
        placeholder="输入你的问题..."
        :disabled="sending"
      />
      <button
        type="submit"
        class="rounded-lg bg-accent px-6 py-3 text-sm font-medium text-white transition-opacity hover:opacity-90 disabled:opacity-50"
        :disabled="!question.trim() || sending"
      >
        {{ sending ? "思考中..." : "提问" }}
      </button>
    </form>

    <p v-if="error" class="mt-3 text-sm text-red-500">{{ error }}</p>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ ssr: false });

const route = useRoute();
const api = useApi();

const question = ref((route.query.q as string) || "");
const sending = ref(false);
const error = ref("");
const messages = ref<{ role: string; content: string; sources?: any[] }[]>([]);
const suggestions = ref<string[]>([]);

try {
  const res = await api.get<any>("/rag/suggestions");
  if (res.success) suggestions.value = res.data;
} catch {}

async function send() {
  if (!question.value.trim() || sending.value) return;
  const q = question.value.trim();
  messages.value.push({ role: "user", content: q });
  question.value = "";
  sending.value = true;
  error.value = "";

  try {
    const res = await api.post<any>("/rag/ask", { question: q });
    if (res.success) {
      messages.value.push({
        role: "assistant",
        content: res.data.answer,
        sources: res.data.sources || [],
      });
    }
  } catch {
    error.value = "请求失败，请稍后再试";
  } finally {
    sending.value = false;
  }
}

function askQuestion(q: string) {
  question.value = q;
  send();
}

useSeoMeta({ title: "AI 智能问答 - 智能内容平台" });
</script>
