/*! For license information please see src_modules_js-tabs_js.js.LICENSE.txt */
"use strict";(self.webpackChunk=self.webpackChunk||[]).push([["src_modules_js-tabs_js"],{"./src/modules/js-tabs.js":(__unused_webpack_module,__webpack_exports__,__webpack_require__)=>{eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   JsTabs: () => (/* binding */ JsTabs)\n/* harmony export */ });\n/* harmony import */ var _modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../modules/modules-config.js */ \"./src/modules/modules-config.js\");\n\nlet instance = null;\nclass JsTabs {\n\n  constructor(item, options = {}) {\n    if (!instance) {\n      let btns = item.querySelectorAll(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.domselectors.component.tabs.tabcontrol);\n      if (btns.length === 0) {\n        btns = item.querySelectorAll(((item.dataset.selector) ? item.dataset.selector : 'legend'));\n\n      }\n\n      this.toggledisable = (item.dataset.toggledisable) ? true : false;\n      this.togglewhat = (item.dataset.togglewhat) ? item.dataset.togglewhat : null;\n      let l = 0;\n      btns.forEach((btn, index) => {\n        const target = (btn.dataset.target) ? item.querySelector('#' + btn.dataset.target) : btn.closest(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.domselectors.component.tabs.tab);\n        if (!target) return;\n        const ev = (item.dataset.event) ? item.dataset.event : 'click';\n        btn.style.left = l + 'px';\n        if (index === 0 && target.parentElement.querySelectorAll('.' + _modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.css.active).length === 0) {\n          target.classList.add(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.css.active);\n          this.toggleTab(target, true);\n\n        } else this.toggleTab(target, target.classList.contains(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.css.active));\n        l += parseInt(btn.offsetWidth) + 20;\n        btn.addEventListener(ev, (e) => {\n          if (e.currentTarget.disabled === true) {\n            e.preventDefault();\n            return;\n          }\n          const oldactive = item.dataset.selector ? target.parentElement.querySelector('.' + _modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.css.active) : item.querySelector(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.domselectors.component.tabs.tab + '.' + _modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.css.active);\n          if (oldactive !== null) {\n            oldactive.classList.remove(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.css.active);\n            this.toggleTab(oldactive, false);\n          }\n          target.classList.add(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.css.active);\n          this.toggleTab(target, true);\n        });\n      })\n      if (!item.dataset.toggle) this.toggleDisplayListener(item, btns);\n      instance = this;\n    }\n    return instance;\n  }\n\n  toggleTab(tab, show) {\n    let what = (this.togglewhat) ? document.getElementById(this.togglewhat) : null;\n\n    let tabcontents = tab.querySelectorAll(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.domselectors.component.tabs.tabcontent);\n    if (tabcontents.length === 0) tabcontents = [tab];\n    tabcontents.forEach(tabcontent => {\n      if (show === true) tabcontent.classList.remove(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.css.hide);\n      else if (!tab.classList.contains('active')) tabcontent.classList.add(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.css.hide);\n      if (this.toggledisable === true) {\n        tabcontent.querySelectorAll('input, select, button, textarea').forEach(el => {\n          if (show) {\n            el.removeAttribute('disabled');\n            if (el.dataset.checked) {\n              el.checked = el.dataset.checked;\n              delete el.dataset.checked;\n            }\n          } else {\n            el.disabled = true;\n            if (el.checked) {\n              el.dataset.checked = el.checked;\n              el.removeAttribute('checked');\n            }\n          }\n        });\n        if (what) what.value = tabcontent.dataset.what;\n        if (show) {\n          const form = tab.closest('form');\n          if (tabcontent.dataset.path && form !== null) form.setAttribute('action', tabcontent.dataset.path);\n        }\n      }\n    });\n  }\n  toggleDisplayListener(item, btns) {\n    // flat/ tabs display\n    const dismiss = item.querySelector('[data-dismiss=\"tabs\"]');\n    const toggle_tab = ((index, btn, show) => {\n      btn.disabled = show;\n      this.toggleTab(btn.closest(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.domselectors.component.tabs.tab), show);\n    })\n    if (dismiss) dismiss.addEventListener('click', (e) => {\n      const icon = item.querySelector('.tabs-display');\n      btns.forEach((btn, index) => toggle_tab(index, btn, (item.classList.contains(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.css.component.tabs.name))));\n      item.classList.toggle(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.css.component.tabs.name);\n      icon.classList.toggle('expand');\n      icon.classList.toggle('shrink');\n    });\n  }\n}//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvbW9kdWxlcy9qcy10YWJzLmpzIiwibWFwcGluZ3MiOiI7Ozs7O0FBR3NDO0FBQ3RDO0FBQ087O0FBRVAsZ0NBQWdDO0FBQ2hDO0FBQ0EsdUNBQXVDLG9FQUFZO0FBQ25EO0FBQ0E7O0FBRUE7O0FBRUE7QUFDQTtBQUNBO0FBQ0E7QUFDQSx5R0FBeUcsb0VBQVk7QUFDckg7QUFDQTtBQUNBO0FBQ0EsdUVBQXVFLDJEQUFHO0FBQzFFLCtCQUErQiwyREFBRztBQUNsQzs7QUFFQSxVQUFVLHNEQUFzRCwyREFBRztBQUNuRTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSw2RkFBNkYsMkRBQUcsOEJBQThCLG9FQUFZLDRCQUE0QiwyREFBRztBQUN6SztBQUNBLHVDQUF1QywyREFBRztBQUMxQztBQUNBO0FBQ0EsK0JBQStCLDJEQUFHO0FBQ2xDO0FBQ0EsU0FBUztBQUNULE9BQU87QUFDUDtBQUNBO0FBQ0E7QUFDQTtBQUNBOztBQUVBO0FBQ0E7O0FBRUEsMkNBQTJDLG9FQUFZO0FBQ3ZEO0FBQ0E7QUFDQSxxREFBcUQsMkRBQUc7QUFDeEQsMkVBQTJFLDJEQUFHO0FBQzlFO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSxZQUFZO0FBQ1o7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EsU0FBUztBQUNUO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBLEtBQUs7QUFDTDtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSxpQ0FBaUMsb0VBQVk7QUFDN0MsS0FBSztBQUNMO0FBQ0E7QUFDQSxtRkFBbUYsMkRBQUc7QUFDdEYsNEJBQTRCLDJEQUFHO0FBQy9CO0FBQ0E7QUFDQSxLQUFLO0FBQ0w7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovLy8uL3NyYy9tb2R1bGVzL2pzLXRhYnMuanM/MWMwNCJdLCJzb3VyY2VzQ29udGVudCI6WyJpbXBvcnQge1xuICBjc3MsXG4gIGRvbXNlbGVjdG9yc1xufSBmcm9tICcuLi9tb2R1bGVzL21vZHVsZXMtY29uZmlnLmpzJztcbmxldCBpbnN0YW5jZSA9IG51bGw7XG5leHBvcnQgY2xhc3MgSnNUYWJzIHtcblxuICBjb25zdHJ1Y3RvcihpdGVtLCBvcHRpb25zID0ge30pIHtcbiAgICBpZiAoIWluc3RhbmNlKSB7XG4gICAgICBsZXQgYnRucyA9IGl0ZW0ucXVlcnlTZWxlY3RvckFsbChkb21zZWxlY3RvcnMuY29tcG9uZW50LnRhYnMudGFiY29udHJvbCk7XG4gICAgICBpZiAoYnRucy5sZW5ndGggPT09IDApIHtcbiAgICAgICAgYnRucyA9IGl0ZW0ucXVlcnlTZWxlY3RvckFsbCgoKGl0ZW0uZGF0YXNldC5zZWxlY3RvcikgPyBpdGVtLmRhdGFzZXQuc2VsZWN0b3IgOiAnbGVnZW5kJykpO1xuXG4gICAgICB9XG5cbiAgICAgIHRoaXMudG9nZ2xlZGlzYWJsZSA9IChpdGVtLmRhdGFzZXQudG9nZ2xlZGlzYWJsZSkgPyB0cnVlIDogZmFsc2U7XG4gICAgICB0aGlzLnRvZ2dsZXdoYXQgPSAoaXRlbS5kYXRhc2V0LnRvZ2dsZXdoYXQpID8gaXRlbS5kYXRhc2V0LnRvZ2dsZXdoYXQgOiBudWxsO1xuICAgICAgbGV0IGwgPSAwO1xuICAgICAgYnRucy5mb3JFYWNoKChidG4sIGluZGV4KSA9PiB7XG4gICAgICAgIGNvbnN0IHRhcmdldCA9IChidG4uZGF0YXNldC50YXJnZXQpID8gaXRlbS5xdWVyeVNlbGVjdG9yKCcjJyArIGJ0bi5kYXRhc2V0LnRhcmdldCkgOiBidG4uY2xvc2VzdChkb21zZWxlY3RvcnMuY29tcG9uZW50LnRhYnMudGFiKTtcbiAgICAgICAgaWYgKCF0YXJnZXQpIHJldHVybjtcbiAgICAgICAgY29uc3QgZXYgPSAoaXRlbS5kYXRhc2V0LmV2ZW50KSA/IGl0ZW0uZGF0YXNldC5ldmVudCA6ICdjbGljayc7XG4gICAgICAgIGJ0bi5zdHlsZS5sZWZ0ID0gbCArICdweCc7XG4gICAgICAgIGlmIChpbmRleCA9PT0gMCAmJiB0YXJnZXQucGFyZW50RWxlbWVudC5xdWVyeVNlbGVjdG9yQWxsKCcuJyArIGNzcy5hY3RpdmUpLmxlbmd0aCA9PT0gMCkge1xuICAgICAgICAgIHRhcmdldC5jbGFzc0xpc3QuYWRkKGNzcy5hY3RpdmUpO1xuICAgICAgICAgIHRoaXMudG9nZ2xlVGFiKHRhcmdldCwgdHJ1ZSk7XG5cbiAgICAgICAgfSBlbHNlIHRoaXMudG9nZ2xlVGFiKHRhcmdldCwgdGFyZ2V0LmNsYXNzTGlzdC5jb250YWlucyhjc3MuYWN0aXZlKSk7XG4gICAgICAgIGwgKz0gcGFyc2VJbnQoYnRuLm9mZnNldFdpZHRoKSArIDIwO1xuICAgICAgICBidG4uYWRkRXZlbnRMaXN0ZW5lcihldiwgKGUpID0+IHtcbiAgICAgICAgICBpZiAoZS5jdXJyZW50VGFyZ2V0LmRpc2FibGVkID09PSB0cnVlKSB7XG4gICAgICAgICAgICBlLnByZXZlbnREZWZhdWx0KCk7XG4gICAgICAgICAgICByZXR1cm47XG4gICAgICAgICAgfVxuICAgICAgICAgIGNvbnN0IG9sZGFjdGl2ZSA9IGl0ZW0uZGF0YXNldC5zZWxlY3RvciA/IHRhcmdldC5wYXJlbnRFbGVtZW50LnF1ZXJ5U2VsZWN0b3IoJy4nICsgY3NzLmFjdGl2ZSkgOiBpdGVtLnF1ZXJ5U2VsZWN0b3IoZG9tc2VsZWN0b3JzLmNvbXBvbmVudC50YWJzLnRhYiArICcuJyArIGNzcy5hY3RpdmUpO1xuICAgICAgICAgIGlmIChvbGRhY3RpdmUgIT09IG51bGwpIHtcbiAgICAgICAgICAgIG9sZGFjdGl2ZS5jbGFzc0xpc3QucmVtb3ZlKGNzcy5hY3RpdmUpO1xuICAgICAgICAgICAgdGhpcy50b2dnbGVUYWIob2xkYWN0aXZlLCBmYWxzZSk7XG4gICAgICAgICAgfVxuICAgICAgICAgIHRhcmdldC5jbGFzc0xpc3QuYWRkKGNzcy5hY3RpdmUpO1xuICAgICAgICAgIHRoaXMudG9nZ2xlVGFiKHRhcmdldCwgdHJ1ZSk7XG4gICAgICAgIH0pO1xuICAgICAgfSlcbiAgICAgIGlmICghaXRlbS5kYXRhc2V0LnRvZ2dsZSkgdGhpcy50b2dnbGVEaXNwbGF5TGlzdGVuZXIoaXRlbSwgYnRucyk7XG4gICAgICBpbnN0YW5jZSA9IHRoaXM7XG4gICAgfVxuICAgIHJldHVybiBpbnN0YW5jZTtcbiAgfVxuXG4gIHRvZ2dsZVRhYih0YWIsIHNob3cpIHtcbiAgICBsZXQgd2hhdCA9ICh0aGlzLnRvZ2dsZXdoYXQpID8gZG9jdW1lbnQuZ2V0RWxlbWVudEJ5SWQodGhpcy50b2dnbGV3aGF0KSA6IG51bGw7XG5cbiAgICBsZXQgdGFiY29udGVudHMgPSB0YWIucXVlcnlTZWxlY3RvckFsbChkb21zZWxlY3RvcnMuY29tcG9uZW50LnRhYnMudGFiY29udGVudCk7XG4gICAgaWYgKHRhYmNvbnRlbnRzLmxlbmd0aCA9PT0gMCkgdGFiY29udGVudHMgPSBbdGFiXTtcbiAgICB0YWJjb250ZW50cy5mb3JFYWNoKHRhYmNvbnRlbnQgPT4ge1xuICAgICAgaWYgKHNob3cgPT09IHRydWUpIHRhYmNvbnRlbnQuY2xhc3NMaXN0LnJlbW92ZShjc3MuaGlkZSk7XG4gICAgICBlbHNlIGlmICghdGFiLmNsYXNzTGlzdC5jb250YWlucygnYWN0aXZlJykpIHRhYmNvbnRlbnQuY2xhc3NMaXN0LmFkZChjc3MuaGlkZSk7XG4gICAgICBpZiAodGhpcy50b2dnbGVkaXNhYmxlID09PSB0cnVlKSB7XG4gICAgICAgIHRhYmNvbnRlbnQucXVlcnlTZWxlY3RvckFsbCgnaW5wdXQsIHNlbGVjdCwgYnV0dG9uLCB0ZXh0YXJlYScpLmZvckVhY2goZWwgPT4ge1xuICAgICAgICAgIGlmIChzaG93KSB7XG4gICAgICAgICAgICBlbC5yZW1vdmVBdHRyaWJ1dGUoJ2Rpc2FibGVkJyk7XG4gICAgICAgICAgICBpZiAoZWwuZGF0YXNldC5jaGVja2VkKSB7XG4gICAgICAgICAgICAgIGVsLmNoZWNrZWQgPSBlbC5kYXRhc2V0LmNoZWNrZWQ7XG4gICAgICAgICAgICAgIGRlbGV0ZSBlbC5kYXRhc2V0LmNoZWNrZWQ7XG4gICAgICAgICAgICB9XG4gICAgICAgICAgfSBlbHNlIHtcbiAgICAgICAgICAgIGVsLmRpc2FibGVkID0gdHJ1ZTtcbiAgICAgICAgICAgIGlmIChlbC5jaGVja2VkKSB7XG4gICAgICAgICAgICAgIGVsLmRhdGFzZXQuY2hlY2tlZCA9IGVsLmNoZWNrZWQ7XG4gICAgICAgICAgICAgIGVsLnJlbW92ZUF0dHJpYnV0ZSgnY2hlY2tlZCcpO1xuICAgICAgICAgICAgfVxuICAgICAgICAgIH1cbiAgICAgICAgfSk7XG4gICAgICAgIGlmICh3aGF0KSB3aGF0LnZhbHVlID0gdGFiY29udGVudC5kYXRhc2V0LndoYXQ7XG4gICAgICAgIGlmIChzaG93KSB7XG4gICAgICAgICAgY29uc3QgZm9ybSA9IHRhYi5jbG9zZXN0KCdmb3JtJyk7XG4gICAgICAgICAgaWYgKHRhYmNvbnRlbnQuZGF0YXNldC5wYXRoICYmIGZvcm0gIT09IG51bGwpIGZvcm0uc2V0QXR0cmlidXRlKCdhY3Rpb24nLCB0YWJjb250ZW50LmRhdGFzZXQucGF0aCk7XG4gICAgICAgIH1cbiAgICAgIH1cbiAgICB9KTtcbiAgfVxuICB0b2dnbGVEaXNwbGF5TGlzdGVuZXIoaXRlbSwgYnRucykge1xuICAgIC8vIGZsYXQvIHRhYnMgZGlzcGxheVxuICAgIGNvbnN0IGRpc21pc3MgPSBpdGVtLnF1ZXJ5U2VsZWN0b3IoJ1tkYXRhLWRpc21pc3M9XCJ0YWJzXCJdJyk7XG4gICAgY29uc3QgdG9nZ2xlX3RhYiA9ICgoaW5kZXgsIGJ0biwgc2hvdykgPT4ge1xuICAgICAgYnRuLmRpc2FibGVkID0gc2hvdztcbiAgICAgIHRoaXMudG9nZ2xlVGFiKGJ0bi5jbG9zZXN0KGRvbXNlbGVjdG9ycy5jb21wb25lbnQudGFicy50YWIpLCBzaG93KTtcbiAgICB9KVxuICAgIGlmIChkaXNtaXNzKSBkaXNtaXNzLmFkZEV2ZW50TGlzdGVuZXIoJ2NsaWNrJywgKGUpID0+IHtcbiAgICAgIGNvbnN0IGljb24gPSBpdGVtLnF1ZXJ5U2VsZWN0b3IoJy50YWJzLWRpc3BsYXknKTtcbiAgICAgIGJ0bnMuZm9yRWFjaCgoYnRuLCBpbmRleCkgPT4gdG9nZ2xlX3RhYihpbmRleCwgYnRuLCAoaXRlbS5jbGFzc0xpc3QuY29udGFpbnMoY3NzLmNvbXBvbmVudC50YWJzLm5hbWUpKSkpO1xuICAgICAgaXRlbS5jbGFzc0xpc3QudG9nZ2xlKGNzcy5jb21wb25lbnQudGFicy5uYW1lKTtcbiAgICAgIGljb24uY2xhc3NMaXN0LnRvZ2dsZSgnZXhwYW5kJyk7XG4gICAgICBpY29uLmNsYXNzTGlzdC50b2dnbGUoJ3NocmluaycpO1xuICAgIH0pO1xuICB9XG59Il0sIm5hbWVzIjpbXSwic291cmNlUm9vdCI6IiJ9\n//# sourceURL=webpack-internal:///./src/modules/js-tabs.js\n")}}]);