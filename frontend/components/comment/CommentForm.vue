<template>
  <form class="mb-6 rounded-lg border border-border-default p-4" @submit.prevent="handleSubmit">
    <div class="mb-3">
      <input
        v-model="nickname"
        type="text"
        class="w-full rounded-md border border-border-default px-3 py-2 text-sm outline-none focus:border-accent"
        placeholder="昵称"
        maxlength="20"
        required
      />
    </div>
    <div class="mb-3">
      <textarea
        v-model="content"
        class="w-full rounded-md border border-border-default px-3 py-2 text-sm outline-none focus:border-accent"
        placeholder="写评论..."
        rows="3"
        maxlength="500"
        required
      ></textarea>
      <div class="mt-1 text-xs text-text-tertiary">{{ content.length }}/500</div>
    </div>
    <div class="flex items-center justify-between">
      <p v-if="error" class="text-xs text-red-500">{{ error }}</p>
      <p v-else-if="success" class="text-xs text-green-600">{{ success }}</p>
      <span v-else></span>
      <button
        type="submit"
        class="rounded-md bg-accent px-4 py-1.5 text-sm text-white transition-opacity hover:opacity-90 disabled:opacity-50"
        :disabled="!nickname.trim() || !content.trim() || submitting"
      >
        {{ submitting ? "提交中..." : "发布评论" }}
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { useApi } from "~/composables/useApi";

const props = defineProps<{
  articleSlug: string;
}>();

const emit = defineEmits<{
  submitted: [];
}>();

const api = useApi();
const nickname = ref("");
const content = ref("");
const submitting = ref(false);
const error = ref("");
const success = ref("");

async function handleSubmit() {
  if (!nickname.value.trim() || !content.value.trim()) return;
  submitting.value = true;
  error.value = "";
  success.value = "";
  try {
    await api.post(`/public/articles/${props.articleSlug}/comments`, {
      nickname: nickname.value.trim(),
      content: content.value.trim(),
    });
    success.value = "评论发布成功";
    content.value = "";
    emit("submitted");
    setTimeout(() => { success.value = ""; }, 3000);
  } catch (e: any) {
    error.value = e?.data?.message || "发布失败";
  } finally {
    submitting.value = false;
  }
}
</script>
