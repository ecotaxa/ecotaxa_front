//
// Typescript interface for the Vuex store
// see https://next.vuex.vuejs.org/guide/typescript-support.html#typing-usestore-composition-function
//
//import { ComponentCustomProperties } from "vue";
import { Store } from "vuex";

declare module "@vue/runtime-core" {
  // declare your own store states
  export interface State {
    token: string | null;
  }

  // provide typings for `this.$store`
  export interface ComponentCustomProperties {
    $store: Store<State>;
  }
}
