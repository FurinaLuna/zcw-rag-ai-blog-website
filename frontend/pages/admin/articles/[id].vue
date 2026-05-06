<template>
  <div>
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-2xl font-bold text-text-primary">
        {{ isNew ? "新建文章" : "编辑文章" }}
      </h1>
    </div>

    <form class="max-w-3xl" @submit.prevent="save">
      <FormField id="title" label="标题" required class="mb-4">
        <input id="title" v-model="form.title" type="text" required
          class="w-full rounded-md border border-border-default px-3 py-2 text-sm outline-none focus:border-accent"
          style="height: 40px" />
      </FormField>

      <FormField id="slug" label="Slug" required class="mb-4">
        <input id="slug" v-model="form.slug" type="text" required
          class="w-full rounded-md border border-border-default px-3 py-2 text-sm font-mono outline-none focus:border-accent"
          style="height: 40px" />
      </FormField>

      <FormField id="category" label="分类" class="mb-4">
        <select id="category" v-model="form.category_id"
          class="w-full rounded-md border border-border-default px-3 py-2 text-sm" style="height: 40px">
          <option :value="null">无分类</option>
          <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
        </select>
      </FormField>

      <FormField id="summary" label="摘要" :helper="`${(form.summary || '').length}/160`" class="mb-4">
        <textarea id="summary" v-model="form.summary" rows="2" maxlength="160"
          class="w-full rounded-md border border-border-default px-3 py-2 text-sm outline-none focus:border-accent" />
      </FormField>

      <FormField id="content" label="正文 (Markdown)" class="mb-4">
        <textarea id="content" v-model="form.content_md" placeholder="输入 Markdown 内容..."
          class="w-full rounded-md border border-border-default px-3 py-2 font-mono text-sm outline-none focus:border-accent"
          style="min-height: 520px" />
      </FormField>

      <FormField id="seo_title" label="SEO 标题" class="mb-4">
        <input id="seo_title" v-model="form.seo_title" type="text" maxlength="60"
          class="w-full rounded-md border border-border-default px-3 py-2 text-sm outline-none focus:border-accent"
          style="height: 40px" />
      </FormField>

      <FormField id="seo_desc" label="SEO 描述" class="mb-6">
        <textarea id="seo_desc" v-model="form.seo_description" rows="2" maxlength="160"
          class="w-full rounded-md border border-border-default px-3 py-2 text-sm outline-none focus:border-accent" />
      </FormField>

      <div class="flex gap-3">
        <BaseButton type="submit" variant="primary" size="md" :loading="saving">
          {{ saving ? "保存中..." : "保存草稿" }}
        </BaseButton>
        <BaseButton
          v-if="!isNew && article?.status !== 'published'"
          type="button"
          variant="secondary"
          size="md"
          @click="publish"
        >
          发布
        </BaseButton>
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
const article = ref<ArticleAdminResponse | null>(null);
const categories = ref<CategoryResponse[]>([]);
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
  const catRes = await api.get<ApiResponse<CategoryResponse[]>>("/admin/categories");
  if (catRes.success) categories.value = catRes.data;
} catch {}

if (!isNew.value) {
  try {
    const res = await api.get<ApiResponse<ArticleAdminResponse>>(`/admin/articles/${route.params.id}`);
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
      const res = await api.post<ApiResponse<ArticleAdminResponse>>("/admin/articles", form);
      if (res.success) {
        message.value = "创建成功";
        navigateTo(`/admin/articles/${res.data.id}`);
      }
    } else {
      await api.put(`/admin/articles/${route.params.id}`, form);
      message.value = "保存成功";
    }
  } catch (e: unknown) {
    const err = e as { data?: { message?: string }; message?: string } | undefined;
    message.value = err?.data?.message || err?.message || "保存失败";
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
  } catch {
    message.value = "发布失败";
    errorMsg.value = true;
  }
}
</script>
