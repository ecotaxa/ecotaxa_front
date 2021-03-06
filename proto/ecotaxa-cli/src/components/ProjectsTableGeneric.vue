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
    <div class="card">
      <DataTable
        :value="projects"
        sortMode="single"
        v-model:selection="selectedProject"
        selectionMode="single"        
        dataKey="projid"
      >
      <!--DataTable
        class="EcoTaxaProjectsTable"      
        :value="projects"
        v-model:selection="selectedProject"
        dataKey="projid"
      -->
        <!--Column selectionMode="single" headerStyle="width: 3em"></Column-->
        <Column field="title" header="Title" :sortable="true"></Column>
        <Column field="projid" header="ID" :sortable="true"></Column>
        <Column field="name" header="Name" :sortable="true"></Column>
        <Column field="email" header="Mail" :sortable="true"></Column>
        <Column
          field="user_Status"
          header="User status"
          :sortable="true"
        ></Column>
        <Column field="status" header="Status" :sortable="true"></Column>
        <Column field="objcount" header="Nb objects" :sortable="true"></Column>
        <Column
          field="pctvalidated"
          header="% validated"
          :sortable="true"
        ></Column>
        <Column
          field="instrument"
          header="Instrument"
          :sortable="true"
        ></Column>
        <Column
          field="cnn_network_id"
          header="CNN Network"
          :sortable="true"
        ></Column>
        <Column
          field="nbMatchingFeatures"
          header="Nb Match. Features"
          :sortable="true"
        ></Column>
      </DataTable>
    </div>
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
import * as utils from "../utils/utilsProjects";
import { exportDataToTSVFile } from "@/utils/exportDataToTSVFile";
import { _MAILTO } from "@/utils/utilsConsts";
import { defineComponent } from "vue";
import DataTable from "primevue/datatable";
import Column from "primevue/column";

const myProps = {
  // several data of Projects.vue become properties here
  // I keep the same names for convenience only
  loggedUserId: 0 as number,
  yourProjects: false as boolean,
  forManaging: false as boolean,
  filterSubset: false as boolean,
  titleFilter: "" as string,
  instrumentFilter: "" as string,
  display_cnn_network_id: false as boolean,
  display_nbMatchingFeatures: false as boolean,
  stringsMatching: "" as string,
};
const myData = {
  projects: Array<utils.project>(),
  nb_taxa: new Map<number, number>(),
  nbRequests: Number(0),
  selectedProject:Number(0),
};
type projectsTableGenericT = Readonly<typeof myProps> & typeof myData;
export type { projectsTableGenericT };

//@Options({
const myComp = defineComponent({
  // export default {
  name: "ProjectsTableGeneric",
  data: function () {
    return myData;
  },
  components: {
    DataTable: DataTable,
    Column: Column,
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
    // TODO: Can remove the "as" maybe and avoid duplication of props. See ExtractPropTypes
    utils.processProjects(this as projectsTableGenericT); // ==> Run query immediately when reaching this page
  },
  methods: {
    exportProjectsToTSVFile(): void {
      // Build a temp. special projects array to perform the export.
      // Dispatch the nb_taxa map into this special projects array.
      class projectExport extends utils.project {
        nb_taxa: number;

        constructor(father: utils.project) {
          super(father);
          this.nb_taxa = 0;
        }
      }

      const myProjects: Array<projectExport> = new Array<projectExport>();
      for (const oneProject of this.projects) {
        const oneProjectExport: projectExport = new projectExport(oneProject);
        if (oneProjectExport.projid !== undefined)
          oneProjectExport.nb_taxa = this.nb_taxa.get(oneProjectExport.projid)!;
        oneProjectExport.email = oneProjectExport.email.replace(_MAILTO, "");
        myProjects.push(oneProjectExport);
      }

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

export default myComp;
</script>
