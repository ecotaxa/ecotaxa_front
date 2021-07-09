<template>
  <div class="EcoTaxaBannerGeneric">
    <div>
      <a href="/">
        <img src="../assets/logo_ecotaxa_25.png"        
        />
      </a>
    </div>
    <div>
      <h1>{{bannerTitle}}</h1>
    </div>
    <div>
      <span><br />{{ myID.userName}}&nbsp;&nbsp;</span>
    </div>
  </div>
</template>

<script lang="ts">
import * as utils from "../utils/utilsProjects";
import { defineComponent } from "vue";

const myProps = {
  bannerTitle: "" as string,
};

const myData = {
  myID: new utils.identification(),
};

type ecotaxaBannerT = Readonly<typeof myProps> & typeof myData;
export type { ecotaxaBannerT };

const myComp = defineComponent({
  name: "Projects",
  data: function () {
    return myData;
  },
  props: {
    bannerTitle: String,
  },
  mounted() {
    utils.pUserName(this.myID);
  },  
});

export default myComp;
</script>


