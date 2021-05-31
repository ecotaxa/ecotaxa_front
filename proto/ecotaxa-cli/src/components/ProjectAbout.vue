<template>
  <a href="/">
    <img height="30" src="../assets/logo_ecotaxa_25.png" style="margin: 10px 0"
  /></a>
  <div><br />This is About Project for {{ to_show }}</div>
  <div id="ecotaxa" class="jumbotron text-left">
    <br />
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
    <h3>Sample fields</h3>
    <br />
    <ul class="list-group list-group-horizontal">
      <li
        class="list-group-item"
        v-for="sample in sampleArray"
        :key="sample.index"
      >
        {{ sample }}
      </li>
    </ul>
    <h3>Acquisition and Processing fields</h3>
    <br />
    <ul class="list-group list-group-horizontal">
      <li
        class="list-group-item"
        v-for="myAcquOrProc in acquAndProcArray"
        :key="myAcquOrProc.index"
      >
        {{ myAcquOrProc }}
      </li>
    </ul>
    <h3>Object fields</h3>
    <br />
    <ul class="list-group list-group-horizontal">
      <li
        class="list-group-item"
        v-for="myObjectField in objectArray"
        :key="myObjectField.index"
      >
        {{ myObjectField }}
      </li>
    </ul>
    <br />
    <br />
    <h2>Project Users</h2>
    <table class="table table-bordered table-striped col-sm-6">
      <tr>
        <th>Name</th>
        <th>Number of annotations</th>
        <th>Last annotation date</th>
        <th>User Status</th>
      </tr>
      <tr v-for="myUser in projectUsers" :key="myUser.id">
        <template v-if="myUser.active === true">
          <td>
            <a :href="myUser.email">{{ myUser.name }}</a>
          </td>
          <td>{{ myUser.actions }}</td>
          <td>{{ myUser.annot }}</td>
          <td>{{ myUser.status }}</td>
        </template>
        <template v-else>
          <td>
            <strike
              ><a :href="myUser.email">{{ myUser.name }}</a></strike
            >
          </td>
          <td>
            <strike>{{ myUser.actions }} </strike>
          </td>
          <td>
            <strike>{{ myUser.annot }} </strike>
          </td>
          <td>
            <strike>{{ myUser.status }} </strike>
          </td>
        </template>
      </tr>
    </table>
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
    <h3>
      Taxa
      <button type="button" @click="exportTaxa" class="btn btn-primary">
        Export in .tsv format
      </button>
    </h3>
    <table class="table table-bordered table-striped col-sm-6">
      <tr>
        <th>Taxon (ID)</th>
        <th>Validated</th>
        <th>Dubious</th>
        <th>Predicted</th>
      </tr>
      <tr v-for="myTaxon in projectTaxa" :key="myTaxon.id">
        <td>{{ myTaxon.name }}&emsp;({{ myTaxon.id }})</td>
        <td>{{ myTaxon.nb_validated }}</td>
        <td>{{ myTaxon.nb_dubious }}</td>
        <td>{{ myTaxon.nb_predicted }}</td>
      </tr>
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
/*
  display:flex;
  flex-direction: row;
  flex-wrap: wrap;
  max-width: 10000px;
*/
</script>
<!-- Add "scoped" attribute to limit CSS to this component only -->

<style scoped>
.list-group {
  flex-wrap: wrap;
}

.list-group-item {
  min-width: 200px;
}

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
