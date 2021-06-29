import { ProjectsApi } from "../../gen";
import { SamplesApi } from "../../gen";
import { TaxonomyTreeApi } from "../../gen";
import { AxiosResponse } from "axios";
import { ProjectModel, UserModel } from "gen/api";
import { _MAX_REQUEST_LENGTH } from "./utilsConsts";
import { _SEPARATOR } from "./utilsConsts";
import { _MAILTO } from "./utilsConsts";
import { userStatus } from "./utilsConsts";

////////////////////////////////////////////////////////////////////
export function processProject(myProject: any): void {
  const api: ProjectsApi = new ProjectsApi();
  api
    .projectQueryProjectsProjectIdGet(parseInt(myProject.projectID))
    .then((data) => {
      simpleFieldsOK(myProject, data);
      sampleAcquisitionProcessingObjectFieldsOK(myProject, data);
      projectUsersOK(myProject, data);
    })
    .catch((reason) => {
      simpleFieldsKO(myProject, reason);
      sampleAcquisitionProcessingObjectFieldsKO(myProject, reason);
      projectUsersKO(myProject, reason);
    });
}
////////////////////////////////////////////////////////////////////
function simpleFieldsOK(myProject: any, data: AxiosResponse<ProjectModel>): void {
  myProject.projectTitle = data.data.title;
  myProject.projectDescription = data.data.projtype;
  myProject.projectComment = data.data.comments;
  myProject.projectLicense = data.data.license;
  myProject.projectSCNnetwork = data.data.cnn_network_id;
  myProject.contactMail = _MAILTO + data.data.contact?.email;
  myProject.contactName = data.data.contact?.name;
}
function simpleFieldsKO(myProject: any, reason: any): void {
  //console.trace();
  console.log(reason);
  alert(reason);
  myProject.projectTitle = "Invalid Project ID"; // TODO : global error treatment
  myProject.projectDescription = "Invalid Project ID"; // TODO : global error treatment
  myProject.projectComment = "Invalid Project ID"; // TODO : global error treatment
  myProject.projectLicense = "Invalid Project ID"; // TODO : global error treatment
  myProject.projectSCNnetwork = "Invalid Project ID"; // TODO : global error treatment
  myProject.contactMail = "";
  myProject.contactName = "Invalid Project ID"; // TODO : global error treatment
}
////////////////////////////////////////////////////////////////////
function sampleAcquisitionProcessingObjectFieldsOK(myProject: any, data: AxiosResponse<ProjectModel>): void {
  /* For information : data.data.sample_free_cols will look like
  let sample_free_cols: { [key: string]: string } = {
    scan_operator: "t01",
    ship: "t02",
    program: "t03",
    // ...
  };
  console.log(sample_free_cols["ship"]);
  console.log(Object.keys(sample_free_cols)[1]); */
  if (data.data.sample_free_cols !== undefined) {
    myProject.sampleArray = Object.keys(data.data.sample_free_cols);
  }

  if (data.data.acquisition_free_cols !== undefined) {
    myProject.acquAndProcArray = Object.keys(data.data.acquisition_free_cols);
  }
  if (data.data.process_free_cols !== undefined) {
    myProject.acquAndProcArray = myProject.acquAndProcArray.concat(Object.keys(data.data.process_free_cols));
  }

  if (data.data.obj_free_cols !== undefined) {
    myProject.objectArray = Object.keys(data.data.obj_free_cols);
  }
}
function sampleAcquisitionProcessingObjectFieldsKO(myProject: any, reason: any): void {
  console.log(reason);
  alert(reason);
  myProject.sampleArray = []; // TODO : global error treatment
  myProject.acquAndProcArray = [];
  myProject.objectArray = [];
}
////////////////////////////////////////////////////////////////////
// From a single project ID and a user ID, fetch his number of actions (annotations),
// and hist last active date on the project.
// Here take first item of Array, as we pass a single project ID
// if (data.data[0].activities[i].id === userID) {
//  activities[i].nb_actions
////////////////////////////////////////////////////////////////////
/*Il y a 4 statuts d'utilisateurs dans un projet:
    visitor = non loggé ou n'ayant pas de statut particulier dans ce projet
    viewer = enregistré sur le projet mais n'a pas le droit de faire quoi que ce soit
    annotator = enregistré et a le droit de bouger des images
    manager = a tous les droits
Donc un manager est un "utilisateur" mais avec des droits spéciaux.
Et les managers peuvent changer au cours de la vie du projet
Donc il faut vraiment le voir comme un flag à un temps t.
*/

