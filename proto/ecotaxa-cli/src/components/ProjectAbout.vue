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
        <p>
          No comment. But the comment could be much longer and fill in several
          lines automatically indented as you should see here (otherwise resize
          the window to make it smaller and see the result)
        </p>
      </div>
      <div class="col-sm-4">
        <h3>License</h3>
        <p>CC BY-NC 4.0</p>
      </div>
      <div class="col-sm-4">
        <h3>SCN Network</h3>
        <p>SCN_zooscan_group1</p>
      </div>
      <div class="col-sm-4">
        <h3>Contact</h3>
        <p>
          <a href="mailto:ecotaxa.api.user@gmail.com">Jon Doe</a>
        </p>
      </div>
      <div class="col-sm-4">
        <h3>Other fields to come...</h3>
        <p>Other field value, the arrays and lists would come at the end</p>
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
  <br />
  <div class="container">
    <h2>Project Managers</h2>

    <h2>Dropdowns</h2>
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
        <a class="dropdown-item" href="mailto:amanda.elineau@obs-vlfr.fr"
          >Amanda Elineau</a
        >
        <a class="dropdown-item" href="mailto:lombard@obs-vlfr.fr"
          >Fabien Lombard</a
        >
        <a class="dropdown-item" href="mailto:hirata@ime.usp.br"
          >Roberto Hirata</a
        >
        <a class="dropdown-item" href="mailto:stace@whoi.edu">Stace Beaulieu</a>
        <a class="dropdown-item" href="mailto:jp.li@siat.ac.cn">Jianping Li</a>
        <a class="dropdown-item" href="mailto:annotateur@obs-vlfr.fr"
          >Annotateur OBS</a
        >
        <a class="dropdown-item" href="mailto:ecotaxa.api.user@gmail.com"
          >Test API user</a
        >
        <a class="dropdown-item" href="mailto:irisson@obs-vlfr.fr"
          >Jean-Olivier Irisson</a
        >
        <a class="dropdown-item" href="mailto:laurent.reese@gmail.com"
          >Laurent Reese</a
        >
      </div>
    </div>
  </div>
  <br />
  <div class="container">
    <br />
    <h2>Project Users</h2>
    <ul class="list-group">
      <!-- tabs are here OF COURSE temporary, just to see visual effect-->
      <li class="list-group-item">
        <a href="mailto:javier.gilabert@upct.es">Javier Gilabert</a>
        &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;
        <span class="badge">10</span>
        &emsp;
        <span class="day">8</span>
        <span class="month">June</span>
        <span class="year">2011</span>
      </li>
      <!-- tabs are here OF COURSE temporary, just to see visual effect-->
      <li class="list-group-item">
        <a href="mailto:nur.garcia.herrera@awi.de">Nur Garcia Herrera</a>
        &emsp;&emsp;&emsp;&emsp;
        <span class="badge">9</span>
        &emsp;
        <span class="day">4</span>
        <span class="month">July</span>
        <span class="year">2015</span>
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
        <th>Sample ID</th>
        <th>Unclassified</th>
        <th>Validated</th>
        <th>Dubious</th>
        <th>Predicted</th>
      </tr>
      <tr>
        <td>15713</td>
        <td>34</td>
        <td>567</td>
        <td>12</td>
        <td>956</td>
      </tr>
      <tr>
        <td>15711</td>
        <td>3254</td>
        <td>45</td>
        <td>0</td>
        <td>34</td>
      </tr>
      <tr>
        <td>15749</td>
        <td>76</td>
        <td>9175</td>
        <td>29</td>
        <td>18</td>
      </tr>
      <tr>
        <td>15733</td>
        <td>895</td>
        <td>923</td>
        <td>9</td>
        <td>1</td>
      </tr>
      <tr>
        <td>15707</td>
        <td>34</td>
        <td>567</td>
        <td>12</td>
        <td>956</td>
      </tr>
      <tr>
        <td>15762</td>
        <td>435</td>
        <td>899</td>
        <td>1723</td>
        <td>52</td>
      </tr>
      <tr>
        <td>15718</td>
        <td>895</td>
        <td>923</td>
        <td>9</td>
        <td>1</td>
      </tr>
      <tr>
        <td>15757</td>
        <td>76</td>
        <td>9175</td>
        <td>29</td>
        <td>18</td>
      </tr>
      <tr>
        <td>15712</td>
        <td>3254</td>
        <td>45</td>
        <td>0</td>
        <td>34</td>
      </tr>
      <tr>
        <td>15760</td>
        <td>34</td>
        <td>567</td>
        <td>12</td>
        <td>956</td>
      </tr>
      <tr>
        <td>...</td>
        <td>...</td>
        <td>...</td>
        <td>...</td>
        <td>...</td>
      </tr>
    </table>
  </div>
  <br />
  <div class="container">
    <h3>
      Taxas
      <button type="button" class="btn btn-primary">
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
      <tr>
        <td>11498</td>
        <td>67</td>
        <td>2</td>
        <td>56</td>
      </tr>
      <tr>
        <td>11509</td>
        <td>5</td>
        <td>3</td>
        <td>4</td>
      </tr>
      <tr>
        <td>11512</td>
        <td>175</td>
        <td>9</td>
        <td>8</td>
      </tr>
      <tr>
        <td>11514</td>
        <td>23</td>
        <td>9</td>
        <td>1</td>
      </tr>
      <tr>
        <td>11518</td>
        <td>67</td>
        <td>2</td>
        <td>56</td>
      </tr>
      <tr>
        <td>12846</td>
        <td>99</td>
        <td>723</td>
        <td>2</td>
      </tr>
      <tr>
        <td>12908</td>
        <td>23</td>
        <td>9</td>
        <td>1</td>
      </tr>
      <tr>
        <td>18758</td>
        <td>175</td>
        <td>9</td>
        <td>8</td>
      </tr>
      <tr>
        <td>25631</td>
        <td>5</td>
        <td>0</td>
        <td>4</td>
      </tr>
      <tr>
        <td>25828</td>
        <td>67</td>
        <td>2</td>
        <td>56</td>
      </tr>
      <tr>
        <td>...</td>
        <td>...</td>
        <td>...</td>
        <td>...</td>
      </tr>
    </table>
  </div>
