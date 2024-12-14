/*! For license information please see 912.c2cbf4e713761b7b0814.js.LICENSE.txt */
"use strict";(self.webpackChunk=self.webpackChunk||[]).push([[912],{8912:(e,t,s)=>{s.d(t,{JSONTree:()=>o});const i=void 0===window.Emitter?class{constructor(){this.events={}}on(e,t){this.events[e]=this.events[e]||[],this.events[e].push(t)}once(e,t){t.once=!0,this.on(e,t)}emit(e,...t){if(void 0!==this.events[e])for(const s of[...this.events[e]])if(s(...t),s.once){const t=this.events[e].indexOf(s);this.events[e].splice(t,1)}}}:window.Emitter;class n extends i{constructor(e,t={}){super(),e.addEventListener("click",(e=>{if(e&&e.clientX&&1===e.detail&&e.offsetX>=0)return e.preventDefault();const s=this.active();s&&s.dataset.type===n.FILE&&(e.preventDefault(),this.emit("action",s),!0===t["no-focus-on-action"]&&window.clearTimeout(this.id))})),e.classList.add("simple-tree"),t.dark&&e.classList.add("dark"),this.parent=e.appendChild(document.createElement("details")),this.parent.appendChild(document.createElement("summary")),this.parent.open=!0,this.interrupt=e=>e}append(e,t,s,i=()=>{}){return s?t.insertBefore(e,s):t.appendChild(e),i(),e}remove(e){if(e.dataset.type===n.FILE)e.remove();else{e.closest("details").remove()}this.emit("removed",e)}file(e,t=this.parent,s){t=t.closest("details"),e=this.interrupt(e);const i=this.append(Object.assign(document.createElement("a"),{textContent:e.name,href:"#",id:e.id}),t,s);return i.dataset.type=n.FILE,this.emit("created",i,e),i}folder(e,t=this.parent,s){t=t.closest("details"),e=this.interrupt(e);const i=document.createElement("details"),r=Object.assign(document.createElement("summary"),{textContent:e.name});return i.appendChild(r),this.append(i,t,s,(()=>{i.open=e.open,i.dataset.type=n.FOLDER})),this.emit("created",r,e),r}open(e){e.open=!0}hierarchy(e=this.active()){if(this.parent.contains(e)){const t=[];for(;e!==this.parent;)e.dataset.type===n.FILE?t.push(e):e.dataset.type===n.FOLDER&&t.push(e.querySelector("summary")),e=e.parentElement;return t}return[]}getPath(e,t="/"){return this.hierarchy(e).map((e=>e.textContent)).reverse().join(t)}siblings(e=this.parent.querySelector("a, details")){return this.parent.contains(e)?(void 0===e.dataset.type&&(e=e.parentElement),[...e.parentElement.children].filter((e=>e.dataset.type===n.FILE||e.dataset.type===n.FOLDER)).map((e=>e.dataset.type===n.FILE?e:e.querySelector("summary")))):[]}children(e){const t=e.querySelector("a, details");return t?this.siblings(t):[]}}n.FILE="file",n.FOLDER="folder";class r extends n{constructor(e,t){super(e,t),e.addEventListener("click",(e=>{const t=e.target.parentElement;t.open&&"false"===t.dataset.loaded&&e.preventDefault()})),e.classList.add("async-tree")}folder(...e){const t=super.folder(...e),s=t.closest("details");return s.addEventListener("toggle",(i=>{this.emit("false"===s.dataset.loaded&&s.open?"fetch":"open",t,e[0])})),t.resolve=()=>{s.dataset.loaded=!0,this.emit("open",t)},t}asyncFolder(e,t,s){const i=this.folder(e,t,s),n=i.closest("details");return n.dataset.loaded=!1,e.open&&this.open(n),i}unloadFolder(e){const t=e.closest("details");t.open=!1;const s=this.active();s&&this.parent.contains(s)&&this.select(t),[...t.children].slice(1).forEach((e=>e.remove())),t.dataset.loaded=!1}browse(e,t=this.siblings()){for(const s of t)if(e(s)){if(this.select(s),s.dataset.type===n.FILE)return this.emit("browse",s);const t=s.closest("details");return t.open?this.browse(e,this.children(t)):void window.setTimeout((()=>{this.once("open",(()=>this.browse(e,this.children(t)))),this.open(t)}),0)}this.emit("browse",!1)}}class a extends r{constructor(e,t={}){super(e,t),e.addEventListener("click",(e=>{if(e.detail>1){const t=this.active();if(t&&t!==e.target&&("A"===e.target.tagName||"SUMMARY"===e.target.tagName))return this.select(e.target,"click");t&&this.focus(t)}})),window.addEventListener("focus",(()=>{const e=this.active();e&&this.focus(e)})),e.addEventListener("focusin",(e=>{this.active()!==e.target&&this.select(e.target,"focus")})),this.on("created",((e,t)=>{t.selected&&this.select(e)})),e.classList.add("select-tree"),t.navigate&&this.parent.addEventListener("keydown",(e=>{const{code:t}=e;"ArrowUp"!==t&&"ArrowDown"!==t||(this.navigate("ArrowUp"===t?"backward":"forward"),e.preventDefault())}))}focus(e){window.clearTimeout(this.id),this.id=window.setTimeout((()=>document.hasFocus()&&e.focus()),100)}select(e){const t=e.querySelector("summary");t&&(e=t),[...this.parent.querySelectorAll(".selected")].forEach((e=>e.classList.remove("selected"))),e.classList.add("selected"),this.focus(e),this.emit("select",e)}active(){return this.parent.querySelector(".selected")}navigate(e="forward"){const t=this.active();if(t){const s=[...this.parent.querySelectorAll("a, summary")],i=s.indexOf(t),n="forward"===e?s.slice(i+1):s.slice(0,i).reverse();for(const e of n)if(e.getBoundingClientRect().height)return this.select(e)}}}class o extends a{json(e,t){"boolean"!=typeof e&&e.forEach((e=>{if(e.type===n.FOLDER||!0===e.children){const s=this[e.asynced||!0===e.children?"asyncFolder":"folder"](e,t);e.children&&this.json(e.children,s)}else this.file(e,t)}))}}}}]);