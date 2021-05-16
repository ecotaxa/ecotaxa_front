//
// Main app creation
//
import { createApp } from "vue";
import App from "./components/App.vue";
import { store, key } from "./store/store";

const app = createApp(App);

// add the store to all components in the app
app.use(store, key);

// mount the app
app.mount("#app");

// TODO: Typing for $store