import { ProjectsApi } from "../../gen";
import { ProjectModel } from "gen/api";
import { UsersApi } from "../../gen";
import { _MAX_REQUEST_LENGTH } from "./utilsConsts";
import { _SEPARATOR } from "./utilsConsts";
import { _MAILTO } from "./utilsConsts";
import { userStatus } from "./utilsConsts";
import {projectsTableGenericT} from "@/components/ProjectsTableGeneric.vue";

////////////////////////////////////////////////////////////////////

// class project implements ProjectModel {
class project implements ProjectModel {
  title;
  projid;
  name: string;
  email: string;
  user_Status: userStatus;
  status;
  objcount;
  pctvalidated;
  instrument;
  cnn_network_id;
  nbMatchingFeatures: number;
  // Use the copy constructor to build a project object from a ProjectModel object
  constructor(father: ProjectModel) {
    this.title = father.title;
    this.projid = father.projid;
    if (father.contact !== undefined && father.contact !== null)
      this.name = father.contact.name;
    else
      this.name = "";
    if (father.contact !== undefined && father.contact !== null)
      this.email = _MAILTO + father.contact.email;
    else
      this.email = "";
    this.user_Status = userStatus._NONE;
    this.status = father.status;
    this.objcount = father.objcount;
    if (father.pctvalidated !== undefined && father.pctvalidated !== null)
      this.pctvalidated = Math.round(father.pctvalidated * 100) / 100;
    else
      this.pctvalidated = 0;
    this.instrument = father.instrument;
    this.cnn_network_id = father.cnn_network_id;
    this.nbMatchingFeatures = 0;
  }
}

export { project };

export function processUserName(myProjects: any): void {
  const api: UsersApi = new UsersApi();
  api
    .showCurrentUserUsersMeGet()
    .then((data) => {
      myProjects.userName = data.data.name;
      myProjects.loggedUserId = data.data.id;
      myProjects.userMail = _MAILTO + data.data.email;
    })
    .catch((reason) => {
      // TODO : global error treatment      
      console.log(reason);
      alert(reason);
      myProjects.userName = "<< User probably not logged in >>";
      myProjects.loggedUserId = 0;
      myProjects.userMail = "";
    });
}

////////////////////////////////////////////////////////////////////
export function processProjects(theProjects: projectsTableGenericT): void {
  theProjects.nbRequests++; // this function makes a request
  theProjects.projects = [];
  theProjects.nb_taxa = new Map<number, number>();
  const api: ProjectsApi = new ProjectsApi();
  api
    .searchProjectsProjectsSearchGet(!theProjects.yourProjects, !theProjects.yourProjects,
      theProjects.forManaging,
      theProjects.titleFilter,
      theProjects.instrumentFilter,
      theProjects.filterSubset,
    )
    .then((data) => {
      if (data.data !== undefined && data.data.length > 0) {
        theProjects.projects = new Array<project>();
        data.data.forEach(dataI => {
          if (dataI !== undefined) {
            // DO A *new*
            // Better to use the copy constructor to build a project object from a ProjectModel object
            // instead of doing = through several fields, like objcount or status, or projid
            const oneProject: project = new project(dataI);
            if (dataI.obj_free_cols !== undefined) {
              // TODO : think of factorizinz that if used elsewhere
              if (theProjects.stringsMatching !== undefined && theProjects.stringsMatching !== "") {
                const stringsMatching: string = theProjects.stringsMatching;
                const stringsMatchingArray: Array<string> = stringsMatching.split(" ");
                if (stringsMatchingArray.length) {
                  const freecolsArray: Array<string> = Object.keys(dataI.obj_free_cols);
                  stringsMatchingArray.forEach(element => {
                    if (element !== undefined) {
                      if (freecolsArray.indexOf(element) !== -1)
                        oneProject.nbMatchingFeatures++;
                    }
                  })
                }
              }
            }
            // Here work on the user status on each project (different from project status)
            oneProject.user_Status = findUserStatus(dataI, theProjects.loggedUserId);
            theProjects.projects.push(oneProject);
          }
        });
      }
    })
    .then(() => {
      // TODO EVERYWHERE : give a type to "this", instead of "any", otherwise we lose all the TS useful checking.
      // Build the projectID list and initialize the nb_taxa map
      let projectIDlist: string = ""; // build list of project IDs
      const projs: project[] = theProjects.projects;
      projs.forEach(oneProject => {
        const pid: number | undefined = oneProject.projid;
        if (pid !== undefined) {
          projectIDlist += pid.toString() + _SEPARATOR;
          theProjects.nb_taxa.set(pid, 0);
        }
      });
      if (projectIDlist.length > _MAX_REQUEST_LENGTH) {
        setProjectsAllCategories(api, projectIDlist, theProjects);
      }
      else {
        setProjectsCategories(api, projectIDlist, theProjects);
      }
    })
    .catch((reason) => {
      // TODO : global error treatment      
      console.log(reason);
      alert(reason);
      theProjects.projects = [];
    })
    .finally(() => {
      theProjects.nbRequests--;
    }
    );
}

function findUserStatus(dataI: ProjectModel, userId: number): userStatus {
  let theUsers = dataI.annotators;
  if (theUsers !== undefined) {
    for (const element of theUsers) {
      if (element.id === userId)
        return userStatus._ANNOTATOR;
    }
  }
  theUsers = dataI.managers;
  if (theUsers !== undefined) {
    for (const element of theUsers) {
      if (element.id === userId)
        return userStatus._MANAGER;
    }
  }
  theUsers = dataI.viewers;
  if (theUsers !== undefined) {
    for (const element of theUsers) {
      if (element.id === userId)
        return userStatus._VIEWER;
    }
  }
  return userStatus._NONE;
}

function setProjectsAllCategories(api: ProjectsApi, projectIDlist: string, theProjects: any): void {
  const nbPackets: number = Math.floor(projectIDlist.length / _MAX_REQUEST_LENGTH) + 1;
  let oldSmallStep: number = 0;
  let smallStep: number = _MAX_REQUEST_LENGTH;
  for (let curPacket: number = 0; curPacket < nbPackets; curPacket++) {
    for (; smallStep < projectIDlist.length; smallStep++)
      if (projectIDlist[smallStep] === _SEPARATOR)
        break; // found the separator, in order to get a full projectID

    const subProjectIDlist: string = projectIDlist.substring(oldSmallStep, smallStep);
    setProjectsCategories(api, subProjectIDlist, theProjects);

    oldSmallStep = smallStep + 1; // + 1 to swallow the separator
    smallStep += _MAX_REQUEST_LENGTH;
    if (smallStep > projectIDlist.length) smallStep = projectIDlist.length;
  }
}

function setProjectsCategories(api: ProjectsApi, projectIDlist: string, theProjects: any): void {
  if (projectIDlist !== "") {
    theProjects.nbRequests++;
    api
      .projectSetGetStatsProjectSetTaxoStatsGet(projectIDlist, "all")
      .then((data) => {
        // analyze the answer by going through the array items, and work with the map
        data.data.forEach(element => {
          const pid: number = element.projid;
          theProjects.nb_taxa.set(pid, theProjects.nb_taxa.get(pid) + 1);
        });
      })
      .catch((reason) => {
        // TODO : global error treatment      
        console.log(reason);
        alert(reason);
      })
      .finally(() => { theProjects.nbRequests--; })
  }
}
