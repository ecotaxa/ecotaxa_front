/*! For license information please see 179.c905d041e0c7d411dec0.js.LICENSE.txt */
"use strict";(self.webpackChunk=self.webpackChunk||[]).push([[179],{6179:(e,t,s)=>{s.d(t,{JsFilesStore:()=>a});s(4860);class a{name="filesstore";store;writestream;_events={};eventnames={added:"item.added",found:"item.found",notfound:"item.notfound"};constructor(e=null,t=null,s={}){this.name=e||this.name,this.init(s)}async init(e){if(navigator.storage&&navigator.storage.estimate){const e=await navigator.storage.estimate(),t=e.usage/e.quota*100;console.log(`You've used ${t}% of the available storage.`);const s=e.quota-e.usage;console.log(`You can write up to ${s} more bytes.`),console.log("quota",e)}}async addItem(e){return!0}async getItem(e){return!0}async getFile(){return this.store.getFile()}async addItems(e){Array.isArray(e)&&e.forEach((async e=>!0))}async getItems(e=null,t=null,s=!0,a=null){if(Array.isArray(t)){if(null===e&&null===t)return!0;if(null!==t){const t=[];return null!==e?t.filter((t=>t.source===e)):t}return[]}}async updateItem(e,t){return!!this.getItem(t.uuid)&&await this.addItem(t)}async closeStream(){const e=await this.getFile();console.log(e)}}}}]);