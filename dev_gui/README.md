# ecotaxa_front
Frontend development of the EcoTaxa application
## install
 npm install  
## in [package.json](https://github.com/ecotaxa/ecotaxa_front/blob/master/dev_gui/package.json) add '-P pathto/ecotaxa_back' if ecotaxa_back local repo is not  ../ecotaxa_back
### default Interface
   ./run_ecotaxa.sh  ( - B docker to user docker ecotaxa_db , -P path/to/ecotaxa_back if ecotaxa_back local dev repo is not ../ecotaxa_back)  
### New interface (which is being deployed since 2023-Q4)  
  cd `ecotaxa_front/dev_gui`
#### DEVELOPMENT
  npm run dev
   - style.css , the bundle main.js --> appli/static/src/main.js (for dev js and css are included in js)  
#### PRODUCTION
npm run build
  - style.css , the bundle main.js --> appli/static/dist/css/main.[contenthash].css appli/static/dist/main.[contenthash].js
