<template>
  <Banner />
  <img alt="Vue logo" src="./assets/logo.png" />
  <span> {{ a }} </span>
  <login />
  <about-me />
  <HelloWorld msg="Welcome to Your Vue.js + TypeScript App" />
</template>

<script lang="ts">
//import { defineComponent } from "vue";
import HelloWorld from "./components/HelloWorld.vue";
import Login from "./components/Login.vue";
import Banner from "./components/Banner.vue";
import AboutMe from "./components/AboutMe.vue";
import { Options, Vue } from "vue-class-component";

@Options({
  components: {
    HelloWorld,
    Login,
    Banner,
    AboutMe,
  },
})
export default class App extends Vue {}
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
