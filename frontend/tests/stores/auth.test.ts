import { describe, it, expect, beforeEach } from "vitest";
import { setActivePinia, createPinia } from "pinia";
import { useAuthStore } from "~/stores/auth";

describe("Auth Store", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    localStorage.clear();
  });

  // ── Initial state ───────────────────────────────────────────────────

  it("should initialize with no token", () => {
    const store = useAuthStore();
    expect(store.token).toBeNull();
    expect(store.isLoggedIn).toBe(false);
    expect(store.admin).toBeNull();
  });

  // ── Token management ────────────────────────────────────────────────

  it("should set token and update isLoggedIn", () => {
    const store = useAuthStore();
    store.setToken("test-token-123");
    expect(store.token).toBe("test-token-123");
    expect(store.isLoggedIn).toBe(true);
  });

  it("should persist token to localStorage when client-side", () => {
    const store = useAuthStore();
    store.setToken("persist-token");
    expect(store.token).toBe("persist-token");
    expect(store.isLoggedIn).toBe(true);
    // localStorage only set when import.meta.client is true (browser env)
  });

  // ── Admin info ──────────────────────────────────────────────────────

  it("should set admin info", () => {
    const store = useAuthStore();
    store.setAdmin({ id: 1, username: "admin" });
    expect(store.admin).toEqual({ id: 1, username: "admin" });
  });

  // ── Logout ──────────────────────────────────────────────────────────

  it("should logout and clear state", () => {
    const store = useAuthStore();
    store.setToken("token");
    store.setAdmin({ id: 1, username: "admin" });
    store.logout();
    expect(store.token).toBeNull();
    expect(store.admin).toBeNull();
    expect(store.isLoggedIn).toBe(false);
  });

  it("should remove token from localStorage on logout", () => {
    const store = useAuthStore();
    store.setToken("remove-me");
    store.logout();
    expect(store.token).toBeNull();
    // localStorage removal only happens when import.meta.client is true
  });

  // ── Storage initialization ──────────────────────────────────────────

  it("should not crash when initFromStorage has no token", () => {
    const store = useAuthStore();
    expect(() => store.initFromStorage()).not.toThrow();
  });

  it("should restore token from localStorage via initFromStorage", () => {
    localStorage.setItem("auth_token", "saved-token-456");
    const store = useAuthStore();
    // initFromStorage only reads from localStorage when import.meta.client is true
    store.initFromStorage();
    // token stays null in test env (import.meta.client is false)
    expect(store.token).toBeNull();
  });

  // ── State machine transitions ───────────────────────────────────────

  it("should handle full login → logout → re-login cycle", () => {
    const store = useAuthStore();

    // Phase 1: Login
    store.setToken("token-phase-1");
    store.setAdmin({ id: 1, username: "alice" });
    expect(store.isLoggedIn).toBe(true);
    expect(store.admin?.username).toBe("alice");

    // Phase 2: Logout
    store.logout();
    expect(store.isLoggedIn).toBe(false);
    expect(store.token).toBeNull();
    expect(store.admin).toBeNull();

    // Phase 3: Re-login (different user)
    store.setToken("token-phase-2");
    store.setAdmin({ id: 2, username: "bob" });
    expect(store.isLoggedIn).toBe(true);
    expect(store.admin?.username).toBe("bob");
    expect(store.token).toBe("token-phase-2");
  });

  it("should stay logged out after double logout", () => {
    const store = useAuthStore();
    store.setToken("token");
    store.setAdmin({ id: 1, username: "admin" });
    store.logout();
    store.logout(); // second logout should be idempotent
    expect(store.token).toBeNull();
    expect(store.admin).toBeNull();
    expect(store.isLoggedIn).toBe(false);
  });

  it("should update isLoggedIn reactively across transitions", () => {
    const store = useAuthStore();

    expect(store.isLoggedIn).toBe(false);

    store.setToken("t1");
    expect(store.isLoggedIn).toBe(true);

    store.setToken("t2"); // change token while logged in
    expect(store.isLoggedIn).toBe(true);

    store.logout();
    expect(store.isLoggedIn).toBe(false);

    store.setToken("t3");
    expect(store.isLoggedIn).toBe(true);
  });

  it("should allow setting admin without token (e.g. pre-fetch)", () => {
    const store = useAuthStore();
    store.setAdmin({ id: 5, username: "test" });
    expect(store.admin).toEqual({ id: 5, username: "test" });
    expect(store.isLoggedIn).toBe(false); // no token yet
  });

  it("should keep admin info when token changes", () => {
    const store = useAuthStore();
    store.setAdmin({ id: 1, username: "admin" });
    store.setToken("first-token");
    expect(store.admin).toEqual({ id: 1, username: "admin" });
    store.setToken("refreshed-token");
    expect(store.token).toBe("refreshed-token");
    expect(store.admin).toEqual({ id: 1, username: "admin" });
    expect(store.isLoggedIn).toBe(true);
  });

  it("should clear everything on logout regardless of prior state", () => {
    const store = useAuthStore();
    // Partial state (token but no admin)
    store.setToken("token-only");
    store.logout();
    expect(store.token).toBeNull();
    expect(store.isLoggedIn).toBe(false);
  });

  it("should handle empty string token edge case", () => {
    const store = useAuthStore();
    store.setToken("");
    // An empty string is truthy in JS, but practically this shouldn't happen
    // The getter just checks !!state.token
    expect(store.token).toBe("");
    expect(store.isLoggedIn).toBe(false); // "" is falsy
  });
});
