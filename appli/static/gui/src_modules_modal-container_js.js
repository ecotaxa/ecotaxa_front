/*! For license information please see src_modules_modal-container_js.js.LICENSE.txt */
"use strict";(self.webpackChunk=self.webpackChunk||[]).push([["src_modules_modal-container_js"],{"./src/modules/modal-container.js":(__unused_webpack_module,__webpack_exports__,__webpack_require__)=>{eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   ModalContainer: () => (/* binding */ ModalContainer)\n/* harmony export */ });\n/* harmony import */ var _modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../modules/modules-config.js */ \"./src/modules/modules-config.js\");\n\n\nclass ModalContainer {\n  listener = null;\n  trigger = null;\n  modal = null;\n  modalcontent = null;\n  constructor(trigger) {\n    const defaultOptions = {};\n\n    // todo search for options in the item data attrs\n    if (!this.modal && (!this.trigger || this.trigger !== trigger)) {\n      this.trigger = trigger;\n\n      if (trigger.dataset.what === _modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.models.help) {\n        this.modal = (document.getElementById(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.domselectors.component.modal.help.substr(1))) ? document.getElementById(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.domselectors.component.modal.help.substr(1)) : document.querySelector(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.domselectors.component.modal.help);\n      } else if (trigger.dataset.target && trigger.dataset.target !== 'unique') {\n        const md = document.getElementById(trigger.dataset.target);\n        if (md && md.classList.contains(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.domselectors.component.modal.modalcontainer.substr(1))) this.modal = md;\n        else if (md) this.modal = md.closest(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.domselectors.component.modal.modalcontainer);\n        else this.modal = trigger.closest(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.domselectors.component.modal.modalcontainer);\n\n      } else this.modal = trigger.closest(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.domselectors.component.modal.modalcontainer);\n      this.modalcontent = this.modal.querySelector(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.domselectors.component.modal.modalcontent);\n      if (this.modal === null) return null;\n      this.addListeners();\n    }\n    return this;\n  }\n  addListeners() {\n    this.modal.addEventListener('toggle', (e) => {\n      const open = e.currentTarget.open;\n      if (open) document.body.classList.add(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.css.hidevscroll);\n      else document.body.classList.remove(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.css.hidevscroll);\n      const summary = this.modal.querySelector('summary');\n      if (summary) {\n        summary.setAttribute('aria-hidden', !open);\n        this.toggleAction(summary);\n      }\n\n    });\n\n  }\n\n  setContent(html) {\n    // data have been sanitzed before in other scripts and from the server\n    html = html instanceof HTMLElement ? html.outerHTML : html;\n\n    this.modalcontent.innerHTML = html;\n    return this.modalcontent;\n  }\n  getContentSiblings() {\n    return this.modal.querySelectorAll('details');\n  }\n  getBySelector(selector) {\n    return this.modal.querySelector(selector);\n  }\n  modalOpen(trigger) {\n    if (!this.modal.hasOwnProperty('open')) this.modal.open = true;\n    this.openContent(trigger);\n  }\n\n  openContent(trigger) {\n\n    if (!trigger.dataset.for) return;\n    if (trigger.dataset.close) return this.dismissModal();\n    if (this.modal.classList.contains(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.domselectors.component.modal.help.substr(1))) {\n      const siblings = this.getContentSiblings();\n      siblings.forEach(sibling => {\n        if (sibling !== trigger) sibling.removeAttribute('open');\n      });\n      const paragraph = this.modal.querySelector('#' + trigger.dataset.for);\n      if (paragraph) paragraph.open = true;\n      else console.log('help ' + trigger.dataset.for+'display error', this.modal);\n    }\n    this.toggleAction(trigger);\n  }\n\n\n  toggleAction(trigger) {\n    const summary = this.modal.querySelector('summary');\n    let action = trigger.dataset.action;\n    if (!action) return;\n    if (trigger.dataset.what) {\n      document.querySelectorAll('[data-close]').forEach(sibling => {\n        if (sibling !== trigger) delete sibling.dataset.close;\n      });\n    }\n    if (trigger.dataset.for) {\n      if (trigger.dataset.close) delete trigger.dataset.close;\n      else trigger.dataset.close = true;\n    }\n  }\n\n  dismissModal(erase = false, content = null) {\n    if (this.modalcontent) {\n      const event = new Event('dismissmodal');\n      this.modalcontent.querySelectorAll('.js').forEach(element => element.dispatchEvent(event));\n      if (erase) this.modalcontent.innerHTML = ``;\n\n    }\n    if (this.trigger.dataset.for) {\n      this.modal.open = false;\n      this.toggleAction(this.trigger);\n    }\n\n  }\n\n}//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvbW9kdWxlcy9tb2RhbC1jb250YWluZXIuanMiLCJtYXBwaW5ncyI6Ijs7Ozs7QUFJc0M7O0FBRS9CO0FBQ1A7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOztBQUVBO0FBQ0E7QUFDQTs7QUFFQSxtQ0FBbUMsOERBQU07QUFDekMsOENBQThDLG9FQUFZLDREQUE0RCxvRUFBWSwwREFBMEQsb0VBQVk7QUFDeE0sUUFBUTtBQUNSO0FBQ0Esd0NBQXdDLG9FQUFZO0FBQ3BELDZDQUE2QyxvRUFBWTtBQUN6RCwwQ0FBMEMsb0VBQVk7O0FBRXRELFFBQVEsa0NBQWtDLG9FQUFZO0FBQ3RELG1EQUFtRCxvRUFBWTtBQUMvRDtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EsNENBQTRDLDJEQUFHO0FBQy9DLDBDQUEwQywyREFBRztBQUM3QztBQUNBO0FBQ0E7QUFDQTtBQUNBOztBQUVBLEtBQUs7O0FBRUw7O0FBRUE7QUFDQTtBQUNBOztBQUVBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOztBQUVBOztBQUVBO0FBQ0E7QUFDQSxzQ0FBc0Msb0VBQVk7QUFDbEQ7QUFDQTtBQUNBO0FBQ0EsT0FBTztBQUNQO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7O0FBR0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSxPQUFPO0FBQ1A7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOztBQUVBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7O0FBRUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7QUFFQTs7QUFFQSIsInNvdXJjZXMiOlsid2VicGFjazovLy8uL3NyYy9tb2R1bGVzL21vZGFsLWNvbnRhaW5lci5qcz8zNGFlIl0sInNvdXJjZXNDb250ZW50IjpbImltcG9ydCB7XG4gIGRvbXNlbGVjdG9ycyxcbiAgY3NzLFxuICBtb2RlbHNcbn0gZnJvbSAnLi4vbW9kdWxlcy9tb2R1bGVzLWNvbmZpZy5qcyc7XG5cbmV4cG9ydCBjbGFzcyBNb2RhbENvbnRhaW5lciB7XG4gIGxpc3RlbmVyID0gbnVsbDtcbiAgdHJpZ2dlciA9IG51bGw7XG4gIG1vZGFsID0gbnVsbDtcbiAgbW9kYWxjb250ZW50ID0gbnVsbDtcbiAgY29uc3RydWN0b3IodHJpZ2dlcikge1xuICAgIGNvbnN0IGRlZmF1bHRPcHRpb25zID0ge307XG5cbiAgICAvLyB0b2RvIHNlYXJjaCBmb3Igb3B0aW9ucyBpbiB0aGUgaXRlbSBkYXRhIGF0dHJzXG4gICAgaWYgKCF0aGlzLm1vZGFsICYmICghdGhpcy50cmlnZ2VyIHx8IHRoaXMudHJpZ2dlciAhPT0gdHJpZ2dlcikpIHtcbiAgICAgIHRoaXMudHJpZ2dlciA9IHRyaWdnZXI7XG5cbiAgICAgIGlmICh0cmlnZ2VyLmRhdGFzZXQud2hhdCA9PT0gbW9kZWxzLmhlbHApIHtcbiAgICAgICAgdGhpcy5tb2RhbCA9IChkb2N1bWVudC5nZXRFbGVtZW50QnlJZChkb21zZWxlY3RvcnMuY29tcG9uZW50Lm1vZGFsLmhlbHAuc3Vic3RyKDEpKSkgPyBkb2N1bWVudC5nZXRFbGVtZW50QnlJZChkb21zZWxlY3RvcnMuY29tcG9uZW50Lm1vZGFsLmhlbHAuc3Vic3RyKDEpKSA6IGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3IoZG9tc2VsZWN0b3JzLmNvbXBvbmVudC5tb2RhbC5oZWxwKTtcbiAgICAgIH0gZWxzZSBpZiAodHJpZ2dlci5kYXRhc2V0LnRhcmdldCAmJiB0cmlnZ2VyLmRhdGFzZXQudGFyZ2V0ICE9PSAndW5pcXVlJykge1xuICAgICAgICBjb25zdCBtZCA9IGRvY3VtZW50LmdldEVsZW1lbnRCeUlkKHRyaWdnZXIuZGF0YXNldC50YXJnZXQpO1xuICAgICAgICBpZiAobWQgJiYgbWQuY2xhc3NMaXN0LmNvbnRhaW5zKGRvbXNlbGVjdG9ycy5jb21wb25lbnQubW9kYWwubW9kYWxjb250YWluZXIuc3Vic3RyKDEpKSkgdGhpcy5tb2RhbCA9IG1kO1xuICAgICAgICBlbHNlIGlmIChtZCkgdGhpcy5tb2RhbCA9IG1kLmNsb3Nlc3QoZG9tc2VsZWN0b3JzLmNvbXBvbmVudC5tb2RhbC5tb2RhbGNvbnRhaW5lcik7XG4gICAgICAgIGVsc2UgdGhpcy5tb2RhbCA9IHRyaWdnZXIuY2xvc2VzdChkb21zZWxlY3RvcnMuY29tcG9uZW50Lm1vZGFsLm1vZGFsY29udGFpbmVyKTtcblxuICAgICAgfSBlbHNlIHRoaXMubW9kYWwgPSB0cmlnZ2VyLmNsb3Nlc3QoZG9tc2VsZWN0b3JzLmNvbXBvbmVudC5tb2RhbC5tb2RhbGNvbnRhaW5lcik7XG4gICAgICB0aGlzLm1vZGFsY29udGVudCA9IHRoaXMubW9kYWwucXVlcnlTZWxlY3Rvcihkb21zZWxlY3RvcnMuY29tcG9uZW50Lm1vZGFsLm1vZGFsY29udGVudCk7XG4gICAgICBpZiAodGhpcy5tb2RhbCA9PT0gbnVsbCkgcmV0dXJuIG51bGw7XG4gICAgICB0aGlzLmFkZExpc3RlbmVycygpO1xuICAgIH1cbiAgICByZXR1cm4gdGhpcztcbiAgfVxuICBhZGRMaXN0ZW5lcnMoKSB7XG4gICAgdGhpcy5tb2RhbC5hZGRFdmVudExpc3RlbmVyKCd0b2dnbGUnLCAoZSkgPT4ge1xuICAgICAgY29uc3Qgb3BlbiA9IGUuY3VycmVudFRhcmdldC5vcGVuO1xuICAgICAgaWYgKG9wZW4pIGRvY3VtZW50LmJvZHkuY2xhc3NMaXN0LmFkZChjc3MuaGlkZXZzY3JvbGwpO1xuICAgICAgZWxzZSBkb2N1bWVudC5ib2R5LmNsYXNzTGlzdC5yZW1vdmUoY3NzLmhpZGV2c2Nyb2xsKTtcbiAgICAgIGNvbnN0IHN1bW1hcnkgPSB0aGlzLm1vZGFsLnF1ZXJ5U2VsZWN0b3IoJ3N1bW1hcnknKTtcbiAgICAgIGlmIChzdW1tYXJ5KSB7XG4gICAgICAgIHN1bW1hcnkuc2V0QXR0cmlidXRlKCdhcmlhLWhpZGRlbicsICFvcGVuKTtcbiAgICAgICAgdGhpcy50b2dnbGVBY3Rpb24oc3VtbWFyeSk7XG4gICAgICB9XG5cbiAgICB9KTtcblxuICB9XG5cbiAgc2V0Q29udGVudChodG1sKSB7XG4gICAgLy8gZGF0YSBoYXZlIGJlZW4gc2FuaXR6ZWQgYmVmb3JlIGluIG90aGVyIHNjcmlwdHMgYW5kIGZyb20gdGhlIHNlcnZlclxuICAgIGh0bWwgPSBodG1sIGluc3RhbmNlb2YgSFRNTEVsZW1lbnQgPyBodG1sLm91dGVySFRNTCA6IGh0bWw7XG5cbiAgICB0aGlzLm1vZGFsY29udGVudC5pbm5lckhUTUwgPSBodG1sO1xuICAgIHJldHVybiB0aGlzLm1vZGFsY29udGVudDtcbiAgfVxuICBnZXRDb250ZW50U2libGluZ3MoKSB7XG4gICAgcmV0dXJuIHRoaXMubW9kYWwucXVlcnlTZWxlY3RvckFsbCgnZGV0YWlscycpO1xuICB9XG4gIGdldEJ5U2VsZWN0b3Ioc2VsZWN0b3IpIHtcbiAgICByZXR1cm4gdGhpcy5tb2RhbC5xdWVyeVNlbGVjdG9yKHNlbGVjdG9yKTtcbiAgfVxuICBtb2RhbE9wZW4odHJpZ2dlcikge1xuICAgIGlmICghdGhpcy5tb2RhbC5oYXNPd25Qcm9wZXJ0eSgnb3BlbicpKSB0aGlzLm1vZGFsLm9wZW4gPSB0cnVlO1xuICAgIHRoaXMub3BlbkNvbnRlbnQodHJpZ2dlcik7XG4gIH1cblxuICBvcGVuQ29udGVudCh0cmlnZ2VyKSB7XG5cbiAgICBpZiAoIXRyaWdnZXIuZGF0YXNldC5mb3IpIHJldHVybjtcbiAgICBpZiAodHJpZ2dlci5kYXRhc2V0LmNsb3NlKSByZXR1cm4gdGhpcy5kaXNtaXNzTW9kYWwoKTtcbiAgICBpZiAodGhpcy5tb2RhbC5jbGFzc0xpc3QuY29udGFpbnMoZG9tc2VsZWN0b3JzLmNvbXBvbmVudC5tb2RhbC5oZWxwLnN1YnN0cigxKSkpIHtcbiAgICAgIGNvbnN0IHNpYmxpbmdzID0gdGhpcy5nZXRDb250ZW50U2libGluZ3MoKTtcbiAgICAgIHNpYmxpbmdzLmZvckVhY2goc2libGluZyA9PiB7XG4gICAgICAgIGlmIChzaWJsaW5nICE9PSB0cmlnZ2VyKSBzaWJsaW5nLnJlbW92ZUF0dHJpYnV0ZSgnb3BlbicpO1xuICAgICAgfSk7XG4gICAgICBjb25zdCBwYXJhZ3JhcGggPSB0aGlzLm1vZGFsLnF1ZXJ5U2VsZWN0b3IoJyMnICsgdHJpZ2dlci5kYXRhc2V0LmZvcik7XG4gICAgICBpZiAocGFyYWdyYXBoKSBwYXJhZ3JhcGgub3BlbiA9IHRydWU7XG4gICAgICBlbHNlIGNvbnNvbGUubG9nKCdoZWxwICcgKyB0cmlnZ2VyLmRhdGFzZXQuZm9yKydkaXNwbGF5IGVycm9yJywgdGhpcy5tb2RhbCk7XG4gICAgfVxuICAgIHRoaXMudG9nZ2xlQWN0aW9uKHRyaWdnZXIpO1xuICB9XG5cblxuICB0b2dnbGVBY3Rpb24odHJpZ2dlcikge1xuICAgIGNvbnN0IHN1bW1hcnkgPSB0aGlzLm1vZGFsLnF1ZXJ5U2VsZWN0b3IoJ3N1bW1hcnknKTtcbiAgICBsZXQgYWN0aW9uID0gdHJpZ2dlci5kYXRhc2V0LmFjdGlvbjtcbiAgICBpZiAoIWFjdGlvbikgcmV0dXJuO1xuICAgIGlmICh0cmlnZ2VyLmRhdGFzZXQud2hhdCkge1xuICAgICAgZG9jdW1lbnQucXVlcnlTZWxlY3RvckFsbCgnW2RhdGEtY2xvc2VdJykuZm9yRWFjaChzaWJsaW5nID0+IHtcbiAgICAgICAgaWYgKHNpYmxpbmcgIT09IHRyaWdnZXIpIGRlbGV0ZSBzaWJsaW5nLmRhdGFzZXQuY2xvc2U7XG4gICAgICB9KTtcbiAgICB9XG4gICAgaWYgKHRyaWdnZXIuZGF0YXNldC5mb3IpIHtcbiAgICAgIGlmICh0cmlnZ2VyLmRhdGFzZXQuY2xvc2UpIGRlbGV0ZSB0cmlnZ2VyLmRhdGFzZXQuY2xvc2U7XG4gICAgICBlbHNlIHRyaWdnZXIuZGF0YXNldC5jbG9zZSA9IHRydWU7XG4gICAgfVxuICB9XG5cbiAgZGlzbWlzc01vZGFsKGVyYXNlID0gZmFsc2UsIGNvbnRlbnQgPSBudWxsKSB7XG4gICAgaWYgKHRoaXMubW9kYWxjb250ZW50KSB7XG4gICAgICBjb25zdCBldmVudCA9IG5ldyBFdmVudCgnZGlzbWlzc21vZGFsJyk7XG4gICAgICB0aGlzLm1vZGFsY29udGVudC5xdWVyeVNlbGVjdG9yQWxsKCcuanMnKS5mb3JFYWNoKGVsZW1lbnQgPT4gZWxlbWVudC5kaXNwYXRjaEV2ZW50KGV2ZW50KSk7XG4gICAgICBpZiAoZXJhc2UpIHRoaXMubW9kYWxjb250ZW50LmlubmVySFRNTCA9IGBgO1xuXG4gICAgfVxuICAgIGlmICh0aGlzLnRyaWdnZXIuZGF0YXNldC5mb3IpIHtcbiAgICAgIHRoaXMubW9kYWwub3BlbiA9IGZhbHNlO1xuICAgICAgdGhpcy50b2dnbGVBY3Rpb24odGhpcy50cmlnZ2VyKTtcbiAgICB9XG5cbiAgfVxuXG59Il0sIm5hbWVzIjpbXSwic291cmNlUm9vdCI6IiJ9\n//# sourceURL=webpack-internal:///./src/modules/modal-container.js\n")}}]);