export default defineNuxtConfig({
  ssr: true,

  modules: ["@nuxtjs/tailwindcss", "@pinia/nuxt"],

  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || "http://localhost:8000/api/v1",
      monitorEndpoint:
        process.env.NUXT_PUBLIC_MONITOR_ENDPOINT ||
        "http://localhost:8000/api/v1/monitor/report",
      siteName: process.env.NUXT_PUBLIC_SITE_NAME || "智能内容平台",
    },
  },

  routeRules: {
    "/": { prerender: true },
    "/articles": { prerender: true },
    "/articles/**": { ssr: true },
    "/topics": { prerender: true },
    "/topics/**": { ssr: true },
    "/search": { ssr: false },
    "/ask": { ssr: false },
    "/about": { prerender: true },
    "/admin/**": { ssr: false },
  },

  typescript: {
    strict: true,
    shim: false,
  },

  app: {
    head: {
      title: "智能内容平台",
      meta: [
        { charset: "utf-8" },
        { name: "viewport", content: "width=device-width, initial-scale=1" },
        { name: "description", content: "基于混合渲染与向量检索的智能内容服务平台" },
      ],
      link: [{ rel: "icon", type: "image/svg+xml", href: "/favicon.svg" }],
    },
  },

  nitro: {
    prerender: {
      crawlLinks: true,
      routes: ["/"],
    },
  },

  compatibilityDate: "2025-01-28",
});
