<template>
  <div class="default-layout">
    <a href="#main-content" class="skip-to-content">跳转到主要内容</a>
    <SiteHeader />
    <main id="main-content" class="min-h-screen">
      <slot />
    </main>
    <SiteFooter />
    <RAGFloatingButton />
    <BackToTop />
  </div>
</template>