class projUser implements UserModel {
  id;  
  email;
  name;
  active?;
  nb_actions: number;
  last_annot: string;
  status: userStatus;
  
  constructor(myID: number | undefined, myStatus: userStatus) {
    this.id = myID;
    this.email = "";
    this.name = "";
    this.active = false;
    this.nb_actions = 0;
    this.last_annot = "N/A";    
    this.status = myStatus;
    }
}

export { projUser };

function projectUsersOK(myProject: any, data: AxiosResponse<ProjectModel>): void {
  myProject.projectUsers = new Array<projUser>();
  // Also add the managers in oneArray, because they are also users
  if (data.data.managers !== undefined) {
    for (let i: number = 0; i < data.data.managers.length; i++) {
      // The new keyword below is *absolutely* necessary, do NOT reuse the same variable to change only the field values
      const managerI = data.data.managers[i];
      const oneUser: projUser = new projUser(managerI.id, userStatus._MANAGER);
      oneUser.email = _MAILTO + managerI.email;
      oneUser.active = managerI.active;      
      oneUser.name = managerI.name;
      myProject.projectUsers.push(oneUser);
    }
  }
  if (data.data.annotators !== undefined) {
    for (let i: number = 0; i < data.data.annotators.length; i++) {
      // The new keyword below is *absolutely* necessary, do NOT reuse the same variable to change only the field values
      const annotatorI = data.data.annotators[i];
      const oneUser: projUser = new projUser(annotatorI.id, userStatus._ANNOTATOR);
      oneUser.email = _MAILTO + annotatorI.email;
      oneUser.name = annotatorI.name;
      oneUser.active = annotatorI.active;
      myProject.projectUsers.push(oneUser);
    }
  }
  if (data.data.viewers !== undefined) {
    for (let i: number = 0; i < data.data.viewers.length; i++) {
      // The new keyword below is *absolutely* necessary, do NOT reuse the same variable to change only the field values
      const viewerI = data.data.viewers[i];
      const oneUser: projUser = new projUser(viewerI.id, userStatus._VIEWER);
      oneUser.email = _MAILTO + viewerI.email;
      oneUser.name = viewerI.name;
      oneUser.active = viewerI.active;      
      myProject.projectUsers.push(oneUser);
    }
  }
  // Now we're going to add actions and annotations
  const api2: ProjectsApi = new ProjectsApi(); // create another API as the first one is currently used
  api2
    .projectSetGetUserStatsProjectSetUserStatsGet(myProject.projectID)
    .then((data) => {
      // We are working on a single project here, so take data[0]
      if (data.data !== undefined && data.data[0] !== undefined) {
        const data0activities = data.data[0].activities;
        if (data0activities !== undefined) {
          for (let i: number = 0; i < myProject.projectUsers.length; i++) {
            for (let j: number = 0; j < data0activities.length; j++) {
              if (myProject.projectUsers[i].id === data0activities[j].id) {
                // find corresponding IDs between Projects and ProjectsStats
                myProject.projectUsers[i].nb_actions = data0activities[j].nb_actions;
                myProject.projectUsers[i].last_annot = data0activities[j].last_annot?.replace("T", " ");
              }
            }
          }
        }
      }
    })
    .catch((reason) => {
      projectUsersKO(myProject, reason);
    });
}

