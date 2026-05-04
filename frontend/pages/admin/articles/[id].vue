<template>
  <div>
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-2xl font-bold text-text-primary">
        {{ isNew ? "新建文章" : "编辑文章" }}
      </h1>
    </div>

    <form class="max-w-3xl" @submit.prevent="save">
      <div class="mb-4">
        <label class="mb-1.5 block text-sm font-medium text-text-primary" for="title">标题 *</label>
        <input
          id="title"
          v-model="form.title"
          type="text"
          class="w-full rounded-md border border-border-default px-3 py-2 text-sm outline-none focus:border-accent"
          style="height: 40px"
          required
        />
      </div>

      <div class="mb-4">
        <label class="mb-1.5 block text-sm font-medium text-text-primary" for="slug">Slug *</label>
        <input
          id="slug"
          v-model="form.slug"
          type="text"
          class="w-full rounded-md border border-border-default px-3 py-2 text-sm font-mono outline-none focus:border-accent"
          style="height: 40px"
          required
        />
      </div>

      <div class="mb-4">
        <label class="mb-1.5 block text-sm font-medium text-text-primary" for="category">分类</label>
        <select id="category" v-model="form.category_id" class="w-full rounded-md border border-border-default px-3 py-2 text-sm" style="height: 40px">
          <option :value="null">无分类</option>
          <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
        </select>
      </div>

      <div class="mb-4">
        <label class="mb-1.5 block text-sm font-medium text-text-primary" for="summary">摘要</label>
        <textarea
          id="summary"
          v-model="form.summary"
          class="w-full rounded-md border border-border-default px-3 py-2 text-sm outline-none focus:border-accent"
          rows="2"
          maxlength="160"
        />
        <span class="mt-1 text-xs text-text-tertiary">{{ (form.summary || "").length }}/160</span>
      </div>

      <div class="mb-4">
        <label class="mb-1.5 block text-sm font-medium text-text-primary" for="content">正文 (Markdown)</label>
        <textarea
          id="content"
          v-model="form.content_md"
          class="w-full rounded-md border border-border-default px-3 py-2 font-mono text-sm outline-none focus:border-accent"
          style="min-height: 520px"
          placeholder="输入 Markdown 内容..."
        />
      </div>

      <div class="mb-4">
        <label class="mb-1.5 block text-sm font-medium text-text-primary" for="seo_title">SEO 标题</label>
        <input
          id="seo_title"
          v-model="form.seo_title"
          type="text"
          class="w-full rounded-md border border-border-default px-3 py-2 text-sm outline-none focus:border-accent"
          style="height: 40px"
          maxlength="60"
        />
      </div>

      <div class="mb-6">
        <label class="mb-1.5 block text-sm font-medium text-text-primary" for="seo_desc">SEO 描述</label>
        <textarea
          id="seo_desc"
          v-model="form.seo_description"
          class="w-full rounded-md border border-border-default px-3 py-2 text-sm outline-none focus:border-accent"
          rows="2"
          maxlength="160"
        />
      </div>

      <div class="flex gap-3">
        <button
          type="submit"
          class="rounded-md bg-accent px-6 py-2 text-sm font-medium text-white disabled:opacity-50"
          style="height: 40px"
          :disabled="saving"
        >
          {{ saving ? "保存中..." : "保存草稿" }}
        </button>
        <button
          v-if="!isNew && article?.status !== 'published'"
          type="button"
          class="rounded-md border border-accent px-6 py-2 text-sm font-medium text-accent"
          style="height: 40px"
          @click="publish"
        >
          发布
        </button>
      </div>

      <p v-if="message" class="mt-3 text-sm" :class="errorMsg ? 'text-red-500' : 'text-green-600'">{{ message }}</p>
    </form>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "admin", middleware: "auth", ssr: false });

const route = useRoute();
const api = useApi();

const isNew = computed(() => route.params.id === "new");
const article = ref<any>(null);
const categories = ref<any[]>([]);
const saving = ref(false);
const message = ref("");
const errorMsg = ref(false);

const form = reactive({
  title: "",
  slug: "",
  category_id: null as number | null,
  summary: "",
  content_md: "",
  seo_title: "",
  seo_description: "",
});

try {
  const catRes = await api.get<any>("/admin/categories");
  if (catRes.success) categories.value = catRes.data;
} catch {}

if (!isNew.value) {
  try {
    const res = await api.get<any>(`/admin/articles/${route.params.id}`);
    if (res.success) {
      article.value = res.data;
      Object.assign(form, {
        title: res.data.title,
        slug: res.data.slug,
        category_id: res.data.category?.id || null,
        summary: res.data.summary || "",
        content_md: res.data.content_md || "",
        seo_title: res.data.seo_title || "",
        seo_description: res.data.seo_description || "",
      });
    }
  } catch {}
}

async function save() {
  saving.value = true;
  message.value = "";
  errorMsg.value = false;
  try {
    if (isNew.value) {
      const res = await api.post<any>("/admin/articles", form);
      if (res.success) {
        message.value = "创建成功";
        navigateTo(`/admin/articles/${res.data.id}`);
      }
    } else {
      await api.put(`/admin/articles/${route.params.id}`, form);
      message.value = "保存成功";
    }
  } catch (e: any) {
    message.value = e?.data?.message || "保存失败";
    errorMsg.value = true;
  } finally {
    saving.value = false;
  }
}

async function publish() {
  try {
    await api.post(`/admin/articles/${route.params.id}/publish`);
    message.value = "发布成功";
    errorMsg.value = false;
  } catch (e: any) {
    message.value = "发布失败";
    errorMsg.value = true;
  }
}
</script>
