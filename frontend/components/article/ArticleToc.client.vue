<template>
  <nav v-if="headings.length > 0" class="article-toc" aria-label="文章目录">
    <h4 class="mb-3 text-xs font-semibold uppercase tracking-wide text-text-tertiary">目录</h4>
    <ul class="space-y-1">
      <li v-for="(h, i) in headings" :key="i">
        <a
          :href="`#${h.id}`"
          class="block rounded px-2 py-1 text-sm transition-colors hover:text-accent"
          :class="[
            h.level === 3 ? 'pl-6 text-text-tertiary' : 'text-text-secondary',
            activeId === h.id ? 'border-l-2 border-accent bg-accent/5 font-medium text-accent' : 'border-l-2 border-transparent',
          ]"
          @click.prevent="scrollTo(h.id)"
        >
          {{ h.text }}
        </a>
      </li>
    </ul>
  </nav>
</template>

<script setup lang="ts">
interface Heading {
  id: string;
  text: string;
  level: number;
}

const headings = ref<Heading[]>([]);
const activeId = ref("");

function extractHeadings() {
  const hs = document.querySelectorAll(".prose h2, .prose h3");
  headings.value = Array.from(hs)
    .filter((h) => h.textContent)
    .map((h, i) => {
      const id = `heading-${i}`;
      h.id = id;
      return {
        id,
        text: h.textContent || "",
        level: parseInt(h.tagName[1] || "2"),
      };
    });
}

let observer: IntersectionObserver | null = null;

function setupObserver() {
  observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          activeId.value = entry.target.id;
        }
      }
    },
    { rootMargin: "-80px 0px -60% 0px" }
  );
  headings.value.forEach((h) => {
    const el = document.getElementById(h.id);
    if (el) observer!.observe(el);
  });
}

function scrollTo(id: string) {
  const el = document.getElementById(id);
  if (el) {
    el.scrollIntoView({ behavior: "smooth", block: "start" });
    activeId.value = id;
  }
}

onMounted(() => {
  nextTick(() => {
    extractHeadings();
    if (headings.value.length > 0) setupObserver();
  });
});

onUnmounted(() => {
  observer?.disconnect();
});
</script>
