/*! For license information please see 912.433470a3c7336df2942f.js.LICENSE.txt */
"use strict";(self.webpackChunk=self.webpackChunk||[]).push([[912],{3438:(t,e,n)=>{n.a(t,(async(t,s)=>{try{n.d(e,{HK:()=>h,Pc:()=>d,gt:()=>l,v3:()=>u});var r=n(4860),i=n(7114),a=n(7104),o=n(2438),c=t([a,o]);[a,o]=c.then?(await c)():c;const l=Object.freeze({node:"N",branch:"B",root:"R",discard:"D",discarded:"X"}),d={selector:"[data-name]",tags:{tag:"ul",subtag:"li",label:"span"},selectors:{entries:".entries"},draggables:[],prefix:"entry",css:{on:"on",entryN:"entryN",entryB:"entryB",entryR:"entryR",entryD:"entryD",editable:"editable",dragging:"dragging",dragover:"dragover",dragitem:"dragitem",selected:"selected"},event:{name:"eventEntry"}};class h{eventnames={attach:"attach",control:"control"};name;type;label;entries=[];event={listener:window,name:d.event.name,init:{bubbles:!1,cancelable:!0}};constructor(t,e={}){return this.name=t.name,this.type=t.type,this.id=t.id,this.parent=t.parent,this.options={...d,...e},this.uuid=(0,r.UP)(),this.eventnames={...this.eventnames,...this.options.eventnames},this.label=e.label?e.label:null,this.event={name:d.event.name,listener:e.listener?e.listener:this.uuid},this.init(t),this}init(t){const e={name:this.name,type:this.type};null!==this.label&&(e.label=this.label);const n=(0,r.xJ)(this.options.tags.subtag,{draggable:this.isDraggable(),dataset:e}),s=`${this.options.prefix}${this.type}`;this.label=(0,r.xJ)(this.options.tags.label,{class:s,text:t.label?t.label:t.name},n),this.container=n,this.initEvents()}initEvents(){}getParent(){return this.parent}getLabelElement(){return this.label}getParentElement(){return this.container.parentElement.closest(this.options.selector)}getEntries(){return this.entries}getEntriesElement(t=!1){let e=this.container.querySelector(this.options.selectors.entries);return t&&null===e?(0,r.xJ)(this.options.tags.tag,{class:this.options.selectors.entries.substr(1)},this.container):e}appendEntry(t){if(t.parent&&t.parent.entries){const e=t.parent.entries.indexOf(t);delete t.parent.entries[e]}t.parent=this,this.entries.push(t);return this.getEntriesElement(!0).append(t.container),t}newEntry(t){return new h(t,this.options)}setAttributes(t){return t}extraStyles(t){}setDiscard(){}createEntry(t){this.options.css.icons=[],t=this.setAttributes(t),this.extraStyles(t);const e=this.newEntry(t,this.options);return this.appendEntry(e),e.addListeners(),e.setDiscard(),e}findEntry(t){const e=this.getEntries();for(const n of e)if(n.name===t)return n;return null}createListEntries(t){this.getEntriesElement(!0);t.forEach((t=>{t.forEach((t=>{this.createEntry(t)}))}))}removeEntries(){this.entries=[];const t=this.getEntriesElement();t&&t.remove()}isActive(){return this.active}toggleActive(){this.active=!this.active,this.container.classList.toggle(this.options.css.on)}setSelected(t=!0){const e=this.options.css.selected;!0===t?this.container.classList.add(e):this.container.classList.remove(e),this.setOn(t)}setOn(t=!0){this.active=t,!0===t?this.container.classList.add(this.options.css.on):this.container.classList.remove(this.options.css.on)}setOff(){this.setSelected(!1)}getListeners(){let t=[];let e=t=>{t.stopImmediatePropagation(),this.branchListener((()=>{this.emitEvent(this.eventnames.attach)}))};return[l.root,l.discard].indexOf(this.type)<0&&this.type===l.node&&(e=t=>{t.stopImmediatePropagation(),this.toggleActive(),this.emitEvent()}),t.unshift({name:"click",target:"label",func:e}),t}isBranch(t=!0){const e=[l.branch];return t&&e.indexOf(l.root)<0&&e.push(l.root),e.indexOf(this.type)>=0}isDiscarded(){return[l.discard,l.discarded].indexOf(this.type)>=0}emitEvent(t=null,e=null){const n={entry:this};t&&(n.action=t),e?n.event=e:e=this.eventnames.control,o.j.emit(this.event.name,n,this.event.listener)}moveHandlers(){return[{name:"dragstart",func:t=>{this.handleDragStart(t)}},{name:"dragend",func:t=>{this.handleDragEnd(t)}}]}dropHandlers(){return[{name:"dragover",func:t=>{this.handleDragOver(t)}},{name:"drop",func:t=>{this.handleDrop(t)}}]}branchListener(t=null){this.toggleActive(),this.isActive()&&this.branchActivate(t).then((()=>{this.emitEvent()}))}addListeners(){const t=this.getListeners();for(const e of t){("label"===e.target?this.getLabelElement():this.container).addEventListener(e.name,e.func)}}removeListeners(t){for(const e in t){("label"===e.target?this.getLabelElement():this.container).removeEventListener(e.label,e.func)}}destroy(){this.container.remove()}handleDragStart(t){t.stopImmediatePropagation(),this.container.classList.add(this.options.css.dragging),t.dataTransfer.effectAllowed="move",this.emitEvent("dragstart",t)}handleDragOver(t){t.stopPropagation(),t.preventDefault(),this.emitEvent("dragover",t)}handleDragEnd(t){t.stopPropagation(),t.preventDefault(),this.container.classList.remove(this.options.css.dragging),this.emitEvent("dragend",t)}resetDragOver(){document.querySelectorAll("."+this.options.css.dragover).forEach((t=>{t.classList.remove(this.options.css.dragover)}))}handleDrop(t){t.stopImmediatePropagation(),this.emitEvent("drop",t)}setWait(){this.loaded=this.container.dataset.loaded=!1,this.container.classList.add(i.AH.wait)}setLoaded(){this.container.classList.remove(i.AH.wait),this.loaded=this.container.dataset.loaded=!0}findEntry(t,e){const n=this.getEntries();for(const s of n)if(s.name===t&&s.type===e)return s;return null}async branchActivate(t=null){this.loaded?t&&t(this):this.list().then((()=>{t&&t(this)}))}getCurrentPath(){const t=(e,n=[])=>e.name&&(n.push(e.name),null!==(e=e.getParent()))?t(e,n):n;let e=t(this);return e.length>1&&(e=e.reverse()),e}async jsonEntries(t){return await t.json()}isDraggable(){return this.options.draggables&&this.options.draggables.indexOf(this.type)>=0}async list(){if(this.type===l.node)return;const t=this.getUrl?this.getUrl():null;if(null===t)return;this.options.tags.tag,this.options.tags.subtag;this.setWait(),this.removeEntries();const e={headers:new Headers({"content-type":"application/json"})},n=await fetch(t,(0,r.Uc)(e));if(n.ok){const t=await this.jsonEntries(n);if(t.length){let e=[],n=[];for(;t.length>0;){const s=t.shift();!1===s.children?e.push(s):n.push(s)}e.sort(((t,e)=>t.name<e.name)),n.sort(((t,e)=>t.name<e.name)),this.createListEntries([n,e])}this.setLoaded()}else a.y.addMessage({parent:this.container,type:"error",content:n.error+" "+n.text})}moveTo(t){const e=t.getCurrentPath(),n=t.type===l.discard?l.discarded:t.type;e.pop(),e.forEach(((e,s)=>{let r=t.findEntry(e,n);null===r&&(r=t.createEntry({type:n,name:e})),t=r})),null===t.findEntry(this.name,this.type)&&(this.from=this.parent,t.appendEntry(this))}unMove(){this.from&&(this.moveTo(this.from),this.from=null)}}function u(t=document,e={}){let n,s=null;function a(t,e=null,i=null){const a=(0,r.xJ)("span",{}),o=n.children.length;if(null===e||o<e+1?n.append(a):0===e||0===o?n.prepend(a):n.inserBefore(crtl,n.children[e]),t.typentries&&(a.dataset.typentries=t.typentries),t.icon){(0,r.xJ)("i",{class:["icon",t.icon]},a);a.dataset.title=t.text}else a.textContent=t.text;const c=t.trigger?t.trigger:"click";a.addEventListener(c,(e=>{if(null===s)return;const n={callback:()=>{console.log("done",t.action)}};s[t.action]||null===i?s[t.action]&&s[t.action](n):i(s),t.callback&&t.callback(e)})),t.ctrl=a}function o(){null!==s&&(s.container.classList.remove(e.selectors.hascontrols.substr(1)),n.classList.add(i.AH.hide),n.disabled=!0,t.append(n),s=null)}function c(t,e=!1){const n=t.ctrl,r=n.dataset.typentries?n.dataset.typentries.split(","):[],a=e?l.discarded:s.container.dataset.type;r.indexOf(a)>=0?n.classList.remove(i.AH.hide):n.classList.add(i.AH.hide)}function d(){if(null===s)return;const t=s.isDiscarded();Object.values(e.controls).filter((t=>t.icon||t.text)).forEach((e=>{c(e,t)}))}return e=Object.assign({selectors:{typentries:"[data-typentries]",hascontrols:".has-controls"},controls:{list:{action:"list",typentries:["B","T"]}},css:{entrycontrols:"entrycontrols",entries:".entries"}},e),n=(0,r.xJ)("div",{class:[e.css.entrycontrols,i.AH.hide]}),Object.values(e.controls).filter((t=>t.icon||t.text)).forEach((t=>{a(t)})),{options:e,addControl:a,attachControls:function(t){o(),s=t,s.container.prepend(n),s.container.classList.add(e.selectors.hascontrols.substr(1)),d(),n.classList.remove(i.AH.hide),delete n.disabled},detachControls:o,showControls:function(t=!0){!0===t?n.classList.remove(i.AH.hide):n.classList.add(i.AH.hide),n.disabled=!t},activateControls:d,activateControl:c}}s()}catch(p){s(p)}}))},8912:(t,e,n)=>{n.a(t,(async(t,s)=>{try{n.d(e,{JsTree:()=>d});var r=n(4860),i=(n(7114),n(2438)),a=n(3438),o=t([i,a]);[i,a]=o.then?(await o)():o;const c={api_parameters:{entry:"entry",rootname:""},url:"/gui/search/taxotreejson",trigger:null,entry:{root:"#",draggable:!1,tags:{tag:"ul",subtag:"li",label:"span"},event:{name:"eventEntry"}},entrycontrols:{controls:{select:{action:"select",text:"select entry",icon:"icon-check",typentries:[a.gt.branch,a.gt.node]}}},droptarget:"droptarget",tree:"taxotree"};function l(t,e){const n=new a.HK(t,e);return n.eventnames={attach:"attach",detach:"detach",select:"select"},n.newEntry=function(t){return l(t,this.options)},n.select=function(){this.emitEvent(this.eventnames.select)},n.getUrl=function(){return this.options.url+"?"+new URLSearchParams({id:this.id})},n.setAttributes=function(t){return t.type=t.type?t.type:!0===t.children?a.gt.branch:a.gt.node,t.data={parent:t.parent},t.parent=this,t},n}function d(t,e={}){(t=t instanceof HTMLElement?t:document.querySelector(t)).innerHTML="",e={...c,...e};const n=(0,r.UP)();if(!t||null!==t.querySelector("."+e.tree))return;e.entry={...a.Pc,...e.entry},e.entry.url=e.url,e.entry.root=e.root?e.root:"#";const s="attach",o="detach",d="action";let h=null;e.selectors&&(h=JSON.parse(e.selectors),delete e.selectors),h&&(e.selectors=h),e.entry.draggable=!1;const u=(0,r.xJ)(e.entry.tags.tag,{class:e.tree},t);let p,g,y,m=null;function f(t){m&&m.attachControls(t),g=t,i.j.emit(s,{entry:g},e.listener)}function v(){const t=g&&g.parent?g.parent:p;m&&m.attachControls(t),i.j.emit(o,{entry:g},e.listener),g=t}return function(){const t=a.gt.root,s={};m=null===m?(0,a.v3)(u,e.entrycontrols):null,Object.entries(e.entrycontrols.controls).forEach((([t,e])=>{s[t]=e.action})),e.entry.actions=s,e.entry.listener=n,i.j.on(e.entry.event.name,(t=>{const s=t.entry.eventnames;let r,a;switch(t.action){case s.attach:f(t.entry);break;case"dragstart":r=a=t.entry,t.entry.container.classList.add(t.entry.options.css.dragging),v();break;case"dragover":if(!r)return;y!==t.entry.container&&(y&&y.classList.remove(t.entry.options.css.dragover),t.entry.container.classList.add(t.entry.options.css.dragover),y=t.entry.container);break;case"dragend":r=null,y&&y.classList.remove(t.entry.options.css.dragover),y=null;break;case"drop":if(!r)return i.j.emit(d,t,n),!0;r.container;const o=t.entry;if(o.resetDragOver(),null!==r)if(r.options.actions.move)try{r.move(o),[r.options.type.trashed].indexOf(o.type)>=0&&f(o)}catch(t){console.log("errordrop ",t),r.unMove()}else console.log("noactionon drop");else console.log(" parent===null or dragitem===null or dragitem===parent",r);break;case s.select:if(e.actions&&e.actions.select)e.actions.select(entry);else{const n=e.droptarget?document.getElementById(e.droptarget):null;if(n){if(n.tomselect){const e=n.tomselect;let s=e.getOption(t.entry.id);s||(s={},s[e.settings.valueField]=t.entry.id,s[e.settings.searchField]=t.entry.name,e.addOption(s)),e.addItem(t.entry.id)}else switch(n.tagName.toLowerCase()){case"input":case"textarea":n.value=t.entry.id;break;default:n.textContent=t.entry.id}e.trigger&&e.trigger.click()}else console.log("no-target")}break;default:t.entry.active?f(t.entry):f(p)}}),n),p=l({type:t,name:"",id:e.entry.root,label:e.api_parameters.rootname},e.entry),p.addListeners(),p.label.click()}(),u.append(p.container),{uuid:n,getActiventry:function(){return g},setActiventry:function(t=null){g=t},entrycontrols:m,attachControls:f,detachControls:v}}s()}catch(h){s(h)}}))},2438:(t,e,n)=>{n.a(t,(async(t,s)=>{try{n.d(e,{j:()=>o});var r=n(7104),i=(n(4860),t([r]));function a(t,e){const n=[],s="ALL_EVENTS";function r(t,e,r=s){n[r]=n[r]||[],n[r][t]=n[r][t]||[],n[r][t].push(e)}return{on:r,once:function(t,e,n=s){e.once=!0,r(t,e,n)},off:function(t,e,r=s){t in n[r]!=!1&&n[r][t].splice(n[r][t].indexOf(e),1)},emit:function(t,e={},r=s){if(n[r]=n[r]||[],t in n[r]!=!1)for(const s of n[r][t])if(s(e),s.once)break}}}r=(i.then?(await i)():i)[0];const o=await a(),c={error:"error"};o.on(c.error,(t=>{r.y.renderAlert({type:r.y.alertconfig.types.error,content:t,inverse:!0,dismissible:!0})})),s()}catch(l){s(l)}}),1)}}]);