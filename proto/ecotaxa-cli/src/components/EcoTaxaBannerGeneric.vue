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
        <TieredMenu ref="menu" :model="items" :popup="true" />
      </span>
    </div>
  </div>
</template>

<script lang="ts">
import * as banner from "../utils/utilsBanner";
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
        // Others entries to come as dev progresses
        {
          label: "Home / Explore",
          url: "https://ecotaxa.obs-vlfr.fr",
        },
        {
          visible: () => this.isLogged(),
          label: "Select Project",
          items: [],
        },
        /*
        {
          label: "Create new project",
          visible: () => this.isLogged(),
          url: 'not plugged'          
        },
        */
        {
          label: "Particle Module",
          // to : "/projects", was just a trial
          url: "https://ecotaxa.obs-vlfr.fr/part/",
        },
        {
          label: "Particle projects management",
          visible: () => this.isLogged(),
          url: "https://ecotaxa.obs-vlfr.fr/part/prj/",
        },
        {
          label: "Change Password",
          visible: () => this.isLogged(),
          url: "https://ecotaxa.obs-vlfr.fr/change",
        },
        /*
        {
          label: "Create your EcoTaxa account",
          visible: () => !this.isLogged(),
          url: 'https://ecotaxa.obs-vlfr.fr/register'          
        },
        {
          label: "Log out",
          visible: () => this.isLogged(),
          url: 'https://ecotaxa.obs-vlfr.fr/logout'                 
        },
        {
          label: "Log in",
          visible: () => !this.isLogged(),
          url: 'https://ecotaxa.obs-vlfr.fr/login'          
        },
        */
      ],
    };
  },
  props: {
    bannerTitle: String,
  },
  mounted() {
    utils.pUserName(this.myID);
    banner.fillMenuWithUserProjects(this.items);
  },
  methods: {
    toggle: function (event: any) {
      const menu: any = this.$refs.menu;
      menu.toggle(event);
    },
    isLogged: function (): boolean {
      return this.myID.logged();
    },
  }
});

// export default myComp;
</script>


