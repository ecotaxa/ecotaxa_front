import { ProjectsApi } from "../../gen";
import { SamplesApi } from "../../gen";
import { TaxonomyTreeApi } from "../../gen";
const _NUMCOL: number = 7; // number of Columns we want to display for the tables in this component

////////////////////////////////////////////////////////////////////
export function processProjectSimpleFields(myObject: any): void {
  const api: ProjectsApi = new ProjectsApi();
  api
    .projectQueryProjectsProjectIdGet(parseInt(myObject.projectID))
    .then((data) => {
      myObject.projectTitle = data.data.title;
      myObject.projectDescription = data.data.projtype;
      myObject.projectComment = data.data.comments;
      myObject.projectLicense = data.data.license;
      myObject.projectSCNnetwork = data.data.cnn_network_id;
      myObject.contactMail = "mailto:" + data.data.contact?.email;
      myObject.contactName = data.data.contact?.name;
    })
    .catch((reason) => {
      console.log(reason);
      myObject.projectTitle = "Invalid Project ID"; // TODO : global error treatment
      myObject.projectDescription = "Invalid Project ID"; // TODO : global error treatment
      myObject.projectComment = "Invalid Project ID"; // TODO : global error treatment
      myObject.projectLicense = "Invalid Project ID"; // TODO : global error treatment
      myObject.projectSCNnetwork = "Invalid Project ID"; // TODO : global error treatment
      myObject.contactMail = "";
      myObject.contactName = "Invalid Project ID"; // TODO : global error treatment
    });
}
////////////////////////////////////////////////////////////////////
export function processProjectSampleFields(myObject: any): void {
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
    .projectQueryProjectsProjectIdGet(parseInt(myObject.projectID))
    .then((data) => {
      if (data.data.sample_free_cols !== undefined) {
        const sampleFlatArray = Object.keys(data.data.sample_free_cols);
        const nbItems: number = sampleFlatArray.length;
        //let myArrayString: Array<string>;
        const myArrayArrayString = new Array<Array<string>>();
        //let nbRows: number = Math.round(nbItems / _NUMCOL);
        let row: number = 0;
        let col: number = 0;
        while (col + row * _NUMCOL < nbItems) {
          const myArrayString = new Array<string>();
          for (; col < _NUMCOL && col + row * _NUMCOL < nbItems; col++) {
            myArrayString.push(sampleFlatArray[col + row * _NUMCOL]);
          }
          myArrayArrayString.push(myArrayString);
          col = 0;
          row++;
        }
        myObject.sampleArrayArray = myArrayArrayString;
        //console.log(nbRows);
        //console.log(myArrayArrayString);
      }
    })
    .catch((reason) => {
      console.log(reason);
      myObject.sampleArrayArray = ""; // TODO : global error treatment
    });
}
////////////////////////////////////////////////////////////////////
export function processAcquisitionAndProcessingFields(myObject: any): void {
  const api: ProjectsApi = new ProjectsApi();
  api
    .projectQueryProjectsProjectIdGet(parseInt(myObject.projectID))
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
        const nbItems: number = myFlatArray.length;
        const myArrayArrayString = new Array<Array<string>>();
        //let nbRows: number = Math.round(nbItems / _NUMCOL);
        let row: number = 0;
        let col: number = 0;
        while (col + row * _NUMCOL < nbItems) {
          const myArrayString = new Array<string>();
          for (; col < _NUMCOL && col + row * _NUMCOL < nbItems; col++) {
            myArrayString.push(myFlatArray[col + row * _NUMCOL]);
          }
          myArrayArrayString.push(myArrayString);
          col = 0;
          row++;
        }
        myObject.acquAndProcArrayArray = myArrayArrayString;
        //console.log(nbRows);
        //console.log(myArrayArrayString);
      }
    })
    .catch((reason) => {
      console.log(reason);
      myObject.acquAndProcArrayArray = ""; // TODO : global error treatment
    });
}
////////////////////////////////////////////////////////////////////
export function processObjectFields(myObject: any): void {
  const api: ProjectsApi = new ProjectsApi();
  api
    .projectQueryProjectsProjectIdGet(parseInt(myObject.projectID))
    .then((data) => {
      let myFlatArray: Array<string> = new Array<string>();
      if (data.data.obj_free_cols !== undefined)
        myFlatArray = Object.keys(data.data.obj_free_cols);
      if (myFlatArray.length) {
        const nbItems: number = myFlatArray.length;
        const myArrayArrayString = new Array<Array<string>>();
        //let nbRows: number = Math.round(nbItems / _NUMCOL);
        let row: number = 0;
        let col: number = 0;
        while (col + row * _NUMCOL < nbItems) {
          const myArrayString = new Array<string>();
          for (; col < _NUMCOL && col + row * _NUMCOL < nbItems; col++) {
            myArrayString.push(myFlatArray[col + row * _NUMCOL]);
          }
          myArrayArrayString.push(myArrayString);
          col = 0;
          row++;
        }
        myObject.objectArrayArray = myArrayArrayString;
        //console.log(nbRows);
        //console.log(myArrayArrayString);
      }
    })
    .catch((reason) => {
      console.log(reason);
      myObject.objectArrayArray = ""; // TODO : global error treatment
    });
}
////////////////////////////////////////////////////////////////////
// From a single project ID and a user ID, fetch his number of actions (annotations),
// and hist last active date on the project.
// Here take first item of Array, as we pass a single project ID
// if (data.data[0].activities[i].id === userID) {
//  activities[i].nb_actions
////////////////////////////////////////////////////////////////////
class projUser {
  name: string;
  email: string;
  id: number | undefined; // TODO : fix : undefined needed because of a strange compilation error
  actions: number | undefined; // TODO : fix : undefined needed because of a strange compilation error
  annot: string | undefined; // It's a date. TODO : fix : undefined needed because of a strange compilation error
  constructor() {
    this.name = "";
    this.email = "";
    this.id = undefined;
    this.actions = 0;
    this.annot = "";
  }
}
export { projUser };

