"use strict";(self.webpackChunk=self.webpackChunk||[]).push([[109],{109:(i,n,s)=>{s.d(n,{JsAccordion:()=>t});class t{constructor(i,n=null,s=null,t=null,e={},a=null){this.el=i,this.summary=a?a instanceof HTMLElement?a:i.querySelector(a):i.querySelector("summary")?i.querySelector("summary"):i,this.summary&&(this.content=t?t instanceof HTMLElement?t:i.querySelector(t):i.nextElementSibling,this.content&&(this.options=Object.assign({shrink:{opacity:[100,0],scaleY:[1,0]},expand:{opacity:[0,100],scaleY:[0,1]}},e),Object.freeze(this.options),this.animation=null,this.isClosing=!1,this.isExpanding=!1,this.summary.addEventListener("click",(i=>this.onClick(i))),this.callbackopen=n,this.callbackclose=s))}onClick(i){i.preventDefault(),this.isClosing||!this.el.open?this.callbackopen?this.callbackopen(this.el,(()=>{this.open()})):this.open():(this.isExpanding||this.el.open)&&this.shrink()}shrink(){this.isClosing=!0,this.animation&&this.animation.cancel(),this.animation=this.content.animate(this.options.shrink,{duration:400,easing:"ease-out"}),this.animation.onfinish=()=>this.onAnimationFinish(!1),this.animation.oncancel=()=>this.isClosing=!1,this.callbackclose&&this.callbackclose(this.el)}open(){this.el.open=!0,window.requestAnimationFrame((()=>this.expand()))}expand(){this.isExpanding=!0,this.animation&&this.animation.cancel(),this.animation=this.content.animate(this.options.expand,{duration:400,easing:"ease-out"}),this.animation.onfinish=()=>this.onAnimationFinish(!0),this.animation.oncancel=()=>this.isExpanding=!1}onAnimationFinish(i){this.el.open=i,this.animation=null,this.isClosing=!1,this.isExpanding=!1}}}}]);