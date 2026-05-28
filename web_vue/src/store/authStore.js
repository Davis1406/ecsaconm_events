import { defineStore } from "pinia";

export const useAuthStore = defineStore({
  id: "auth",
  state: () => ({
    loginUser: {},
    permissions: [],
    accessToken: "",
  }),

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
    async reset() {
      this.loginUser = {};
      this.permissions = [];
      this.accessToken = "";
    },
  },
  persist: true,
});