function projectUsersKO(myProject: any, reason: any): void {
  //console.trace();
  console.log(reason);
  alert(reason);
  myProject.projectUsers = []; // TODO : global error treatment
}
////////////////////////////////////////////////////////////////////
// "Samples with objects and status"
// 1) Use samplesSearchSamplesSearchGet to get a list of samples from a project ID
// 2) Then sampleSetGetStatsSampleSetTaxoStatsGet : from a list of sample IDs
// 3) From JO : "Pour les samples et taxa, il faudrait afficher le nom (orig_id et name) plutôt que l'identifiant numérique"
// ==> sampleQuerySampleSampleIdGet : donne l'orig_id === le name
class sampleWithObjectsAndStatus {
  orig_id: string;
  sampleid: number | undefined;
  nb_unclassified: number | undefined;
  nb_validated: number | undefined;
  nb_dubious: number | undefined;
  nb_predicted: number | undefined;
  constructor(mysampleid: number | undefined, myorigid: string) {
    this.sampleid = mysampleid;
    this.orig_id = myorigid;
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
      myProject.samplesWithObjectsAndStatus = new Array<sampleWithObjectsAndStatus>();
      const myData = data.data;
      for (let i: number = 0; i < myData.length; i++) {
        // The new keyword below is *absolutely* necessary, do NOT reuse the same variable to change only the field values
        const oneSample: sampleWithObjectsAndStatus = new sampleWithObjectsAndStatus(myData[i].sampleid, myData[i].orig_id);
        myProject.samplesWithObjectsAndStatus.push(oneSample);
      }
    })
    .then(() => {
      // Now I'm going to add nb_Unclassified, nb_Validated, nb_Dubious, nb_Predicted
      // TODO : verify if we can (with no mem leaks) reuse api instead declaring api2
      let sampleIDlist: string = ""; // build list of sample IDs
      for (let i: number = 0; i < myProject.samplesWithObjectsAndStatus.length; i++) {
        const sample: sampleWithObjectsAndStatus = myProject.samplesWithObjectsAndStatus[i];
        sampleIDlist += sample.sampleid + _SEPARATOR;
      }
      // Special case : if sampleIDlist is too long : for project 4421 or 1409 the problem exists
      if (sampleIDlist.length > _MAX_REQUEST_LENGTH) {
        processSamplesLongRequest(myProject, sampleIDlist);
      } else {
        processThroughSampleList(myProject, sampleIDlist);
      }
    })
    .catch((reason) => {
      processSamplesWithObjectsAndStatusKO(myProject, reason);
    });
}

function processThroughSampleList(myProject: any, samplelist: string) {
  if (samplelist !== "") {
    const api2: SamplesApi = new SamplesApi(); // create another API as the first one is currently used
    api2
      .sampleSetGetStatsSampleSetTaxoStatsGet(samplelist)
      .then((data) => {
        // analyze the answer by going through the array items
        for (let i: number = 0; i < data.data.length; i++) {
          const myDataI = data.data[i];
          // ! the 2 arrays (i.e. "request" and "answer") are not in the same order
          for (let j: number = 0; j < myProject.samplesWithObjectsAndStatus.length; j++) {
            if (myDataI.sample_id === myProject.samplesWithObjectsAndStatus[j].sampleid) {
              myProject.samplesWithObjectsAndStatus[j].nb_unclassified = myDataI.nb_unclassified;
              myProject.samplesWithObjectsAndStatus[j].nb_validated = myDataI.nb_validated;
              myProject.samplesWithObjectsAndStatus[j].nb_dubious = myDataI.nb_dubious;
              myProject.samplesWithObjectsAndStatus[j].nb_predicted = myDataI.nb_predicted;
            }
          }
        }
      })
      .catch((reason) => {
        processSamplesWithObjectsAndStatusKO(myProject, reason);
      });
  }
}

function processSamplesLongRequest(myProject: any, sampleIDlist: string) {
  const nbPackets: number = Math.floor(sampleIDlist.length / _MAX_REQUEST_LENGTH) + 1;
  let oldSmallStep: number = 0;
  let smallStep: number = _MAX_REQUEST_LENGTH;
  for (let curPacket: number = 0; curPacket < nbPackets; curPacket++) {
    for (; smallStep < sampleIDlist.length; smallStep++)
      if (sampleIDlist[smallStep] === _SEPARATOR)
        break; // found the separator, in order to get a full sampleID

    const subSampleIDlist: string = sampleIDlist.substring(oldSmallStep, smallStep);

    processThroughSampleList(myProject, subSampleIDlist);

    oldSmallStep = smallStep + 1; // + 1 to swallow the separator
    smallStep += _MAX_REQUEST_LENGTH;
    if (smallStep > sampleIDlist.length) smallStep = sampleIDlist.length;
  }
}