export function processProjectUsers(myProject: any): void {
  const api: ProjectsApi = new ProjectsApi();
  api
    .projectQueryProjectsProjectIdGet(parseInt(myProject.projectID))
    .then((data) => {
      let oneArray: Array<projUser> = new Array<projUser>();
      // Also add the managers in oneArray, because they are also users
      if (data.data.managers !== undefined) {
        for (let i: number = 0; i < data.data.managers.length; i++) {
          // The new keyword below is *absolutely* necessary, do NOT reuse the same variable to change only the field values
          const oneManager: projUser = new projUser();
          oneManager.email = "mailto:" + data.data.managers[i].email;
          oneManager.name = data.data.managers[i].name;
          oneManager.id = data.data.managers[i].id; // will be used in the second .then to identify the user
          myProject.projectManagers.push(oneManager);
        }
      }
      oneArray = oneArray.concat(myProject.projectManagers);
      if (data.data.annotators !== undefined) {
        for (let i: number = 0; i < data.data.annotators.length; i++) {
          // The new keyword below is *absolutely* necessary, do NOT reuse the same variable to change only the field values
          const oneUser: projUser = new projUser();
          oneUser.email = "mailto:" + data.data.annotators[i].email;
          oneUser.name = data.data.annotators[i].name;
          oneUser.id = data.data.annotators[i].id; // will be used in the second .then to identify the user
          oneArray.push(oneUser);
        }
      }
      return oneArray;
    })
    .then((arr) => {
      // arr is my array partially built with email + name + id
      // Now we're going to add actions and annotations
      const api2: ProjectsApi = new ProjectsApi(); // create another API as the first one is currently used
      api2
        .projectSetGetUserStatsProjectSetUserStatsGet(myProject.projectID)
        .then((data) => {
          // We are working on a single project here, so take data[0]
          // TODO here : create and use temp vars named data0 and data0actvities to factorize
          const data0activities = data.data[0].activities;
          if (data0activities !== undefined) {
            for (let i: number = 0; i < arr.length; i++) {
              for (let j: number = 0; j < data0activities.length; j++) {
                if (arr[i].id === data0activities[j].id) {
                  // find corresponding IDs between Projects and ProjectsStats
                  arr[i].actions = data0activities[j].nb_actions;
                  arr[i].annot = data0activities[j].last_annot; // TODO : convert
                }
              }
            }
            myProject.projectUsers = arr;
          }
        })
        .catch((reason) => {
          console.log(reason);
          // Think about your session cookie whenever you fall down here !
          // alert(reason);
          myProject.projectUsers = []; // TODO : global error treatment
        });
    })
    .catch((reason) => {
      console.log(reason);
      alert(reason);
      myProject.projectUsers = []; // TODO : global error treatment
    });
}
////////////////////////////////////////////////////////////////////
// "Samples with objects and status"
// 1) Use samplesSearchSamplesSearchGet to get a list of samples from a project ID
// 2) Then sampleSetGetStatsSampleSetTaxoStatsGet : from a list of sample IDs
// 3) From JO : "Pour les samples et taxa, il faudrait afficher le nom (orig_id et name) plutôt que l'identifiant numérique"
// ==> sampleQuerySampleSampleIdGet : donne l'orig_id === le name
class sampleWithObjectsAndStatus {
  sampleid: number | undefined;
  orig_id: string;
  nb_unclassified: number | undefined;
  nb_validated: number | undefined;
  nb_dubious: number | undefined;
  nb_predicted: number | undefined;
  constructor() {
    this.sampleid = 0;
    this.orig_id = "";
    this.nb_unclassified = 0;
    this.nb_validated = 0;
    this.nb_dubious = 0;
    this.nb_predicted = 0;
  }
}
export { sampleWithObjectsAndStatus };

