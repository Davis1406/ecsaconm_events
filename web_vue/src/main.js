import { createApp } from "vue";
import App from "./App.vue";
import "./assets/css/tailwind.css";
import router from "./router";
import { createPinia } from "pinia";
import piniaPluginPersistedstate from "pinia-plugin-persistedstate";
import { useThemeStore } from "./store/themeStore";

// Real statement (not a comment — comments get stripped by minification and
// don't change the output hash) so a rebuild always produces a fresh
// index-*.js filename. Needed once already: a Cloudflare edge cache poisoned
// the previous index-*.js/css with stale HTML during a mid-deploy race
// window (blank white page for anyone hitting the cached URL) — a brand new,
// never-cached filename routes around that without needing a cache purge.
window.__ECSA_BUILD__ = "2026-09-14T10:20Z";

const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);

const app = createApp(App);
app.use(router).use(pinia);

useThemeStore(pinia).init();

app.mount("#app");