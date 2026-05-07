import { describe, it, expect, vi, beforeEach } from "vitest";
import { setActivePinia, createPinia } from "pinia";

const mockFetch = vi.fn();
const mockCreate = vi.fn((options: any) => {
  return async (...args: any[]) => {
    const ctx = { options: { ...args[1] } };
    if (options.onRequest) options.onRequest(ctx);
    return mockFetch(args[0], ctx.options);
  };
});

vi.stubGlobal("$fetch", { create: mockCreate });
vi.stubGlobal("useRuntimeConfig", () => ({
  public: {
    apiBase: "http://localhost:8000/api/v1",
    monitorEndpoint: "http://localhost:8000/api/v1/monitor/report",
    siteName: "Test Site",
  },
}));

describe("useApi", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    mockFetch.mockReset();
    mockFetch.mockResolvedValue({ success: true, data: {} });
    localStorage.clear();
  });

  it("GET sends correct URL and method", async () => {
    const { useApi } = await import("~/composables/useApi");
    const api = useApi();
    await api.get("/test");
    expect(mockFetch).toHaveBeenCalledWith("/test", { method: "GET" });
  });

  it("POST sends body and method", async () => {
    const { useApi } = await import("~/composables/useApi");
    const api = useApi();
    await api.post("/items", { name: "test" });
    expect(mockFetch).toHaveBeenCalledWith("/items", { method: "POST", body: { name: "test" } });
  });

  it("PUT sends body and method", async () => {
    const { useApi } = await import("~/composables/useApi");
    const api = useApi();
    await api.put("/items/1", { name: "updated" });
    expect(mockFetch).toHaveBeenCalledWith("/items/1", { method: "PUT", body: { name: "updated" } });
  });

  it("DELETE sends correct method", async () => {
    const { useApi } = await import("~/composables/useApi");
    const api = useApi();
    await api.delete("/items/1");
    expect(mockFetch).toHaveBeenCalledWith("/items/1", { method: "DELETE" });
  });

  it("injects Authorization header when token exists", async () => {
    const { useAuthStore } = await import("~/stores/auth");
    const auth = useAuthStore();
    auth.setToken("test-token-123");

    const { useApi } = await import("~/composables/useApi");
    const api = useApi();
    await api.get("/protected");

    const headers = mockFetch.mock.calls[0]![1]!.headers;
    expect(headers).toBeDefined();
    expect(headers!.get("Authorization")).toBe("Bearer test-token-123");
  });

  it("does not inject token without auth", async () => {
    const { useApi } = await import("~/composables/useApi");
    const api = useApi();
    await api.get("/public");
    expect(mockFetch.mock.calls[0]![1]!.headers).toBeUndefined();
  });

  it("handles GET request failure", async () => {
    mockFetch.mockRejectedValueOnce(new Error("Network Error"));
    const { useApi } = await import("~/composables/useApi");
    const api = useApi();
    await expect(api.get("/fail")).rejects.toThrow("Network Error");
  });

  it("GET passes query params correctly", async () => {
    const { useApi } = await import("~/composables/useApi");
    const api = useApi();
    await api.get("/search", { q: "test", page: 1 });
    expect(mockFetch).toHaveBeenCalledWith("/search", { method: "GET", params: { q: "test", page: 1 } });
  });
});
