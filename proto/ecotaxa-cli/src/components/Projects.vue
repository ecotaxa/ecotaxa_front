<template>
  <body>
    <div class="EcoTaxaFocusIntro">
      <h1>
        Projects available for <a :href="userMail">{{ userName }}</a>
        <h4>
          {{ waiting }}
        </h4>
      </h1>
    </div>
    <div id="#app" class="container">
      <input type="checkbox" v-model="yourProjects" />Projects I'm in&emsp;
      <input type="checkbox" v-model="forManaging" />For managing&emsp;
      <input type="checkbox" v-model="filterSubset" />Filter subsets&emsp;
      <br />
      Title filter&emsp;<input type="text" v-model="titleFilter" />&emsp;&emsp;
      Instrument Filter&emsp;<input type="text" v-model="instrumentFilter" />
      <br />
       <br />
      <button
        type="button"
        @click="runProjectsQuery"
        class="EcoTaxaButton"
      >
        Run Query
      </button>
      <br />
       <br />
      <table class="EcoTaxaProjectsTable">
        <thead>
          <tr>
            <th>Title (ID)</th>
            <th>Contact</th>
            <th>Status</th>
            <th>Nb objects</th>
            <th>% validated</th>
            <th>Nb taxa</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="myProject in projects" :key="myProject.index">
            <td>{{ myProject.title }}&emsp;({{ myProject.projid }})</td>
            <td>
              <a :href="myProject.email">{{ myProject.name }}</a>
            </td>
            <td>{{ myProject.status }}</td>
            <td>{{ myProject.objcount }}</td>
            <td>{{ myProject.pctvalidated }}</td>
            <td>{{ nb_taxa.get(myProject.projid) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </body>
</template>

<script lang="ts">
// import { Prop } from "vue-property-decorator";
import { Options, Vue } from "vue-class-component";
import * as utils from "../utils/utilsProjects";

@Options({
  name: "Projects",
  data: function () {
    return {
      userName: String(""), // user currently logged in
      userMail: String(""),
      projects: Array<utils.project>(),
      yourProjects: Boolean(true), // this checkbox set to true by default
      forManaging: Boolean(false),
      filterSubset: Boolean(false),
      titleFilter: String(""),
      instrumentFilter: String(""),
      nb_taxa: new Map<number, number>(),
      nbRequests: Number(0),
    };
  },
  mounted() {
    utils.processUserName(this);
    utils.processProjects(this); // ==> Run query button when reaching this page
  },
  computed: {
    waiting: function (): string {
      if (this.nbRequests === 0) return "";
      return "Please wait for server answer...";
    },
  },
  methods: {
    runProjectsQuery: function () {
      this.nbRequests == 0; // should not be necessary
      utils.processProjects(this);
    },
  },
})
export default class Projects extends Vue {
  userName!: string;
  userMail!: string;
  waiting!: string;
}
</script>
