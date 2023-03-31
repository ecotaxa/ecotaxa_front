/*! For license information please see src_modules_js-tabs_js.js.LICENSE.txt */
"use strict";(self.webpackChunk=self.webpackChunk||[]).push([["src_modules_js-tabs_js"],{"./src/modules/js-tabs.js":(__unused_webpack_module,__webpack_exports__,__webpack_require__)=>{eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"JsTabs\": () => (/* binding */ JsTabs)\n/* harmony export */ });\n/* harmony import */ var _modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../modules/modules-config.js */ \"./src/modules/modules-config.js\");\n\nlet instance = null;\nclass JsTabs {\n\n  constructor(item, options = {}) {\n    if (!instance) {\n      let btns = item.querySelectorAll(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.domselectors.component.tabs.tabcontrol);\n      if (btns.length === 0) {\n        btns = item.querySelectorAll(((item.dataset.selector) ? item.dataset.selector : 'legend'));\n\n      }\n\n      this.toggledisable = (item.dataset.toggledisable) ? true : false;\n      let l = 0;\n      btns.forEach((btn, index) => {\n        const target = (btn.dataset.target) ? item.querySelector('#' + btn.dataset.target) : btn.closest(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.domselectors.component.tabs.tab);\n        if (!target) return;\n        const ev = (item.dataset.event) ? item.dataset.event : 'click';\n        btn.style.left = l + 'px';\n        if (index === 0) {\n          target.classList.add(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.css.active);\n          this.toggleTab(target, true);\n        } else this.toggleTab(target, false);\n        l += parseInt(btn.offsetWidth) + 20;\n        btn.addEventListener(ev, (e) => {\n          if (e.currentTarget.disabled === true) {\n            e.preventDefault();\n            return;\n          }\n          const oldactive = item.dataset.selector ? target.parentElement.querySelector('.' + _modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.css.active) : item.querySelector(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.domselectors.component.tabs.tab + '.' + _modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.css.active);\n          if (oldactive !== null) {\n            oldactive.classList.remove(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.css.active);\n            this.toggleTab(oldactive, false);\n          }\n          target.classList.add(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.css.active);\n          this.toggleTab(target, true);\n        });\n      })\n      if (!item.dataset.toggle) this.toggleDisplayListener(item, btns);\n      instance = this;\n    }\n    return instance;\n  }\n\n  toggleTab(tab, show) {\n    let what = (this.togglewhat) ? document.querySelector(this.togglewhat) : null;\n    let tabcontents = tab.querySelectorAll(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.domselectors.component.tabs.tabcontent);\n    if (tabcontents.length === 0) tabcontents = [tab];\n    tabcontents.forEach(tabcontent => {\n      if (show === true) tabcontent.classList.remove(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.css.hide);\n      else if (!tab.classList.contains('active')) tabcontent.classList.add(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.css.hide);\n      if (this.toggledisable === true) {\n        tabcontent.querySelectorAll('input, select, button, textarea').forEach(el => {\n          if (show) {\n            el.removeAttribute('disabled');\n            if (what) what.value = el.dataset.what;\n          } else el.disabled = true;\n        });\n      }\n    });\n\n  }\n  toggleDisplayListener(item, btns) {\n    // flat/ tabs display\n    const dismiss = item.querySelector('[data-dismiss=\"tabs\"]');\n    const toggle_tab = ((index, btn, show) => {\n      btn.disabled = show;\n      this.toggleTab(btn.closest(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.domselectors.component.tabs.tab), show);\n    })\n    if (dismiss) dismiss.addEventListener('click', (e) => {\n      const icon = item.querySelector('.tabs-display');\n      btns.forEach((btn, index) => toggle_tab(index, btn, (item.classList.contains(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.css.component.tabs.name))));\n      item.classList.toggle(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.css.component.tabs.name);\n      icon.classList.toggle('expand');\n      icon.classList.toggle('shrink');\n    });\n  }\n}//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvbW9kdWxlcy9qcy10YWJzLmpzLmpzIiwibWFwcGluZ3MiOiI7Ozs7O0FBR3NDO0FBQ3RDO0FBQ087O0FBRVAsZ0NBQWdDO0FBQ2hDO0FBQ0EsdUNBQXVDLDhGQUFzQztBQUM3RTtBQUNBOztBQUVBOztBQUVBO0FBQ0E7QUFDQTtBQUNBLHlHQUF5Ryx1RkFBK0I7QUFDeEk7QUFDQTtBQUNBO0FBQ0E7QUFDQSwrQkFBK0Isa0VBQVU7QUFDekM7QUFDQSxVQUFVO0FBQ1Y7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EsNkZBQTZGLGtFQUFVLHVCQUF1Qix1RkFBK0IsU0FBUyxrRUFBVTtBQUNoTDtBQUNBLHVDQUF1QyxrRUFBVTtBQUNqRDtBQUNBO0FBQ0EsK0JBQStCLGtFQUFVO0FBQ3pDO0FBQ0EsU0FBUztBQUNULE9BQU87QUFDUDtBQUNBO0FBQ0E7QUFDQTtBQUNBOztBQUVBO0FBQ0E7QUFDQSwyQ0FBMkMsOEZBQXNDO0FBQ2pGO0FBQ0E7QUFDQSxxREFBcUQsZ0VBQVE7QUFDN0QsMkVBQTJFLGdFQUFRO0FBQ25GO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSxZQUFZO0FBQ1osU0FBUztBQUNUO0FBQ0EsS0FBSzs7QUFFTDtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSxpQ0FBaUMsdUZBQStCO0FBQ2hFLEtBQUs7QUFDTDtBQUNBO0FBQ0EsbUZBQW1GLCtFQUF1QjtBQUMxRyw0QkFBNEIsK0VBQXVCO0FBQ25EO0FBQ0E7QUFDQSxLQUFLO0FBQ0w7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovLy8uL3NyYy9tb2R1bGVzL2pzLXRhYnMuanM/MWMwNCJdLCJzb3VyY2VzQ29udGVudCI6WyJpbXBvcnQge1xuICBjc3MsXG4gIGRvbXNlbGVjdG9yc1xufSBmcm9tICcuLi9tb2R1bGVzL21vZHVsZXMtY29uZmlnLmpzJztcbmxldCBpbnN0YW5jZSA9IG51bGw7XG5leHBvcnQgY2xhc3MgSnNUYWJzIHtcblxuICBjb25zdHJ1Y3RvcihpdGVtLCBvcHRpb25zID0ge30pIHtcbiAgICBpZiAoIWluc3RhbmNlKSB7XG4gICAgICBsZXQgYnRucyA9IGl0ZW0ucXVlcnlTZWxlY3RvckFsbChkb21zZWxlY3RvcnMuY29tcG9uZW50LnRhYnMudGFiY29udHJvbCk7XG4gICAgICBpZiAoYnRucy5sZW5ndGggPT09IDApIHtcbiAgICAgICAgYnRucyA9IGl0ZW0ucXVlcnlTZWxlY3RvckFsbCgoKGl0ZW0uZGF0YXNldC5zZWxlY3RvcikgPyBpdGVtLmRhdGFzZXQuc2VsZWN0b3IgOiAnbGVnZW5kJykpO1xuXG4gICAgICB9XG5cbiAgICAgIHRoaXMudG9nZ2xlZGlzYWJsZSA9IChpdGVtLmRhdGFzZXQudG9nZ2xlZGlzYWJsZSkgPyB0cnVlIDogZmFsc2U7XG4gICAgICBsZXQgbCA9IDA7XG4gICAgICBidG5zLmZvckVhY2goKGJ0biwgaW5kZXgpID0+IHtcbiAgICAgICAgY29uc3QgdGFyZ2V0ID0gKGJ0bi5kYXRhc2V0LnRhcmdldCkgPyBpdGVtLnF1ZXJ5U2VsZWN0b3IoJyMnICsgYnRuLmRhdGFzZXQudGFyZ2V0KSA6IGJ0bi5jbG9zZXN0KGRvbXNlbGVjdG9ycy5jb21wb25lbnQudGFicy50YWIpO1xuICAgICAgICBpZiAoIXRhcmdldCkgcmV0dXJuO1xuICAgICAgICBjb25zdCBldiA9IChpdGVtLmRhdGFzZXQuZXZlbnQpID8gaXRlbS5kYXRhc2V0LmV2ZW50IDogJ2NsaWNrJztcbiAgICAgICAgYnRuLnN0eWxlLmxlZnQgPSBsICsgJ3B4JztcbiAgICAgICAgaWYgKGluZGV4ID09PSAwKSB7XG4gICAgICAgICAgdGFyZ2V0LmNsYXNzTGlzdC5hZGQoY3NzLmFjdGl2ZSk7XG4gICAgICAgICAgdGhpcy50b2dnbGVUYWIodGFyZ2V0LCB0cnVlKTtcbiAgICAgICAgfSBlbHNlIHRoaXMudG9nZ2xlVGFiKHRhcmdldCwgZmFsc2UpO1xuICAgICAgICBsICs9IHBhcnNlSW50KGJ0bi5vZmZzZXRXaWR0aCkgKyAyMDtcbiAgICAgICAgYnRuLmFkZEV2ZW50TGlzdGVuZXIoZXYsIChlKSA9PiB7XG4gICAgICAgICAgaWYgKGUuY3VycmVudFRhcmdldC5kaXNhYmxlZCA9PT0gdHJ1ZSkge1xuICAgICAgICAgICAgZS5wcmV2ZW50RGVmYXVsdCgpO1xuICAgICAgICAgICAgcmV0dXJuO1xuICAgICAgICAgIH1cbiAgICAgICAgICBjb25zdCBvbGRhY3RpdmUgPSBpdGVtLmRhdGFzZXQuc2VsZWN0b3IgPyB0YXJnZXQucGFyZW50RWxlbWVudC5xdWVyeVNlbGVjdG9yKCcuJyArIGNzcy5hY3RpdmUpIDogaXRlbS5xdWVyeVNlbGVjdG9yKGRvbXNlbGVjdG9ycy5jb21wb25lbnQudGFicy50YWIgKyAnLicgKyBjc3MuYWN0aXZlKTtcbiAgICAgICAgICBpZiAob2xkYWN0aXZlICE9PSBudWxsKSB7XG4gICAgICAgICAgICBvbGRhY3RpdmUuY2xhc3NMaXN0LnJlbW92ZShjc3MuYWN0aXZlKTtcbiAgICAgICAgICAgIHRoaXMudG9nZ2xlVGFiKG9sZGFjdGl2ZSwgZmFsc2UpO1xuICAgICAgICAgIH1cbiAgICAgICAgICB0YXJnZXQuY2xhc3NMaXN0LmFkZChjc3MuYWN0aXZlKTtcbiAgICAgICAgICB0aGlzLnRvZ2dsZVRhYih0YXJnZXQsIHRydWUpO1xuICAgICAgICB9KTtcbiAgICAgIH0pXG4gICAgICBpZiAoIWl0ZW0uZGF0YXNldC50b2dnbGUpIHRoaXMudG9nZ2xlRGlzcGxheUxpc3RlbmVyKGl0ZW0sIGJ0bnMpO1xuICAgICAgaW5zdGFuY2UgPSB0aGlzO1xuICAgIH1cbiAgICByZXR1cm4gaW5zdGFuY2U7XG4gIH1cblxuICB0b2dnbGVUYWIodGFiLCBzaG93KSB7XG4gICAgbGV0IHdoYXQgPSAodGhpcy50b2dnbGV3aGF0KSA/IGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3IodGhpcy50b2dnbGV3aGF0KSA6IG51bGw7XG4gICAgbGV0IHRhYmNvbnRlbnRzID0gdGFiLnF1ZXJ5U2VsZWN0b3JBbGwoZG9tc2VsZWN0b3JzLmNvbXBvbmVudC50YWJzLnRhYmNvbnRlbnQpO1xuICAgIGlmICh0YWJjb250ZW50cy5sZW5ndGggPT09IDApIHRhYmNvbnRlbnRzID0gW3RhYl07XG4gICAgdGFiY29udGVudHMuZm9yRWFjaCh0YWJjb250ZW50ID0+IHtcbiAgICAgIGlmIChzaG93ID09PSB0cnVlKSB0YWJjb250ZW50LmNsYXNzTGlzdC5yZW1vdmUoY3NzLmhpZGUpO1xuICAgICAgZWxzZSBpZiAoIXRhYi5jbGFzc0xpc3QuY29udGFpbnMoJ2FjdGl2ZScpKSB0YWJjb250ZW50LmNsYXNzTGlzdC5hZGQoY3NzLmhpZGUpO1xuICAgICAgaWYgKHRoaXMudG9nZ2xlZGlzYWJsZSA9PT0gdHJ1ZSkge1xuICAgICAgICB0YWJjb250ZW50LnF1ZXJ5U2VsZWN0b3JBbGwoJ2lucHV0LCBzZWxlY3QsIGJ1dHRvbiwgdGV4dGFyZWEnKS5mb3JFYWNoKGVsID0+IHtcbiAgICAgICAgICBpZiAoc2hvdykge1xuICAgICAgICAgICAgZWwucmVtb3ZlQXR0cmlidXRlKCdkaXNhYmxlZCcpO1xuICAgICAgICAgICAgaWYgKHdoYXQpIHdoYXQudmFsdWUgPSBlbC5kYXRhc2V0LndoYXQ7XG4gICAgICAgICAgfSBlbHNlIGVsLmRpc2FibGVkID0gdHJ1ZTtcbiAgICAgICAgfSk7XG4gICAgICB9XG4gICAgfSk7XG5cbiAgfVxuICB0b2dnbGVEaXNwbGF5TGlzdGVuZXIoaXRlbSwgYnRucykge1xuICAgIC8vIGZsYXQvIHRhYnMgZGlzcGxheVxuICAgIGNvbnN0IGRpc21pc3MgPSBpdGVtLnF1ZXJ5U2VsZWN0b3IoJ1tkYXRhLWRpc21pc3M9XCJ0YWJzXCJdJyk7XG4gICAgY29uc3QgdG9nZ2xlX3RhYiA9ICgoaW5kZXgsIGJ0biwgc2hvdykgPT4ge1xuICAgICAgYnRuLmRpc2FibGVkID0gc2hvdztcbiAgICAgIHRoaXMudG9nZ2xlVGFiKGJ0bi5jbG9zZXN0KGRvbXNlbGVjdG9ycy5jb21wb25lbnQudGFicy50YWIpLCBzaG93KTtcbiAgICB9KVxuICAgIGlmIChkaXNtaXNzKSBkaXNtaXNzLmFkZEV2ZW50TGlzdGVuZXIoJ2NsaWNrJywgKGUpID0+IHtcbiAgICAgIGNvbnN0IGljb24gPSBpdGVtLnF1ZXJ5U2VsZWN0b3IoJy50YWJzLWRpc3BsYXknKTtcbiAgICAgIGJ0bnMuZm9yRWFjaCgoYnRuLCBpbmRleCkgPT4gdG9nZ2xlX3RhYihpbmRleCwgYnRuLCAoaXRlbS5jbGFzc0xpc3QuY29udGFpbnMoY3NzLmNvbXBvbmVudC50YWJzLm5hbWUpKSkpO1xuICAgICAgaXRlbS5jbGFzc0xpc3QudG9nZ2xlKGNzcy5jb21wb25lbnQudGFicy5uYW1lKTtcbiAgICAgIGljb24uY2xhc3NMaXN0LnRvZ2dsZSgnZXhwYW5kJyk7XG4gICAgICBpY29uLmNsYXNzTGlzdC50b2dnbGUoJ3NocmluaycpO1xuICAgIH0pO1xuICB9XG59Il0sIm5hbWVzIjpbXSwic291cmNlUm9vdCI6IiJ9\n//# sourceURL=webpack-internal:///./src/modules/js-tabs.js\n")}}]);