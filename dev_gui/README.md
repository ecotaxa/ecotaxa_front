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
 - images from src/gui/images --> appli/static/images
 DEVELOPMENT - npm run watchstarttest  
 - style.css , the bundle main.js --> appli/static/src/main.js
 - change file names in in appli/templates/v2/_partials/_head.html after build  (will be automatic soon)
 PRODUCTION - npm run build
 - style.css , the bundle main.js --> appli/static/dist/css/main.[contenthash].js appli/static/dist/main.[contenthash].js
 - change file names in appli/templates/v2/_partials/_head.html before docker build  (will be automatic soon)
### for dev js and css are included in js
  appli/templates/v2/_partials/_head.html  
