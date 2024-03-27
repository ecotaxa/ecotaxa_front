/*! For license information please see 672.77a0e3b9c3564ba34d2f.js.LICENSE.txt */
"use strict";(self.webpackChunk=self.webpackChunk||[]).push([[672],{6672:(e,t,n)=>{n.d(t,{TaxoMapping:()=>c});var a=n(7856),s=n.n(a);const l="taxoline",i="mapping-line",d="cancel-line";class c{numlines=0;constructor(e){if(!(!e instanceof HTMLElement)){if(!e.taxomapping){const t=e.dataset.name?e.dataset.name:null;if(null===t)return null;this.keepname=t,this.init(e),e.taxomapping=this}return e.taxomapping}}init(e){if(e.dataset.addline){let t={};["select","replace"].forEach((n=>{t[n]=e.querySelector('[name="item-'+n+'"]')})),this.linecontrols=t,t=null;let n=e.querySelector("."+e.dataset.addline);n=null===n?this.createBtn(e):n,n.addEventListener("click",(t=>{this.addLine(e)})),this.btn=n}window.addEventListener("pageshow",(t=>{(event.persisted||void 0!==window.performance&&2===window.performance.navigation.type)&&this.beforeSubmit(e)})),this.beforeSubmit(e)}createBtn(e){const t=document.createElement("div");return t.classList.add(e.dataset.addline),t.insertAdjacentHTML("afterbegin",'<i class="icon icon-plus-sm block mx-auto"></i>'),t.textContent=e.dataset.addtext?s()(e.dataset.addtext).sanitize():"Add",e.append(t),t}addLine(e){let t=!0;if(Object.values(this.linecontrols).forEach((e=>{const n=e.tomselect?e.tomselect.items.length?e.tomselect.items[0]:"":new String(e.value);t=t&&n.length>0})),!1===t)return void(this.btn.dataset.title=e.dataset.notselected?e.dataset.notselected:"select values to replace");this.btn.dataset.title&&delete this.btn.dataset.title;const n=document.createElement("div");n.classList.add(l),n.classList.add("pb-2"),this.numlines++,Object.values(this.linecontrols).forEach((t=>{const a=document.createElement("div");if(a.classList.add(i),a.classList.add("mr-2"),t.tomselect){const n=e.querySelector(".ts-control > div");a.dataset.value=t.value,a.textContent=n.textContent,a.dataset.replace=this.numlines,t.tomselect.clear(!0)}else a.dataset.value=t.options[t.selectedIndex].value,a.textContent=t.options[t.selectedIndex].text,n.dataset.index=t.selectedIndex,a.dataset.select=this.numlines,t.options[t.selectedIndex].disabled=!0,t.selectedIndex=-1;t.parentElement.insertBefore(a,t),n.append(a)})),this.btnCancel(n,e.dataset.cancel?e.dataset.cancel:"cancel"),e.parentElement.insertBefore(n,e)}btnCancel(e,t){const n=document.createElement("div");n.id="cancel_"+this.numlines,n.classList.add(d),["action","name"].forEach((e=>{delete n.dataset[e]})),e.append(n),n.insertAdjacentHTML("afterbegin",'<i class="icon icon-cancel absolute centered"></i>'),n.addEventListener("click",(t=>{this.linecontrols.select.options[e.dataset.index].disabled=!1,e.remove()}))}beforeSubmit(e){const t=e.closest("form");if(null===t)return;const n=()=>{let e=t.querySelector('input[name="'+this.keepname+'"]');null!==e&&e.remove(),e=document.createElement("input"),e.type="hidden",e.name=this.keepname;let n={};return t.querySelectorAll("[data-select]").forEach((e=>{const t=e.parentElement.querySelector('[data-replace="'+e.dataset.select+'"]');null!==t&&(n[e.dataset.value]=t.dataset.value)})),t.append(e),e.value=JSON.stringify(n),!0};t.formsubmit?t.formsubmit.addHandler("submit",n):t.addEventListener("submit",(e=>{n()}))}}}}]);