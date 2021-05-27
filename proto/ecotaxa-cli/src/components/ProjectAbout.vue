<template>
  <div>This is About Project for {{ to_show }}</div>
  <div id="ecotaxa" class="jumbotron text-left">
    <h1>Basic Information about project {{ projectID }}</h1>
    <br />
    <p>
      <a v-bind:href="urlLink"> Details about Project {{ projectID }} </a>
    </p>
  </div>

  <div class="container">
    <div class="row">
      <div class="col-sm-4">
        <h3>Title</h3>
        <p>{{ projectTitle }}</p>
      </div>
      <div class="col-sm-4">
        <h3>Description</h3>
        <p>{{ projectDescription }}</p>
      </div>
      <div class="col-sm-4">
        <h3>Comments</h3>
        <p>{{ projectComment }}</p>
      </div>
      <div class="col-sm-4">
        <h3>License</h3>
        <p>{{ projectLicense }}</p>
      </div>
      <div class="col-sm-4">
        <h3>SCN Network</h3>
        <p>{{ projectSCNnetwork }}</p>
      </div>
      <div class="col-sm-4">
        <h3>Contact</h3>
        <p>
          <a :href="contactMail">{{ contactName }}</a>
        </p>
      </div>
    </div>
  </div>
  <div class="container">
    <h3>Sample fields</h3>
    <br />
    <table class="table table-bordered table-striped">
      <tbody>
        <tr v-for="samples in sampleArrayArray" :key="samples.index">
          <td v-for="sample in samples" :key="sample.index">
            {{ sample }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
  <div class="container">
    <h3>Acquisition and Processing fields</h3>
    <br />
    <table class="table table-bordered table-striped col-sm-6">
      <tbody>
        <tr v-for="myfields in acquAndProcArrayArray" :key="myfields.index">
          <td v-for="myAcquOrProc in myfields" :key="myAcquOrProc.index">
            {{ myAcquOrProc }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
  <div class="container">
    <h3>Object fields</h3>
    <br />
    <table class="table table-bordered table-striped col-sm-6">
      <tbody>
        <tr v-for="myfields in objectArrayArray" :key="myfields.index">
          <td v-for="myobjectfield in myfields" :key="myobjectfield.index">
            {{ myobjectfield }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>

  <div class="container" style="visibility: hidden">
    <!-- I want to keep this important example here and hidden -->
    <div class="btn-group">
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
  </div>
  <div class="container">
    <h2>Project Managers</h2>
    <div class="dropdown">
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

  <div class="container">
    <br />
    <h2>Project Users</h2>
    <ul
      class="list-group"
      v-for="myUser in projectUsers"
      :key="myUser.index"
    >
      <li class="list-group-item">
        <a :href="myUser.email">
          <span>
            {{ myUser.name }}
          </span>
        </a>
        &emsp;&emsp;
        <span class="badge">{{ myUser.actions }}</span>
        &emsp;&emsp;
        <span class="date">{{ myUser.annot }}</span>
      </li>
    </ul>
  </div>

  <div class="container">
    <br />
    <h3>Samples with objects and status</h3>
    <button type="button" @click="exportSamples" class="btn btn-primary">
      Export in .tsv format
    </button>
    <p></p>
    <table class="table table-bordered table-striped col-sm-6">
      <tr>
        <th>Sample name (ID)</th>
        <th>Unclassified</th>
        <th>Validated</th>
        <th>Dubious</th>
        <th>Predicted</th>
      </tr>
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
    </table>
  </div>
  <br />
  <div class="container">
    <h3>
      Taxa
      <button type="button" @click="exportTaxa" class="btn btn-primary">
        Export in .tsv format
      </button>
    </h3>
    <table class="table table-bordered table-striped col-sm-6">
      <tr>
        <th>Taxon ID</th>
        <th>Validated</th>
        <th>Dubious</th>
        <th>Predicted</th>
      </tr>
      <tr v-for="myTaxon in projectTaxa" :key="myTaxon.id">
        <td>{{ myTaxon.id }}</td>
        <td>{{ myTaxon.nb_validated }}</td>
        <td>{{ myTaxon.nb_dubious }}</td>
        <td>{{ myTaxon.nb_predicted }}</td>
      </tr>
    </table>
  </div>
</template>

<script lang="ts">
// import { Prop } from "vue-property-decorator";
import { Options, Vue } from "vue-class-component";
//import { onMounted, ref } from "vue";
// import 'bootst rap';
import { Dropdown } from "bootstrap";
import * as utils from "../utils/utils";

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
      projectLicense: String(""),
      projectSCNnetwork: String(""),
      contactMail: String(""),
      contactName: String(""),
      sampleArrayArray: Array<Array<string>>(),
      acquAndProcArrayArray: Array<Array<string>>(),
      objectArrayArray: Array<Array<string>>(),
      projectManagers: Array<utils.projectUserType>(), // a manager is a user
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
      console.log(event);
      alert(event.type);
    });

    utils.processProjectSimpleFields(this);
    utils.processProjectSampleFields(this);
    utils.processAcquisitionAndProcessingFields(this);
    utils.processObjectFields(this);
    utils.processProjectManagers(this);
    utils.processProjectUsers(this);
    utils.processSamplesWithObjectsAndStatus(this);
    utils.processTaxa(this);
  },
  methods: {
    exportSamples() {
      // 3 possible solutions to export Samples with objects and status
      // https://stackoverflow.com/questions/48611671/vue-js-write-json-object-to-local-file
      // We will use the "blob" solution, with a plugging already written, see :
      // https://www.iamrohit.in/vuejs-component-export-json-data-csv-file/
      alert("Not yet implemented !");
    },
    exportTaxa() {
      alert("Not yet implemented !");
    },
  },
  computed: {
    urlLink: function (): string {
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
  },
})
export default class ProjectAbout extends Vue {
  projectID!: string;
  urlLink!: string;
  to_show = this.projectID;
}
</script>
<!-- Add "scoped" attribute to limit CSS to this component only -->

<style scoped>
.badge {
  min-width: 28px;
  border-radius: 10px;
  background-color: grey;
  color: white;
}

h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
