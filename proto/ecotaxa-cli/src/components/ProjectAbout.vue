<template>
  <div class="EcoTaxaFocusIntro">
    <h1>Project {{ projectID }} : {{ projectTitle }}</h1>
    <!--p-->
    <a v-bind:href="urlLink"> Go to Project {{ projectID }} </a>
    <!--/p-->
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
    <table class="EcoTaxaUsersTable">
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
              <span class="EcoTaxaBadge">{{ myUser.nb_actions }}</span>
            </td>
            <td>{{ myUser.last_annot }}</td>
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
                ><strike>{{ myUser.nb_actions }}</strike></span
              >
            </td>
            <td>
              <strike>{{ myUser.last_annot }} </strike>
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
    <button type="button" @click="exportSamplesToTSVFile" class="EcoTaxaButton">
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
    <button type="button" @click="exportTaxaToTSVFile" class="EcoTaxaButton">
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
</template>

<script lang="ts">
// import { Prop } from "vue-property-decorator";
//import { Options, Vue } from "vue-class-component";
//import { onMounted, ref } from "vue";
// import 'bootst rap';
import { Dropdown } from "bootstrap";
import * as utils from "../utils/utilsProjectAbout";
import { exportDataToTSVFile } from "@/utils/exportDataToTSVFile";
import { computeLicense } from "../utils/manageLicenses";
import { defineComponent } from "vue";

const myProps = {
    projectID: "" as string,
    };
const myData = {
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
      vanilla: null, 
};     

type projectAboutT = Readonly<typeof myProps> & typeof myData;
export type {projectAboutT};

const myComp = defineComponent({
  name: "ProjectAbout",
  data: function () {
    return myData;
  },
  props: {projectID: {type: String, default: "",},},
  mounted() {
    const dd_ref:any = this.$refs.vanillaDD;
    // Add the DD handler code - not working without line below
    this.vanilla = new Dropdown(dd_ref);
    // Add a custom event
    dd_ref.addEventListener("hidden.bs.dropdown", function (event: Event) {
      alert(event.type);
    });

    utils.processProject(this as projectAboutT);
    utils.processSamplesWithObjectsAndStatus(this as projectAboutT);
    utils.processTaxa(this as projectAboutT);
  },
  methods: {
    exportTaxaToTSVFile(): void {
      exportDataToTSVFile(
        this.projectTaxa,
        "Taxa",
        this.projectID,
        "id",
        "display_name",
        "nb_validated",
        "nb_dubious",
        "nb_predicted"
      );
    },
    exportSamplesToTSVFile(): void {
      exportDataToTSVFile(
        this.samplesWithObjectsAndStatus,
        "Samples",
        this.projectID,
        "orig_id",
        "sampleid",
        "nb_unclassified",
        "nb_validated",
        "nb_dubious",
        "nb_predicted"
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
});

export default myComp;
</script>
