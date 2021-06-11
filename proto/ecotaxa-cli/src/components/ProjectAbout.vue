<template>
  <body class="body">
    <a href="/">
      <img
        height="30"
        src="../assets/logo_ecotaxa_25.png"
        style="margin: 10px 0"
    /></a>
    <div class="EcoTaxaFocusIntro">
      <h1>Project {{ projectID }} : {{ projectTitle }}</h1>
      <br />
      <p>
        <a v-bind:href="urlLink"> Details about Project {{ projectID }} </a>
      </p>
    </div>
    <div id="#app" class="container">
      <div class="row">
        <div class="EcoTaxaBasicInformation">
          <h3>Description</h3>
          <p>{{ projectDescription }}</p>
        </div>
        <div class="EcoTaxaBasicInformation">
          <h3>Comments</h3>
          <p>{{ projectComment }}</p>
        </div>
        <div class="EcoTaxaBasicInformation">
          <h3>License</h3>
          <!--
          {{ projectLicense }}
          {{ copyright }}
          -->
          <span>
            <img v-bind:src="copyright" height="60" />
          </span>
        </div>
        <div class="EcoTaxaBasicInformation">
          <h3>SCN Network</h3>
          <p>{{ projectSCNnetwork }}</p>
        </div>
        <div class="EcoTaxaBasicInformation">
          <h3>Contact</h3>
          <p>
            <a :href="contactMail">{{ contactName }}</a>
          </p>
        </div>
      </div>
      <br />
      <br />
      <h2>Sample fields</h2>
      <h6 v-if="sampleArray.length == 0">(none)</h6>
      <br />
      <ul class="EcoTaxaListGroupHorizontal">
        <li
          class="EcoTaxaSampleFields"
          v-for="sample in sampleArray"
          :key="sample.index"
        >
          {{ sample }}
        </li>
      </ul>
      <br />
      <h2>Acquisition and Processing fields</h2>
      <h6 v-if="acquAndProcArray.length == 0">(none)</h6>
      <br />
      <ul class="EcoTaxaListGroupHorizontal">
        <li
          class="EcoTaxaAcquAndProcFields"
          v-for="myAcquOrProc in acquAndProcArray"
          :key="myAcquOrProc.index"
        >
          {{ myAcquOrProc }}
        </li>
      </ul>
      <br />
      <h2>Object fields</h2>
      <h6 v-if="objectArray.length == 0">(none)</h6>
      <br />
      <ul class="EcoTaxaListGroupHorizontal">
        <li
          class="EcoTaxaObjectFields"
          v-for="myObjectField in objectArray"
          :key="myObjectField.index"
        >
          {{ myObjectField }}
        </li>
      </ul>
      <br />
      <h2>Project Users</h2>
      <table class="EcoTaxaProjectUsersTable">
        <thead>
          <tr>
            <th>Name</th>
            <th>Number of annotations</th>
            <th>Last annotation date</th>
            <th>User Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="myUser in projectUsers" :key="myUser.id">
            <template v-if="myUser.active === true">
              <td>
                <a :href="myUser.email">{{ myUser.name }}</a>
              </td>
              <td>
                <span class="EcoTaxaBadge">{{ myUser.actions }}</span>
              </td>
              <td>{{ myUser.annot }}</td>
              <td>{{ myUser.status }}</td>
            </template>
            <template v-else>
              <td>
                <a :href="myUser.email"
                  ><strike>{{ myUser.name }}</strike></a
                >
              </td>
              <td>
                <span class="EcoTaxaBadge"
                  ><strike>{{ myUser.actions }}</strike></span
                >
              </td>
              <td>
                <strike>{{ myUser.annot }} </strike>
              </td>
              <td>
                <strike>{{ myUser.status }} </strike>
              </td>
            </template>
          </tr>
        </tbody>
      </table>
      <br />
      <h2>Samples with objects and status</h2>
      <button
        type="button"
        @click="exportSamplesToTSVFile"
        class="EcoTaxaExportButtonToTSV"
      >
        Export in .tsv format
      </button>
      <table class="EcoTaxaSamplesTable">
        <thead>
          <tr>
            <th>Sample name (ID)</th>
            <th>Unclassified</th>
            <th>Validated</th>
            <th>Dubious</th>
            <th>Predicted</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="mySample in samplesWithObjectsAndStatus"
            :key="mySample.sampleid"
          >
            <td>{{ mySample.orig_id }}&emsp;({{ mySample.sampleid }})</td>
            <td>{{ mySample.nb_unclassified }}</td>
            <td>{{ mySample.nb_validated }}</td>
            <td>{{ mySample.nb_dubious }}</td>
            <td>{{ mySample.nb_predicted }}</td>
          </tr>
        </tbody>
      </table>
      <br />
      <h2>Taxa</h2>
      <button
        type="button"
        @click="exportTaxaToTSVFile"
        class="EcoTaxaExportButtonToTSV"
      >
        Export in .tsv format
      </button>
      <table class="EcoTaxaTaxaTable">
        <thead>
          <tr>
            <th>Unique Name</th>
            <th>Validated</th>
            <th>Dubious</th>
            <th>Predicted</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="myTaxon in projectTaxa" :key="myTaxon.id">
            <!--td>{{ myTaxon.display_name }}&emsp;({{ myTaxon.id }})</td-->
            <td>{{ myTaxon.display_name }}</td>
            <td>{{ myTaxon.nb_validated }}</td>
            <td>{{ myTaxon.nb_dubious }}</td>
            <td>{{ myTaxon.nb_predicted }}</td>
          </tr>
        </tbody>
      </table>
      <!-- I want to keep this important example here and hidden -->
      <div class="btn-group" style="visibility: hidden">
        <button
          ref="vanillaDD"
          class="btn btn-secondary dropdown-toggle"
          type="button"
          id="dropdownMenuButton1"
          data-toggle="dropdown"
          aria-expanded="false"
        >
          Dropdown button
        </button>
        <div class="dropdown-menu" aria-labelledby="dropdownMenuButton1">
          <a class="dropdown-item" href="#">Action</a>
          <a class="dropdown-item" href="#">Another action</a>
          <a class="dropdown-item" href="#">Something else here</a>
        </div>
      </div>
      <!-- I want to keep this important example here and hidden -->
      <div class="dropdown" style="visibility: hidden">
        <button
          type="button"
          class="btn btn-primary dropdown-toggle"
          data-bs-target="#people"
          data-bs-toggle="dropdown"
        >
          View List
        </button>
        <div class="dropdown-menu" id="people">
          <a
            class="dropdown-item"
            v-for="myProjectManager in projectManagers"
            :key="myProjectManager.name"
            :href="myProjectManager.email"
          >
            {{ myProjectManager.name }}</a
          >
        </div>
      </div>
    </div>
  </body>
