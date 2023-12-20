# ecotaxa_front
Frontend development of the EcoTaxa application
## install
 npm install  
##  [webpack.config.js](https://github.com/ecotaxa/ecotaxa_front/blob/master/dev_gui/webpack.config.js)
replace the dirRoot path by the path of 
## in [package.json](https://github.com/ecotaxa/ecotaxa_front/blob/master/dev_gui/package.json) replace path in "watchstartfront" script
 - cd `ecotaxa_front/dev_gui`
 - use `npm run watchstartfront` enable to launch DB, ecotaxa_back and ecotaxa_front
 - or `npm run watchstarttest` to dev in the new (which is being deployed since 2023-Q4) interface
## generated and modified files are copied by webpack to ecotaxa /appli
 - style.css , the bundle main.js --> appli/static/css and appli/static/js
 - py files from src/gui  --> appli/gui
 - images from src/gui/images --> appli/static/images
 - templates from src/templates/v2   --> appli/templates/v2
