<template>
  <body>
    <div class="EcoTaxaFocusIntro">
      <h1>Welcome to EcoTaxa</h1>
      Hereunder temp. table to test generic component (on projects table)
      <ProjectsTableGeneric
        :yourProjects=false
        :forManaging=false
        :filterSubset=myFilterSubset
        :display_cnn_network_id=false
        :titleFilter="myTitleFilter"
      />
    </div>
  </body>
</template>

<script lang="ts">
// @ is an alias to /src
// import HelloWorld from "@/components/HelloWorld.vue";

import ProjectsTableGeneric from "./ProjectsTableGeneric.vue";

export default {
  name: "Home",
  components: {
    // HelloWorld
    /*ProjectsTableGeneric:*/ ProjectsTableGeneric,
  },
  data: function () {
    return {
      myTitleFilter: "learning", 
      myFilterSubset: true,      
      // N.B. myTitleFilter and myFilterSubset can be referenced in the html part, with or without ""
    }
  }
};
</script>
