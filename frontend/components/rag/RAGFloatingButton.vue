<template>
  <ClientOnly>
    <div class="rag-floating">
      <button
        ref="triggerRef"
        class="flex h-14 w-14 items-center justify-center rounded-full bg-accent text-white shadow-lg transition-transform hover:scale-105"
        aria-label="打开智能问答"
        @click="open = !open"
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
        </svg>
      </button>

      <Teleport to="body">
        <div
          v-if="open"
          class="rag-dialog fixed bottom-20 right-5 z-50 w-[380px] max-w-[calc(100vw-32px)] rounded-lg border border-border-default bg-bg-surface shadow-popover"
          role="dialog"
          aria-label="智能问答"
        >
          <div class="flex items-center justify-between border-b border-border-default px-4 py-3">
            <h3 class="text-sm font-medium">AI 智能问答</h3>
            <button class="text-text-tertiary hover:text-text-primary" aria-label="关闭" @click="open = false">
              Esc
            </button>
          </div>
          <div class="max-h-80 overflow-y-auto p-4">
            <div v-if="messages.length === 0" class="text-sm text-text-tertiary">
              基于站内知识库提问，例如「Nuxt3 有哪些核心特性？」
            </div>
            <div v-for="(msg, i) in messages" :key="i" :class="msg.role === 'user' ? 'mb-2 text-right' : 'mb-2'">
              <div
                :class="msg.role === 'user'
                  ? 'inline-block rounded-lg bg-accent px-3 py-1.5 text-sm text-white'
                  : 'inline-block max-w-full rounded-lg bg-gray-100 px-3 py-1.5 text-sm text-text-primary'"
              >
                {{ msg.content }}
              </div>
            </div>
          </div>
          <form class="border-t border-border-default p-3" @submit.prevent="send">
            <div class="flex gap-2">
              <input
                v-model="question"
                type="text"
                class="flex-1 rounded-md border border-border-default px-3 py-1.5 text-sm outline-none focus:border-accent"
                placeholder="输入问题..."
                :disabled="sending"
              />
              <button
                type="submit"
                class="rounded-md bg-accent px-3 py-1.5 text-sm text-white disabled:opacity-50"
                :disabled="!question.trim() || sending"
              >
                {{ sending ? "..." : "发送" }}
              </button>
            </div>
          </form>
        </div>
      </Teleport>
    </div>
  </ClientOnly>
</template>

<script setup lang="ts">
const open = ref(false);
const question = ref("");
const sending = ref(false);
const messages = ref<{ role: string; content: string }[]>([]);

const triggerRef = ref<HTMLElement | null>(null);

function onKeydown(e: KeyboardEvent) {
  if (e.key === "Escape") {
    open.value = false;
    triggerRef.value?.focus();
  }
}

onMounted(() => window.addEventListener("keydown", onKeydown));
onUnmounted(() => window.removeEventListener("keydown", onKeydown));

async function send() {
  if (!question.value.trim() || sending.value) return;
  const q = question.value.trim();
  messages.value.push({ role: "user", content: q });
  question.value = "";
  sending.value = true;

  try {
    const api = useApi();
    const res = await api.post<ApiResponse<AskResponse>>("/rag/ask", { question: q });
    if (res.success && res.data) {
      messages.value.push({
        role: "assistant",
        content: res.data.answer || "抱歉，暂时无法回答该问题。",
      });
    } else {
      messages.value.push({
        role: "assistant",
        content: "抱歉，暂时无法回答该问题。",
      });
    }
  } catch {
    messages.value.push({
      role: "assistant",
      content: "请求失败，请稍后再试。",
    });
  } finally {
    sending.value = false;
  }
}
</script>
