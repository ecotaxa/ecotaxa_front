<template>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
  </head>

  <div class="EcoTaxaIconPlusRouting">
    <img src="./assets/logo_ecotaxa_25.png" />
    <span>
      <router-link to="/">Home</router-link> |
      <router-link to="/projects">Projects</router-link> |
      <router-link to="/prj_about/185">Project 185</router-link>
    </span>
    <span />
    <!-- this empty item is *mandatory* -->
  </div>
  <router-view />

  <!--div id="nav" >
    <img class="alignleft"
      height="30"
      src="./assets/logo_ecotaxa_25.png"
      style="margin: 10px 0"
    />
    <span class="aligncenter">
    <router-link to="/">Home</router-link> |
    <router-link to="/about">About</router-link> |
    <router-link to="/prj_about/185">Project 185</router-link>
    </span>
    <span/>
  </div>
  <router-view /-->

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
//import { Options, Vue } from "vue-class-component";
import { defineComponent } from "@vue/runtime-core";
// import ProjectAbout from "./components/ProjectAbout.vue";

export default defineComponent({
//@Options({
  components: {
    /*Issue382,
    Login,    
    HelloWorld,
    Banner,
    AboutMe,*/
  },
  data() {
    return {
      text: "",
    };
  },
  mounted() {
    this.$forceUpdate(); // keep it while in dev. phase, to avoid using cache
  },  
});

/*
export default class App extends Vue {
  mounted() {
    this.$forceUpdate(); // keep it while in dev. phase, to avoid using cache
  }
}
*/
</script>


