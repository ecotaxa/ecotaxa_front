/*! For license information please see 329.f9e65b916f14d5f175fc.js.LICENSE.txt */
"use strict";(self.webpackChunk=self.webpackChunk||[]).push([[329],{329:(e,t,i)=>{i.d(t,{JsDetail:()=>d});var s=i(2838),l=i.n(s),a=i(7114),n=i(4860);function d(e){let t,i,s,d=null;function o(s){const l=e.istable?s.closest("td"):s,n=s.closest(".overflow");return n&&(n.classList.remove("overflow"),n.style.maxWidth=n.dataset.maxw),l.style.minHeight="none",l.style.height="auto",l.style.overflow=s.style.overflowX=s.parentElement.style.overflowX="hidden",i.classList.add(a.AH.hide),t.append(i),d=null,d}return e={istable:!0,over:!1,waitdiv:null,...e},Object.freeze(e),{applyTo:function(l,d){if(d instanceof HTMLElement&&(t=d,t.classList.add(a.AH.relative),!(l instanceof HTMLElement)))return i=(0,n.xJ)("div",{id:l,class:a.AH.hide},t),e.waitdiv&&(e.waitdiv.textContent=e.waitdiv.dataset.wait?e.waitdiv.dataset.wait:a.lr.wait,i.append(e.waitdiv)),s=(0,n.xJ)("div",{},i),i},activeDetail:function(t,s=!1){return!0===t?(i.lastElementChild.innerHTML="",i.classList.remove(a.AH.hide),e.waitdiv&&e.waitdiv.classList.remove(a.AH.hide)):(i.classList.add(a.AH.hide),e.waitdiv&&e.waitdiv.classList.add(a.AH.hide),d&&o(d),!0===s&&(i.lastElementChild.innerHTML=""),d=null),d},expandDetail:function(n,r=null){d&&d!==n&&o(d),d=n,e.waitdiv&&e.waitdiv.classList.add(a.AH.hide),null!==r&&(s.innerHTML=l().sanitize(r)),n.append(i);const f=e.istable?n.closest("td"):n;let v=e.istable?parseInt(t.querySelector("table").offsetTop):0;v=v+(parseInt(f.offsetTop)+parseInt(n.offsetHeight)+6)+"px";const c=parseInt(f.offsetHeight)+parseInt(i.offsetHeight)+6+"px",h=parseInt(t.offsetWidth)+"px";return requestAnimationFrame((()=>{i.style.minWidth=h,i.style.width=h,f.style.overflow="visible",n.style.overflowX="visible",i.style.top=v,f.style.minHeight=c,f.style.height=c})),d}}}}}]);