# INSTALL the ".css reload" mechanism on a PC (Ubuntu)
### Please fix this doc when you use it and find improvements
##
## 1) N.B. The file ecotaxa_dev/appli/static/live.js is used (from ecotaxa_dev/appli/templates/layout_bs5.html)
### An updated version of live.js can be found here : https://livejs.com/live.js
## 2) N.B. The mechanism described in this document works *only* with Chrome (not Firefox, not yet tested on other browsers)
## 3) If not done install sass :
```
npm install -g sass
```
## 4) In ecotaxa_dev/appli/static/PrimeAndBootstrap5 folder, run :
```
sass --watch ecotaxa.scss:ecotaxa.css
```
### It will warn each time the ecotaxa.scss file is recompiled
## 5) Run the application :
### Each time ecotaxa.scss is modified, ecotaxa.css is regenerated and the styles will be automatically updated in your (Chrome) browser.
