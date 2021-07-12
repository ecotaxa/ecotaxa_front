<template>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
  </head>
  <EcoTaxaBannerGeneric 
    v-bind:bannerTitle="theTitle"
  />
  <div class="EcoTaxaRouting">
    <span>
      <router-link to="/">Home</router-link> |
      <router-link to="/projects/">Projects</router-link> |
      <router-link to="/prj_about/185">Project 185</router-link>
    </span>
  </div>
  <router-view />
</template>

<script lang="ts">
/* import Banner from "./components/Banner.vue";
import HelloWorld from "./components/HelloWorld.vue";
import Login from "./components/Login.vue";
import Banner from "./components/Banner.vue";
import AboutMe from "./components/AboutMe.vue";
import Login from "./components/Login.vue";*/

import { defineComponent } from "vue";
import EcoTaxaBannerGeneric from "./components/EcoTaxaBannerGeneric.vue";

export default defineComponent({
  components: {
    EcoTaxaBannerGeneric: EcoTaxaBannerGeneric,
  },
  data() {
    return {
      theTitle: String("Welcome to EcoTaxa"),
    };
  },
  mounted() {
    this.$forceUpdate(); // keep it while in dev. phase, to avoid using cache
  },
});

</script>


