<template>
  <div id="ecotaxa" class="jumbotron text-left">
    <h1>Basic Information about project {{ projectID }}</h1>
    <br />
    <!--h1>{{ urlLink }}</h1-->

    <p>
      <a v-bind:href="urlLink"> Details about Project {{ projectID }} </a>
    </p>

    <!--p>
      <a href="https://ecotaxa.obs-vlfr.fr/prj/185"
        >Details about Project {{ projectID }}</a
      >      
    </p-->
  </div>

  <div class="container">
    <div class="row">
      <div class="col-sm-4">
        <h3>Title</h3>
        <p>Demo Zooscan for API tests (point B WP2 200)</p>
      </div>
      <div class="col-sm-4">
        <h3>Description</h3>
        <p>Données PtB Zooscan filet WP2, semaine ET mardi.</p>
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
    <table class="table table-bordered table-striped col-sm-12">
      <!-- hard coded just to see the result-->
      <!-- find a proper generic solution with Vuejs/TypeScript -->
      <tr>
        <td>scan_operator</td>
        <td>ship</td>
        <td>program</td>
        <td>stationid</td>
        <td>bottomdepth</td>
        <td>ctdrosettefilename</td>
        <td>other_ref</td>
        <td>tow_nb</td>
      </tr>
      <tr>
        <td>tow_type</td>
        <td>net_type</td>
        <td>net_mesh</td>
        <td>net_surf</td>
        <td>zmax</td>
        <td>zmin</td>
        <td>tot_vol</td>
        <td>comment</td>
      </tr>
      <tr>
        <td>tot_vol_qc</td>
        <td>depth_qc</td>
        <td>sample_qc</td>
        <td>barcode</td>
        <td>duration</td>
        <td>ship_speed</td>
        <td>cable_length</td>
        <td>cable_angle</td>
      </tr>
      <tr>
        <td>cable_speed</td>
        <td>nb_jar</td>
        <td>open</td>
      </tr>
    </table>
  </div>
  <div class="container">
    <h3>Acquisition and Processing fields</h3>
    <br />
    <table class="table table-bordered table-striped col-sm-6">
      <!-- hard coded to see the merge between acquisition and processing-->
      <!-- find a proper generic solution with Vuejs/TypeScript -->
      <tr>
        <td>min_mesh</td>
        <td>max_mesh</td>
        <td>sub_part</td>
        <td>sub_method</td>
        <td>hardware</td>
        <td>software</td>
      </tr>
      <tr>
        <td>author</td>
        <td>imgtype</td>
        <td>scan_date</td>
        <td>scan_time</td>
        <td>quality</td>
        <td>bitpixel</td>
      </tr>
      <tr>
        <td>greyfrom</td>
        <td>scan_resolution</td>
        <td>rotation</td>
        <td>miror</td>
        <td>xsize</td>
        <td>ysize</td>
      </tr>
      <tr>
        <td>xoffset</td>
        <td>yoffset</td>
        <td>lut_color_balance</td>
        <td>lut_filter</td>
        <td>lut_min</td>
        <td>lut_max</td>
      </tr>
      <tr>
        <td>lut_odrange</td>
        <td>lut_ratio</td>
        <td>lut_16b_median</td>
        <td>instrument</td>
        <td>date</td>
        <td>time</td>
      </tr>
      <tr>
        <td>img_software_version</td>
        <td>img_resolution</td>
        <td>img_od_grey</td>
        <td>img_od_std</td>
        <td>img_background_img</td>
        <td>particle_version</td>
      </tr>
      <tr>
        <td>particle_threshold</td>
        <td>particle_pixel_size_mm</td>
        <td>particle_min_size_mm</td>
        <td>particle_max_size_mm</td>
        <td>particle_sep_mask</td>
        <td>particle_bw_ratio</td>
      </tr>
    </table>
  </div>
  <br />
  <div class="container">
    <h2>Project Managers</h2>

    <div class="dropdown">
      <button
        type="button"
        class="btn btn-primary dropdown-toggle"
        data-toggle="dropdown"
      >
        View List
      </button>
      <div class="dropdown-menu">
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
    <button type="button" class="btn btn-primary">Export in .tsv format</button>
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
import { Options, Vue } from "vue-class-component";

@Options({
  props: {
    projectID: String,
  },
  data: function () {
    return {
      //urlLink: String("coucou"),
      urlLink: String(window.location.pathname + "prj/" + this.projectID)
    };
  },
})
export default class Issue382 extends Vue {
  projectID!: string;
  urlLink!: string;
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<!--style scoped>
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
</style-->
