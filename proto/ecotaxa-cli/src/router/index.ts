import {createRouter, createWebHistory, RouteRecordRaw} from "vue-router";
import Home from "../views/Home.vue";
import ProjectAbout from "@/components/ProjectAbout.vue";

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
        props: route => ({projectID: route.params["prj_id"]})
    },
    {
        path: "/about",
        name: "About",
        // route level code-splitting
        // this generates a separate chunk (about.[hash].js) for this route
        // which is lazy-loaded when the route is visited.
        component: () =>
            import(/* webpackChunkName: "about" */ "../views/About.vue"),
    },
    {
        path: '/:catchAll(.*)',
        component: {template: "Not found"},
        name: 'NotFound'
    }
];

const my_router = createRouter({
    history: createWebHistory(process.env.BASE_URL),
    routes,
});

export default my_router;
