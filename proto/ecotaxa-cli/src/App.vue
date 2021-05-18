<template>
  <!--Banner />
  <img alt="Vue logo" src="./assets/logo.png" />
  <span> {{ a }} </span>
  <about-me />
  <HelloWorld msg="Welcome to Your Vue.js + TypeScript App" /-->
  <login />
  <br>
  <Issue382 projectID=186 />
</template>

<script lang="ts">
/* import HelloWorld from "./components/HelloWorld.vue";
import Login from "./components/Login.vue";
import Banner from "./components/Banner.vue";
import AboutMe from "./components/AboutMe.vue";*/
import Login from "./components/Login.vue";
import { Options, Vue } from "vue-class-component";
import Issue382 from "./components/Issue382.vue";

@Options({
  components: {
    Issue382,
    Login,    
    /*HelloWorld,
    Login,
    Banner,
    AboutMe,*/
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
