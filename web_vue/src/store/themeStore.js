import { defineStore } from "pinia";

export const useThemeStore = defineStore({
  id: "theme",
  state: () => ({
    isDark: false,
  }),

  getters: {
    theme: (state) => (state.isDark ? "dark" : "light"),
  },

  actions: {
    init() {
      const saved = localStorage.getItem("theme");
      if (saved === "dark" || saved === "light") {
        this.setTheme(saved);
      } else {
        const prefersDark =
          window.matchMedia &&
          window.matchMedia("(prefers-color-scheme: dark)").matches;
        this.setTheme(prefersDark ? "dark" : "light");
      }
    },
    setTheme(theme) {
      this.isDark = theme === "dark";
      localStorage.setItem("theme", theme);
      this.apply();
    },
    toggle() {
      this.setTheme(this.isDark ? "light" : "dark");
    },
    apply() {
      const el = document.documentElement;
      if (this.isDark) {
        el.classList.add("dark");
      } else {
        el.classList.remove("dark");
      }
    },
  },
});
