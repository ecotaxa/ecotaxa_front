<template>
  <div id="login">
    Status: {{ status }} Is logged: {{ is_logged }}
    <form @submit.prevent="login">
      <input v-model="username" placeholder="username" />
      <input v-model="password" placeholder="password" type="password" />
      <input type="submit" value="log in" />
    </form>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";

export default defineComponent({
  // type inference enabled
  name: "Login",
  data() {
    return {
      status: "",
      username: "",
      password: "",
    };
  },
  methods: {
    async login() {
      const { username, password } = this;
      await this.$store.dispatch("try_login", { username, password });
    },
  },

  computed: {
    is_logged() {
      // TODO: a getter
      return this.$store.state.token !== null;
    },
  },
});
</script>