</template>

<script lang="ts">
const _NUMCOL: number = 7; // number of Columns we want to display for the tables in this component
// import { Prop } from "vue-property-decorator";
import { Options, Vue } from "vue-class-component";
//import { onMounted, ref } from "vue";
// import 'bootst rap';
import { Dropdown } from "bootstrap";
import { ProjectsApi } from "../../gen";

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
      sampleArrayArray: Array<Array<string>>(),
      acquAndProcArrayArray: Array<Array<string>>(),
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

    this.displayProjectTitle(this.projectID);
    this.displayProjectDescription(this.projectID);
    this.displayProjectSampleFields(this.projectID);
    this.displayAcquisitionAndProcessingFields(this.projectID);
  },
  methods: {
    exportSamples() {
      // 3 possible solutions to export Samples with objects and status
      // https://stackoverflow.com/questions/48611671/vue-js-write-json-object-to-local-file
      // We will use the "blob" solution, with a plugging already written, see :
      // https://www.iamrohit.in/vuejs-component-export-json-data-csv-file/
      alert("exportSamples");
    },

    displayProjectTitle(pID: string): void {
      const api: ProjectsApi = new ProjectsApi();
      api
        .projectQueryProjectsProjectIdGet(parseInt(pID))
        .then((data) => {
          this.projectTitle = data.data.title;
        })
        .catch((reason) => {
          console.log(reason);
          this.projectTitle = "Invalid Project ID"; // TODO : global error treatment
        });
    },
    displayProjectDescription(pID: string): void {
      const api: ProjectsApi = new ProjectsApi();
      api
        .projectQueryProjectsProjectIdGet(parseInt(pID))
        .then((data) => {
          this.projectDescription = data.data.projtype;
        })
        .catch((reason) => {
          console.log(reason);
          this.projectDescription = "Invalid Project ID"; // TODO : global error treatment
        });
    },
    displayProjectSampleFields(pID: string): void {
      /* For information : data.data.sample_free_cols will look like
      let sample_free_cols: { [key: string]: string } = {
        scan_operator: "t01",
        ship: "t02",
        program: "t03",
        // ...
      };
      console.log(sample_free_cols["ship"]);
      console.log(Object.keys(sample_free_cols)[1]); */

      const api: ProjectsApi = new ProjectsApi();
      api
        .projectQueryProjectsProjectIdGet(parseInt(pID))
        .then((data) => {
          if (data.data.sample_free_cols !== undefined) {
            let sampleFlatArray = Object.keys(data.data.sample_free_cols);
            let nbItems: number = sampleFlatArray.length;
            let myArrayString: Array<string>;
            let myArrayArrayString = new Array<Array<string>>();
            //let nbRows: number = Math.round(nbItems / _NUMCOL);
            let row: number = 0;
            let col: number = 0;
            while (col + row * _NUMCOL < nbItems) {
              myArrayString = new Array<string>();
              for (; col < _NUMCOL && col + row * _NUMCOL < nbItems; col++) {
                myArrayString.push(sampleFlatArray[col + row * _NUMCOL]);
              }
              myArrayArrayString.push(myArrayString);
              col = 0;
              row++;
            }
            this.sampleArrayArray = myArrayArrayString;
            //console.log(nbRows);
            //console.log(myArrayArrayString);
          }
        })
        .catch((reason) => {
          console.log(reason);
          this.sampleArrayArray = "Invalid Project ID"; // TODO : global error treatment
        });
    },
    displayAcquisitionAndProcessingFields(pID: string): void {
      const api: ProjectsApi = new ProjectsApi();
      api
        .projectQueryProjectsProjectIdGet(parseInt(pID))
        .then((data) => {
          // Join acquisition_free_cols and process_free_cols
          let myFlatArray: Array<string> = new Array<string>();
          if (data.data.acquisition_free_cols !== undefined)
            myFlatArray = Object.keys(data.data.acquisition_free_cols);
          if (data.data.process_free_cols !== undefined)
            myFlatArray = myFlatArray.concat(
              Object.keys(data.data.process_free_cols)
            );
          if (myFlatArray.length) {
            let nbItems: number = myFlatArray.length;
            let myArrayString: Array<string>;
            let myArrayArrayString = new Array<Array<string>>();
            //let nbRows: number = Math.round(nbItems / _NUMCOL);
            let row: number = 0;
            let col: number = 0;
            while (col + row * _NUMCOL < nbItems) {
              myArrayString = new Array<string>();
              for (; col < _NUMCOL && col + row * _NUMCOL < nbItems; col++) {
                myArrayString.push(myFlatArray[col + row * _NUMCOL]);
              }
              myArrayArrayString.push(myArrayString);
              col = 0;
              row++;
            }
            this.acquAndProcArrayArray = myArrayArrayString;
            //console.log(nbRows);
            //console.log(myArrayArrayString);
          }
        })
        .catch((reason) => {
          console.log(reason);
          this.acquAndProcArrayArray = "Invalid Project ID"; // TODO : global error treatment
        });
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
