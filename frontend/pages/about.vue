<template>
  <div class="mx-auto max-w-content px-4 py-12">
    <h1 class="mb-8 text-2xl font-bold text-text-primary">关于本项目</h1>

    <div class="prose">
      <p>智能内容平台是一个基于现代 Web 技术栈构建的技术内容服务平台，融合了以下核心技术能力：</p>

      <h2>核心技术</h2>
      <ul>
        <li><strong>Nuxt3 混合渲染</strong>：SSG/SSR/CSR 混合渲染策略，兼顾首屏性能与 SEO</li>
        <li><strong>FastAPI 后端服务</strong>：高性能异步 Python API 服务</li>
        <li><strong>PostgreSQL + pgvector</strong>：统一存储业务数据与向量数据</li>
        <li><strong>RAG 智能问答</strong>：基于站内私有知识库的检索增强生成</li>
        <li><strong>前端监控 SDK</strong>：自研性能与异常采集体系</li>
      </ul>

      <h2>技术栈</h2>
      <ul>
        <li>前端：Nuxt3 + Vue3 + TypeScript + TailwindCSS + Pinia</li>
        <li>后端：FastAPI + SQLAlchemy + PgVector</li>
        <li>数据：PostgreSQL 16 + Redis</li>
        <li>AI：BGE Embedding + LLM API</li>
        <li>部署：Docker + Docker Compose</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
useSeoMeta({ title: "关于 - 智能内容平台" });
</script>
