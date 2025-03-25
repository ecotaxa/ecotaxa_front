/*! For license information please see 89.ddd5690eeaa80d575f69.js.LICENSE.txt */
(self.webpackChunk=self.webpackChunk||[]).push([[89],{2438:(t,e,s)=>{"use strict";s.a(t,(async(t,i)=>{try{s.d(e,{j:()=>l});var a=s(7104),n=(s(4860),t([a]));function r(t,e){const s=[],i="ALL_EVENTS";function a(t,e,a=i){s[a]=s[a]||[],s[a][t]=s[a][t]||[],s[a][t].push(e)}return{on:a,once:function(t,e,s=i){e.once=!0,a(t,e,s)},off:function(t,e,a=i){t in s[a]!=!1&&s[a][t].splice(s[a][t].indexOf(e),1)},emit:function(t,e={},a=i){if(s[a]=s[a]||[],t in s[a]!=!1)for(const i of s[a][t])if(i(e),i.once)break}}}a=(n.then?(await n)():n)[0];const l=await r(),o={error:"error"};l.on(o.error,(t=>{a.y.renderAlert({type:a.y.alertconfig.types.error,content:t,inverse:!0,dismissible:!0})})),i()}catch(d){i(d)}}),1)},2634:()=>{},5930:(t,e,s)=>{"use strict";!function(){const t=CSS.highlights?new Highlight:null}()},9780:(t,e,s)=>{"use strict";s.a(t,(async(t,i)=>{try{s.d(e,{TableComponent:()=>v});var a=s(9418),n=s(4982),r=s.n(n),l=s(4860),o=s(2438),d=(s(5930),s(7334)),c=s.n(d),h=s(7114),u=t([o]);o=(u.then?(await u)():u)[0];let p=[];const m={collectionlist:"/gui/collectionlist/",prjlist:"/gui/prjlist/",prjsamplestats:"/gui/prjsamplestats",userslist:"/gui/admin/userslist/",guestslist:"/gui/guestslist/",organizationslist:"/gui/organizationslist/",prjpredict:"/gui/prjsforprediction/"},g={showfull:"showfull",tipinline:"tip-inline",searchresults:"search-results",selectaction:"selectaction",absinput:"absinput",disabled:"table-disabled",ascending:"table-ascending",descending:"table-descending",tipover:"tipover absolute z-10 text-stone-50 rounded-sm bg-stone-600 px-2 py-0.5 -mt-5 ml-12 ",hide:"hide",nowrap:"truncate",buttonexpand:"button-expand",bordert:"border-t",borderb:"border-b",maxtabstath:"max-tabstat-h",overflowyhidden:"overflow-y-hidden",icochevrondown:"icon-chevron-down",iconchevronup:"icon-chevron-up",pointer:"cursor-pointer",hidden:"hidden"},b={table:".table-table",wrapper:".table-wrapper",top:".table-top",input:".table-input",search:".table-search",export:".button-export",filters:".table-filters",sorter:".table-sorter",details:'details[data-what="about"]',tip:"."+h.AH.component.table.tip,tipover:".tipover",wait:"wait-please",sorton:".sorton"};Object.freeze(g),Object.freeze(b);const f="#NOTFOUND#";class v{uuid=null;grid={columns:[],active:[],hidden:[],data:[]};domdef={columns:[],data:[]};wrapper=null;dom=null;params=null;_events={};eventnames={init:"table.init",update:"table.update",refresh:"table.refresh",resize:"table.resize",search:"table.search",searchend:"table.searchend",sorting:"table.sorting",sorted:"table.sorted",load:"table.loaded",dismiss:"table.dismiss"};labels={placeholder:"Search...",perPage:"{select} entries per page",noRows:"No entries found",info:"Showing {start} to {end} of {rows} entries",noResults:"No result match your search query"};cellidname="id";searching=!1;sorting=!1;initialized=!1;plugins={};constructor(t,e={}){if(t&&(t=t instanceof HTMLElement?t:document.querySelector(t)))return this.uuid=t.dataset.uuid?t.dataset.uuid:(0,l.UP)(),p[this.uuid]&&r()(t.dataset,p[this.uuid].params)?this.refresh():this.init(t),p[this.uuid]}init(t){this.params=t.dataset;let e=t.querySelector("table");e||(e=document.createElement("table"),t.appendChild(e)),e.id="table-"+t.id,e.classList.add(b.table.substr(1)),this.dom=e;let s={nodename:"DIV",attributes:{class:b.top.substr(1)}},i=this.objToElement({nodename:"DIV",attributes:{class:b.wrapper.substr(1)},childnodes:[s]});t.appendChild(i),i.appendChild(e),this.wrapper=i,this.labels=this.params.labels?this.params.labels:this.labels,this.cellidname=this.params.hasOwnProperty("cellid")?this.params.cellid:this.cellidname,this.params.from=this.params.from?a.A.sanitize(this.params.from):null;const n=this.params.from&&Object.keys(m).indexOf(this.params.from)>=0?m[this.params.from]:null;this.dom.classList.add(h.AH.hide),n?this.params.defer?this.deferLoad(t,n):this.fetchData(t,n):this.tableActivate(t),this.dt=Date.now()}waitActivate(t){let e=t.querySelector("#"+b.wait);e||(e=document.createElement("div"),e.id=b.wait,t.append(e)),this.waitdiv=e}waitDeactivate(t=null,e="info"){this.waitdiv&&(t?(this.waitdiv.classList.remove(h.AH.hide),null===e&&(this.waitdiv.innerHTML=`${t}`),this.waitdiv.innerHTML=`<div class="alert is-${e}">${t}</div>`):this.waitdiv.classList.add(h.AH.hide))}deferLoad(t,e){const s=t.querySelector(this.params.defer);s&&s.addEventListener("click",(i=>{this.fetchData(t,e),s.remove()}))}fetchData(t,e,s=0){this.waitActivate(t);const i=this.params.pagesize?this.params.pagesize:0;let n=e;this.params.fromid&&(n+="/"+this.params.fromid);let r=this.params.import?{typeimport:a.A.sanitize(this.params.import),gz:!0}:{};i&&(r.window_start=s,r.window_size=i),this.params.listall&&(r.listall=this.params.listall);const o=new URLSearchParams(window.location.search),d=this.cellidname+"s";if(d.length)for(const t of o.entries())d.indexOf(t[0])>=0&&(r[t[0]]=t[1]);Object.keys(r).length&&(n+="?"+new URLSearchParams(r)),this.dt=Date.now(),fetch(n,(0,l.Uc)()).then((t=>t.ok?t.json():Promise.reject(t))).then((async n=>{if(this.waitdiv&&(this.waitdiv.innerHTML=this.waitdiv.dataset.loaded?a.A.sanitize(this.waitdiv.dataset.loaded):h.lr.dataloaded),s>0&&(n.data.length?this.domInsertRows(n):i=0),0===i){let e=Date.now();console.log("seconds to fetch ",(Date.now()-this.dt)/1e3),this.dt=e,n.data.length||s>0?await this.tableActivate(t,n):this.waitDeactivate("no result","default"),e=Date.now(),console.log("plugins loaded",(Date.now()-this.dt)/1e3),this.dt=e}else this.fetchData(t,e,s+i)})).catch((t=>{console.log("error",t),this.waitDeactivate(t.status+" "+t.statusText,"error")}))}async dataToTable(t){if(t.data&&t.columns){let e;await this.convertColumns(t);let s=this.dom.tHead;s?s.querySelector("tr")?(e=s.querySelector("tr"),e.innerHTML=""):e=document.createElement("tr"):(s=document.createElement("thead"),e=document.createElement("tr"),this.dom.appendChild(s));let i=this.dom.tBodies.length?this.dom.tBodies[0]:null;i||(i=document.createElement("tbody"),this.dom.appendChild(i));const n=!t.hasOwnProperty("data")||t.hasOwnProperty("type")&&"json"===t.type;this.grid.columns.forEach(((t,s)=>{if(t.hidden)this.grid.hidden.push(s);else{const i=document.createElement("th");i.innerHTML=a.A.sanitize(t.label),t.sort&&(i.dataset.sort=t.sort),t.format&&(i.dataset.type=t.type),t.name&&(i.dataset.name=t.name),this.params.import&&["selectcells","what","autocomplete","parts","value"].forEach((e=>{t.hasOwnProperty(e)&&(i.dataset[e]=t[e])})),i.dataset.sortable=!!t.sortable,e.appendChild(i),this.grid.active.push(s)}})),s.appendChild(e);this.params.lastused&&this.params.lastused.length;n?(this.grid.data=[],t.data.forEach(((e,s)=>{const i=[];let a=0;Object.entries(t.columns).forEach((([t,s],n)=>{s.hasOwnProperty("emptydata")||(e.hasOwnProperty(t)?i[a]=e[t]:s.field&&e.hasOwnProperty(s.field)?i[a]=e[s.field]:i[a]=null,a++)})),this.grid.data.push(i)}))):this.grid.data=t.data;const r=this.dom.tFoot;if(0===this.grid.active.length)return i.innerHTML=`<tr><td>${this.labels.noRows}</td</tr>`,void(r&&r.remove());if(r&&r.querySelector("tr")){const t=r.querySelector("tr").childNodes;this.grid.hidden.forEach((e=>{t[e].remove()}))}this.renderTbody(i)}}tableToData(){if(!this.dom.querySelector("thead"))return void this.dom.classList.remove(h.AH.hide);this.params.lastused&&this.params.lastused.length;this.dom.classList.add(h.AH.hide);const t=this.dom.querySelectorAll("thead tr th").length?this.dom.querySelectorAll("thead tr th"):this.dom.querySelectorAll("thead tr td"),e=this.dom.querySelectorAll("tbody tr");function s(t){return t.childNodes.length?s(t.childNodes[0]):t.innerText}t.forEach(((t,e)=>{const i=Object.assign({},t.dataset);i.mask&&t.classList.add(g.hidden),i.hidden&&(0,l.FB)(i.hidden)&&(i.hidden=!0,t.remove()),i.label=s(t),i.type&&(i.format=i.type,delete i.type),i.index=e,i.hidden?this.grid.hidden.push(e):this.grid.active.push(e),this.grid.columns.push(i)}));const i=this.getCellId(this.cellidname);e.forEach(((t,e)=>{i<0?t.dataset[this.cellidname]=e:e===i&&(t.dataset[this.cellidname]=this.getCellData(e,this.cellidname,i));const s=[];t.querySelectorAll("th,td").forEach(((t,e)=>{this.grid.columns[e].hasOwnProperty("mask")&&t.classList.add(g.hidden),this.grid.hidden.indexOf(e)>=0&&t.remove(),s.push(t.innerText)})),this.grid.data.push(s)})),this.dom.querySelectorAll("tfoot tr th").forEach(((t,e)=>{this.grid.columns[e].hasOwnProperty("mask")&&t.classList.add(g.hidden),this.grid.hidden.indexOf(e)>=0&&t.remove()})),this.dom.classList.remove(h.AH.hide)}renderTbody(t){const e=this.grid.data.length;for(let s=0;s<e;s++){const e=this.createTableRow(this.grid.data[s],s);t.append(e)}}async tableActivate(t,e=null){o.j.once(this.eventnames.load,(()=>{this.initPlugins(t),this.initSearch(),this.initSort(),this.waitDeactivate(),this.dom.classList.remove(h.AH.hide),this.afterLoad&&this.afterLoad(),t.dataset.table=this.params.table=!0,this.initialized=!0}),this.uuid),o.j.once(this.eventnames.dismiss,(t=>{this.destroy()}),this.uuid),e?e=await this.dataToTable(e):await this.tableToData(),this.grid.data.length&&o.j.emit(this.eventnames.load,{},this.uuid),p[this.uuid]=!0}tableAppendRows(t){console.log("rows")}destroy(){this.dataImport&&(this.dataImport=null),this.dom=null,delete p[this.uuid]}refresh(t){this.dataImport&&this.dataImport.resetSelectors()}labelFormatter(t){let e="";return["number","progress","decimal"].find((e=>e===t.format))&&(e=h.AH.right),t.subfield?`${t.label} <span class="sublabel">${t.sublabel}</span>`:t.label?`<span class="${e}">${t.label}</span>`:""}getCellId(t){let e=this.grid.columns.filter((e=>e.name===t));return e.length?e[0].index:-1}getCellData(t,e,s=null){return(s=null===s?this.getCellId(e):s)<0?null:this.grid.data.length&&this.grid.data[t]?this.grid.data[t][s]:null}rowAttributes(t,e){const s=this.getCellData(e,this.cellidname);return t.dataset[this.cellidname]=s,this.setRowAttributes&&(t=this.setRowAttributes(this,t,s)),t}createTableRow(t,e,s=!1){const i=document.createElement("tr");let a;return this.grid.columns.forEach((n=>{if(n.hasOwnProperty("hidden")&&!0===n.hidden)return;const r=t[n.index];n.hasOwnProperty("render")?(a=n.render(r,e,n.index),a.nodename=s?"TH":"TD",a=this.objToElement(a)):(a=s?document.createElement("th"):document.createElement("td"),a.appendChild(document.createTextNode(r))),i.appendChild(a)})),this.rowAttributes(i,e)}objToElement(t){if("#text"===t.nodename)return document.createTextNode(t.data);const e=document.createElement(t.nodename);if(t.hasOwnProperty("html")?e.innerHTML=t.html:e.textContent=t.data,t.hasOwnProperty("attributes"))for(const s in t.attributes)e.setAttribute(s,t.attributes[s]);return t.hasOwnProperty("childnodes")&&t.childnodes.forEach((t=>{e.appendChild(this.objToElement(t))})),e}setTextNode(t){return{nodename:"#text",data:t}}async getFormatters(){let t={controls:(t,e,s,i={})=>{const a=this.grid.columns[s],n=this.getCellData(e,a.field),r=a.actions?a.actions:null;if(!r)return"";let l=[];return Object.entries(r).forEach((([t,e])=>{l.push({nodename:"A",attributes:{class:`btn is-${t} `,href:`${e.link}${n}`},childnodes:[this.setTextNode(e.label)]})})),i.hasOwnProperty("attributes")||(i.attributes={}),i.attributes.class=h.AH.component.table.controls,i.childnodes=l,i},select:(t,e,s,i={})=>{const a=this.grid.columns[s];return t=isNaN(t)?this.getCellData(e,a.field):t,i.childnodes=[{nodename:"INPUT",attributes:{type:"radio",name:`${this.uuid}select`,value:String(t)}}],i},selectmultiple:(t,e,s,i={})=>{const a=this.grid.columns[s];return t=isNaN(t)&&a.hasOwnProperty("field")?this.getCellData(e,a.field):t,i.childnodes=[{nodename:"INPUT",attributes:{type:"checkbox",name:`${this.uuid}select[]`,value:String(t)}}],i},decimal:(t,e,s,i={})=>(isNaN(t)&&(t=0),(t=parseFloat(t).toFixed(2))-parseInt(t)==0&&(t=parseInt(t)),i.hasOwnProperty("attributes")||(i.attributes={}),i.attributes.class=h.AH.number,i.childnodes=[this.setTextNode(t)],i),number:(t,e,s,i={})=>(isNaN(t)&&(t=0),i.hasOwnProperty("attributes")||(i.attributes={}),i.attributes.class=h.AH.number,i.childnodes=[this.setTextNode(t)],i),check:(t,e,s,i={})=>{switch(isNaN(t)&&(t=""),t){case!0:case"Y":case 1:t="";break;default:t="no-"}const a={nodename:"I",attributes:{class:`icon-sm  icon-${t}check `},childnodes:[]},n=this.grid.columns[s],r=this.getCellData(e,this.cellidname);return n.hasOwnProperty("toggle")?i.childnodes=[{nodename:"A",attributes:{"data-request":"toggle","data-action":`${n.toggle.link}/${r}`,href:"javascript:void()"},childnodes:[a]}]:i.childnodes=[a],i},text:(t,e,s,i={})=>(null===t?i.childnodes=[]:(t=t.replaceAll("\r\n",", "),i.childnodes=""!==t?[{nodename:"DIV",attributes:{class:h.AH.component.table.tip},childnodes:[this.setTextNode(t)]}]:[]),i),default:(t,e,s,i={})=>(i.childnodes=null===t||""===t?[]:[this.setTextNode(t)],i)},e=null;switch(this.params.from){case"collectionlist":e=await s.e(243).then(s.bind(s,243)),this.cellidname=h.Jn.id;break;case"prjlist":e=await s.e(942).then(s.bind(s,8942)),this.cellidname=h.Jn.projid;break;case"prjsamplestats":e=await s.e(853).then(s.bind(s,8853)),this.cellidname=h.Jn.sampleid;break;case"prjpredict":e=await s.e(702).then(s.bind(s,9702)),this.cellidname=h.Jn.projid}return e?{...t,...e.default(this)}:t}async convertColumns(t){const e=t.columns?t.columns:this.params.columns?JSON.parse(this.params.columns):null;if(!e)return;const s=await this.getFormatters(),i=[];Object.entries(t.columns).forEach((([t,e])=>{e.hasOwnProperty("emptydata")||i.push(t)}));const a=(t,e,a)=>{if(!e)return{index:a,name:t,hidden:!0};let n={index:a,name:t,label:this.labelFormatter(e),sortable:!0};n.index=e.hasOwnProperty("emptydata")?i.indexOf(e.emptydata):i.indexOf(t),e.notsortable?n.sortable=!1:e.sortable&&(n.sort=n.sortable),n.searchable=!n.notsearchable,e.hidden&&(n.hidden=(0,l.FB)(e.hidden)),["number","decimal"].find((t=>t===e.format))&&(n.type="number");if("select"===t){(e.select&&"controls"==e.select?"controls":e.selectcells?"imports":e.select)&&(n={...e,...n},n.sortable=n.searchable=!1)}if(!e.hasOwnProperty("hidden")){const t=e.select&&e.select==h.Jn.controls?h.Jn.controls:e.selectcells?h.Jn.imports:e.select,i=e.format?e.format:e.subfield?e.subfield:t||"default";s&&s[i]&&(n.render=s[i])}return n};this.grid.columns=Object.entries(e).map((([t,e],s)=>a(t,e,s)))}initEvents(){o.j.on(this.eventnames.update,(()=>{this.dom.classList.remove(h.AH.hide)}),this.uuid)}initPlugins(t){if(this.grid.data.length){if(this.params.import&&this.initImport&&this.initImport(this),this.params.expand&&this.makeExpandable(t),this.params.export&&this.makeExportable(t),this.params.details||this.dom.querySelector(b.details)?this.initDetails():this.initEvents(),this.params.onselect&&this.initSelect(t),this.dom.querySelectorAll("thead [data-altsort]").length&&this.initAlternateSort(this.dom.querySelectorAll("thead [data-altsort]")),this.params.filters){const t=this.wrapper.querySelector(b.top);if(t&&t.children.length){const e=document.querySelector(b.filters);e&&t.prepend(e)}}this.dom.querySelector(b.tip)&&this.initTips()}}initSort(){const t=this.dom.querySelectorAll("thead th");let e=0;this.grid.columns.forEach(((s,i)=>{if(!s.hasOwnProperty("hidden")){if(s.sortable){const i=t[e],a=document.createElement("a");a.classList.add(b.sorter.substr(1)),a.appendChild(i.childNodes[0]),i.appendChild(a),i.childNodes.forEach((t=>{i.appendChild(t)})),a.addEventListener("click",(t=>{if(t.stopImmediatePropagation(),!0===this.sorting||!0===this.searching)return t.preventDefault(),!1;this.sortColumn(i,s.index)}))}e++}})),this.sorting=!1,o.j.on(this.eventnames.sorting,(t=>{this.plugins.jsDetail&&this.plugins.jsDetail.activeDetail(!1),this.dom.querySelectorAll(".table-sorter").forEach(((e,s)=>{e.classList.add(s===t.index?h.AH.wait:h.AH.disabled)})),this.sorting=!0}),this.uuid),o.j.on(this.eventnames.sorted,(t=>{this.dom.querySelectorAll(".table-sorter").forEach(((e,s)=>{e.classList.remove(s===t.index?h.AH.wait:h.AH.disabled)})),this.sorting=!1}),this.uuid)}sortColumn(t,e,s=null){s=null===s?!t.classList.contains(g.ascending)&&(!!t.classList.contains(g.descending)||!t.dataset.sort):s,t.classList.toggle(g.ascending),t.classList.toggle(g.descending),o.j.emit(this.eventnames.sorting,{dir:s,index:t.cellIndex},this.uuid);let i=this.grid.data.map(((t,s)=>{const i=(0,l.vZ)(t[e])?JSON.stringify(t[e]):Array.isArray(t[e])?t[e][0]:t[e];return{value:"string"==typeof i?i.toLowerCase():null===i?0:i,row:s}}));if(!1===s?(t.classList.remove(g.ascending),t.classList.add(g.descending),t.setAttribute("aria-sort","descending")):(t.classList.remove(g.descending),t.classList.add(g.ascending),t.setAttribute("aria-sort","ascending")),void 0!==this.dom.dataset.lastth&&t.cellIndex!=this.dom.dataset.lastth){const t=this.dom.querySelectorAll("thead th");t[this.dom.dataset.lastth].classList.remove(g.descending),t[this.dom.dataset.lastth].classList.remove(g.ascending),t[this.dom.dataset.lastth].removeAttribute("aria-sort")}this.dom.dataset.lastth=t.cellIndex;const a=new Intl.Collator(void 0,{numeric:!0,sensitivity:"base"});i.sort(((t,e)=>a.compare(s?t.value:e.value,s?e.value:t.value)));const n=this.dom.querySelector("tbody"),r=n.cloneNode(),d=n.querySelectorAll("tr");n.innerHTML="";const c=[];i.forEach(((t,e)=>{r.appendChild(d[t.row]),c.push(this.grid.data[t.row])})),this.dom.replaceChild(r,n),o.j.emit(this.eventnames.sorted,{dir:s,index:t.cellIndex},this.uuid)}displaySelected(t,e,s,i=null){const a=this.dom.querySelectorAll("tbody tr");null===i&&(i=function(t,e,s){t.hidden=e});const n=0===t.length&&0===e.length;a.forEach(((a,r)=>{if(n)i(a,!1);else{const n=t.length>0&&0===e.length?f:null!==a.dataset[this.cellidname]?a.dataset[this.cellidname]:a.cells[s].textContent,r=e.indexOf(n);i(a,r<0,r)}}))}initSearch(){const t=this.wrapper.querySelector(b.top);if(!this.params.searchable||null===t)return;if(this.grid.data.length<10)return this.toggleAddOns();this.toggleAddOns([b.search+" input"],!1),this.searching=!1;const e=this.getCellId(this.cellidname);let s=t.querySelector(b.search);null===s&&(s=this.objToElement({nodename:"DIV",attributes:{class:b.search.substr(1)},childnodes:[{nodename:"input",attributes:{type:"search",name:"table-search",placeholder:this.labels.placeholder,class:`${b.input.substr(1)} ${h.AH.input}`}}]}),t.appendChild(s));const i=s.querySelector("input");if(!i)return;let a="";const n=c()(((t,s=!1)=>{const i=function(t,e){t=function(t,e){return e?t:t.toLowerCase()}(t,e);let s,i=[];for(;null!==(s=t.match(/"([^"]+)"/));)i.push(s[1]),t=t.substring(0,s.index)+t.substring(s.index+s[0].length);return(t=t.trim()).length&&(i=i.concat(t.split(/\s+/))),i}(t);o.j.emit(this.eventnames.search,{searchstring:t,queries:i},this.uuid);let a=this.grid.data,n=[];i.forEach((t=>{n=[],a=a.filter(((i,a)=>{if(i.filter((e=>{switch(typeof e){case"object":e=e||"";try{e=JSON.stringify(e)}catch(t){console.log("search",t),e=""}break;case"array":e=e.join(" ");break;default:e=String(e)}return(s?e.indexOf(t)>-1:e.toLowerCase().indexOf(t))>-1})).length>0)return e<0?n.push(String(a)):n.push(String(i[e])),i}))})),o.j.emit(this.eventnames.searchend,{queries:i,indexes:n,cellid:e},this.uuid)}),300),r=(t,e,s)=>{this.displaySelected(t,e,s)},l=c()((()=>{this.searching=!0;this.dom.querySelectorAll('tbody tr[hidden=""]').forEach(((t,e)=>{t.hidden=!1})),this.searching=!1,i.classList.remove(h.AH.wait)}),500),d=t=>{t!==a&&(i.classList.add(h.AH.wait),a=t,""===t?l():t.length>2&&n(t))};i.addEventListener("input",(t=>{d(t.target.value)})),i.addEventListener("click",(t=>{d(t.target.value)})),o.j.on(this.eventnames.search,(t=>{!1===this.searching&&this.plugins.jsDetail&&this.plugins.jsDetail.activeDetail(!1),this.searching=!0}),this.uuid),o.j.on(this.eventnames.searchend,(t=>{r(t.queries,t.indexes,t.cellid),i.classList.remove(h.AH.wait),this.searching=!1}),this.uuid),o.j.on(this.eventnames.update,(()=>{!1===this.searching&&setTimeout((()=>{refresh_details()}),300)}),this.uuid),this.toggleAddOns([b.search+" input"],!0)}initSelect(t){const e=this.dom.querySelectorAll('input[name^="'+this.uuid+'"]');if(0===e.length)return;e[0].name;let s=t.querySelector("."+g.selectaction);if(!s)return;document.body.append(s),s.querySelector("a").addEventListener("click",(t=>{let i=[];e.forEach((t=>{t.checked&&i.push(t.value)})),s.dataset.input?(document.getElementById(s.dataset.input).value=i.join(","),s.dataset.form&&document.getElementById(s.dataset.form).submit()):t.currentTarget.href=this.params.onselect+encodeURI(i.join(","))}));const i=s.querySelector("[data-dismiss]");i&&i.addEventListener("click",(t=>{t.preventDefault(),t.stopImmediatePropagation(),a(null,null)}));const a=(t=null,e=null,a=!1)=>{if(s.dataset.close&&(document.body.append(s),i.classList.remove(g.hidden),s.classList.add(g.absinput)),null!==t&&null!==e)s.classList.remove(h.AH.hide),s.style.top=t+"px",s.style.left=e+"px";else if(!0===a)s.classList.add(h.AH.hide),delete s.dataset.close;else{s.dataset.close=!0,i.classList.add(g.hidden);(this.wrapper.querySelector(b.top)?this.wrapper.querySelector(b.top):this.wrapper).prepend(s),s.classList.remove(g.absinput)}};e.forEach((t=>{t.addEventListener("change",(e=>{t.checked?a(t.offsetTop,t.offsetLeft):0===this.dom.querySelectorAll('input[name^="'+this.uuid+'"]:checked').length&&a(null,null,!0)}))})),this.dom.querySelectorAll('input[name^="'+this.uuid+'"]:checked').length>0&&(s.classList.remove(h.AH.hide),a(null,null))}async initDetails(){const t=this.wrapper,e=t.querySelector("#"+g.tipinline)?t.querySelector("#"+g.tipinline):g.tipinline;if(!this.plugins.JsDetail){const{JsDetail:t}=await s.e(329).then(s.bind(s,329));this.plugins.JsDetail=t}if(!this.plugins.JsAccordion){const{JsAccordion:t}=await s.e(148).then(s.bind(s,5148));this.plugins.JsAccordion=t}const i=this.plugins.JsDetail({waitdiv:this.waitdiv}),a=i.applyTo(e,t),n=(t,e=null)=>{i.activeDetail(!1);e&&e()},r=(t,e=null)=>{let s=i.activeDetail(!0);if(s&&s===t)s=i.expandDetail(t),e&&e();else{s&&s.querySelector("summary").click();const a=this.params.detailsurl+t.dataset.id+"?"+new URLSearchParams({partial:!0});s=i.activeDetail(!0),fetch(a,(0,l.Uc)()).then((t=>t.text())).then((a=>{s=i.expandDetail(t,a),e&&e()})).catch((t=>{console.log("request",t)}))}};(()=>{const t=this.dom.querySelectorAll(b.details);t&&this.plugins.JsAccordion.applyTo(t,r,n,a)})()}initAlternateSort(t){let e,s=[];t.forEach((t=>{const e=t.closest("th");Object.entries(t.dataset).forEach((([s,i])=>{e.dataset[s]=i,t.classList.add("inline-block")})),s.push(e)}));const i=t=>{let s;const i=t.classList.contains(g.ascending),a=t.classList.contains(g.descending);s=parseInt(t.dataset.sortactive)===parseInt(e)?i?"desc":"asc":i?"asc":a?"desc":"asc",this.sortColumn(t,e,s)};(t=s).forEach((t=>{const s=t.dataset.altsort?t.dataset.altsort.split(","):null;if(!s)return;const a=t.querySelector(b.sorter);a&&a.classList.add(g.disabled);const n=t.querySelector(b.sorton);t.append(n);const r=t.querySelectorAll('[role="button"]');t.addEventListener("click",(e=>{e.preventDefault(),i(t)}),!1);const l=(t,i)=>{e=0===i?this.grid.columns.findIndex((e=>e.index===t.cellIndex)):this.grid.columns.findIndex((t=>t.name===s[i-1]))};t.dataset.sortactive=t.cellIndex,r.forEach(((e,s)=>{e.addEventListener("click",(e=>{e.preventDefault();const i=e.currentTarget.parentElement.querySelector("."+h.AH.active);i&&i.classList.remove(h.AH.active),e.currentTarget.classList.add(h.AH.active),l(t,s)}))})),t.dataset.tip&&Object.values(this.dom.rows).forEach(((e,i)=>{if(0===i)return;const a=this.grid.columns.findIndex((e=>e.name===s[parseInt(t.dataset.tip)-1]));0!==e.cells.length&&a!==t.cellIndex&&(e.cells[t.cellIndex].addEventListener("mouseenter",(t=>{const s=document.createElement("div");s.setAttribute("class",g.tipover),s.innerHTML=e.cells[a].innerHTML,t.currentTarget.append(s)})),e.cells[t.cellIndex].addEventListener("mouseout",(t=>{const e=t.currentTarget.querySelector(b.tipover);e&&e.remove()})))}))}))}makeExpandable(t){if(t.querySelector("table").offsetHeight<t.offsetHeight)return;const e=document.createElement("div");e.classList.add(g.buttonexpand),e.classList.add(g.bordert),e.title=this.params.expand,e.innerHTML=`<span class="small-caps block mx-auto p-0">${this.params.expand}</span><i class="clear-both p-0 mx-auto icon icon-chevron-down hover:fill-secondblue-500"></i><span class="small-caps block mx-auto p-0 hidden">${this.params.shrink}</span>`,t.parentElement.insertBefore(e,t.nextElementSibling),t.classList.add(g.overflowyhidden),t.classList.remove(g.maxtabstath),t.parentElement.style.height="auto";const s=parseInt(this.wrapper.querySelector("tbody tr").offsetHeight)*(this.params.maxrows?this.params.maxrows:20);t.classList.add("max-h-["+s+"px]"),t.style.height=s+"px",e.addEventListener("click",(i=>{const a=t.classList.contains(g.overflowyhidden);c()((()=>{e.classList.toggle(g.bordert),e.classList.toggle(g.borderb);const i=e.querySelector("i");i.classList.toggle(g.icochevrondown),i.classList.toggle(g.iconchevronup),t.classList.toggle(g.overflowyhidden),t.classList.toggle("max-h-["+s+"px]"),e.querySelectorAll("span").forEach((t=>{t.classList.toggle(g.hidden)})),t.style.height=a?s+"px":"auto"}),100)()}))}makeExportable(t){const e=document.createElement("div");e.classList.add(b.export.slice(1)),e.classList.add("is-pick"),e.innerHTML=`<i class="icon icon-arrow-down-on-square"></i><span>${this.params.exportlabel?this.params.exportlabel:"export statistics "}</span>`,this.wrapper.prepend(e);this.grid.columns;let i=[];this.grid.columns.forEach(((t,e)=>{"select"===t.name&&i.push(t.index)})),e.addEventListener("click",(async e=>{if(e.preventDefault(),!this.plugins.exportCSV){const{exportCSV:t}=await s.e(691).then(s.bind(s,6691));this.plugins.exportCSV=t}let a=this.plugins.exportCSV(this,{download:!1,linedelimiter:"\n",columndelimiter:"\t",skipcolumns:i});a=encodeURI(`data:text/tsv;charset=utf-8,${a}`),(0,l.pd)(a,(t.id?t.id:"stats_proj")+".tsv")}))}initTips(){let t=null;this.dom.querySelectorAll(b.tip).forEach((e=>{e.addEventListener("click",(e=>{e.preventDefault(),e.stopImmediatePropagation();const s=e.target.parentElement;null!==t&&t.classList.remove(g.showfull),t!==s?(s.classList.add(g.showfull),t=s):t=null}))}))}toggleAddOns(t=null,e=!1){(t=t||[b.search+" input",b.export]).forEach((t=>{(t=this.wrapper.querySelector(t))&&(e?t.classList.remove(h.AH.hide):t.classList.add(h.AH.hide))}))}}i()}catch(t){i(t)}}))}}]);