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
        class="EcoTaxaExportButtonToTSV"
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
            <th>% classified</th>
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
            <td>{{ myProject.pctclassified }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </body>
</template>

<script lang="ts">
// import { Prop } from "vue-property-decorator";
import { Options, Vue } from "vue-class-component";
import * as utils from "../utils/utils";

@Options({
  name: "Projects",
  data: function () {
    return {
      userName: String(""), // user currently logged in
      userMail: String(""),
      projects: Array<utils.project>(),
      waiting: String(""),
      // TODO : yourProjects + yP is temporary code
      yourProjects: Boolean(true), // this checkbox set to true by default
      forManaging : Boolean(false),
      filterSubset:Boolean(false),
      titleFilter:String(""),
      instrumentFilter:String("")
    };
  },
  mounted() {
    utils.processUserName(this);
    // utils.processProjects(this);
  },
  methods: {
    runProjectsQuery: function () {
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



