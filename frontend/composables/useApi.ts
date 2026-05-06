import { useAuthStore } from "~/stores/auth";

/** Allowed query parameter value types */
type ParamValue = string | number | boolean | undefined | null

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
      const detail = (response._data as any)?.detail || (response._data as any)?.message || "";
      const msg = detail ? ` (${detail})` : "";

      const messages: Record<number, string> = {
        401: "未登录或登录已过期，请重新登录",
        403: "没有权限执行此操作" + msg,
        404: "请求的资源不存在" + msg,
        422: "请求参数有误" + msg,
        500: "服务器内部错误，请稍后重试",
      };

      const errorMessage = messages[response.status] || `请求失败 (${response.status})`;

      if (response.status === 401) {
        authStore.logout();
        if (import.meta.client && !window.location.pathname.startsWith("/admin/login")) {
          window.location.href = "/admin/login";
        }
      }

      throw new Error(errorMessage);
    },
  });

  function req<T>(url: string, opts: {
    method: "GET" | "POST" | "PUT" | "DELETE"
    params?: Record<string, ParamValue>
    body?: Record<string, unknown>
  }): Promise<T> {
    return fetcher<T>(url, opts) as Promise<T>;
  }

  return {
    /** GET request with typed response and optional query params */
    get: <T>(url: string, params?: Record<string, ParamValue>): Promise<T> =>
      req<T>(url, { method: "GET", params }),

    /** POST request with typed response and optional JSON body */
    post: <T>(url: string, body?: Record<string, unknown>): Promise<T> =>
      req<T>(url, { method: "POST", body }),

    /** PUT request with typed response and optional JSON body */
    put: <T>(url: string, body?: Record<string, unknown>): Promise<T> =>
      req<T>(url, { method: "PUT", body }),

    /** DELETE request with typed response */
    delete: <T>(url: string): Promise<T> =>
      req<T>(url, { method: "DELETE" }),
  };
}
