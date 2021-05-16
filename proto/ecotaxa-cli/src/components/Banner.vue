<template>
  <div id="banner">Public API call: {{ to_show }}</div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { MiscApi } from "../../gen";

export default defineComponent({
  // type inference enabled
  name: "Banner",
  data() {
    return {
      to_show: "????xx",
    };
  },
  mounted() {
    const api = new MiscApi();
    api
      .usedConstantsConstantsGet()
      .then((data) => {
        const mgr = data.data.app_manager;
        this.to_show = mgr ? mgr.toString() : "no manager";
      })
      .catch(() => {
        this.to_show = "problème";
      });
  },
});
</script>
