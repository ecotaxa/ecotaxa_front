# ecotaxa_front
Frontend development of the EcoTaxa application
## install
 npm install  
## webpack.config.js
replace the dirRoot path by the path of ecotaxa front dev dir
## in package json replace path in "watchstartfront" script
 and use npm run watchstartfront  
 or npm run watch  if the dev starts otherwise
## generated and modified files are copied by webpack to ecotaxa /appli
 - style.css , the bundle main.js --> appli/static/css and appli/static/js
 - py files from src/gui  --> appli/gui
 - images from src/gui/images --> appli/static/images
 - templates from src/templates/v2   --> appli/templates/v2
