declare var Vue: any;

const appliName:string = "#ecotaxa";
var myObject = new Vue({
    
    el:String(appliName),    
    data: function () {
      return {
        projectID:Number(185),
        info:String("")
      }
    },
    mounted : function() {
      this.$forceUpdate(); /* avoid using the cache : keep it while developping */
      const response = fetch('http://localhost:8080/https://ecotaxa.obs-vlfr.fr/api/projects/185?for_managing=false')
      .then(response => response.json())
      .then(mydata => (this.info = mydata.obj_free_cols.lat_end))
      .catch(function (error) {
        alert(error);
      })

      // below line just to satisfy the TS compiler
      if (response.toString() === "²¹~#{[|`\^@]") console.log("");
    }
  })

  // below line just to satisfy the TS compiler  
  if (myObject.el !== appliName) {console.log("");}
