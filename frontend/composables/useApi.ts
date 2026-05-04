import { useAuthStore } from "~/stores/auth";

export function useApi() {
  const config = useRuntimeConfig();
  const authStore = useAuthStore();

  const fetcher = $fetch.create({
    baseURL: config.public.apiBase as string,
    onRequest({ options }) {
      const token = authStore.token;
      if (token) {
        options.headers = new Headers(options.headers);
        options.headers.set("Authorization", `Bearer ${token}`);
      }
    },
    onResponseError({ response }) {
      if (response.status === 401) {
        authStore.logout();
        if (import.meta.client && !window.location.pathname.startsWith("/admin/login")) {
          window.location.href = "/admin/login";
        }
      }
    },
  });

  function req<T>(url: string, opts: { method: "GET" | "POST" | "PUT" | "DELETE"; params?: Record<string, unknown>; body?: Record<string, unknown> }) {
    return fetcher<T>(url, opts) as Promise<T>;
  }

  return {
    get: <T>(url: string, params?: Record<string, unknown>) =>
      req<T>(url, { method: "GET", params }),

    post: <T>(url: string, body?: Record<string, unknown>) =>
      req<T>(url, { method: "POST", body }),

    put: <T>(url: string, body?: Record<string, unknown>) =>
      req<T>(url, { method: "PUT", body }),

    delete: <T>(url: string) =>
      req<T>(url, { method: "DELETE" }),
  };
}
