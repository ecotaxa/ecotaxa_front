//
// Main app creation
//
// Bootstrap for vue3 (see e.g. https://www.techiediaries.com/vue-bootstrap/)

// import Vue from "vue";
// Vue.use(BootstrapVue); // DOES NOT WORK

import { createApp } from "vue";
import "bootstrap";
//import BootstrapVue from "bootstrap-vue";
import { store, key } from "./store/store";
import "@/assets/custom.scss";
//import "bootstrap/dist/css/bootstrap.min.css";
//import "bootstrap-vue/dist/bootstrap-vue.css";
import App from "./App.vue";
// add the store to all components in the app
import my_router from "./router";

const app = createApp(App);

// use router, see routing rules there
app.use(my_router);
// app.use(BootstrapVue); DOES NOT WORK

// add the store to all components in the app
// TODO: Typing for $store
app.use(store, key);
app.mount("#app");
