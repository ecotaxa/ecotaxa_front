const _SLOT_FOR_PROJECTS:number = 1;
const _SLOT_FOR_PROJECTS_ERR_MSG: string = "You should change _SLOT_FOR_PROJECTS value";
import { ProjectsApi } from "../../gen";
import { ProjectModel } from "gen/api";

export function fillMenuWithUserProjects(items: any) {
  const api: ProjectsApi = new ProjectsApi();
  api
    .searchProjectsProjectsSearchGet(false, false, true)
    .then((data) => {
      // DO NOT remove the following protection (unless you find better)
      if (items[_SLOT_FOR_PROJECTS].label !== "Select Project")
        throw (_SLOT_FOR_PROJECTS_ERR_MSG);
  
      if (data.data !== undefined && data.data.length > 0) {
        const myitems: Array<{ label: string, visible: boolean, url: string, class:string }> = new Array<{ label: string, visible: boolean, url: string, class:string }>(data.data.length);
        for (let i = 0; i < data.data.length; i++) {
          const dataI:ProjectModel = data.data[i];
          if (dataI.projid !== undefined) {
            const val: string =
              "[" + dataI.projid.toString() + "] " + dataI.title;
            const val2: { label: string, visible: boolean, url: string, class:string } = {
              label: val,
              visible: true,
              url:
                "https://ecotaxa.obs-vlfr.fr" +
                "/prj/" +
                dataI.projid.toString(),
              class:"EcoTaxaProjectMenuItem", // TODO : this *must* be temporary to try the style
            };
            myitems[i] = val2;
          }
        }
        // TODO ! I don't like this _SLOT_FOR_PROJECTS, but lost too much time so far
        // (After a long long fight), it really seems I must propagate {{items}} towards this location,
        // otherwise it does not work.
        items[_SLOT_FOR_PROJECTS].items = myitems;
      }
    })
    .catch((reason) => {
      console.log(reason);
      //if (reason === _SLOT_FOR_PROJECTS_ERR_MSG)
        alert(reason);
    });
}

