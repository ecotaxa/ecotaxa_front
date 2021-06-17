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
      <!--input type="checkbox" id="checkbox" v-model="yourProjects" true-value="true" false-value="false"/>
      <label for="checkbox">&emsp;Your projects</label-->

      <input type="checkbox" @click="yourProjectsToggle" v-model="yourProjects" />&emsp;Your projects

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
      yourProjects: Boolean(true), // just to set the checkbox to true by default
      yP : Boolean(true), // to really handle the value
    };
  },
  mounted() {
    utils.processUserName(this);
    utils.processProjects(this);
  },
  methods: {
    yourProjectsToggle: function () {
      this.yP = !this.yP;
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



