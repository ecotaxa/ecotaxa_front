/*! For license information please see 64.70f49d73fe63585b7834.js.LICENSE.txt */
"use strict";(self.webpackChunk=self.webpackChunk||[]).push([[64],{8064:(e,n,t)=>{t.d(n,{exportCSV:()=>i});t(9162);const i=function(e,n={},t=!0){if(!e.grid.columns.length||!0===t&&!e.grid.data.length)return!1;function i(e){return null==e?null:((e=(e=(e=(e=(e=e.trim()).replace(/\s{2,}/g," ")).replace(/\n/g,"  ")).replace(/"/g,'""')).replace(/#/g,"%23")).includes(",")&&(e=`"${e}"`),e)}function l(e){return(e=e.join(n.columndelimiter)).trim()}n={download:!0,skipcolumns:[],linedelimiter:"\n",columndelimiter:",",...n};let d=[],o=[];const c=[],r=e.dom.querySelectorAll("thead th");e.grid.columns.forEach((e=>{if((!0===t||!e.hasOwnProperty("hidden"))&&(0===n.skipcolumns.length||n.skipcolumns.indexOf(e.index)<0)){const l={name:e.name?e.name:e.label?e.label:String(e.index),hidden:!!e.hasOwnProperty("hidden"),index:e.index};if((!0===t||!e.hidden)&&(0===n.skipcolumns.length||n.skipcolumns.indexOf(e.index)<0)){let n=r[e.index].dataset.name?r[e.index].dataset.name:r[e.index].textContent;n||(n="C"+e.index),o.push(i(n)),c.push(l)}}})),d.push(l(o));const s=e.dom.querySelectorAll("tbody tr");for(let c=0;c<s.length;c++){o=[];const r=s[c].querySelectorAll("th,td");e.grid.columns.forEach((l=>{const d=l.index;if((!0===t||!l.hidden)&&(0===n.skipcolumns.length||n.skipcolumns.indexOf(d)<0)){const n=l.hidden?e.grid.data[c][d]:r[d]?r[d].innerText:"None";o.push(i(n))}})),d.push(l(o))}const a=d.join(n.linedelimiter);return n.download&&(link=document.createElement("a"),link.href=encodeURI(`data:text/csv;charset=utf-8,${a}`),link.download=`${n.filename||"datatable_export"}.csv`,document.body.appendChild(link),link.click(),document.body.removeChild(link)),a}}}]);