function processSamplesWithObjectsAndStatusKO(myProject: any, reason: any): void {
  console.log(reason);
  alert(reason);
  myProject.samplesWithObjectsAndStatus = []; // TODO : global error treatment
}

/////////////////////////////////////////////////////////////////////
class taxon {
  id: number;
  display_name: string;
  nb_validated: number | undefined;
  nb_dubious: number | undefined;
  nb_predicted: number | undefined;
  constructor(mytaxon: number) {
    this.id = mytaxon;
    this.display_name = "";
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
      myProject.projectTaxa = new Array<taxon>();
      const myData = data.data[0]; // 0 because we work on a precise single project
      if (myData !== undefined && myData.used_taxa !== undefined) {
        for (let i: number = 0; i < myData.used_taxa.length; i++) {
          if (myData.used_taxa[i] !== -1) {
            const oneTaxon: taxon = new taxon(myData.used_taxa[i]);
            myProject.projectTaxa.push(oneTaxon);
          }
        }
      }
    })
    .then(() => {
      // myProject.projectTaxa array partially built with taxon id.
      // Now I'm going to add nb_unclassified, nb_validated, nb_dubious, nb_predicted
      // TODO : verify if we can (with no mem leaks) reuse api instead declaring api2
      let taxonIDlist: string = ""; // build list of taxon IDs
      for (let i: number = 0; i < myProject.projectTaxa.length; i++) {
        const oneTaxon: taxon = myProject.projectTaxa[i];
        taxonIDlist += oneTaxon.id + _SEPARATOR;
      }
      api
        .projectSetGetStatsProjectSetTaxoStatsGet(myProject.projectID, taxonIDlist)
        .then((data) => {
          // analyze the answer by going through the array items
          for (let i: number = 0; i < data.data.length; i++) {
            const dataI = data.data[i];
            // ! the 2 arrays (i.e. "request" and "answer") are not in the same order
            for (let j: number = 0; j < myProject.projectTaxa.length; j++) {
              if (dataI !== undefined && dataI.used_taxa !== undefined) {
                if (dataI.used_taxa[0] === myProject.projectTaxa[j].id) {
                  myProject.projectTaxa[j].nb_validated = dataI.nb_validated;
                  myProject.projectTaxa[j].nb_dubious = dataI.nb_dubious;
                  myProject.projectTaxa[j].nb_predicted = dataI.nb_predicted;
                }
              }
            }
          }
          // return arr; not necessary ! arr is known in the following .then scope
        })
        .then(() => {
          // Now I'm going to add the taxon name
          const api3: TaxonomyTreeApi = new TaxonomyTreeApi();
          api3
            .queryTaxaSetTaxonSetQueryGet(taxonIDlist)
            .then((data) => {
              // analyze the answer by going through the array items
              for (let i: number = 0; i < data.data.length; i++) {
                const dataI = data.data[i];
                for (let j: number = 0; j < myProject.projectTaxa.length; j++) {
                  if (dataI.id === myProject.projectTaxa[j].id) { // found !
                    myProject.projectTaxa[j].display_name = dataI.display_name;
                  }
                }
              }
            })
            .catch((reason) => {
              // TODO : can I throw it to upper level, as it's the same treatment
              processTaxaKO(myProject, reason);
            });
        })
        .catch((reason) => {
          processTaxaKO(myProject, reason);
        });
    })
    .catch((reason) => {
      processTaxaKO(myProject, reason);
    })
    .catch((reason) => {
      processTaxaKO(myProject, reason);
    });
}

function processTaxaKO(myProject: any, reason: any): void {
  //console.trace();
  console.log(reason);
  alert(reason);
  myProject.projectTaxa = []; // TODO : global error treatment
}