export function processSamplesWithObjectsAndStatus(myProject: any): void {
  const api: SamplesApi = new SamplesApi();
  api
    .samplesSearchSamplesSearchGet(myProject.projectID, "*")
    .then((data) => {
      const oneArray: Array<sampleWithObjectsAndStatus> = new Array<sampleWithObjectsAndStatus>();
      const myData = data.data;
      for (let i: number = 0; i < myData.length; i++) {
        // The new keyword below is *absolutely* necessary, do NOT reuse the same variable to change only the field values
        const oneSample: sampleWithObjectsAndStatus = new sampleWithObjectsAndStatus();
        oneSample.sampleid = myData[i].sampleid;
        oneSample.orig_id = myData[i].orig_id;
        oneArray.push(oneSample);
      }
      return oneArray;
    })
    .then((arr) => {
      // arr is my array partially built with sampleid and orig_id fields
      // Now I'm going to add nb_Unclassified, nb_Validated, nb_Dubious, nb_Predicted
      // TODO : verify if we can (with no mem leaks) reuse api instead declaring api2
      let sampleIDlist: string = ""; // build list of sample IDs
      arr.forEach((sample) => {
        sampleIDlist += sample.sampleid + " ";
      });
      const api2: SamplesApi = new SamplesApi(); // create another API as the first one is currently used
      api2
        .sampleSetGetStatsSampleSetTaxoStatsGet(sampleIDlist)
        .then((data) => {
          // analyze the answer by going through the array items
          for (let i: number = 0; i < data.data.length; i++) {
            const myDataI = data.data[i];
            // ! the 2 arrays (i.e. "request" and "answer" are not in the same order)
            for (let j: number = 0; j < arr.length; j++) {
              if (myDataI.sample_id === arr[j].sampleid) {
                arr[j].nb_unclassified = myDataI.nb_unclassified;
                arr[j].nb_validated = myDataI.nb_validated;
                arr[j].nb_dubious = myDataI.nb_dubious;
                arr[j].nb_predicted = myDataI.nb_predicted;
              }
            }
          }
          myProject.samplesWithObjectsAndStatus = arr;
        })
        .catch((reason) => {
          console.log(reason);
          alert(reason);
          myProject.samplesWithObjectsAndStatus = []; // TODO : global error treatment
        });
    })
    .catch((reason) => {
      console.log(reason);
      alert(reason);
      myProject.samplesWithObjectsAndStatus = []; // TODO : global error treatment
    });
}
/////////////////////////////////////////////////////////////////////
class taxon {
  id: number;
  name: string;
  nb_unclassified: number | undefined;
  nb_validated: number | undefined;
  nb_dubious: number | undefined;
  nb_predicted: number | undefined;
  constructor(mytaxon: number) {
    this.id = mytaxon;
    this.name = "";
    this.nb_unclassified = 0;
    this.nb_validated = 0;
    this.nb_dubious = 0;
    this.nb_predicted = 0;
  }
}
export { taxon };
export function processTaxa(myProject: any): void {
  // use projectSetGetStatsProjectSetTaxoStatsGet: async (ids: string, taxaIds?: string)
  // 1) call with just projectID to get all the taxon IDs
  // 2) call with projectID and list of taxon IDs, in order to get all information about all taxa
  // 3) use API: /taxon_set/query to get the taxon name from a taxon ID
  const api: ProjectsApi = new ProjectsApi();
  api
    .projectSetGetStatsProjectSetTaxoStatsGet(myProject.projectID)
    .then((data) => {
      const oneArray: Array<taxon> = new Array<taxon>();
      const myData = data.data[0]; // 0 because we work on a precise single project
      if (myData !== undefined && myData.used_taxa !== undefined) {
        for (let i: number = 0; i < myData.used_taxa.length; i++) {
          if (myData.used_taxa[i] !== -1) {
            const oneTaxon: taxon = new taxon(myData.used_taxa[i]);
            oneArray.push(oneTaxon);
          }
        }
      }
      return oneArray;
    })
    .then((arr) => {
      // arr is my array partially built with taxon id
      // Now I'm going to add nb_unclassified, nb_validated, nb_dubious, nb_predicted
      // TODO : verify if we can (with no mem leaks) reuse api instead declaring api2
      let taxonIDlist: string = ""; // build list of sample IDs
      arr.forEach((taxon) => {
        taxonIDlist += taxon.id + " ";
      });
      const api2: ProjectsApi = new ProjectsApi(); // create another API as the first one is currently used
      api2
        .projectSetGetStatsProjectSetTaxoStatsGet(myProject.projectID, taxonIDlist)
        .then((data) => {
          // analyze the answer by going through the array items
          for (let i: number = 0; i < data.data.length; i++) {
            const dataI = data.data[i];
            // ! the 2 arrays (i.e. "request" and "answer" are not in the same order)            
            for (let j: number = 0; j < arr.length; j++) {
              if (dataI !== undefined && dataI.used_taxa !== undefined) {
                if (dataI.used_taxa[0] === arr[j].id) {
                  arr[j].nb_unclassified = dataI.nb_unclassified; // TODO : probably useless field
                  arr[j].nb_validated = dataI.nb_validated;
                  arr[j].nb_dubious = dataI.nb_dubious;
                  arr[j].nb_predicted = dataI.nb_predicted;
                }
              }
            }
          }
          // return arr; not necessary ! arr is known in the following .then scope
        })
        .then(() => {
          // arr is known here !
          // Now I'm going to add the taxon name
          const api3: TaxonomyTreeApi = new TaxonomyTreeApi();
          api3
            .queryTaxaSetTaxonSetQueryGet(taxonIDlist)
            .then((data) => {
              // analyze the answer by going through the array items
              for (let i: number = 0; i < data.data.length; i++) {
                const dataI = data.data[i];
                for (let j: number = 0; j < arr.length; j++) {
                  if (dataI.id === arr[j].id) {
                    arr[j].name = dataI.name;
                  }
                }
              }
              myProject.projectTaxa = arr;
            })
            .catch((reason) => {
              console.log(reason);
              alert(reason);
              myProject.projectTaxa = []; // TODO : global error treatment
            });
        })
        .catch((reason) => {
          console.log(reason);
          alert(reason);
          myProject.projectTaxa = []; // TODO : global error treatment
        });
    })
    .catch((reason) => {
      console.log(reason);
      alert(reason);
      myProject.projectTaxa = []; // TODO : global error treatment
    })
    .catch((reason) => {
      console.log(reason);
      alert(reason);
      myProject.projectTaxa = []; // TODO : global error treatment
    });
}
