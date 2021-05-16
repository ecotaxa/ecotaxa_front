import { InjectionKey } from "vue";
import { createStore, Store, useStore } from "vuex";
import { AuthentificationApi } from "../../gen/api";

// define the typings for the store state
export interface State {
  // the login token or nothing
  token: string | null;
}

// define injection key
export const key: InjectionKey<Store<State>> = Symbol();

export const store = createStore<State>({
  state: {
    // the JWT token retrieved by login API call
    token: null,
  },
  mutations: {
    settoken(state, token: string) {
      state.token = token;
    },
  },
  actions: {
    try_login(context, creds) {
      var api = new AuthentificationApi();
      const req = { username: creds.username, password: creds.password };
      api
        .loginLoginPost(req)
        .then((data) => {
          context.commit("settoken", data.data.toString());
          console.log(data);
        })
        .catch(() => {});
    },
  },
});

// Re-export for single-line import to our store
export { useStore };
