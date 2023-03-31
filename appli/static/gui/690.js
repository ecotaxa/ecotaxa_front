(self.webpackChunk=self.webpackChunk||[]).push([[690,615],{3583:()=>{},615:(e,t,s)=>{"use strict";s.r(t),s.d(t,{FormSubmit:()=>r});var i=s(7856),a=s.n(i);let l=null;const n="invalid",o="input-validate";class r{handlers=[];form=null;listener=null;constructor(e,t={}){if(!l){if(!e)return;const s={};this.options=Object.assign(s,t),this.form=e instanceof HTMLElement?e:document.querySelector(e),this.validateFields(!0),this.init(),l=this}return l}init(){this.form.addEventListener("submit",(async e=>{console.log("----------------formsubmit",e);const t=await this.submitForm();return t||e.preventDefault(),t})),this.form.querySelectorAll("input[data-match]").forEach((e=>{const t=e.dataset.match;if(!t)return;const s=document.getElementById(t);if(!s)return;const i=e.dataset.matchinvalid?e.dataset.matchinvalid:"no match",a=e.closest("label");[e,s].forEach((t=>{t.addEventListener("keyup",(l=>{((t,s)=>{t.value!==s.value?(t.setCustomValidity(i),s.setCustomValidity(i),e!=t&&(a&&a.classList.add(n),e.classList.add(o))):(t.setCustomValidity(""),s.setCustomValidity(""),t.dataset.invalid="",s.dataset.invalid="",e!=t&&(a&&a.classList.remove(n),e.classList.remove(o))),t.reportValidity(),s.reportValidity(),t.focus()})(t,t===e?s:e)}))}))}))}validateField(e){e.value=a().sanitize(e.value);const t=e.checkValidity(),s=e.closest(".form-box")?e.closest(".form-box").querySelector("label"):null;return t&&s?s.classList.remove(n):t||s&&(s.dataset.invalid=(e=>{let t="invalid";return e.required&&(t=e.dataset.required?e.dataset.required:this.form.dataset.required?this.form.dataset.required:"invalid"),"invalid"===t&&(t=e.dataset.invalid?e.dataset.invalid:this.form.dataset.invalid?this.form.dataset.invalid:"invalid input"),t})(e),s.classList.add(n)),e.classList.contains("tomselected")&&e.nextElementSibling?e.nextElementSibling.classList.add(o):e.classList.add(o),t}validateFields(e=!1){let t=!0;return this.form.querySelectorAll("input,textarea, select").forEach((s=>{if(!0===e)s.dataset.listen||(["change","blur"].forEach((e=>{s.addEventListener(e,(e=>{this.validateField(e.currentTarget)}))})),s.dataset.listen=!0);else{const e=this.validateField(s);t=t&&e}})),t}addHandler(e){this.handlers.push(e)}fieldEnable(){this.form.querySelectorAll('input[data-sub="enable"]').forEach((e=>{e.removeAttribute("disabled")}))}async submitHandler(){if(!this.validateFields())return!1;if(0===this.handlers.length)return!0;let e=!0;return await Promise.all(this.handlers.map((async t=>{const s=await t();e=e&&s}))),!0===e&&(this.handlers=[]),console.log("resp",e),e}async submitForm(){return!!this.validateFields(!1)&&(!!await this.submitHandler()&&(this.fieldEnable(),void this.form.submit()))}}},2627:(e,t,s)=>{"use strict";s.r(t),s.d(t,{JsTomSelect:()=>A});var i=s(7856),a=s.n(i),l=s(6031),n=s.n(l),o=s(3379),r=s.n(o),d=s(7795),c=s.n(d),u=s(569),m=s.n(u),h=s(3565),p=s.n(h),v=s(9216),f=s.n(v),b=s(4589),g=s.n(b),y=s(3583),k=s.n(y),S={};S.styleTagTransform=g(),S.setAttributes=p(),S.insert=m().bind(null,"head"),S.domAPI=c(),S.insertStyleElement=f(),r()(k(),S),k()&&k().locals&&k().locals;var q=s(9162),x=s(2817);let E={};class A{applyTo(e,t=null){const s=e.getAttribute("id"),i=e.hasAttribute("multiple"),l=e.dataset.type;let o={url:"",settings:{}},r=t=>{t.addEventListener("click",(t=>{const s=t.currentTarget.closest(x.EY.component.tomselect.item).dataset.value;s&&(t.stopImmediatePropagation(),e.tomselect.removeItem(s))}))};switch(l){case x.Cq.project:o.url="/gui/prjlist/",o.settings={valueField:"id",searchField:"text",labelField:"text",openOnFocus:!1,maxItems:1,allowEmptyOption:!1,onItemAdd:function(t){if(t!=e.dataset.value){let e=window.location.href.split("/");e.pop(),e=e.join("/")+"/"+t,window.open(e,"_blank").focus()}this.removeItem(t)}};break;case x.Cq.user:o.url="/api/users/search?by_name=",o.settings={valueField:"id",searchField:"name",labelField:"name",onInitialize:function(){e.tomselect.items.forEach((e=>{E[e]=!0}))},onItemAdd:function(t){if(E[t]){if(!this.revertSettings||this.revertSettings.tabIndex<0||!e.querySelectorAll("option"))return;const s=e.querySelectorAll("option")[this.revertSettings.tabIndex].value;this.removeOption(t),this.addItem(s),E[t]=!1}else E[t]=!0},onItemRemove:function(t){if(E[t]&&delete E[t],!this.revertSettings||this.revertSettings.tabIndex<0)return;const s=e.querySelectorAll("option")[this.revertSettings.tabIndex].value;void 0!==E[s]&&delete E[s]}};break;case x.Cq.instr:o.url="/search/instruments",o.settings={valueField:"id",labelField:"text",searchField:"id",maxItems:1,preload:!0};break;case x.Cq.taxo:n().define("no_close",(()=>{this.close=()=>{}})),o.url="/search/taxo",o.settings={valueField:"id",labelField:"text",searchField:"text",onInitialize:()=>{const e=document.getElementById(s).nextElementSibling;e.classList.contains("ts-wrapper")&&e.querySelectorAll(x.EY.component.tomselect.tsdelet).forEach((e=>{r(e)}))}}}const d={create:!1,maxOptions:null,preload:!1,hideSelected:!0,duplicates:!1,allowEmptyOption:!0,closeAfterSelect:!0,placeholder:e.placeholder?e.placeholder:e.dataset.placeholder?e.dataset.placeholder:"",onDropdownClose:function(){},shouldLoad:function(e){return e.length>2},load:function(e,t){if(e=a().sanitize(e),this.loading>10)return void t();let s="";switch(l){case x.Cq.user:s=o.url+encodeURIComponent("%"+e+"%");break;case x.Cq.instr:case x.Cq.taxo:s=o.url,e&&(s+="?q="+encodeURIComponent(e));break;case x.Cq.project:s=o.url,e&&(s+="?filt_title="+encodeURIComponent(e))}null!==s&&fetch(s,(0,q.fetchSettings)()).then((e=>e.json())).then((e=>(l===x.Cq.project&&e.data&&e.data.length&&(e=e.data.map((e=>({id:e[1],text:e[3][0]})))),l===x.Cq.instr&&e.length&&(e=e.reduce(((e,t,s)=>{let i={id:t=a().sanitize(t),text:t};return e.push(i),e}),[])),e.length&&"object"==typeof e&&(e=Object.entries(e)),t(e)))).catch((e=>{console.log("tomselect-err",e)}))},render:{option:function(e,t){if(null==e)return"";const s=e.optgroup?`data-optgroup=${e.optgroup}`:"";return`<div class="py-2 flex  ${i?"inline-flex":""} " ${s} data-value="${e[o.settings.valueField]}">${t(e[this.settings.labelField])}</div>`},item:function(e,t){if(null==e)return"";const s=e.optgroup?`item-${e.optgroup}`:"",l=i?`<i class="${x.EY.component.tomselect.tsdelet.substr(1)}"></i>`:"";return a().sanitize('<div class="'+(i?"flex inline-flex ":"")+` ${s}" data-value="${e[this.settings.valueField]}">${t(e[this.settings.labelField])} ${l}</div>`)},no_results:function(t,s){return a().sanitize('<div class="no-results">'+(e.dataset.noresults?e.dataset.noresults:"No result found for ")+s(t.input)+"</div>")}}};if(o.settings=Object.assign(d,o.settings),null!==s){const t=new(n())("#"+s,o.settings);switch(t.wrapper.classList.remove(x.EY.component.tomselect.ident),t.wrapper.classList.remove("js"),t.wrapper.setAttribute("data-component","tom-select"),l){case"taxo":t.on("item_add",((e,t)=>{null!==t&&t.classList.add("new"),null!==(t=t.querySelector(".ts-delet"))&&r(t)}));break;case"user":e.dataset.priv&&t.on("item_add",(function(e,t){null!==(t=t.querySelector(x.EY.component.tomselect.tsdelet))&&r(t)}))}return t}console.log("noid")}}},5690:(e,t,s)=>{"use strict";s.r(t),s.d(t,{ProjectPrivileges:()=>u});var i=s(7856),a=s.n(i),l=s(615),n=s(4672),o=s(2627),r=s(2817);const d={oneatleast:"oneatleast",nomanager:"nomanager",nocontact:"nocontact",uhasnopriv:"uhasnopriv",importpriverror:"importpriverror",emptyname:"emptyname"};let c=null;class u{options;alertBox;current_uid;fieldset;fieldset_alert_zone;constructor(e={}){if(!c){const t={groupid:"#section-privileges",separ:".new-privilege",addbtn:'[data-add="block"]',target:"member",ident:"member",privilege:"privilege",delet:"delet",contact:"contact",contactfieldname:"contact_user_id"};if(this.options=Object.assign({},t,e),this.fieldset=document.querySelector(this.options.groupid),!this.fieldset)return;this.fieldset_alert_zone=this.fieldset.querySelector(".tab-content")?this.fieldset.querySelector(".tab-content"):this.fieldset,this.options.separ=this.options.separ instanceof HTMLElement?this.options.separ:document.querySelector(this.options.separ)?document.querySelector(this.options.separ):null,this.options.addbtn=this.options.addbtn instanceof HTMLElement?this.options.addbtn:document.querySelector(this.options.addbtn),this.options.addbtn&&this.addListener();const s=this.fieldset.querySelectorAll('[data-block="'+this.options.target+'"]');this.current_uid=this.fieldset.dataset.u,this.alertBox=new n.AlertBox,s.forEach((e=>{this.activateEvents(e)}));const i=this.fieldset.closest("form"),a=async()=>await this.cleanPrivileges();new l.FormSubmit(i).addHandler(a),c=this}return c}newLine(e=!1,t=0){let s;if(t>0&&(s=this.getLinePrivilege(t),s))return s;const i=this.fieldset.querySelectorAll('[data-block="'+this.options.target+'"]');if(0===i.length)return;const a=i.length-1;return s=i[a],null!==s&&(s=this.clearLine(s.cloneNode(!0),a,this.options.separ?this.options.separ:s),this.activateEvents(s)),!0===e?s:void 0}addListener(){this.options.target=this.options.addbtn.dataset.target?this.options.addbtn.dataset.target:this.options.target,this.options.addbtn.addEventListener("click",(async e=>{e.preventDefault(),this.newLine()}))}clearLine(e,t,s=null){let i=null;if(e.dataset.mod="",e.disabled=!1,e.querySelectorAll("[data-elem]").forEach((e=>{e.querySelectorAll("[data-component]").forEach((e=>{"tom-select"===e.dataset.component&&e.remove()})),e.querySelectorAll("input, select, label").forEach((e=>{switch(e.disabled=!1,s&&["id","for","aria-controls","name"].forEach((s=>{let i=e.getAttribute(s);null!==i&&(i="name"===s?i.replace("["+t+"]","["+(t+1)+"]"):i.replace("_"+t,"_"+(t+1)),e.setAttribute(s,i))})),e.tagName.toLowerCase()){case"input":e.checked=!1,e.name==this.options.contactfieldname&&(e.value="0",e.disabled=!0);break;case"select":e.selectedIndex=-1;break;case"label":e.classList.remove(r.iv.peerchecked)}e.tomselect&&(i=e,e.tomselect.clear(),e.tomselect.destroy()),e.classList.contains(r.iv.component.autocomplete.tomselected)&&(i=e,e.classList.forEach((t=>{0==t.indexOf("ts-")&&e.classList.remove(t)})),e.classList.remove(r.iv.component.autocomplete.tomselected),"select-one"==e.type&&delete e.type)}))})),s&&(e.classList.add("new"),s.after(e)),null!==i){(new o.JsTomSelect).applyTo(i),i.tomselect.clearOptions();let e=this.fieldset.dataset.options;e=e||[],i.tomselect.addOptions(e)}return e}setLine(e,t={key:"",value:""},s,i){if(!(s=r.HN[s]?r.HN[s]:r.HN.viewers))return;const{member:l,privs:n,contact:o,delet:d}=this.getInputs(e,s);if(l&&n&&o&&d){if(t.key=a().sanitize(t.key),t.value=a().sanitize(t.value),l.tomselect){let e={};e[l.tomselect.settings.valueField]=t.key,e[l.tomselect.settings.labelField]=t.value,l.tomselect.getOption(t.key)||l.tomselect.addOption(e),l.tomselect.addItem(t.key,!1),l.tomselect.refreshOptions()}else{const e=l.querySelector('select option[value="'+t.key+'"]');e?e.selected=!0:l.insertAdjacentHTML("beforeend",'<option value="'+t.key+'" selected>'+t.value+"</option>")}n.checked=!0,o.value=t.key,s===r.hp.manage&&(o.disabled=!1,!0===i&&(o.checked=!0))}}getInputs(e,t=!1){const s=e.querySelector("[name*='["+this.options.ident+"]']");let i;return i=t?e.querySelector('input[name*="['+this.options.privilege+']"][value="'+t+'"]'):e.querySelectorAll('input[name*="['+this.options.privilege+']"]'),{member:s,privs:i,contact:e.querySelector('input[name="'+this.options.contactfieldname+'"]'),delet:e.querySelector("input[name*='["+this.options.delet+"]']")}}async importPrivileges(e,t=!1,s=null,i=null,a=null){let l=!0!==t||null;try{return Object.entries(e).forEach((([e,t])=>{t.forEach((t=>{l=l?this.newLine(!0,t.id):this.clearAll(!0),l&&(this.setLine(l,{key:t.id,value:t.name},e,s&&parseInt(s.id)===parseInt(t.id)),i&&i(l),a&&a())}))})),this.alertBox.dismissAlert(d.importpriverror),!0}catch(e){return await this.alertBox.build({dismissible:!0,message:d.importpriverror,codeid:!0,parent:this.fieldset_alert_zone,type:r.iN.danger}),console.log("err",e),!1}}activateEvents(e){if(!e)return;const{member:t,privs:s,contact:i,delet:a}=this.getInputs(e);if(!(t&&s&&i&&a))return;const l=e=>[...e.parentElement.children].filter((t=>1==t.nodeType&&t!=e&&t.classList.contains("row")&&null!==t.dataset.block&&t.dataset.block===this.options.target)),n=(t,s,i,a=!1)=>{t&&t.value===r.hp.manage?(i.disabled=!0,s.disabled=!1,this.alertBox.dismissAlert(d.nomanager),s.checked&&this.alertBox.dismissAlert(d.nocontact)):(s.checked=!1,i.disabled=!1,s.disabled=!0),!0===a&&o(e),i.ckecked||(this.alertBox.dismissAlert(d.nobody),this.alertBox.dismissAlert(d.oneatleast))},o=e=>{l(e).forEach((e=>{const t=e.querySelector("input[name*='["+this.options.delet+"]']"),s=e.querySelector('input[name="'+this.options.contactfieldname+'"]'),i=e.querySelector('input[name*="['+this.options.privilege+']"]:checked');n(i,s,t,!1)}))};t.addEventListener("change",(e=>{i.value=t.value,t.value&&(this.alertBox.dismissAlert(d.emptyname),this.alertBox.dismissAlert(d.oneatleast),this.alertBox.dismissAlert(d.nobody))})),s.forEach((e=>{e.addEventListener("change",(t=>{e.checked&&n(e,i,a,!1)})),e.checked&&n(e,i,a,!1)})),i.addEventListener("change",(t=>{t.target.checked?a.disabled=!0:a.disabled=!1;const s=e.querySelector('input[name*="['+this.options.privilege+']"]:checked');n(s,i,a,!0)})),a.addEventListener("click",(l=>{const n=a.closest("label");if(this.fieldset.querySelectorAll('[data-block="'+this.options.target+'"]:not([data-mod="remove"])').length<=1&&l.target.checked)return a.disabled=!0,a.checked=!1,void this.alertBox.build({dismissible:!0,message:d.oneatleast,codemessage:d.oneatleast,type:r.iN.warning,parent:l.currentTarget.id||null});l.target.checked?(this.alertBox.dismissAlert(d.oneatleast),e.classList.contains("new")?e.remove():(n&&n.dataset.restore&&n.setAttribute("title",n.dataset.restore),e.setAttribute("data-mod","remove"),s.forEach((e=>{e.disabled=!0,e.checked=!1})),i.checked=!1,i.disabled=!0,t.disabled=!0)):(n&&n.dataset.remove&&n.setAttribute("title",n.dataset.remove),e.removeAttribute("data-mod"),s.forEach((e=>e.disabled=!1)),i.disabled=!1,t.disabled=!1)})),a.addEventListener("mouseover",(t=>{if(t.target.disabled){let s=e.querySelector('input[name*="['+this.options.privilege+']"]:checked');if(!s)return;s=s.value.toLowerCase(),t.target.title=t.target.dataset[s]?t.target.dataset[s]:t.target.title}})),this.current_uid===t.value&&(a.disabled=!0)}async cleanPrivileges(){const e=e=>e.querySelector('[name*="['+this.options.ident+']"]').value,t=e=>{const t=e.querySelector('[name*="['+this.options.privilege+']"]:checked');return!(!t||!t.value)},s=e=>{e.querySelectorAll('[name*="members["').forEach((e=>{let t=e.name;t=t.split("["),t.pop(),e.name=t.join("["),e.name.indexOf("["+this.options.privilege+"]")>0&&(e.type="checkbox",e.classList.add("hidden"))}))};if(!0===await(async()=>0===this.fieldset.querySelectorAll('[name*="['+this.options.privilege+']"][value="'+r.hp.manage+'"]:checked').length?(await this.alertBox.build({dismissible:!0,message:d.nomanager,codeid:!0,type:r.iN.danger,parent:this.fieldset_alert_zone}),!1):(this.alertBox.dismissAlert(d.nomanager),null===this.fieldset.querySelector('[name="'+this.options.contactfieldname+'"]:checked')?(await this.alertBox.build({dismissible:!0,codeid:!0,message:d.nocontact,type:r.iN.danger,parent:this.fieldset_alert_zone}),!1):(this.alertBox.dismissAlert(d.nocontact),!0)))()){const i=this.fieldset.querySelectorAll('[data-block="'+this.options.target+'"]');let a=i.length,l=!0;for(const s of i)if(s.dataset.mod&&"remove"===s.dataset.mod){if(!(a>1))return!1;s.remove(),a--}else{if(!e(s)){const e=s.querySelector('[name*="['+this.options.ident+']"]');return e.focus(),e.tomselect&&e.tomselect.focus(),await this.alertBox.build({dismissible:!0,insertafter:!0,message:d.emptyname,codeid:!0,type:r.iN.warning,parent:s}),!1}t(s)?this.alertBox.dismissAlert(d.uhasnopriv):(this.alertBox.dismissAlert(d.emptyname),await this.alertBox.build({dismissible:!0,insertafter:!0,codeid:!0,message:d.uhasnopriv,type:r.iN.warning,parent:s}),l=!1)}if(!l)return l;for(const e of i)s(e);return 0===a?(await this.alertBox.build({dismissible:!0,codeid:!0,message:d.nobody,type:r.iN.warning,parent:this.fieldset_alert_zone}),!1):(this.alertBox.dismissAlert(d.nobody),!0)}return!1}getLinePrivilege(e){let t=null;const s=this.fieldset.querySelectorAll('[data-block="'+this.options.target+'"]');for(const i of s)if(parseInt(i.querySelector('[name*="['+this.options.ident+']"]').value)===parseInt(e)){t=i;break}return t}clearAll(e=!1){const t=this.fieldset.querySelectorAll('[data-block="'+this.options.target+'"]');if(t.forEach(((e,t)=>{const{member:s,privs:i,contact:a,delet:l}=this.getInputs(e);t>0&&this.current_uid!==s.value&&e.remove()})),this.clearLine(t[0],0),this.activateEvents(t[0]),!0===e)return t[0]}}}}]);