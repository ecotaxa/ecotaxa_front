/*! For license information please see 598.js.LICENSE.txt */
"use strict";(self.webpackChunk=self.webpackChunk||[]).push([[598],{9941:(t,i,e)=>{e.d(i,{JsDetail:()=>h});var s=e(7856),a=e.n(s),l=e(2817);let n=null;class h{current=null;constructor(t,i,e={}){if(null===n){const s={istable:!0,over:!1,waitdiv:null};this.options=Object.assign(s,e),Object.freeze(this.options),this.wrapper=i,this.detail=t,this.init(),n=this}return n}init(){if(this.detail instanceof HTMLElement)return;const t=document.createElement("div");t.id=this.detail,t.classList.add(l.iv.hide),this.options.waitdiv&&(this.options.waitdiv.textContent=this.options.waitdiv.dataset.wait?this.options.waitdiv.dataset.wait:l.WL.wait,t.append(this.options.waitdiv)),t.append(document.createElement("div")),this.detail=t,this.wrapper.classList.add("relative"),this.wrapper.append(this.detail)}expandDetail(t,i=null){this.current&&this.current!==t&&this.shrinkDetail(this.current),this.current=t,this.options.waitdiv&&this.options.waitdiv.classList.add(l.iv.hide),null!==i&&(this.detail.lastElementChild.innerHTML=a().sanitize(i));const e=this.options.istable?t.closest("td"):t,s=this.options.istable?parseInt(this.wrapper.querySelector("table").offsetTop):0,n=parseInt(e.offsetHeight)+parseInt(this.detail.offsetHeight)+6,h=parseInt(this.wrapper.offsetWidth);this.detail.style.minWidth=this.detail.style.width=h+"px",e.style.overflow=t.style.overflowX="visible",this.detail.style.top=s+parseInt(e.offsetTop)+parseInt(t.offsetHeight)+6+"px",e.style.minHeight=e.style.height=n+"px"}shrinkDetail(t){const i=this.options.istable?t.closest("td"):t,e=t.closest(".overflow");e&&(e.classList.remove("overflow"),e.style.maxWidth=e.dataset.maxw),i.style.minHeight="none",i.style.height="auto",i.style.overflow=t.style.overflowX=t.parentElement.style.overflowX="hidden",this.detail.classList.add(l.iv.hide),this.wrapper.append(this.detail),this.current=null}activeDetail(t,i=!1){!0===t?(this.detail.lastElementChild.innerHTML="",this.detail.classList.remove(l.iv.hide),this.options.waitdiv&&this.options.waitdiv.classList.remove(l.iv.hide)):(this.detail.classList.add(l.iv.hide),this.options.waitdiv&&this.options.waitdiv.classList.add(l.iv.hide),this.current&&this.shrinkDetail(this.current),!0===i&&(this.detail.lastElementChild.innerHTML=""),this.current=null)}}}}]);