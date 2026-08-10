import { defineStore } from "pinia";

export const useAuthStore = defineStore({
  id: "auth",
  state: () => ({
    loginUser: {},
    permissions: [],
    accessToken: "",
    // Snapshot of the admin's session while impersonating another user
    impersonator: null,
  }),

  getters: {
    isImpersonating: (state) => !!state.impersonator,
  },

  actions: {
    async setUser(loginUser) {
      this.loginUser = loginUser;
    },
    async setPermissions(permissions) {
      this.permissions = permissions;
    },
    async setAccessToken(accessToken) {
      this.accessToken = accessToken;
    },
    async startImpersonation(session) {
      // Save the current (admin) session so it can be restored later
      this.impersonator = {
        user: this.loginUser,
        permissions: this.permissions,
        accessToken: this.accessToken,
      };
      this.loginUser = session.user;
      this.permissions = session.permissions;
      this.accessToken = session.access_token;
    },
    async stopImpersonation() {
      if (!this.impersonator) return;
      this.loginUser = this.impersonator.user;
      this.permissions = this.impersonator.permissions;
      this.accessToken = this.impersonator.accessToken;
      this.impersonator = null;
    },
    async reset() {
      this.loginUser = {};
      this.permissions = [];
      this.accessToken = "";
      this.impersonator = null;
    },
  },
  persist: true,
});
