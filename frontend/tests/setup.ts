import { vi } from "vitest";
import { computed, ref, watch, onMounted, onUnmounted } from "vue";

vi.stubGlobal("computed", computed);
vi.stubGlobal("ref", ref);
vi.stubGlobal("watch", watch);
vi.stubGlobal("onMounted", onMounted);
vi.stubGlobal("onUnmounted", onUnmounted);

vi.stubGlobal("useRuntimeConfig", () => ({
  public: {
    apiBase: "http://localhost:8000/api/v1",
    monitorEndpoint: "http://localhost:8000/api/v1/monitor/report",
    siteName: "Test Site",
  },
}));

vi.stubGlobal("useRouter", () => ({
  afterEach: vi.fn(),
  push: vi.fn(),
  replace: vi.fn(),
}));
