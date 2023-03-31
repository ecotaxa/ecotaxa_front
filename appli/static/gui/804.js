"use strict";(self.webpackChunk=self.webpackChunk||[]).push([[804,615],{615:(e,t,i)=>{i.r(t),i.d(t,{FormSubmit:()=>l});var s=i(7856),n=i.n(s);let o=null;const a="invalid",r="input-validate";class l{handlers=[];form=null;listener=null;constructor(e,t={}){if(!o){if(!e)return;const i={};this.options=Object.assign(i,t),this.form=e instanceof HTMLElement?e:document.querySelector(e),this.validateFields(!0),this.init(),o=this}return o}init(){this.form.addEventListener("submit",(async e=>{console.log("----------------formsubmit",e);const t=await this.submitForm();return t||e.preventDefault(),t})),this.form.querySelectorAll("input[data-match]").forEach((e=>{const t=e.dataset.match;if(!t)return;const i=document.getElementById(t);if(!i)return;const s=e.dataset.matchinvalid?e.dataset.matchinvalid:"no match",n=e.closest("label");[e,i].forEach((t=>{t.addEventListener("keyup",(o=>{((t,i)=>{t.value!==i.value?(t.setCustomValidity(s),i.setCustomValidity(s),e!=t&&(n&&n.classList.add(a),e.classList.add(r))):(t.setCustomValidity(""),i.setCustomValidity(""),t.dataset.invalid="",i.dataset.invalid="",e!=t&&(n&&n.classList.remove(a),e.classList.remove(r))),t.reportValidity(),i.reportValidity(),t.focus()})(t,t===e?i:e)}))}))}))}validateField(e){e.value=n().sanitize(e.value);const t=e.checkValidity(),i=e.closest(".form-box")?e.closest(".form-box").querySelector("label"):null;return t&&i?i.classList.remove(a):t||i&&(i.dataset.invalid=(e=>{let t="invalid";return e.required&&(t=e.dataset.required?e.dataset.required:this.form.dataset.required?this.form.dataset.required:"invalid"),"invalid"===t&&(t=e.dataset.invalid?e.dataset.invalid:this.form.dataset.invalid?this.form.dataset.invalid:"invalid input"),t})(e),i.classList.add(a)),e.classList.contains("tomselected")&&e.nextElementSibling?e.nextElementSibling.classList.add(r):e.classList.add(r),t}validateFields(e=!1){let t=!0;return this.form.querySelectorAll("input,textarea, select").forEach((i=>{if(!0===e)i.dataset.listen||(["change","blur"].forEach((e=>{i.addEventListener(e,(e=>{this.validateField(e.currentTarget)}))})),i.dataset.listen=!0);else{const e=this.validateField(i);t=t&&e}})),t}addHandler(e){this.handlers.push(e)}fieldEnable(){this.form.querySelectorAll('input[data-sub="enable"]').forEach((e=>{e.removeAttribute("disabled")}))}async submitHandler(){if(!this.validateFields())return!1;if(0===this.handlers.length)return!0;let e=!0;return await Promise.all(this.handlers.map((async t=>{const i=await t();e=e&&i}))),!0===e&&(this.handlers=[]),console.log("resp",e),e}async submitForm(){return!!this.validateFields(!1)&&(!!await this.submitHandler()&&(this.fieldEnable(),void this.form.submit()))}}},8804:(e,t,i)=>{i.r(t),i.d(t,{JsUpload:()=>l}),i(7856);var s=i(3778),n=(i(615),i(9162)),o=i(2817);const a=new Set(["zip","gz","png","jpg","jpeg","pdf","doc","docx","ppt","pptx","xls","xlsx","heic","heif","7z","bz2","rar","gif","webp","webm","mp4","mov","mp3","aifc"]);let r=null;class l{zipstream;zipsize=0;pathname;zipname;counter=0;counterdisplay=null;ziptrigger=null;displaylist=null;timer=0;targetdir="";dropzone;constructor(e,t=null,i={}){return r||((e=e instanceof HTMLElement?e:document.querySelector(e))?(this.container=e,this.callback=t,this.options=Object.assign({level:0,url:"http://193.49.112.116:5001/gui/job/my_files/",filefield:"file",selector:{makezip:".makezip",droptarget:".droptarget",trigger:".trigger",uploadfile:"uploadfile",formu:"formupload",stepper:"stepper",stepitem:"stepper-item",filetoload:"file_to_load",progress:"progress-upload"},display:{dropzone:"dropzone",counter:"counter",size:"sizetozip",counterzipped:"counterzipped",sizezipped:"sizezipped",dirlist:"dirlist",boxtitle:"boxtitle",timer:"timer"},css:{enabled:"enabled"}},i),this.init(e),r=this,r):void 0)}init(e){this.dropzone=document.createElement("div"),this.dropzone.id=this.options.display.dropzone,this.dropzone.innerHTML=`<input type="file" class="hidden"  name="${this.options.selector.uploadfile}" id="${this.options.selector.uploadfile}">\n            <div class="${this.options.selector.droptarget.slice(1)}">\n            <div id="${this.options.display.boxtitle}"><span class="${this.options.selector.trigger.slice(1)}">${this.container.dataset.textbrowse}</span>  ${this.container.dataset.textdrop}</div>\n          </div><div><span id="${this.options.display.counter}"></span>/<span id="${this.options.display.counterzipped}"></span></div>\n          <div><span id="${this.options.display.size}"></span>/<span id="${this.options.display.sizezipped}"></span></div><div id="${this.options.display.timer}"></div>\n          <div id="${this.options.selector.makezip.slice(1)}" class="button ${this.options.selector.makezip.slice(1)} ${o.iv.hide} "><div id="${this.options.selector.progress}"></div>${e.dataset.ended}</div>`,e.append(this.dropzone),this.counterdisplay=document.getElementById(this.options.display.counter),this.counterzippeddisplay=document.getElementById(this.options.display.counterzipped),this.sizedisplay=document.getElementById(this.options.display.size),this.sizezippeddisplay=document.getElementById(this.options.display.sizezipped),this.ziptrigger=e.querySelector(this.options.selector.makezip),this.displaylist=document.getElementById(this.options.display.dirlist);const t=this.container.querySelector(this.options.selector.droptarget);t.addEventListener("dragover",(e=>{this.handleDragOver(e)})),t.addEventListener("drop",(async e=>{this.handleDrop(e)})),e.querySelector(this.options.selector.trigger).addEventListener("click",(e=>{let t=e;this.openDirDialog(".tsv,.png,.jpg, .jpeg,.zip,.gz,.7z,.bz2",(e=>{console.log("edrop",t)}))}))}attachDropzone(e){console.log("attch",e),this.targetdir=e.parentElement.dataset.name?e.parentElement.dataset.name:"",console.log("targetdir",this.targetdir),this.dropzone.classList.add(this.options.css.enabled),console.log("att",this.dropzone),e.append(this.dropzone)}detachDropzone(){this.targetdir=null,this.container.classList.remove(this.options.css.enabled)}openDirDialog(e,t){const i=document.createElement("input");i.type="file",i.directory=!0,i.multiple=!0,i.webkitdirectory=!0,i.allowdirs=!0,i.accept=e,i.addEventListener("change",t),i.dispatchEvent(new MouseEvent("click"))}handleDragOver(e){e.preventDefault(),e.dataTransfer.dropEffect="move"}handleDrop(e){let t;e.dataTransfer?(e.preventDefault(),t=e.dataTransfer):t=e;const i=[...t.items?t.items:t.files];for(let e=0;e<i.length;e++){let t=i[e].webkitGetAsEntry();if(!0===t.isDirectory){this.enableDropzone(!1);const e=(e,t,i,s)=>{this.timer=new Date,console.log("item-------------------------------------",t),this.enableDropzone(),this.ziptrigger.classList.remove(o.iv.hide),this.ziptrigger.addEventListener("click",(e=>{console.log("upload click"),t.end(),this.enableDropzone(!1,!0);const s=new Response(i);console.log("zipResp",s),this.sendZip(s)}))},i=e=>{console.log("err_read_dir",e)};this.zipname=t.name+".zip",this.pathname=t.fullPath.slice(1).split("."),this.readDirectory(t,e,i)}else t.isFile}}stopOnError(e){console.log("err",e)}incrementCounter(e){this.counter++,this.counterdisplay.textContent=this.counter}decrementCounter(e){this.counter--,this.counterdisplay.textContent=this.counter}enableDropzone(e=!0,t=!1){t&&this.dropzone.classList.add(o.iv.hide),e?this.dropzone.classList.add(this.options.css.enabled):this.dropzone.classList.remove(this.options.css.enabled)}fileType(e){const t=new Uint8Array(e);let i=[];for(let e=0;e<4;e++)i.push(t[e].toString(16));return{input:t,mimetype:(e=>{switch(e){case"89504E47":return"image/png";case"47494638":return"image/gif";case"25504446":return"application/pdf";case"FFD8FFDB":case"FFD8FFE0":case"FFD8FFE1":return"image/jpeg";case"504B0304":return"application/zip";case"EFBBBF22":return"text/tsv";default:return console.log("unknownsign",e),"unknown"}})(e=i.join("").toUpperCase())}}fflToStream(e){const t=this;return new ReadableStream({start(i){e.ondata=(e,s,n)=>{e?i.error(e):(t.zipsize+=s.length,i.enqueue(s),n&&i.close())}},cancel(){e.terminate()}})}async readDirectory(e,t,i,o,a){let r=!1,l=!1,d=[],c=[];const p=e=>{console.log("on_error",e),r||(r=!0,i(e))};o=o||new s.sZ,a=a||this.fflToStream(o),fetch(this.options.url,(0,n.fetchSettings)({mode:"cors",method:"POST",body:o,headers:{"Content-Type":"Application/octet-stream"},duplex:"half"})).then((e=>{console.log("response",e)}));const h=async(e,t,i)=>{this.incrementCounter(e.size),this.addFileToZip(e,t,o,i)},u=async()=>{if(c.length){const e=c.shift();await e(),u()}},m=async(e,i,s,n)=>{if(e.length){const o=e.shift();if(o.isFile){const a=()=>{console.log("entrieslengthleft ",e.length),!e.length&&c.length&&(console.log("serialize"),u()),l&&!e.length?(console.log("oncomplete"),t([],i,s,n)):m(e,i,s,n)};o.file((e=>h(e,o.fullPath.slice(1),a)))}else o.isDirectory&&c.push((async()=>{this.readDirectory(o,m,n,i,s)}))}},g=e.createReader(),f=async e=>{e.length||r?await g.readEntries(f,p):d.length?l=!0:t([],o,a,p),d=[...d,...e],l&&m(d,o,a,p)};g.readEntries(f,p)}compressionLevel(e){if(!e)return console.log("name",e),-1;let t=e.split(".");return t=t.length>1?t[t.length-1]:t[0],a.find((e=>e===t))?2:this.options.level}sendZip(e){Math.round(this.zipsize/2e6)}async addFileToZip(e,t,i,n){const o=this,r=t.slice(t.lastIndexOf(".")+1),l=a.has(r)?new s.Ud(t):e.size>5e6?new s.wL(t,{level:9}):new s.Tf(t,{level:9});return l.ondata=(e,t,i)=>{e&&console.log("err add chunk to zipfile"+t,e)},i.add(l),await(async()=>{const t=e.stream().getReader();try{for(;;){const{done:i,value:s}=await t.read();if(i)return l.push(new Uint8Array(0),!0),o.decrementCounter(e.size),n&&n(),i;l.push(s)}}finally{t.releaseLock()}})()}}}}]);