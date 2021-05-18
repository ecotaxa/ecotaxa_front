//
// Main app creation
//
import { createApp } from "vue";
import App from "./App.vue";
import { store, key } from "./store/store";
import my_router from "./router";

const app = createApp(App)

// use router, see routing rules there
app.use(my_router);

// add the store to all components in the app
// TODO: Typing for $store
app.use(store, key);

// mount the app
app.mount("#app");

