<template>
  <div class="EcoTaxaFocusIntro">
    <!--h1>Welcome to EcoTaxa {{myID.userName}} </h1-->
    Hereunder temp. table to test generic component (on projects table)
  </div>
  <div id="#app" class="container">
    <!--div>
      <InputText type="text" v-model="text" />
      <p>{{ text }}</p>
      <InputNumber
        id="latitude"
        v-model="latitude"
        :min="-90"
        :max="90"
        :min-fraction-digits="6"
        :max-fraction-digits="6"
        placeholder="Acquisition latitude"
      />
    </div-->
    <ProjectsTableGeneric
      loggedUserId=""
      :yourProjects="false"
      :forManaging="false"
      :filterSubset="myFilterSubset"
      :display_cnn_network_id="false"
      :titleFilter="myTitleFilter"
      :display_nbMatchingFeatures="false"
      stringsMatching=""
    />
  </div>
</template>

<script lang="ts"> 
// @ is an alias to /src
import ProjectsTableGeneric from "./ProjectsTableGeneric.vue";
import { defineComponent } from "@vue/runtime-core";
//import InputText from "primevue/inputtext";
//import InputNumber from "primevue/inputnumber";
import * as utils from "../utils/utilsProjects";

export default defineComponent({
  // export default {
  name: "Home",
  components: {
    ProjectsTableGeneric: ProjectsTableGeneric,
    //InputText : InputText,
    //InputNumber : InputNumber,    
  },
  data: function () {
    return {
      myTitleFilter: "learning",
      myFilterSubset: true,
      myID: new utils.identification,
      // N.B. myTitleFilter and myFilterSubset can be referenced in the html part, with or without ""
    };
  },
  mounted() {
    utils.pUserName(this.myID);
  },  
});
</script>
