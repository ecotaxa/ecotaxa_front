/*! For license information please see 702.291b1fd412f735826a93.js.LICENSE.txt */
"use strict";(self.webpackChunk=self.webpackChunk||[]).push([[702],{9702:(e,t,a)=>{a.r(t),a.d(t,{default:()=>r});a(7114);function r(e){return console.log("fromid",e.params.fromid),e.params.fromid&&(e.afterLoad=()=>{const t=e.dom.querySelector('input[name="'+e.uuid+'select[]"][value="'+e.params.fromid+'"]');t&&(t.checked=!0)}),{selectmultiple:(t,a,r,s={})=>{const l=e.grid.columns[r];return t=isNaN(t)&&l.hasOwnProperty("field")?this.getCellData(a,l.field):t,s.childnodes=[{nodename:"INPUT",attributes:{type:"checkbox",name:`${e.uuid}select[]`,value:String(t)}}],s}}}}}]);