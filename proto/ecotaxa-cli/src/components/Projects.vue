<template>
  <div class="EcoTaxaFocusIntro">
    <h1>
      Projects available for <a :href="userMail">{{ userName }}</a>
      <br />
      <!--
      <span v-if="nbRequests">
        <img src="../assets/wait.png" height="40" />
      </span>
      -->
    </h1>
  </div>
  <div id="#app" class="container">
    <input
      type="checkbox"
      v-model="yourProjects"
      @click="reinitQuery"
    />Projects I'm in&emsp;
    <input type="checkbox" v-model="forManaging" @click="reinitQuery" />For
    managing&emsp;
    <input type="checkbox" v-model="filterSubset" @click="reinitQuery" />Filter
    subsets&emsp;
    <br />
    Title filter&emsp;<input
      type="text"
      v-model="titleFilter"
      @click="reinitQuery"
    />&emsp;&emsp; Instrument Filter&emsp;<input
      type="text"
      v-model="instrumentFilter"
      @click="reinitQuery"
    />
    <br />
    <br />
    <button type="button" @click="runProjectsQuery" class="EcoTaxaButton">
      Run Query
    </button>
    <br />
    <br />
    <!-- Here call ProjectsTableGeneric-->

    <span v-if="runQuery">
      <!-- keeping same names like filterSubset="filterSubset" is not mandatory, here it's done for convenience only -->
      <ProjectsTableGeneric
        v-bind:yourProjects="yourProjects"
        v-bind:forManaging="forManaging"
        v-bind:filterSubset="filterSubset"
        v-bind:titleFilter="titleFilter"
        v-bind:instrumentFilter="instrumentFilter"
        ref="ProjectsTableGeneric"
      />
    </span>
  </div>
</template>

<script lang="ts">
// import { Prop } from "vue-property-decorator";
//import my_router from "@/router";
import { Options, Vue } from "vue-class-component";
import * as utils from "../utils/utilsProjects";
import ProjectsTableGeneric from "./ProjectsTableGeneric.vue";

@Options({
  name: "Projects",
  components: {
    ProjectsTableGeneric: ProjectsTableGeneric,
  },
  data: function () {
    return {
      userName: String(""), // user currently logged in
      userMail: String(""),
      yourProjects: Boolean(true), // this checkbox set to true by default
      forManaging: Boolean(false),
      filterSubset: Boolean(false),
      titleFilter: String(""),
      instrumentFilter: String(""),
      runQuery: Boolean(false),
    };
  },
  mounted() {
    utils.processUserName(this);
  },

  methods: {
    runProjectsQuery: function () {
      this.runQuery = true;
    },
    reinitQuery: function () {
      this.runQuery = false;
    },
  },
})
export default class Projects extends Vue {
  userName!: string;
  userMail!: string;
}
</script>
