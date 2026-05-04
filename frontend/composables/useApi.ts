import { useAuthStore } from "~/stores/auth";

export function useApi() {
  const config = useRuntimeConfig();
  const authStore = useAuthStore();

  const fetcher = $fetch.create({
    baseURL: config.public.apiBase as string,
    onRequest({ options }) {
      const token = authStore.token;
      if (token) {
        options.headers = {
          ...options.headers,
          Authorization: `Bearer ${token}`,
        };
      }
    },
    onResponseError({ response }) {
      if (response.status === 401) {
        authStore.logout();
        if (!window.location.pathname.startsWith("/admin/login")) {
          window.location.href = "/admin/login";
        }
      }
    },
  });

  return {
    get: <T>(url: string, params?: Record<string, unknown>) =>
      fetcher<T>(url, { method: "GET", params }),

    post: <T>(url: string, body?: unknown) =>
      fetcher<T>(url, { method: "POST", body }),

    put: <T>(url: string, body?: unknown) =>
      fetcher<T>(url, { method: "PUT", body }),

    delete: <T>(url: string) =>
      fetcher<T>(url, { method: "DELETE" }),
  };
}
