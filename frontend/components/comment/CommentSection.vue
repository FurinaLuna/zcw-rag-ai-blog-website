<template>
  <div class="comment-section mt-12 border-t border-border-default pt-8">
    <h2 class="mb-6 text-lg font-semibold text-text-primary">评论 ({{ total }})</h2>

    <CommentForm :article-slug="articleSlug" @submitted="fetchComments" />

    <div v-if="loading" class="py-8 text-center text-sm text-text-tertiary">
      加载中...
    </div>

    <div v-else-if="comments.length === 0" class="py-8 text-center text-sm text-text-tertiary">
      暂无评论，来说点什么吧
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="comment in comments"
        :key="comment.id"
        class="rounded-lg border border-border-default p-4"
      >
        <div class="mb-2 flex items-center gap-2">
          <span class="text-sm font-medium text-text-primary">{{ comment.nickname }}</span>
          <span class="text-xs text-text-tertiary">{{ formatDate(comment.created_at) }}</span>
        </div>
        <p class="text-sm text-text-secondary">{{ comment.content }}</p>
        <div class="mt-2 flex items-center gap-2">
          <button
            class="flex items-center gap-1 text-xs text-text-tertiary hover:text-accent transition-colors"
            @click="likeComment(comment.id)"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3H14z" />
            </svg>
            {{ comment.likes }}
          </button>
        </div>
      </div>
    </div>

    <Pagination
      v-if="totalPages > 1"
      :current="page"
      :total-pages="totalPages"
      @change="goPage"
    />
  </div>
</template>

<script setup lang="ts">
import dayjs from "dayjs";
import { useApi } from "~/composables/useApi";

const props = defineProps<{
  articleSlug: string;
}>();

const api = useApi();
const comments = ref<CommentResponse[]>([]);
const total = ref(0);
const page = ref(1);
const totalPages = ref(1);
const loading = ref(true);

async function fetchComments() {
  loading.value = true;
  try {
    const res = await api.get<ApiResponse<PaginatedData<CommentResponse>>>(`/public/articles/${props.articleSlug}/comments`, {
      page: page.value,
      page_size: 20,
    });
    if (res.success) {
      comments.value = res.data.items;
      total.value = res.data.total;
      totalPages.value = res.data.total_pages;
    }
  } catch {} finally {
    loading.value = false;
  }
}

async function likeComment(commentId: number) {
  try {
    const res = await api.post<ApiResponse<CommentResponse>>(`/public/comments/${commentId}/like`);
    if (res.success) {
      const target = comments.value.find((c) => c.id === commentId);
      if (target) target.likes = res.data.likes;
    }
  } catch {}
}

function goPage(p: number) {
  page.value = p;
  fetchComments();
}

function formatDate(date: string) {
  return dayjs(date).format("YYYY-MM-DD HH:mm");
}

onMounted(fetchComments);
</script>
