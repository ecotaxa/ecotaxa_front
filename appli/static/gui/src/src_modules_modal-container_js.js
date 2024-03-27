/*! For license information please see src_modules_modal-container_js.js.LICENSE.txt */
"use strict";(self.webpackChunk=self.webpackChunk||[]).push([["src_modules_modal-container_js"],{"./src/modules/modal-container.js":(__unused_webpack_module,__webpack_exports__,__webpack_require__)=>{eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   ModalContainer: () => (/* binding */ ModalContainer)\n/* harmony export */ });\n/* harmony import */ var _modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../modules/modules-config.js */ \"./src/modules/modules-config.js\");\n\n\nclass ModalContainer {\n  listener = null;\n  trigger = null;\n  modal = null;\n  modalcontent = null;\n  constructor(trigger) {\n    const defaultOptions = {};\n\n    // todo search for options in the item data attrs\n    if (!this.modal && (!this.trigger || this.trigger !== trigger)) {\n      this.trigger = trigger;\n\n      if (trigger.dataset.what === _modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.models.help) {\n        this.modal = (document.getElementById(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.domselectors.component.modal.help.substr(1))) ? document.getElementById(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.domselectors.component.modal.help.substr(1)) : document.querySelector(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.domselectors.component.modal.help);\n      } else if (trigger.dataset.target && trigger.dataset.target !== 'unique') {\n        const md = document.getElementById(trigger.dataset.target);\n        if (md && md.classList.contains(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.domselectors.component.modal.modalcontainer.substr(1))) this.modal = md;\n        else if (md) this.modal = md.closest(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.domselectors.component.modal.modalcontainer);\n        else this.modal = trigger.closest(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.domselectors.component.modal.modalcontainer);\n\n      } else this.modal = trigger.closest(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.domselectors.component.modal.modalcontainer);\n      this.modalcontent = this.modal.querySelector(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.domselectors.component.modal.modalcontent);\n      if (this.modal === null) return null;\n      this.addListeners();\n    }\n    return this;\n  }\n  addListeners() {\n    const toggle_modal_background = (open) => {\n\n      if (open) document.body.classList.add(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.css.hidevscroll);\n      else document.body.classList.remove(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.css.hidevscroll);\n      const summary = this.modal.querySelector('summary');\n      if (summary) {\n        summary.setAttribute('aria-hidden', !open);\n        this.toggleAction(summary);\n      }\n    }\n    toggle_modal_background(this.modal.open);\n    this.modal.addEventListener('toggle', (e) => {\n      toggle_modal_background(e.currentTarget.open);\n\n    });\n\n  }\n\n  setContent(html) {\n    // data have been sanitzed before in other scripts and from the server\n    html = html instanceof HTMLElement ? html.outerHTML : html;\n\n    this.modalcontent.innerHTML = html;\n    return this.modalcontent;\n  }\n  getContentSiblings() {\n    return this.modal.querySelectorAll('details');\n  }\n  getBySelector(selector) {\n    return this.modal.querySelector(selector);\n  }\n  modalOpen(trigger) {\n    if (!trigger.dataset.close && !this.modal.open) this.modal.open = true;\n    this.openContent(trigger);\n  }\n\n  openContent(trigger) {\n    if (!trigger.dataset.for) return;\n    if (trigger.dataset.close) return this.dismissModal();\n    if (this.modal.classList.contains(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.domselectors.component.modal.help.substr(1))) {\n      const siblings = this.getContentSiblings();\n      siblings.forEach(sibling => {\n        if (sibling !== trigger) sibling.open = false;\n      });\n      trigger.dataset.for.split('#').forEach(tr => {\n        const paragraph = this.modal.querySelector('#' + tr);\n        if (paragraph) paragraph.open = true;\n        else console.log('help ' + tr + 'display error');\n      })\n\n\n    }\n    this.toggleAction(trigger);\n  }\n\n\n  toggleAction(trigger) {\n    const summary = this.modal.querySelector('summary');\n    /*  let action = trigger.dataset.action;\n      if (!action) return;*/\n    if (trigger.dataset.what) {\n      document.querySelectorAll('[data-close]').forEach(sibling => {\n        if (sibling !== trigger) delete sibling.dataset.close;\n      });\n    }\n    if (trigger.dataset.for) {\n      if (trigger.dataset.close) delete trigger.dataset.close;\n      else trigger.dataset.close = true;\n    }\n  }\n\n  dismissModal(erase = false, content = null) {\n    if (this.modalcontent) {\n      const event = new Event('dismissmodal');\n      this.modalcontent.querySelectorAll('.js').forEach(element => element.dispatchEvent(event));\n      if (erase) this.modalcontent.innerHTML = ``;\n\n    }\n    if (this.trigger.dataset.for) {\n      this.modal.open = false;\n      this.toggleAction(this.trigger);\n    }\n\n  }\n\n}//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvbW9kdWxlcy9tb2RhbC1jb250YWluZXIuanMiLCJtYXBwaW5ncyI6Ijs7Ozs7QUFJc0M7O0FBRS9CO0FBQ1A7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOztBQUVBO0FBQ0E7QUFDQTs7QUFFQSxtQ0FBbUMsOERBQU07QUFDekMsOENBQThDLG9FQUFZLDREQUE0RCxvRUFBWSwwREFBMEQsb0VBQVk7QUFDeE0sUUFBUTtBQUNSO0FBQ0Esd0NBQXdDLG9FQUFZO0FBQ3BELDZDQUE2QyxvRUFBWTtBQUN6RCwwQ0FBMEMsb0VBQVk7O0FBRXRELFFBQVEsa0NBQWtDLG9FQUFZO0FBQ3RELG1EQUFtRCxvRUFBWTtBQUMvRDtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7QUFFQSw0Q0FBNEMsMkRBQUc7QUFDL0MsMENBQTBDLDJEQUFHO0FBQzdDO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7QUFFQSxLQUFLOztBQUVMOztBQUVBO0FBQ0E7QUFDQTs7QUFFQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7QUFFQTtBQUNBO0FBQ0E7QUFDQSxzQ0FBc0Msb0VBQVk7QUFDbEQ7QUFDQTtBQUNBO0FBQ0EsT0FBTztBQUNQO0FBQ0E7QUFDQTtBQUNBO0FBQ0EsT0FBTzs7O0FBR1A7QUFDQTtBQUNBOzs7QUFHQTtBQUNBO0FBQ0E7QUFDQSwwQkFBMEI7QUFDMUI7QUFDQTtBQUNBO0FBQ0EsT0FBTztBQUNQO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7QUFFQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOztBQUVBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7O0FBRUE7O0FBRUEiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly8vLi9zcmMvbW9kdWxlcy9tb2RhbC1jb250YWluZXIuanM/MzRhZSJdLCJzb3VyY2VzQ29udGVudCI6WyJpbXBvcnQge1xuICBkb21zZWxlY3RvcnMsXG4gIGNzcyxcbiAgbW9kZWxzXG59IGZyb20gJy4uL21vZHVsZXMvbW9kdWxlcy1jb25maWcuanMnO1xuXG5leHBvcnQgY2xhc3MgTW9kYWxDb250YWluZXIge1xuICBsaXN0ZW5lciA9IG51bGw7XG4gIHRyaWdnZXIgPSBudWxsO1xuICBtb2RhbCA9IG51bGw7XG4gIG1vZGFsY29udGVudCA9IG51bGw7XG4gIGNvbnN0cnVjdG9yKHRyaWdnZXIpIHtcbiAgICBjb25zdCBkZWZhdWx0T3B0aW9ucyA9IHt9O1xuXG4gICAgLy8gdG9kbyBzZWFyY2ggZm9yIG9wdGlvbnMgaW4gdGhlIGl0ZW0gZGF0YSBhdHRyc1xuICAgIGlmICghdGhpcy5tb2RhbCAmJiAoIXRoaXMudHJpZ2dlciB8fCB0aGlzLnRyaWdnZXIgIT09IHRyaWdnZXIpKSB7XG4gICAgICB0aGlzLnRyaWdnZXIgPSB0cmlnZ2VyO1xuXG4gICAgICBpZiAodHJpZ2dlci5kYXRhc2V0LndoYXQgPT09IG1vZGVscy5oZWxwKSB7XG4gICAgICAgIHRoaXMubW9kYWwgPSAoZG9jdW1lbnQuZ2V0RWxlbWVudEJ5SWQoZG9tc2VsZWN0b3JzLmNvbXBvbmVudC5tb2RhbC5oZWxwLnN1YnN0cigxKSkpID8gZG9jdW1lbnQuZ2V0RWxlbWVudEJ5SWQoZG9tc2VsZWN0b3JzLmNvbXBvbmVudC5tb2RhbC5oZWxwLnN1YnN0cigxKSkgOiBkb2N1bWVudC5xdWVyeVNlbGVjdG9yKGRvbXNlbGVjdG9ycy5jb21wb25lbnQubW9kYWwuaGVscCk7XG4gICAgICB9IGVsc2UgaWYgKHRyaWdnZXIuZGF0YXNldC50YXJnZXQgJiYgdHJpZ2dlci5kYXRhc2V0LnRhcmdldCAhPT0gJ3VuaXF1ZScpIHtcbiAgICAgICAgY29uc3QgbWQgPSBkb2N1bWVudC5nZXRFbGVtZW50QnlJZCh0cmlnZ2VyLmRhdGFzZXQudGFyZ2V0KTtcbiAgICAgICAgaWYgKG1kICYmIG1kLmNsYXNzTGlzdC5jb250YWlucyhkb21zZWxlY3RvcnMuY29tcG9uZW50Lm1vZGFsLm1vZGFsY29udGFpbmVyLnN1YnN0cigxKSkpIHRoaXMubW9kYWwgPSBtZDtcbiAgICAgICAgZWxzZSBpZiAobWQpIHRoaXMubW9kYWwgPSBtZC5jbG9zZXN0KGRvbXNlbGVjdG9ycy5jb21wb25lbnQubW9kYWwubW9kYWxjb250YWluZXIpO1xuICAgICAgICBlbHNlIHRoaXMubW9kYWwgPSB0cmlnZ2VyLmNsb3Nlc3QoZG9tc2VsZWN0b3JzLmNvbXBvbmVudC5tb2RhbC5tb2RhbGNvbnRhaW5lcik7XG5cbiAgICAgIH0gZWxzZSB0aGlzLm1vZGFsID0gdHJpZ2dlci5jbG9zZXN0KGRvbXNlbGVjdG9ycy5jb21wb25lbnQubW9kYWwubW9kYWxjb250YWluZXIpO1xuICAgICAgdGhpcy5tb2RhbGNvbnRlbnQgPSB0aGlzLm1vZGFsLnF1ZXJ5U2VsZWN0b3IoZG9tc2VsZWN0b3JzLmNvbXBvbmVudC5tb2RhbC5tb2RhbGNvbnRlbnQpO1xuICAgICAgaWYgKHRoaXMubW9kYWwgPT09IG51bGwpIHJldHVybiBudWxsO1xuICAgICAgdGhpcy5hZGRMaXN0ZW5lcnMoKTtcbiAgICB9XG4gICAgcmV0dXJuIHRoaXM7XG4gIH1cbiAgYWRkTGlzdGVuZXJzKCkge1xuICAgIGNvbnN0IHRvZ2dsZV9tb2RhbF9iYWNrZ3JvdW5kID0gKG9wZW4pID0+IHtcblxuICAgICAgaWYgKG9wZW4pIGRvY3VtZW50LmJvZHkuY2xhc3NMaXN0LmFkZChjc3MuaGlkZXZzY3JvbGwpO1xuICAgICAgZWxzZSBkb2N1bWVudC5ib2R5LmNsYXNzTGlzdC5yZW1vdmUoY3NzLmhpZGV2c2Nyb2xsKTtcbiAgICAgIGNvbnN0IHN1bW1hcnkgPSB0aGlzLm1vZGFsLnF1ZXJ5U2VsZWN0b3IoJ3N1bW1hcnknKTtcbiAgICAgIGlmIChzdW1tYXJ5KSB7XG4gICAgICAgIHN1bW1hcnkuc2V0QXR0cmlidXRlKCdhcmlhLWhpZGRlbicsICFvcGVuKTtcbiAgICAgICAgdGhpcy50b2dnbGVBY3Rpb24oc3VtbWFyeSk7XG4gICAgICB9XG4gICAgfVxuICAgIHRvZ2dsZV9tb2RhbF9iYWNrZ3JvdW5kKHRoaXMubW9kYWwub3Blbik7XG4gICAgdGhpcy5tb2RhbC5hZGRFdmVudExpc3RlbmVyKCd0b2dnbGUnLCAoZSkgPT4ge1xuICAgICAgdG9nZ2xlX21vZGFsX2JhY2tncm91bmQoZS5jdXJyZW50VGFyZ2V0Lm9wZW4pO1xuXG4gICAgfSk7XG5cbiAgfVxuXG4gIHNldENvbnRlbnQoaHRtbCkge1xuICAgIC8vIGRhdGEgaGF2ZSBiZWVuIHNhbml0emVkIGJlZm9yZSBpbiBvdGhlciBzY3JpcHRzIGFuZCBmcm9tIHRoZSBzZXJ2ZXJcbiAgICBodG1sID0gaHRtbCBpbnN0YW5jZW9mIEhUTUxFbGVtZW50ID8gaHRtbC5vdXRlckhUTUwgOiBodG1sO1xuXG4gICAgdGhpcy5tb2RhbGNvbnRlbnQuaW5uZXJIVE1MID0gaHRtbDtcbiAgICByZXR1cm4gdGhpcy5tb2RhbGNvbnRlbnQ7XG4gIH1cbiAgZ2V0Q29udGVudFNpYmxpbmdzKCkge1xuICAgIHJldHVybiB0aGlzLm1vZGFsLnF1ZXJ5U2VsZWN0b3JBbGwoJ2RldGFpbHMnKTtcbiAgfVxuICBnZXRCeVNlbGVjdG9yKHNlbGVjdG9yKSB7XG4gICAgcmV0dXJuIHRoaXMubW9kYWwucXVlcnlTZWxlY3RvcihzZWxlY3Rvcik7XG4gIH1cbiAgbW9kYWxPcGVuKHRyaWdnZXIpIHtcbiAgICBpZiAoIXRyaWdnZXIuZGF0YXNldC5jbG9zZSAmJiAhdGhpcy5tb2RhbC5vcGVuKSB0aGlzLm1vZGFsLm9wZW4gPSB0cnVlO1xuICAgIHRoaXMub3BlbkNvbnRlbnQodHJpZ2dlcik7XG4gIH1cblxuICBvcGVuQ29udGVudCh0cmlnZ2VyKSB7XG4gICAgaWYgKCF0cmlnZ2VyLmRhdGFzZXQuZm9yKSByZXR1cm47XG4gICAgaWYgKHRyaWdnZXIuZGF0YXNldC5jbG9zZSkgcmV0dXJuIHRoaXMuZGlzbWlzc01vZGFsKCk7XG4gICAgaWYgKHRoaXMubW9kYWwuY2xhc3NMaXN0LmNvbnRhaW5zKGRvbXNlbGVjdG9ycy5jb21wb25lbnQubW9kYWwuaGVscC5zdWJzdHIoMSkpKSB7XG4gICAgICBjb25zdCBzaWJsaW5ncyA9IHRoaXMuZ2V0Q29udGVudFNpYmxpbmdzKCk7XG4gICAgICBzaWJsaW5ncy5mb3JFYWNoKHNpYmxpbmcgPT4ge1xuICAgICAgICBpZiAoc2libGluZyAhPT0gdHJpZ2dlcikgc2libGluZy5vcGVuID0gZmFsc2U7XG4gICAgICB9KTtcbiAgICAgIHRyaWdnZXIuZGF0YXNldC5mb3Iuc3BsaXQoJyMnKS5mb3JFYWNoKHRyID0+IHtcbiAgICAgICAgY29uc3QgcGFyYWdyYXBoID0gdGhpcy5tb2RhbC5xdWVyeVNlbGVjdG9yKCcjJyArIHRyKTtcbiAgICAgICAgaWYgKHBhcmFncmFwaCkgcGFyYWdyYXBoLm9wZW4gPSB0cnVlO1xuICAgICAgICBlbHNlIGNvbnNvbGUubG9nKCdoZWxwICcgKyB0ciArICdkaXNwbGF5IGVycm9yJyk7XG4gICAgICB9KVxuXG5cbiAgICB9XG4gICAgdGhpcy50b2dnbGVBY3Rpb24odHJpZ2dlcik7XG4gIH1cblxuXG4gIHRvZ2dsZUFjdGlvbih0cmlnZ2VyKSB7XG4gICAgY29uc3Qgc3VtbWFyeSA9IHRoaXMubW9kYWwucXVlcnlTZWxlY3Rvcignc3VtbWFyeScpO1xuICAgIC8qICBsZXQgYWN0aW9uID0gdHJpZ2dlci5kYXRhc2V0LmFjdGlvbjtcbiAgICAgIGlmICghYWN0aW9uKSByZXR1cm47Ki9cbiAgICBpZiAodHJpZ2dlci5kYXRhc2V0LndoYXQpIHtcbiAgICAgIGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3JBbGwoJ1tkYXRhLWNsb3NlXScpLmZvckVhY2goc2libGluZyA9PiB7XG4gICAgICAgIGlmIChzaWJsaW5nICE9PSB0cmlnZ2VyKSBkZWxldGUgc2libGluZy5kYXRhc2V0LmNsb3NlO1xuICAgICAgfSk7XG4gICAgfVxuICAgIGlmICh0cmlnZ2VyLmRhdGFzZXQuZm9yKSB7XG4gICAgICBpZiAodHJpZ2dlci5kYXRhc2V0LmNsb3NlKSBkZWxldGUgdHJpZ2dlci5kYXRhc2V0LmNsb3NlO1xuICAgICAgZWxzZSB0cmlnZ2VyLmRhdGFzZXQuY2xvc2UgPSB0cnVlO1xuICAgIH1cbiAgfVxuXG4gIGRpc21pc3NNb2RhbChlcmFzZSA9IGZhbHNlLCBjb250ZW50ID0gbnVsbCkge1xuICAgIGlmICh0aGlzLm1vZGFsY29udGVudCkge1xuICAgICAgY29uc3QgZXZlbnQgPSBuZXcgRXZlbnQoJ2Rpc21pc3Ntb2RhbCcpO1xuICAgICAgdGhpcy5tb2RhbGNvbnRlbnQucXVlcnlTZWxlY3RvckFsbCgnLmpzJykuZm9yRWFjaChlbGVtZW50ID0+IGVsZW1lbnQuZGlzcGF0Y2hFdmVudChldmVudCkpO1xuICAgICAgaWYgKGVyYXNlKSB0aGlzLm1vZGFsY29udGVudC5pbm5lckhUTUwgPSBgYDtcblxuICAgIH1cbiAgICBpZiAodGhpcy50cmlnZ2VyLmRhdGFzZXQuZm9yKSB7XG4gICAgICB0aGlzLm1vZGFsLm9wZW4gPSBmYWxzZTtcbiAgICAgIHRoaXMudG9nZ2xlQWN0aW9uKHRoaXMudHJpZ2dlcik7XG4gICAgfVxuXG4gIH1cblxufSJdLCJuYW1lcyI6W10sInNvdXJjZVJvb3QiOiIifQ==\n//# sourceURL=webpack-internal:///./src/modules/modal-container.js\n")}}]);