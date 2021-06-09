<template>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
  </head>
  <div id="nav">
    <router-link to="/">Home</router-link> |
    <router-link to="/about">About</router-link> |
    <router-link to="/prj_about/185">Project 185</router-link>
  </div>
  <router-view />
  <!--Banner />
  <img alt="Vue logo" src="./assets/logo.png" />  
  <Login />
  <AboutMe />
  <HelloWorld msg="Welcome to Your Vue.js + TypeScript App" />
  <br />
  <Issue382 projectID="186" /-->
</template>

<script lang="ts">
/* import Banner from "./components/Banner.vue";
import HelloWorld from "./components/HelloWorld.vue";
import Login from "./components/Login.vue";
import Banner from "./components/Banner.vue";
import AboutMe from "./components/AboutMe.vue";
import Login from "./components/Login.vue";*/
import { Options, Vue } from "vue-class-component";
// import ProjectAbout from "./components/ProjectAbout.vue";

@Options({
  components: {
    /*Issue382,
    Login,    
    HelloWorld,
    Banner,
    AboutMe,*/
  },
})
export default class App extends Vue {
  mounted() {
    this.$forceUpdate(); // keep it while in dev. phase, to avoid using cache
  }
}
</script>
