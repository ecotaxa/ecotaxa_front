import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router";
import Home from "../components/Home.vue";
import ProjectAbout from "@/components/ProjectAbout.vue";
import Projects from "@/components/Projects.vue";

const routes: Array<RouteRecordRaw> = [
  {
    path: "/",
    name: "Home",
    component: Home,
  },
  {
    path: "/prj_about/:prj_id",
    name: "ProjectAbout",
    component: ProjectAbout,
    props: (route) => ({ projectID: route.params["prj_id"] }),
  },
  {
    path: "/projects",
    name: "Projects",
    component: Projects,    
  },
  {
    path: "/:catchAll(.*)",
    component: { template: "Not found" },
    name: "NotFound",
  },
];

const my_router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default my_router;
