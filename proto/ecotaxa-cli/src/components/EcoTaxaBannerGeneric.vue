<template>
  <div class="EcoTaxaBannerGeneric">
    <div>
      <a href="/">
        <img src="../assets/logo_ecotaxa_25.png" />
      </a>
    </div>
    <div>
      <h1>{{ bannerTitle }}</h1>
    </div>
    <div>
      <span
        ><br />{{ myID.userName }}&nbsp;&nbsp;<br />
        <Button type="button" label="Toggle" @click="toggle">Action</Button>
        <TieredMenu ref="menu" :model="items" :popup="true" :dropdown="true" />
      </span>
    </div>
  </div>
</template>

<script lang="ts">
import * as utils from "../utils/utilsProjects";
import { defineComponent } from "vue";
import TieredMenu from "primevue/tieredmenu";

//const myComp = defineComponent({
export default defineComponent({
  name: "EcoTaxaBannerGeneric",
  components: {
    TieredMenu: TieredMenu,
  },
  data() {
    return {
      myID: new utils.identification(),
      items: [
        {
          label: "Home / Explore",
        },
        {
          label: "Create new project",
          visible: () => this.isLogged(),
        },
        {
          label: "Particle Module",
        },
        {
          label: "Particle projects management",
          visible: () => this.isLogged(),
        },
        {
          label: "Change Password",
          visible: () => this.isLogged(),
        },
        {
          label: "Create your EcoTaxa account",
          visible: () => !this.isLogged(),
        },
        {
          label: "Log out",
          visible: () => this.isLogged(),
        },
        {
          label: "Log in",
          visible: () => !this.isLogged(),
        },
      ],
    };
  },
  props: {
    bannerTitle: String,
  },
  mounted() {
    utils.pUserName(this.myID);
  },
  methods: {
    toggle: function (event: any) {
      const menu: any = this.$refs.menu;
      menu.toggle(event);
    },
    isLogged: function (): boolean {
      return this.myID.logged();
    },
  },
});

// export default myComp;
</script>


