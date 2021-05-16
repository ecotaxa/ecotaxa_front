<template>
  <div>
    <Banner />
    <img alt="Vue logo" src="../assets/logo.png" />
    <span> {{ a }} </span>
    <login />
    <about-me />
    <HelloWorld msg="Welcome to Your Vue.js App " />
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import HelloWorld from "./HelloWorld.vue";
import Login from "./Login.vue";
import Banner from "./Banner.vue";
import AboutMe from "./AboutMe.vue";

export default defineComponent({
  // type inference enabled
  name: "App",
  data() {
    return { a: 0 };
  },
  components: {
    HelloWorld,
    Login,
    Banner,
    AboutMe,
  },
});
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
