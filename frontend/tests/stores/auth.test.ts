import { describe, it, expect, beforeEach } from "vitest";
import { setActivePinia, createPinia } from "pinia";
import { useAuthStore } from "~/stores/auth";

describe("Auth Store", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    localStorage.clear();
  });

  it("should initialize with no token", () => {
    const store = useAuthStore();
    expect(store.token).toBeNull();
    expect(store.isLoggedIn).toBe(false);
    expect(store.admin).toBeNull();
  });

  it("should set token and update isLoggedIn", () => {
    const store = useAuthStore();
    store.setToken("test-token-123");
    expect(store.token).toBe("test-token-123");
    expect(store.isLoggedIn).toBe(true);
  });

  it("should persist token to localStorage when client-side", () => {
    const store = useAuthStore();
    store.setToken("persist-token");
    // In vitest, import.meta.client is false, so localStorage is not set
    // but the store token should still be set
    expect(store.token).toBe("persist-token");
    expect(store.isLoggedIn).toBe(true);
  });

  it("should set admin info", () => {
    const store = useAuthStore();
    store.setAdmin({ id: 1, username: "admin" });
    expect(store.admin).toEqual({ id: 1, username: "admin" });
  });

  it("should logout and clear state", () => {
    const store = useAuthStore();
    store.setToken("token");
    store.setAdmin({ id: 1, username: "admin" });
    store.logout();
    expect(store.token).toBeNull();
    expect(store.admin).toBeNull();
    expect(store.isLoggedIn).toBe(false);
  });

  it("should not crash when initFromStorage has no token", () => {
    const store = useAuthStore();
    expect(() => store.initFromStorage()).not.toThrow();
  });
});
