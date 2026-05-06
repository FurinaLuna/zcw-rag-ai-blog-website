import { defineStore } from "pinia";

interface AuthState {
  token: string | null;
  admin: {
    id: number;
    username: string;
  } | null;
}

export const useAuthStore = defineStore("auth", {
  state: (): AuthState => ({
    token: null,
    admin: null,
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
  },

  actions: {
    setToken(token: string) {
      this.token = token;
      if (import.meta.client) {
        localStorage.setItem("auth_token", token);
      }
    },

    setAdmin(admin: { id: number; username: string }) {
      this.admin = admin;
    },

    async login(username: string, password: string) {
      const { useApi } = await import("~/composables/useApi");
      const api = useApi();
      const res = await api.post<ApiResponse<TokenResponse>>("/admin/login", { username, password });
      if (res.success) {
        this.setToken(res.data.access_token);
        await this.fetchAdmin();
      }
      return res;
    },

    async fetchAdmin() {
      if (!this.token) return;
      try {
        const { useApi } = await import("~/composables/useApi");
        const api = useApi();
        const res = await api.get<ApiResponse<AdminInfo>>("/admin/me");
        if (res.success) {
          this.setAdmin(res.data);
        }
      } catch {
        this.logout();
      }
    },

    logout() {
      this.token = null;
      this.admin = null;
      if (import.meta.client) {
        localStorage.removeItem("auth_token");
      }
    },

    initFromStorage() {
      if (import.meta.client) {
        const token = localStorage.getItem("auth_token");
        if (token) {
          this.token = token;
          this.fetchAdmin();
        }
      }
    },
  },
});
