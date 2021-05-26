import { ProjectsApi } from "../../gen";
const _NUMCOL: number = 7; // number of Columns we want to display for the tables in this component

////////////////////////////////////////////////////////////////////
export function processProjectTitle(myObject: any): void {
  const api: ProjectsApi = new ProjectsApi();
  api
    .projectQueryProjectsProjectIdGet(parseInt(myObject.projectID))
    .then((data) => {
      myObject.projectTitle = data.data.title;
    })
    .catch((reason) => {
      console.log(reason);
      myObject.projectTitle = "Invalid Project ID"; // TODO : global error treatment
    });
}
////////////////////////////////////////////////////////////////////
export function processProjectDescription(myObject: any): void {
  const api: ProjectsApi = new ProjectsApi();
  api
    .projectQueryProjectsProjectIdGet(parseInt(myObject.projectID))
    .then((data) => {
      myObject.projectDescription = data.data.projtype;
    })
    .catch((reason) => {
      console.log(reason);
      myObject.projectDescription = "Invalid Project ID"; // TODO : global error treatment
    });
}
////////////////////////////////////////////////////////////////////
export function processProjectComment(myObject: any): void {
  const api: ProjectsApi = new ProjectsApi();
  api
    .projectQueryProjectsProjectIdGet(parseInt(myObject.projectID))
    .then((data) => {
      myObject.projectComment = data.data.comments;
    })
    .catch((reason) => {
      console.log(reason);
      myObject.projectComment = "Invalid Project ID"; // TODO : global error treatment
    });
}
////////////////////////////////////////////////////////////////////
export function processProjectLicense(myObject: any): void {
  const api: ProjectsApi = new ProjectsApi();
  api
    .projectQueryProjectsProjectIdGet(parseInt(myObject.projectID))
    .then((data) => {
      myObject.projectLicense = data.data.license;
    })
    .catch((reason) => {
      console.log(reason);
      myObject.projectLicense = "Invalid Project ID"; // TODO : global error treatment
    });
}
////////////////////////////////////////////////////////////////////
export function processProjectSCNnetwork(myObject: any): void {
  const api: ProjectsApi = new ProjectsApi();
  api
    .projectQueryProjectsProjectIdGet(parseInt(myObject.projectID))
    .then((data) => {
      myObject.projectSCNnetwork = data.data.cnn_network_id;
    })
    .catch((reason) => {
      console.log(reason);
      myObject.projectSCNnetwork = "Invalid Project ID"; // TODO : global error treatment
    });
}
////////////////////////////////////////////////////////////////////
export function processNameAndContact(myObject: any): void {
  const api: ProjectsApi = new ProjectsApi();
  api
    .projectQueryProjectsProjectIdGet(parseInt(myObject.projectID))
    .then((data) => {
      myObject.contactMail = "mailto:" + data.data.contact?.email;
      myObject.contactName = data.data.contact?.name;
    })
    .catch((reason) => {
      console.log(reason);
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
      myObject.sampleArrayArray = "Invalid Project ID"; // TODO : global error treatment
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
      myObject.acquAndProcArrayArray = "Invalid Project ID"; // TODO : global error treatment
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
      myObject.acquAndProcArrayArray = "Invalid Project ID"; // TODO : global error treatment
    });
}
////////////////////////////////////////////////////////////////////
class projectManagerType {
  name: string;
  email: string;
  constructor(myname: string, myemail: string) {
    this.name = myname;
    this.email = myemail;
  }
}
export { projectManagerType };

export function processProjectManagers(myObject: any): void {
  const api: ProjectsApi = new ProjectsApi();
  api
    .projectQueryProjectsProjectIdGet(parseInt(myObject.projectID))
    .then((data) => {
      if (data.data.managers !== undefined)
        for (let i: number = 0; i < data.data.managers.length; i++) {
          // The new below is *absolutely* necessary, do NOT reuse the same variable to change only the field values
          const oneManager: projectManagerType = new projectManagerType("", "");
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
