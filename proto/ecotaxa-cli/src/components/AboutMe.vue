<template>
  <div id="mebox">Authentified API call: {{ to_show }}</div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { UsersApi } from "../../gen";
import { Configuration } from "../../gen";

export default defineComponent({
  // type inference enabled
  name: "AboutMe",
  data() {
    return {
      to_show: "unknown",
    };
  },
  created() {
    // eslint-disable-next-line no-unused-vars
    this.$store.subscribe((mutation, state) => {
      if (mutation.type === "settoken" && this.$store.state.token !== null) {
        // logged successfully
        const conf = new Configuration({
          accessToken: this.$store.state.token ?? "",
        });

        const api = new UsersApi(conf);
        api
          .showCurrentUserUsersMeGet()
          .then((data) => {
            const prjs = data.data.last_used_projects;
            this.to_show = prjs ? prjs.toString() : "no projects";
            this.to_show = JSON.stringify(data.data);

            console.log(data);
          })
          .catch(() => {
            this.to_show = "api pb";
          });
      }
    });
  },
});
</script>
