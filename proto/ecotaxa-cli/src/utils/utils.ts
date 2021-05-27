import { ProjectsApi } from "../../gen";
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
class projectUserType {
  name: string;
  email: string;
  constructor(myname: string, myemail: string) {
    this.name = myname;
    this.email = myemail;
  }
}
export { projectUserType };

export function processProjectManagers(myObject: any): void {
  const api: ProjectsApi = new ProjectsApi();
  api
    .projectQueryProjectsProjectIdGet(parseInt(myObject.projectID))
    .then((data) => {
      if (data.data.managers !== undefined)
        for (let i: number = 0; i < data.data.managers.length; i++) {
          // The new keyword below is *absolutely* necessary, do NOT reuse the same variable to change only the field values
          const oneManager: projectUserType = new projectUserType("", "");
          oneManager.email = "mailto:" + data.data.managers[i].email;
          oneManager.name = data.data.managers[i].name;
          myObject.projectManagers.push(oneManager);
        }
    })
    .catch((reason) => {
      console.log(reason);
      myObject.projectManagers = [
        { email: "Invalid Project ID", name: "Invalid Project ID" },
      ]; // TODO : global error treatment
    });
}
////////////////////////////////////////////////////////////////////
export function processProjectUsers(myObject: any): void {
  const api: ProjectsApi = new ProjectsApi();
  api
    .projectQueryProjectsProjectIdGet(parseInt(myObject.projectID))
    .then((data) => {
      if (data.data.annotators !== undefined) {
        for (let i: number = 0; i < data.data.annotators.length; i++) {
          // The new keyword below is *absolutely* necessary, do NOT reuse the same variable to change only the field values
          const oneUser: projectUserType = new projectUserType("", "");
          oneUser.email = "mailto:" + data.data.annotators[i].email;
          oneUser.name = data.data.annotators[i].name;
          myObject.projectUsers.push(oneUser);
        }
      }
      // Also add the managers, who are also users
      if (data.data.managers !== undefined) {
        for (let i: number = 0; i < data.data.managers.length; i++) {
          // The new keyword below is *absolutely* necessary, do NOT reuse the same variable to change only the field values
          const oneManager: projectUserType = new projectUserType("", "");
          oneManager.email = "mailto:" + data.data.managers[i].email;
          oneManager.name = data.data.managers[i].name;
          myObject.projectUsers.push(oneManager);
        }
      }
    })
    .catch((reason) => {
      console.log(reason);
      myObject.projectUsers = [
        { email: "Invalid Project ID", name: "Invalid Project ID" },
      ]; // TODO : global error treatment
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

export function TRYprocessProjectUsers(myProject: any): void {
  const api: ProjectsApi = new ProjectsApi();
  api
    .projectQueryProjectsProjectIdGet(parseInt(myProject.projectID))
    .then((data) => {
      const oneArray: Array<projUser> = new Array<projUser>();
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
      // Also add the managers in oneArray, because they are also users
      if (data.data.managers !== undefined) {
        for (let i: number = 0; i < data.data.managers.length; i++) {
          // The new keyword below is *absolutely* necessary, do NOT reuse the same variable to change only the field values
          const oneManager: projUser = new projUser();
          oneManager.email = "mailto:" + data.data.managers[i].email;
          oneManager.name = data.data.managers[i].name;
          oneManager.id = data.data.managers[i].id; // will be used in the second .then to identify the user
          oneArray.push(oneManager);
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
                  arr[i].annot = data0activities[j].last_annot;
                }
              }
            }
            myProject.projectUsersTRY = arr;
          }
        })
        .catch((reason) => {
          console.log(reason);
          alert(reason);
          myProject.projectUsersTRY = []; // TODO : global error treatment
        });
    })
    .catch((reason) => {
      console.log(reason);
      alert(reason);
      myProject.projectUsersTRY = []; // TODO : global error treatment
    });
}
