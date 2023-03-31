/*! For license information please see src_modules_modal-container_js.js.LICENSE.txt */
"use strict";(self.webpackChunk=self.webpackChunk||[]).push([["src_modules_modal-container_js"],{"./src/modules/modal-container.js":(__unused_webpack_module,__webpack_exports__,__webpack_require__)=>{eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"ModalContainer\": () => (/* binding */ ModalContainer)\n/* harmony export */ });\n/* harmony import */ var _modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../modules/modules-config.js */ \"./src/modules/modules-config.js\");\n\n\nclass ModalContainer {\n  listener = null;\n  trigger = null;\n  modal = null;\n  modalcontent = null;\n  constructor(trigger) {\n    const defaultOptions = {};\n    // todo search for options in the item data attrs\n    if (!this.modal && (!this.trigger || this.trigger !== trigger)) {\n      this.trigger = trigger;\n\n      if (trigger.dataset.what === \"help\") {\n        this.modal = (document.getElementById(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.domselectors.component.modal.help.substr(1))) ? document.getElementById(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.domselectors.component.modal.help.substr(1)) : document.querySelector(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.domselectors.component.modal.help);\n      } else if (trigger.dataset.target && trigger.dataset.target !== 'unique') this.modal = document.getElementById(trigger.dataset.target);\n      else this.modal = trigger.closest(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.domselectors.component.modal.modalcontainer);\n      this.modalcontent = this.modal.querySelector(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.domselectors.component.modal.modalcontent);\n\n      this.addListeners();\n    }\n    return this;\n  }\n  addListeners() {\n    this.modal.addEventListener('toggle', (e) => {\n      const open = e.currentTarget.open;\n      if (open) document.body.classList.add(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.css.hidevscroll);\n      else document.body.classList.remove(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.css.hidevscroll);\n      const summary = this.modal.querySelector('summary');\n      if (summary) {\n        summary.setAttribute('aria-hidden', !open);\n        this.toggleAction(summary);\n      }\n\n    });\n\n  }\n\n  setContent(html) {\n    // data have been sanitzed before in other scripts and from the server\n    html = html instanceof HTMLElement ? html.outerHTML : html;\n    this.modalcontent.innerHTML = html;\n    return this.modalcontent;\n  }\n  getContentSiblings() {\n    return this.modal.querySelectorAll('details');\n  }\n  getBySelector(selector) {\n    return this.modal.querySelector(selector);\n  }\n  modalOpen(trigger) {\n    if (!this.modal.open) this.modal.open = true;\n    this.openContent(trigger);\n\n\n  }\n\n  openContent(trigger) {\n\n    if (!trigger.dataset.for) return;\n    if (trigger.dataset.close) return this.dismissModal();\n    const siblings = this.getContentSiblings();\n    siblings.forEach(sibling => {\n      if (sibling !== trigger) sibling.removeAttribute('open');\n    });\n    const paragraph = this.modal.querySelector('#' + trigger.dataset.for);\n    if (paragraph) paragraph.open = true;\n    else console.log('help ' + trigger.dataset.for+'display error', this.modal);\n    this.toggleAction(trigger);\n  }\n\n\n  toggleAction(trigger) {\n    const summary = this.modal.querySelector('summary');\n    let action = trigger.dataset.action;\n    if (!action) return;\n    if (trigger.dataset.what) {\n      document.querySelectorAll('[data-close]').forEach(sibling => {\n        if (sibling !== trigger) delete sibling.dataset.close;\n      });\n    }\n    if (trigger.dataset.for) {\n      if (trigger.dataset.close) delete trigger.dataset.close;\n      else trigger.dataset.close = true;\n    }\n  }\n\n  dismissModal(erase = false, content = null) {\n    if (this.modalcontent) {\n      const event = new Event('dismissmodal');\n      this.modalcontent.querySelectorAll('.js').forEach(element => element.dispatchEvent(event));\n      if (erase) this.modalcontent.innerHTML = ``;\n\n    }\n    if (this.trigger.dataset.for) {\n      this.modal.open = false;\n      this.toggleAction(this.trigger);\n    }\n\n  }\n\n}//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvbW9kdWxlcy9tb2RhbC1jb250YWluZXIuanMuanMiLCJtYXBwaW5ncyI6Ijs7Ozs7QUFHc0M7O0FBRS9CO0FBQ1A7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOztBQUVBO0FBQ0EsOENBQThDLGdHQUF3QyxnQ0FBZ0MsZ0dBQXdDLDhCQUE4Qix5RkFBaUM7QUFDN04sUUFBUTtBQUNSLHdDQUF3QyxtR0FBMkM7QUFDbkYsbURBQW1ELGlHQUF5Qzs7QUFFNUY7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSw0Q0FBNEMsdUVBQWU7QUFDM0QsMENBQTBDLHVFQUFlO0FBQ3pEO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7O0FBRUEsS0FBSzs7QUFFTDs7QUFFQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7OztBQUdBOztBQUVBOztBQUVBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSxLQUFLO0FBQ0w7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7O0FBR0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSxPQUFPO0FBQ1A7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOztBQUVBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7O0FBRUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7QUFFQTs7QUFFQSIsInNvdXJjZXMiOlsid2VicGFjazovLy8uL3NyYy9tb2R1bGVzL21vZGFsLWNvbnRhaW5lci5qcz8zNGFlIl0sInNvdXJjZXNDb250ZW50IjpbImltcG9ydCB7XG4gIGRvbXNlbGVjdG9ycyxcbiAgY3NzXG59IGZyb20gJy4uL21vZHVsZXMvbW9kdWxlcy1jb25maWcuanMnO1xuXG5leHBvcnQgY2xhc3MgTW9kYWxDb250YWluZXIge1xuICBsaXN0ZW5lciA9IG51bGw7XG4gIHRyaWdnZXIgPSBudWxsO1xuICBtb2RhbCA9IG51bGw7XG4gIG1vZGFsY29udGVudCA9IG51bGw7XG4gIGNvbnN0cnVjdG9yKHRyaWdnZXIpIHtcbiAgICBjb25zdCBkZWZhdWx0T3B0aW9ucyA9IHt9O1xuICAgIC8vIHRvZG8gc2VhcmNoIGZvciBvcHRpb25zIGluIHRoZSBpdGVtIGRhdGEgYXR0cnNcbiAgICBpZiAoIXRoaXMubW9kYWwgJiYgKCF0aGlzLnRyaWdnZXIgfHwgdGhpcy50cmlnZ2VyICE9PSB0cmlnZ2VyKSkge1xuICAgICAgdGhpcy50cmlnZ2VyID0gdHJpZ2dlcjtcblxuICAgICAgaWYgKHRyaWdnZXIuZGF0YXNldC53aGF0ID09PSBcImhlbHBcIikge1xuICAgICAgICB0aGlzLm1vZGFsID0gKGRvY3VtZW50LmdldEVsZW1lbnRCeUlkKGRvbXNlbGVjdG9ycy5jb21wb25lbnQubW9kYWwuaGVscC5zdWJzdHIoMSkpKSA/IGRvY3VtZW50LmdldEVsZW1lbnRCeUlkKGRvbXNlbGVjdG9ycy5jb21wb25lbnQubW9kYWwuaGVscC5zdWJzdHIoMSkpIDogZG9jdW1lbnQucXVlcnlTZWxlY3Rvcihkb21zZWxlY3RvcnMuY29tcG9uZW50Lm1vZGFsLmhlbHApO1xuICAgICAgfSBlbHNlIGlmICh0cmlnZ2VyLmRhdGFzZXQudGFyZ2V0ICYmIHRyaWdnZXIuZGF0YXNldC50YXJnZXQgIT09ICd1bmlxdWUnKSB0aGlzLm1vZGFsID0gZG9jdW1lbnQuZ2V0RWxlbWVudEJ5SWQodHJpZ2dlci5kYXRhc2V0LnRhcmdldCk7XG4gICAgICBlbHNlIHRoaXMubW9kYWwgPSB0cmlnZ2VyLmNsb3Nlc3QoZG9tc2VsZWN0b3JzLmNvbXBvbmVudC5tb2RhbC5tb2RhbGNvbnRhaW5lcik7XG4gICAgICB0aGlzLm1vZGFsY29udGVudCA9IHRoaXMubW9kYWwucXVlcnlTZWxlY3Rvcihkb21zZWxlY3RvcnMuY29tcG9uZW50Lm1vZGFsLm1vZGFsY29udGVudCk7XG5cbiAgICAgIHRoaXMuYWRkTGlzdGVuZXJzKCk7XG4gICAgfVxuICAgIHJldHVybiB0aGlzO1xuICB9XG4gIGFkZExpc3RlbmVycygpIHtcbiAgICB0aGlzLm1vZGFsLmFkZEV2ZW50TGlzdGVuZXIoJ3RvZ2dsZScsIChlKSA9PiB7XG4gICAgICBjb25zdCBvcGVuID0gZS5jdXJyZW50VGFyZ2V0Lm9wZW47XG4gICAgICBpZiAob3BlbikgZG9jdW1lbnQuYm9keS5jbGFzc0xpc3QuYWRkKGNzcy5oaWRldnNjcm9sbCk7XG4gICAgICBlbHNlIGRvY3VtZW50LmJvZHkuY2xhc3NMaXN0LnJlbW92ZShjc3MuaGlkZXZzY3JvbGwpO1xuICAgICAgY29uc3Qgc3VtbWFyeSA9IHRoaXMubW9kYWwucXVlcnlTZWxlY3Rvcignc3VtbWFyeScpO1xuICAgICAgaWYgKHN1bW1hcnkpIHtcbiAgICAgICAgc3VtbWFyeS5zZXRBdHRyaWJ1dGUoJ2FyaWEtaGlkZGVuJywgIW9wZW4pO1xuICAgICAgICB0aGlzLnRvZ2dsZUFjdGlvbihzdW1tYXJ5KTtcbiAgICAgIH1cblxuICAgIH0pO1xuXG4gIH1cblxuICBzZXRDb250ZW50KGh0bWwpIHtcbiAgICAvLyBkYXRhIGhhdmUgYmVlbiBzYW5pdHplZCBiZWZvcmUgaW4gb3RoZXIgc2NyaXB0cyBhbmQgZnJvbSB0aGUgc2VydmVyXG4gICAgaHRtbCA9IGh0bWwgaW5zdGFuY2VvZiBIVE1MRWxlbWVudCA/IGh0bWwub3V0ZXJIVE1MIDogaHRtbDtcbiAgICB0aGlzLm1vZGFsY29udGVudC5pbm5lckhUTUwgPSBodG1sO1xuICAgIHJldHVybiB0aGlzLm1vZGFsY29udGVudDtcbiAgfVxuICBnZXRDb250ZW50U2libGluZ3MoKSB7XG4gICAgcmV0dXJuIHRoaXMubW9kYWwucXVlcnlTZWxlY3RvckFsbCgnZGV0YWlscycpO1xuICB9XG4gIGdldEJ5U2VsZWN0b3Ioc2VsZWN0b3IpIHtcbiAgICByZXR1cm4gdGhpcy5tb2RhbC5xdWVyeVNlbGVjdG9yKHNlbGVjdG9yKTtcbiAgfVxuICBtb2RhbE9wZW4odHJpZ2dlcikge1xuICAgIGlmICghdGhpcy5tb2RhbC5vcGVuKSB0aGlzLm1vZGFsLm9wZW4gPSB0cnVlO1xuICAgIHRoaXMub3BlbkNvbnRlbnQodHJpZ2dlcik7XG5cblxuICB9XG5cbiAgb3BlbkNvbnRlbnQodHJpZ2dlcikge1xuXG4gICAgaWYgKCF0cmlnZ2VyLmRhdGFzZXQuZm9yKSByZXR1cm47XG4gICAgaWYgKHRyaWdnZXIuZGF0YXNldC5jbG9zZSkgcmV0dXJuIHRoaXMuZGlzbWlzc01vZGFsKCk7XG4gICAgY29uc3Qgc2libGluZ3MgPSB0aGlzLmdldENvbnRlbnRTaWJsaW5ncygpO1xuICAgIHNpYmxpbmdzLmZvckVhY2goc2libGluZyA9PiB7XG4gICAgICBpZiAoc2libGluZyAhPT0gdHJpZ2dlcikgc2libGluZy5yZW1vdmVBdHRyaWJ1dGUoJ29wZW4nKTtcbiAgICB9KTtcbiAgICBjb25zdCBwYXJhZ3JhcGggPSB0aGlzLm1vZGFsLnF1ZXJ5U2VsZWN0b3IoJyMnICsgdHJpZ2dlci5kYXRhc2V0LmZvcik7XG4gICAgaWYgKHBhcmFncmFwaCkgcGFyYWdyYXBoLm9wZW4gPSB0cnVlO1xuICAgIGVsc2UgY29uc29sZS5sb2coJ2hlbHAgJyArIHRyaWdnZXIuZGF0YXNldC5mb3IrJ2Rpc3BsYXkgZXJyb3InLCB0aGlzLm1vZGFsKTtcbiAgICB0aGlzLnRvZ2dsZUFjdGlvbih0cmlnZ2VyKTtcbiAgfVxuXG5cbiAgdG9nZ2xlQWN0aW9uKHRyaWdnZXIpIHtcbiAgICBjb25zdCBzdW1tYXJ5ID0gdGhpcy5tb2RhbC5xdWVyeVNlbGVjdG9yKCdzdW1tYXJ5Jyk7XG4gICAgbGV0IGFjdGlvbiA9IHRyaWdnZXIuZGF0YXNldC5hY3Rpb247XG4gICAgaWYgKCFhY3Rpb24pIHJldHVybjtcbiAgICBpZiAodHJpZ2dlci5kYXRhc2V0LndoYXQpIHtcbiAgICAgIGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3JBbGwoJ1tkYXRhLWNsb3NlXScpLmZvckVhY2goc2libGluZyA9PiB7XG4gICAgICAgIGlmIChzaWJsaW5nICE9PSB0cmlnZ2VyKSBkZWxldGUgc2libGluZy5kYXRhc2V0LmNsb3NlO1xuICAgICAgfSk7XG4gICAgfVxuICAgIGlmICh0cmlnZ2VyLmRhdGFzZXQuZm9yKSB7XG4gICAgICBpZiAodHJpZ2dlci5kYXRhc2V0LmNsb3NlKSBkZWxldGUgdHJpZ2dlci5kYXRhc2V0LmNsb3NlO1xuICAgICAgZWxzZSB0cmlnZ2VyLmRhdGFzZXQuY2xvc2UgPSB0cnVlO1xuICAgIH1cbiAgfVxuXG4gIGRpc21pc3NNb2RhbChlcmFzZSA9IGZhbHNlLCBjb250ZW50ID0gbnVsbCkge1xuICAgIGlmICh0aGlzLm1vZGFsY29udGVudCkge1xuICAgICAgY29uc3QgZXZlbnQgPSBuZXcgRXZlbnQoJ2Rpc21pc3Ntb2RhbCcpO1xuICAgICAgdGhpcy5tb2RhbGNvbnRlbnQucXVlcnlTZWxlY3RvckFsbCgnLmpzJykuZm9yRWFjaChlbGVtZW50ID0+IGVsZW1lbnQuZGlzcGF0Y2hFdmVudChldmVudCkpO1xuICAgICAgaWYgKGVyYXNlKSB0aGlzLm1vZGFsY29udGVudC5pbm5lckhUTUwgPSBgYDtcblxuICAgIH1cbiAgICBpZiAodGhpcy50cmlnZ2VyLmRhdGFzZXQuZm9yKSB7XG4gICAgICB0aGlzLm1vZGFsLm9wZW4gPSBmYWxzZTtcbiAgICAgIHRoaXMudG9nZ2xlQWN0aW9uKHRoaXMudHJpZ2dlcik7XG4gICAgfVxuXG4gIH1cblxufSJdLCJuYW1lcyI6W10sInNvdXJjZVJvb3QiOiIifQ==\n//# sourceURL=webpack-internal:///./src/modules/modal-container.js\n")}}]);