</template>

<script lang="ts">
// import { Prop } from "vue-property-decorator";
import { Options, Vue } from "vue-class-component";
//import { onMounted, ref } from "vue";
// import 'bootst rap';
import { Dropdown } from "bootstrap";
import * as utils from "../utils/utils";
import { exportDataToTSVFile } from "../utils/exportDataToTSVFile";
import { computeLicense } from "../utils/manageLicenses";

//export default defineComponent({
@Options({
  name: "ProjectAbout",
  props: {
    projectID: {
      type: String,
      default: "",
    },
  },
  data: function () {
    return {
      vanilla: null,
      projectTitle: String(""),
      projectDescription: String(""),
      projectComment: String(""),
      projectLicense: String(""), // see https://www.systemed.fr/normes-droit-regles/licences-creative-commons,5113.html
      projectSCNnetwork: String(""),
      contactMail: String(""),
      contactName: String(""),
      sampleArray: Array<string>(),
      acquAndProcArray: Array<string>(),
      objectArray: Array<string>(),
      projectUsers: Array<utils.projUser>(),
      samplesWithObjectsAndStatus: Array<utils.sampleWithObjectsAndStatus>(),
      projectTaxa: Array<utils.taxon>(),
    };
  },
  mounted() {
    const dd_ref = this.$refs.vanillaDD;
    // Add the DD handler code - not working without line below
    this.vanilla = new Dropdown(dd_ref);
    // Add a custom event
    dd_ref.addEventListener("hidden.bs.dropdown", function (event: Event) {
      alert(event.type);
    });

    utils.processProject(this);
    utils.processSamplesWithObjectsAndStatus(this);
    utils.processTaxa(this);
  },
  methods: {
    exportTaxaToTSVFile(): void {
      exportDataToTSVFile(this.projectTaxa, "Taxa", this.projectID);
    },
    exportSamplesToTSVFile(): void {
      exportDataToTSVFile(
        this.samplesWithObjectsAndStatus,
        "Samples",
        this.projectID
      );
    },
  },
  computed: {
    urlLink: function (): string {
      // TODO : will be used elsewhere so put in a separate "utils.ts" file
      let findDoubleSlash: number = window.location.pathname.indexOf("//");
      let findSlash: number = 0;
      if (findDoubleSlash == -1) {
        // not found
        findSlash = window.location.pathname.indexOf("/");
      } else {
        findSlash = window.location.pathname.indexOf("/", findDoubleSlash + 2);
      }
      let mySub: string = "";
      if (findSlash != -1)
        mySub = window.location.pathname.substring(0, findSlash);
      else mySub = window.location.pathname;
      mySub += "/prj/" + this.projectID;
      return mySub;
    },
    copyright: function (): string {
      return computeLicense(this.projectLicense);
    },
  },
})
export default class ProjectAbout extends Vue {
  projectID!: string;
  urlLink!: string;
  copyright!: string;
  to_show = this.projectID;
}
</script>
