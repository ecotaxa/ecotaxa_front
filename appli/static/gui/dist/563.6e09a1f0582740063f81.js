/*! For license information please see 563.6e09a1f0582740063f81.js.LICENSE.txt */
"use strict";(self.webpackChunk=self.webpackChunk||[]).push([[563],{3563:(t,e,a)=>{a.d(e,{JsTabs:()=>c});var s=a(2817);let l=null;class c{constructor(t,e={}){if(!l){let e=t.querySelectorAll(s.EY.component.tabs.tabcontrol);0===e.length&&(e=t.querySelectorAll(t.dataset.selector?t.dataset.selector:"legend")),this.toggledisable=!!t.dataset.toggledisable,this.togglewhat=t.dataset.togglewhat?t.dataset.togglewhat:null;let a=0;e.forEach(((e,l)=>{const c=e.dataset.target?t.querySelector("#"+e.dataset.target):e.closest(s.EY.component.tabs.tab);if(!c)return;const o=t.dataset.event?t.dataset.event:"click";e.style.left=a+"px",0===l&&0===c.parentElement.querySelectorAll("."+s.iv.active).length?(c.classList.add(s.iv.active),this.toggleTab(c,!0)):this.toggleTab(c,c.classList.contains(s.iv.active)),a+=parseInt(e.offsetWidth)+20,e.addEventListener(o,(e=>{if(!0===e.currentTarget.disabled)return void e.preventDefault();const a=t.dataset.selector?c.parentElement.querySelector("."+s.iv.active):t.querySelector(s.EY.component.tabs.tab+"."+s.iv.active);null!==a&&(a.classList.remove(s.iv.active),this.toggleTab(a,!1)),c.classList.add(s.iv.active),this.toggleTab(c,!0)}))})),t.dataset.toggle||this.toggleDisplayListener(t,e),l=this}return l}toggleTab(t,e){let a=this.togglewhat?document.getElementById(this.togglewhat):null,l=t.querySelectorAll(s.EY.component.tabs.tabcontent);0===l.length&&(l=[t]),l.forEach((l=>{if(!0===e?l.classList.remove(s.iv.hide):t.classList.contains("active")||l.classList.add(s.iv.hide),!0===this.toggledisable&&(l.querySelectorAll("input, select, button, textarea").forEach((t=>{e?(t.disabled=!1,t.dataset.checked&&(t.checked=t.dataset.checked,delete t.dataset.checked)):(t.disabled=!0,t.checked&&(t.dataset.checked=t.checked,t.removeAttribute("checked")))})),a&&(a.value=l.dataset.what),e)){const e=t.closest("form");l.dataset.path&&null!==e&&(e.setAttribute("action",l.dataset.path),window.history.replaceState({additionalInformation:"Updated by jsTabs"},document.title,window.location.origin+l.dataset.path+window.location.search))}}))}toggleDisplayListener(t,e){const a=t.querySelector('[data-dismiss="tabs"]'),l=(t,e,a)=>{e.disabled=a,this.toggleTab(e.closest(s.EY.component.tabs.tab),a)};a&&a.addEventListener("click",(a=>{const c=t.querySelector(".tabs-display");e.forEach(((e,a)=>l(0,e,t.classList.contains(s.iv.component.tabs.name)))),t.classList.toggle(s.iv.component.tabs.name),c.classList.toggle("expand"),c.classList.toggle("shrink")}))}}}}]);