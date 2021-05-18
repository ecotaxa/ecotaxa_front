//
// Main app creation
//
// Bootstrap for vue3 (see e.g. https://www.techiediaries.com/vue-bootstrap/)

import Vue from "vue";
// Vue.use(BootstrapVue); DOES NOT WORK

import { createApp } from "vue";
import BootstrapVue from "bootstrap-vue";
import { store, key } from "./store/store";
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap-vue/dist/bootstrap-vue.css";
import App from "./App.vue";
const app = createApp(App);
// add the store to all components in the app
// app.use(BootstrapVue); DOES NOT WORK
app.use(store, key);
app.mount("#app");

// TODO: Typing for $store
