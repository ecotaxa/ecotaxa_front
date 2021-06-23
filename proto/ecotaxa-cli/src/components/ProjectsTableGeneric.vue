<template>
  <div class="ProjectsTableGeneric">
    <span v-if="nbRequests">
      <img src="../assets/wait.png" height="50" />
    </span>
    <table class="EcoTaxaProjectsTable">
      <thead>
        <tr>
          <th>Title (ID)</th>
          <th>Contact</th>
          <th>Status</th>
          <th>Nb objects</th>
          <th>% validated</th>
          <th>Nb taxa</th>
          <th>Instrument</th>
          <th v-if="display_cnn_network_id">CNN Network</th>
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
          <td>TODOLaurentS</td>
          <td v-if="display_cnn_network_id">
            {{ myProject.cnn_network_id }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script lang="ts">
// import { Prop } from "vue-property-decorator";
import { Options, Vue } from "vue-class-component";
import * as utils from "../utils/utilsProjects";

@Options({
  // export default {
  name: "ProjectsTableGeneric",
  data: function () {
    return {
      projects: Array<utils.project>(),
      nb_taxa: new Map<number, number>(),
      nbRequests: Number(0),
    };
  },
  props: {
    // several data of Projects.vue become properties here
    // I keep the same names for convenience only
    yourProjects: Boolean,
    forManaging: Boolean,
    filterSubset: Boolean,
    titleFilter: String,
    instrumentFilter: String,
    display_cnn_network_id: Boolean,
  },
  mounted() {
    utils.processProjects(this); // ==> Run query immediately when reaching this page
  },
  methods: {},
})
export default class ProjectsTableGeneric extends Vue {
  yourProjects!: boolean;
  forManaging!: boolean;
  filterSubset!: boolean;
  titleFilter!: string;
  instrumentFilter!: string;
}

// export default ProjectsTableGeneric;
</script>
