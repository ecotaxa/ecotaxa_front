<template>
  <div class="ProjectsTableGeneric">
    <span v-if="nbRequests">
      <img src="../assets/wait.png" height="50" />
    </span>
    <span v-if="projects.length && !nbRequests">
      <button
        type="button"
        @click="exportProjectsToTSVFile"
        class="EcoTaxaButton"
      >
        Export in .tsv format
      </button>
    </span>
    <table class="EcoTaxaProjectsTable">
      <thead>
        <tr>
          <th>Title (ID)</th>
          <th>Contact</th>
          <th>User status</th>
          <th>Status</th>
          <th>Nb objects</th>
          <th>% validated</th>
          <th>Nb taxa</th>
          <th>Instrument</th>
          <th v-if="display_cnn_network_id">CNN Network</th>
          <th v-if="display_nbMatchingFeatures">Nb Match. Features</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="myProject in projects" :key="myProject.index">
          <td>{{ myProject.title }}&emsp;({{ myProject.projid }})</td>
          <td>
            <a :href="myProject.email">{{ myProject.name }}</a>
          </td>
          <td>{{ myProject.user_Status }}</td>
          <td>{{ myProject.status }}</td>
          <td>{{ myProject.objcount }}</td>
          <td>{{ myProject.pctvalidated }}</td>
          <td>{{ nb_taxa.get(myProject.projid) }}</td>
          <td>{{ myProject.instrument }}</td>
          <td v-if="display_cnn_network_id">
            {{ myProject.cnn_network_id }}
          </td>
          <td v-if="display_nbMatchingFeatures">
            {{ myProject.nbMatchingFeatures }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script lang="ts">
// import { Prop } from "vue-property-decorator";
// import { Options, Vue } from "vue-class-component";
import * as utils from "../utils/utilsProjects";
import { exportDataToTSVFile } from "../utils/exportDataToTSVFile";
import { _MAILTO } from "../utils/utilsConsts";
import { defineComponent } from "@vue/runtime-core";

//@Options({
export default defineComponent({
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
    loggedUserId: Number,
    yourProjects: Boolean,
    forManaging: Boolean,
    filterSubset: Boolean,
    titleFilter: String,
    instrumentFilter: String,
    display_cnn_network_id: Boolean,
    display_nbMatchingFeatures: Boolean,
    stringsMatching: String,
  },
  mounted() {
    utils.processProjects(this); // ==> Run query immediately when reaching this page
  },
  methods: {
    exportProjectsToTSVFile(): void {
      // Build a temp. special projects array to perform the export.
      // Dispatch the nb_taxa map into this special projects array.
      class projectExport extends utils.project {
        nb_taxa: number | undefined;
        constructor(father: utils.project) {
          super(father);
          this.nb_taxa = 0;
        }
      }

      const myProjects: Array<projectExport> = new Array<projectExport>();
      for (const oneProject of this.projects) {
        const oneProjectExport: projectExport = new projectExport(oneProject);
        if (oneProjectExport.projid !== undefined)        
          oneProjectExport.nb_taxa = this.nb_taxa.get(oneProjectExport.projid);
        oneProjectExport.email = oneProjectExport.email.replace(_MAILTO, "");
        myProjects.push(oneProjectExport);
      }

      /*
      // KEEP it: at one moment I got strange problems with fields of subclass.
      // There is a copy constructor (from mother class) called here.
      const myProjects:Array<projectExport> = new Array<projectExport>();
      for (let i = 0; i < this.projects.length; i++) {
        const oneProjectExport: projectExport = new projectExport(this.projects[i]);
        if (oneProjectExport.projid !== undefined)
          oneProjectExport.nb_taxa = this.nb_taxa.get(oneProjectExport.projid);
        else
          oneProjectExport.nb_taxa = 0;
        oneProjectExport.email = oneProjectExport.email.replace(_MAILTO,"");          
        myProjects.push(oneProjectExport);
      }
      */

      // TODO : review columns orders, JO may have a precise idea
      exportDataToTSVFile(
        myProjects,
        "Projects",
        "EcoTaxa",
        "title",
        "projid",
        "name",
        "email",
        "user_Status",
        "status",
        "objcount",
        "pctvalidated",
        "instrument",
        "cnn_network_id",
        "nbMatchingFeatures",
        "nb_taxa"
      );
    },
  },
});

/*
export default class ProjectsTableGeneric extends Vue {
  yourProjects!: boolean;
  forManaging!: boolean;
  filterSubset!: boolean;
  titleFilter!: string;
  instrumentFilter!: string;
  display_cnn_network_id!: boolean;
}
*/

// export default ProjectsTableGeneric;
</script>
