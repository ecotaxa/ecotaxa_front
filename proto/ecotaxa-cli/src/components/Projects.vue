<template>
  <body>
    <div class="EcoTaxaFocusIntro">
      <h1>
        Projects available for <a :href="userMail">{{ userName }}</a>
        <br>
        {{waiting}}
      </h1>
    </div>
    <div id="#app" class="container">
      <table class="EcoTaxaProjectsTable">
        <thead>
          <tr>
            <th>Title (ID)</th>
            <th>Status</th>
            <th>Nb objects</th>
            <th>% validated</th>
            <th>% classified</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="myProject in projects" :key="myProject.index">
            <td>{{ myProject.title }}&emsp;({{ myProject.projid }})</td>
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
      waiting: String("Wait please...")
    };
  },
  mounted() {
    utils.processUserName(this);    
    utils.processProjects(this);
  },
})
export default class Projects extends Vue {
  userName!: string;
  userMail!: string;
  waiting!: string;
}
</script>



