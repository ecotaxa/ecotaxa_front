<template>
  <div>
    This is About Project for {{ to_show }}
  </div>
</template>

<script lang="ts">
import {Prop} from "vue-property-decorator";
import {Options, Vue} from 'vue-class-component'

@Options({})
export default class ProjectAbout extends Vue {
  @Prop({default: '?'})
  projectID!: string
  // Class properties will be component data
  to_show = this.projectID;
}

</script>
