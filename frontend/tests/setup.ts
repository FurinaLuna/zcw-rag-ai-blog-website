import { vi } from "vitest";

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
