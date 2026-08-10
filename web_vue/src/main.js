import { createApp } from "vue";
import App from "./App.vue";
import "./assets/css/tailwind.css";
import router from "./router";
import { createPinia } from "pinia";
import piniaPluginPersistedstate from "pinia-plugin-persistedstate";
import { useThemeStore } from "./store/themeStore";

const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);

const app = createApp(App);
app.use(router).use(pinia);

useThemeStore(pinia).init();

app.mount("#app");