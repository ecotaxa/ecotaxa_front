/*! For license information please see 690.b221596de1d59a097607.js.LICENSE.txt */
"use strict";(self.webpackChunk=self.webpackChunk||[]).push([[690,57,615],{615:(e,t,s)=>{s.d(t,{FormSubmit:()=>o});var i=s(7856),a=s.n(i),n=s(2817),r=s(7737);n.EY.captcha=".js-captcha",n.iv.invalid="invalid",n.iv.inputvalid="valid",n.iv.required="required",n.iv.tshidden="ts-hidden-accessible";class o{handlers={validate:[],submit:[]};form=null;listener=null;constructor(e,t={}){if(e){if(!e.formsubmit){this.form=e instanceof HTMLElement?e:document.querySelector(e);const s={fetch:null};if(t=Object.assign(t,this.form.dataset),this.options=Object.assign(s,t),!this.form)return;this.tabs=this.form.querySelectorAll(n.EY.component.tabs.tab),this.validateFields(!0),this.init(),e.formsubmit=this}return e.formsubmit}}init(){this.form.addEventListener("keydown",(e=>{"Enter"===e.key&&e.target instanceof HTMLInputElement&&e.preventDefault()})),window.addEventListener("pageshow",(e=>{(event.persisted||void 0!==window.performance&&2===window.performance.navigation.type)&&this.enableForm()})),this.form.addEventListener("validate",(e=>{this.validateFields()})),this.form.addEventListener("submit",(async e=>{e.preventDefault();return await this.submitForm()})),this.specialFields()}specialFields(){this.form.querySelectorAll("input[data-match]").forEach((e=>{const t=e.dataset.match;if(!t)return;const s=document.getElementById(t);if(!s)return;const i=e.dataset.matchinvalid?e.dataset.matchinvalid:"no match",a=(t,s)=>{const a=t.closest(n.EY.component.form.formbox).querySelector('label[for="'+t.id+'"]'),r=s.closest(n.EY.component.form.formbox).querySelector('label[for="'+s.id+'"]'),{patternMismatch:o=!1}=t.validity,l=o?this.get_message(t,"invalid"):"";!0===t.checkValidity()?(t.setCustomValidity(""),t==e&&null!==a?a.classList.remove(n.iv.invalid):null!==r&&r.classList.remove(n.iv.invalid),t.classList.remove(n.iv.invalid),t.value!==s.value?(s.setCustomValidity(i),r&&(r.dataset.invalid=i,r.classList.add(n.iv.invalid)),s.classList.add(n.iv.invalid)):(s.setCustomValidity(""),r&&r.classList.remove(n.iv.invalid),s.classList.remove(n.iv.invalid))):(t.setCustomValidity(l),a.dataset.invalid=l,a&&a.classList.add(n.iv.invalid),t.classList.add(n.iv.invalid)),t.focus()};[e,s].forEach((t=>{t.addEventListener("keyup",(i=>{a(t===e?e:s,t===e?s:e)}))}))}))}get_message(e,t="invalid"){const{valueMissing:s=!0}=e.validity;return s?"* "+(e.dataset.required?e.dataset.required:this.form.dataset.required?this.form.dataset.required:e.validationMessage?e.validationMessage:"required"):e.dataset[t]?e.dataset[t]:e.validationMessage?e.validationMessage:"input invalid"}setLabelState(e,t){const s=this.getFieldLabel(e);if(null!=s)if(!0===t)s.classList.remove(n.iv.invalid);else{s.dataset.invalid=this.get_message(e),s.classList.add(n.iv.invalid);const t=s.getBoundingClientRect(),i=t.left,a=t.top;window.scrollTo({top:a,left:i,behavior:"smooth"})}}validateField(e,t=!1){["select"].indexOf(e.tagName.toLowerCase())>=0?e.querySelectorAll("option:checked").forEach((e=>{e.value=(0,r.Tv)(a().sanitize(e.value))})):e.value=(0,r.Tv)(a().sanitize(e.value)),e.tomselect&&e.classList.remove(n.iv.tshidden);let s=e.checkValidity();e.tomselect&&e.classList.add(n.iv.tshidden),s&&void 0!==e.dataset.unique&&(s=this.validateFieldUnique(e));const i=document.createEvent("Event");return i.initEvent(s?"valid":"invalid",!0,!0),e.dispatchEvent(i),s}getFieldLabel(e){let t=e.closest('[for="'+e.name+'"]')?e.closest('[for="'+e.name+'"]'):e.closest('[data-for="'+e.name+'"]')?e.closest('[data-for="'+e.name+'"]'):null;return null===t&&(t=e.closest(n.EY.component.form.formbox)?e.closest(n.EY.component.form.formbox).querySelector(".label")?e.closest(n.EY.component.form.formbox).querySelector(".label"):e.closest(n.EY.component.form.formbox).querySelector("label"):null),null===t&&(t=e.parentElement&&e.parentElement.dataset.elem&&e.closest("fieldset")?e.closest("fieldset").querySelector("."+e.parentElement.dataset.elem):null),t}validateFieldUnique(e){const t=this.getFieldLabel(e);if(String(e.dataset.unique).toLowerCase()===String(e.value).toLowerCase()){t&&(t.dataset.confirm=window.alertbox.i18nmessages.noduplicate,t.classList.add(window.alertbox.alertconfig.css.confirm));const s=function(){e.dataset.unique=!1,t&&(t.classList.remove(window.alertbox.alertconfig.css.confirm),delete t.dataset.confirm)};return window.alertbox.createConfirm((t?t.textContent+" : ":"")+window.alertbox.i18nmessages.noduplicate,{callback_cancel:s,buttons:{ok:{text:window.alertbox.i18nmessages.modify},cancel:{text:window.alertbox.i18nmessages.saveanyway}}})}return t.dataset.confirm&&(t.classList.remove(window.alertbox.alertconfig.css.confirm),delete t.dataset.confirm),!0}async validateFields(e=!1){let t=!0,s=!0;return[...this.form.elements].forEach((i=>{if(!0===e){if(!i.dataset.listen){if(i.required){const e=this.getFieldLabel(i);e&&e.classList.add(n.iv.required)}i.addEventListener("change",(e=>{this.validateField(e.target)})),i.dataset.listen=!0,i.addEventListener("invalid",(e=>{this.setLabelState(i,!1)})),i.addEventListener("valid",(e=>{this.setLabelState(i,!0)}))}}else i.name&&i.type&&["submit","hidden"].indexOf(i.type)<0&&(["radio","checkbox"].indexOf(i.type)<0||i.required)&&(s=this.validateField(i,!1),t=t&&s)})),!1===e&&(this.tabs.forEach((e=>{e.querySelector(":invalid")||e.querySelector(n.EY.component.alert.danger)?e.classList.add(n.iv.error):e.classList.remove(n.iv.error)})),s=await this.execHandler("validate")),s&&t}addHandler(e,t){this.handlers[e].push(t)}fieldEnable(e=!0){this.form.querySelectorAll('input[data-sub="enable"]').forEach((t=>{t.disabled=!0!==e}))}async execHandler(e){if(0===this.handlers[e].length)return!0;let t=!0;return await Promise.all(this.handlers[e].map((async e=>{const s=await e();t=t&&s}))),t}formFetch(e=null){const t=new FormData(this.form);return t.fetch=!0,fetch(this.form.action,(0,r.wv)({method:"POST",body:t})).then((t=>{switch(e){case"text":case"html":return t.text();default:return t.json()}})).then((e=>{this.displayResponse(e)})).catch((e=>{this.displayResponse(e,!0)})).finally((e=>{this.form.disabled=!0})),!1}async submitForm(){this.fieldEnable();if(await this.validateFields(!1)){if(!0===(!!this.form.querySelector(n.EY.captcha)&&(!this.form.dataset.isbot||!0===this.form.dataset.isbot)))return!1;if(await this.execHandler("submit"))return this.options.fetch?this.formFetch(this.options.fetch):this.form.submit(),this.disableForm(),!0}return!1}enableForm(){this.form.disabled=!1;const e=this.form.querySelector('[type="submit"] svg');e&&e.remove()}disableForm(){this.form.disabled=!0;const e=this.form.querySelector('[type="submit"]');e&&e.insertAdjacentHTML("afterbegin",(0,r.IW)("text-stone-50 ml-1 mr-2 align-text-bottom inline-block"))}displayResponse(e,t=!1){const s=document.createElement("div");s.insertAdjacentHTML("afterbegin",e),!1!==t&&s.classList.add("is-error"),this.form.parentElement.insertBefore(s,this.form),this.form.remove()}}},2057:(e,t,s)=>{s.d(t,{JsTomSelect:()=>g});var i=s(7856),a=s.n(i),n=s(6031),r=s.n(n),o=s(2651),l=s.n(o),d=s(4555),c=s.n(d),m=s(4775),u=s.n(m),h=s(7737),p=s(2817);r().define("remove_button",l()),r().define("clear_button",c()),r().define("caret_position",u());let v={};function f(e,t,s=!1){if(!t)return e.text;let i=[];return Object.keys(e).indexOf(t)>=0?i.push(e[t]):t.indexOf("+")>0&&(!0===s?i.push(e[t.split("+")[0]]):t.split("+").forEach((t=>{t in e&&i.push(e[t])}))),i.join(" ")}class g{applyTo(e,t={},s=null){const i=e.getAttribute("id"),n=e.hasAttribute("multiple"),o=e.dataset.type;let l={url:"",settings:t};switch(e.dataset.create&&"true"===e.dataset.create&&(l.settings.create=!0,l.settings.addPrecedence=!0),e.dataset.empty&&"true"===e.dataset.empty&&(l.settings.allowEmptyOption=!0),e.dataset.maxitems&&(l.settings.maxItems=parseInt(e.dataset.maxitems)),e.dataset.addoption&&(l.settings.addoption=e.dataset.addoption.split(",")),o){case p.Cq.project:const t=n?null:1;l.url="/gui/prjlist/",l.settings={...l.settings,valueField:"id",searchField:"text",labelField:"text",openOnFocus:!1,maxItems:t,allowEmptyOption:!1};break;case p.Cq.user:l.url="/api/users/search?by_name=",l.settings={...l.settings,valueField:"id",searchField:"name",labelField:"name+email",onInitialize:function(){e.currentlist?v=e.currentlist:e.tomselect.items.forEach((e=>{""!==e&&parseInt(e)>0&&(v[e]=!0)}))},onItemAdd:function(t){""!==t&&(v[t]?(window.alertbox?window.alertbox.addItemMessage(window.alertbox.alertconfig.types.danger,e,window.alertbox.i18nmessages.exists):(e.dataset.invalid=window.alertbox.i18nmessages.exists,e.dispatchEvent(new Event("invalid"))),setTimeout((()=>{if(this.removeOption(t),this.revertSettings.tabIndex<0||!e.options.length||!this.revertSettings)this.removeItem(t),v[t]=!0;else{const t=e.options[this.revertSettings.tabIndex].value;this.addItem(t)}window.alertbox?window.alertbox.removeItemMessage(window.alertbox.alertconfig.types.danger,e,window.alertbox.i18nmessages.exists):(delete e.dataset.invalid,e.dispatchEvent(new Event("undeterminate")))}),2e3)):v[t]=!0)},onItemRemove:function(t){if(v[t]&&delete v[t],n||!this.revertSettings||""===this.revertSettings.innerHTML&&0===this.revertSettings.tabIndex||this.revertSettings.tabIndex<0)return;const s=e.options[this.revertSettings.tabIndex].value;void 0!==v[s]&&delete v[s]}};break;case p.Cq.instr:l.url="/search/instruments",l.settings={valueField:"id",labelField:"text",searchField:"id",maxItems:1,preload:!0};break;case p.Cq.taxo:r().define("no_close",(()=>{this.close=()=>{}})),l.url="/search/taxo",l.settings={...l.settings,valueField:"id",labelField:"text",searchField:"text",closeAfterSelect:!0,onInitialize:()=>{const t=document.getElementById(i).nextElementSibling;if(!t.classList.contains("ts-wrapper"))return;t.querySelectorAll(p.EY.component.tomselect.tsdelet).forEach((t=>{(t=>{t.addEventListener("click",(t=>{const s=t.currentTarget.closest(p.EY.component.tomselect.item).dataset.value;s&&(t.stopImmediatePropagation(),e.tomselect.removeItem(s))}))})(t)}))}}}const d={create:!1,minOptions:0,maxOptions:null,preload:!1,hideSelected:!0,duplicates:!1,allowEmptyOption:!0,closeAfterSelect:!0,placeholder:e.placeholder?e.placeholder:e.dataset.placeholder?e.dataset.placeholder:"",onDropdownClose:function(){},shouldLoad:function(e){return e.length>2},onItemRemove:function(){return!0},load:function(e,t){e=a().sanitize(e);if(this.loading>10)return void t();let s="";switch(o){case p.Cq.user:s=l.url+encodeURIComponent("%"+e+"%");break;case p.Cq.instr:case p.Cq.taxo:if(s=l.url,0==e.indexOf("_")&&l.settings.addoption&&e==l.settings.addoption[0])return s=null,t(Object.entries([{text:l.settings.addoption[0],id:l.settings.addoption[1]}]));e&&(s+="?q="+encodeURIComponent(e));break;case p.Cq.project:s=l.url,e&&(s+="?filt_title="+encodeURIComponent(e))}null!==s&&fetch(s,(0,h.wv)()).then((e=>e.json())).then((e=>(o===p.Cq.project&&e.data&&e.data.length&&(e=e.data.map((e=>({id:e[1],text:e[3][0],rights:e[0]})))),o===p.Cq.instr&&e.length&&(e=e.reduce(((e,t,s)=>{let i={id:t=a().sanitize(t),text:t};return e.push(i),e}),[])),e.length&&"object"==typeof e&&(e=Object.entries(e)),t(e)))).catch((e=>{console.log("tomselect-err",e)}))},render:{option:function(e,t){if(null==e)return"";const s=e.hasOwnProperty("optgroup")?`data-optgroup=${e.optgroup}`:"",i=f(e,l.settings.labelField);return`<div class="py-2 flex  ${n?"inline-flex":""} " ${s} data-value="${e[l.settings.valueField]}">${t(i)}</div>`},item:function(e,t){if(null==e)return"";const s=e.optgroup?`item-${e.optgroup}`:"",i=v[e[this.settings.valueField]]?"data-inlist":"",r=f(e,l.settings.labelField,!0);return a().sanitize(`<div class="${n?"flex inline-flex ":""} ${s}"  data-value="${e[this.settings.valueField]}"  ${i}>${t(r)} </div>`)},no_results:function(t,s){return a().sanitize('<div class="no-results">'+(e.dataset.noresults?e.dataset.noresults:"No result found for ")+s(t.input)+"</div>")}}};if(l.settings.plugins={clear_button:{title:e.dataset.clear?e.dataset.clear:"Clear all",html:e=>`<div class="${e.className}" id="clear-${i}" title="${e.title}"><i class="icon ${n?"":"p-[0.125rem]"} icon-x-circle-sm ${n?"":" opacity-50"}"></i></div>`}},l.settings.onClear=function(){return e.tomselect.clear(),!0},n&&(l.settings.plugins={...l.settings.plugins,remove_button:{}},l.settings.plugins={...l.settings.plugins,caret_position:{}}),l.settings=Object.assign(d,l.settings),null!==i){const t=new(r())("#"+i,l.settings);switch(t.wrapper.classList.remove(p.EY.component.tomselect.ident),t.wrapper.classList.remove("js"),t.wrapper.setAttribute("data-component","tom-select"),o){case p.Cq.taxo:t.on("item_add",((e,t)=>{null!==t&&t.classList.add("new")}));break;case p.Cq.project:e.dataset.dest&&t.on("item_add",((s,i)=>{if(s!=e.dataset.value&&t.options[s]&&!i.querySelector("a")){const e={A:"/prj/",V:"/prj/",M:"/gui/prj/edit/"},a=t.options[s].rights,n=Object.keys(a);n&&(n.length>1?(Object.entries(a).forEach((([e,t])=>{i.insertAdjacentHTML("beforeend",` <a data-k="${e}" class="small-caps font-normal ml-2">${t}</a>`)})),i.querySelectorAll("a").forEach((i=>{i.addEventListener("click",(i=>{i.preventDefault(),i.stopPropagation(),window.open(e[i.target.dataset.k]+s,`_proj${s}`).focus(),t.removeItem(s)}))}))):(window.open(e[n[0]]+s,`_proj${s}`).focus(),t.removeItem(s)))}}))}return t}console.log("noid")}getUserList(){return v}}},5690:(e,t,s)=>{s.d(t,{ProjectPrivileges:()=>o});var i=s(7856),a=s.n(i),n=(s(615),s(2057)),r=s(2817);class o{options;keymessages={oneatleast:"oneatleast",nomanager:"nomanager",nocontact:"nocontact",uhasnopriv:"uhasnopriv",importpriverror:"importpriverror",emptyname:"emptyname"};current_uid;fieldset;fieldset_alert_zone;linemodel;currentlist={};constructor(e,t={}){if(null!==e&&e instanceof HTMLElement!=!1){if(!e.jsprivileges){const s={separ:".new-privilege",addbtn:'[data-add="block"]',target:"member",ident:"member",privilege:"privilege",delet:"delet",contact:"contact",contactfieldname:"contact_user_id",domselectors:{tabcontent:".tab-content"}};if(this.options=Object.assign({},s,t),this.fieldset=e,!this.fieldset)return window.alertbox.classError();this.fieldset_alert_zone=e.querySelector(this.options.domselectors.tabcontent)?e.querySelector(this.options.domselectors.tabcontent):e,this.options.separ=this.options.separ instanceof HTMLElement?this.options.separ:document.querySelector(this.options.separ)?document.querySelector(this.options.separ):null,this.options.addbtn=this.options.addbtn instanceof HTMLElement?this.options.addbtn:document.querySelector(this.options.addbtn),this.options.addbtn&&this.addListener();const i=this.fieldset.querySelectorAll('[data-block="'+this.options.target+'"]');if(0===i.length)return window.alertbox.classError();if(this.linemodel=this.clearLine(i[0].cloneNode(!0),0,-1),this.linemodel.classList.add(r.iv.hide),this.linecontainer=i[0].parentElement,null===this.linecontainer)return window.alertbox.classError();this.current_uid=this.fieldset.dataset.u,i.forEach(((e,t)=>{e.dataset.n=t,this.activateEvents(e)}));const a=this.fieldset.closest("form");a&&(a.formsubmit?(a.formsubmit.addHandler("validate",(()=>this.validateFields())),a.formsubmit.addHandler("submit",(()=>this.formatPrivileges()))):a.addEventListener("submit",(async e=>{if(!1!==this.validateFields())return this.formatPrivileges();e.preventDefault()}))),this.orderRows(),e.jsprivileges=this}return e.jsprivileges}}newLine(e=!1,t=0,s=!1){const i=this.linecontainer.children;let a;if(i.length&&t>0&&(a=this.getLinePrivilege(t)),a)return!0===s?a:null;if(a=this.linemodel.cloneNode(!0),a.classList.remove(r.iv.hide),a){this.linecontainer.append(a);const s=this.fieldset.dataset.n?parseInt(this.fieldset.dataset.n)+1:i.length;if(a=this.clearLine(a,-1,s,this.options.separ?this.options.separ:null),a.dataset.n=s,this.fieldset.dataset.n=s,this.activateEvents(a,0===t),!0===e)return a}return null}addListener(){this.options.target=this.options.addbtn.dataset.target?this.options.addbtn.dataset.target:this.options.target,this.options.addbtn.addEventListener("click",(async e=>{e.preventDefault(),this.newLine()}))}indexElement(e,t,s){return["id","name","for","aria-controls"].forEach((i=>{let a=e.getAttribute(i);null!==a&&(a="name"===i?a.replace("["+t+"]","["+s+"]"):a.replace("_"+t,"_"+s),e.setAttribute(i,a))})),e}indexLine(e,t,s=null){s=null===s?t+1:s;return e.querySelectorAll("[data-elem]").forEach((e=>{e.querySelectorAll("input, select, label, div").forEach((e=>{null!==t&&(e=this.indexElement(e,t,s))}))})),e.dataset.n=parseInt(s),this.fieldset.dataset.n=this.fieldset.dataset.n&&this.fieldset.dataset.n>=s?this.fieldset.dataset.n:s,e}clearLine(e,t=null,s=null,i=null){e.dataset.mod="",e.disabled=!1;return e.querySelectorAll("[data-elem]").forEach((e=>{e.querySelectorAll("input, select, label, div").forEach((e=>{switch(e.disabled=!1,null!==t&&(s=null===s?t+1:s,e=this.indexElement(e,t,s)),e.tagName.toLowerCase()){case"input":e.checked=!1,e.name==this.options.contactfieldname&&(e.value="0",e.disabled=!0);break;case"select":Array.from(e.options).forEach((e=>{parseInt(e.value)>0&&e.remove()})),e.selectedIndex=0,e.tomselect?e.tomselect.destroy():["tom-select","tomselected","ts-hidden-accessible"].forEach((t=>{e.classList.remove(t)}));break;case"div":null!==t&&e.dataset.component&&e.remove()}}))})),i&&(e.classList.add("new"),i.after(e)),e}setLine(e,t={key:"",value:""},s,i){if(!(s=r.HN[s]?r.HN[s]:r.HN.viewers))return;const{member:o,privs:l,contact:d,delet:c}=this.getInputs(e,s);if(!(o&&l&&d&&c))return;t.key=a().sanitize(t.key),t.value=a().sanitize(t.value);let m=o.querySelector('option[value="'+t.key+'"]');if(null===m&&(m=document.createElement("option"),m.value=t.key,m.text=t.value,o.append(m)),m.selected=!0,!o.tomselect){(new n.JsTomSelect).applyTo(o)}l.checked=!0,d.value=t.key,s===r.hp.manage?(d.disabled=!1,!0!==i||d.checked||(d.checked=!0)):(d.disabled=!0,d.checked=!1)}getInputs(e,t=!1){const s=e.querySelector("[name*='["+this.options.ident+"]']");let i;i=t?e.querySelector('input[name*="['+this.options.privilege+']"][value="'+t+'"]'):e.querySelectorAll('input[name*="['+this.options.privilege+']"]');return{member:s,privs:i,contact:e.querySelector('input[name="'+this.options.contactfieldname+'"]'),delet:e.querySelector("input[name*='["+this.options.delet+"]']")}}async importPrivileges(e,t=!1,s=null,i=null,a=null){!0===t&&this.clearAll();try{return Object.entries(e).forEach((([e,a])=>{a.forEach((a=>{const n=this.newLine(!0,a.id);n&&(this.setLine(n,{key:a.id,value:a.name},e,null!==s&&s.id===a.id),i&&i(n)),t=!1}))})),a&&a(),window.alertbox.dismissAlert(this.keymessages.importpriverror),this.orderRows(),!0}catch(e){return window.alertbox.renderAlert({type:window.alertbox.alertconfig.types.error,content:this.keymessages.importpriverror,dismissible:!0,inverse:!0}),console.log("err",e),!1}}activateEvents(e,t=!1){if(!e)return;const{member:s,privs:i,contact:a,delet:o}=this.getInputs(e);if(!(s&&i&&a&&o))return;const l=e=>[...e.parentElement.children].filter((t=>1==t.nodeType&&t!=e&&t.classList.contains("row")&&null!==t.dataset.block&&t.dataset.block===this.options.target));if(s.currentlist||(s.currentlist=this.currentlist),s.value&&!this.currentlist[s.value]&&(this.currentlist[s.value]=!0),!0===t&&!s.tomselect){(new n.JsTomSelect).applyTo(s)}const d=(t,s,i,a=!1)=>{t&&t.checked&&(t.checked=!0,window.alertbox.hasItemMessages(e)&&window.alertbox.removeItemMessage(window.alertbox.alertconfig.types.danger,e,this.keymessages.uhasnopriv)),t&&t.value===r.hp.manage?(i.disabled=!0,s.disabled=!1,window.alertbox.dismissAlert(this.keymessages.nomanager),s.checked&&(window.alertbox.dismissAlert(this.keymessages.nocontact),s.dispatchEvent(new Event("valid")))):(s.checked=!1,i.disabled=!1,s.disabled=!0),!0===a&&c(e),i.ckecked||(window.alertbox.dismissAlert(this.keymessages.nobody),window.alertbox.hasItemMessages(e)&&window.alertbox.removeItemMessage(window.alertbox.alertconfig.types.danger,e,this.keymessages.oneatleast))},c=e=>{l(e).forEach((e=>{const t=e.querySelector("input[name*='["+this.options.delet+"]']"),s=e.querySelector('input[name="'+this.options.contactfieldname+'"]'),i=e.querySelector('input[name*="['+this.options.privilege+']"]:checked');d(i,s,t,!1)}))};s.addEventListener("change",(e=>{a.value=s.value,parseInt(s.value)>0&&window.alertbox.hasItemMessages(s)&&window.alertbox.removeItemMessage(window.alertbox.alertconfig.types.danger,s,this.keymessages.emptyname)})),i.forEach((e=>{e.addEventListener("change",(t=>{e.checked&&d(e,a,o,!1)})),e.checked&&d(e,a,o,!1)})),a.addEventListener("change",(t=>{a.checked?o.disabled=!0:o.disabled=!1;const s=e.querySelector('input[name*="['+this.options.privilege+']"]:checked');d(s,a,o,!0)})),o.addEventListener("click",(t=>{const n=o.closest("label");if(this.fieldset.querySelectorAll('[data-block="'+this.options.target+'"]:not([data-mod="remove"])').length<=1&&t.target.checked)return t.preventDefault(),e.removeAttribute("data-mod"),s.disabled=!1,t.target.disabled=!0,void window.alertbox.addItemMessage(window.alertbox.alertconfig.types.danger,e,this.keymessages.oneatleast,3e3);t.target.checked?(window.alertbox.hasItemMessages(s)&&window.alertbox.removeItemMessage(window.alertbox.alertconfig.types.danger,s),e.classList.contains("new")?e.remove():(n&&n.dataset.restore&&(n.dataset.title=n.dataset.restore),e.setAttribute("data-mod","remove"),i.forEach((e=>{e.dataset.checked=e.checked,e.checked=!1,e.disabled=!0})),a.checked=!1,a.disabled=!0,s.disabled=!0)):(n&&n.dataset.remove&&(n.dataset.title=n.dataset.remove),e.removeAttribute("data-mod"),i.forEach((e=>{e.disabled=!1,"true"===e.dataset.checked?e.checked=!0:e.checked=!1})),s.disabled=!1)})),o.addEventListener("mouseover",(t=>{if(t.target.disabled){let s=e.querySelector('input[name*="['+this.options.privilege+']"]:checked');if(!s)return;s=s.value.toLowerCase(),t.target.dataset.title=t.target.dataset[s]?t.target.dataset[s]:t.target.dataset.title}})),this.current_uid===s.value&&(o.disabled=!0)}validateFields(e=!1){const t=e=>e.value,s=e=>{const t=e.querySelector('[name*="['+this.options.privilege+']"]:checked');return!(!t||!t.value)},i=this.fieldset.querySelectorAll('[data-block="'+this.options.target+'"]');let a=i.length,n=!0;for(const e of i){const i=e.querySelector('[name*="['+this.options.ident+']"]');if(e.dataset.mod&&"remove"===e.dataset.mod){if(!(a>1))return!1;e.remove(),a--}else if(!t(i)){window.alertbox.addItemMessage(window.alertbox.alertconfig.types.danger,i,this.keymessages.emptyname),i.focus();if(!0!==!1)return!1;if(!(a>1))return!1;e.remove(),a--}s(e)?window.alertbox.hasItemMessages(e)&&window.alertbox.removeItemMessage(window.alertbox.alertconfig.types.danger,e,this.keymessages.uhasnopriv):(window.alertbox.addItemMessage(window.alertbox.alertconfig.types.danger,e,this.keymessages.uhasnopriv),n=!1)}if(0===a)return window.alertbox.renderAlert({type:window.alertbox.alertconfig.types.danger,content:this.keymessages.nobody,dismissible:!0,inverse:!0}),!1;window.alertbox.dismissAlert(this.keymessages.nobody);return(()=>{if(0===this.fieldset.querySelectorAll('[name*="['+this.options.privilege+']"][value="'+r.hp.manage+'"]:checked').length)return window.alertbox.renderAlert({type:window.alertbox.alertconfig.types.danger,content:this.keymessages.nomanager,dismissible:!0,inverse:!0}),this.tabError(!0),!1;window.alertbox.dismissAlert(this.keymessages.nomanager),this.tabError(!1);return null===this.fieldset.querySelector('[name="'+this.options.contactfieldname+'"]:checked')?(window.alertbox.renderAlert({type:window.alertbox.alertconfig.types.danger,content:this.keymessages.nocontact,dismissible:!0,inverse:!0}),this.tabError(!0),!1):(window.alertbox.dismissAlert(this.keymessages.nocontact),this.tabError(!1),!0)})()&&n}formatPrivileges(){const e=this.fieldset.querySelectorAll('[data-block="'+this.options.target+'"]'),t=e=>{e.querySelectorAll('[name*="members["').forEach((e=>{let t=e.name;t=t.split("["),t.pop(),e.name=t.join("["),e.name.indexOf("["+this.options.privilege+"]")>0&&(e.type="checkbox",e.classList.add("hidden"))}))};return e.forEach((e=>{t(e)})),!0}getLinePrivilege(e){let t=null;const s=this.fieldset.querySelectorAll('[data-block="'+this.options.target+'"]');for(const i of s)if(parseInt(i.querySelector('[name*="['+this.options.ident+']"]').value)===parseInt(e)){t=i;break}return t}clearAll(){this.fieldset.querySelectorAll('[data-block="'+this.options.target+'"]').forEach(((e,t)=>{e.remove()}))}orderRows(){const e=Array.from(this.fieldset.querySelectorAll('[data-block="'+this.options.target+'"]'));if(e.length>2)try{const t=Object.values(r.hp);e.sort(((e,s)=>{const i=this.getInputs(e),a=this.getInputs(s),n=new String(a.member.options[a.member.selectedIndex].text).toLowerCase().split(" "),r=new String(i.member.options[i.member.selectedIndex].text).toLowerCase().split(" "),o=Array.from(i.privs).filter((e=>e.checked)),l=Array.from(a.privs).filter((e=>e.checked)),d=+!i.contact.checked+" "+t.indexOf(o.length?o[0].value:null)+" "+(r.length>1?r.pop()+" "+r[0]:r[0]),c=+!a.contact.checked+" "+t.indexOf(l.length?l[0].value:null)+" "+(n.length>1?n.pop()+" "+n[0]:n[0]);return c>d?-1:d>c?1:0}));const s=this.linecontainer;e.forEach(((e,t)=>{s.appendChild(e)}))}catch(e){console.log("err not sorted",e)}}tabError(e){const t=this.fieldset.classList.contains(r.EY.component.tabs.tab.substr(1))?this.fieldset:this.fieldset.parentElement.classList.contains(r.EY.component.tabs.tab.substr(1))?this.fieldset.parentElement:null;null!==t&&(!0===e?t.classList.add(r.iv.error):t.classList.remove(r.iv.error))}}}}]);