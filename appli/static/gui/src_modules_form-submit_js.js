/*! For license information please see src_modules_form-submit_js.js.LICENSE.txt */
"use strict";(self.webpackChunk=self.webpackChunk||[]).push([["src_modules_form-submit_js"],{"./src/modules/form-submit.js":(__unused_webpack_module,__webpack_exports__,__webpack_require__)=>{eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"FormSubmit\": () => (/* binding */ FormSubmit)\n/* harmony export */ });\n/* harmony import */ var dompurify__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! dompurify */ \"./node_modules/dompurify/dist/purify.js\");\n/* harmony import */ var dompurify__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(dompurify__WEBPACK_IMPORTED_MODULE_0__);\n\n\nlet instance = null;\nconst formcss = {\n  invalid: 'invalid',\n  inputvalidate: 'input-validate'\n}\nclass FormSubmit {\n  handlers = [];\n  form = null;\n  listener = null;\n  constructor(form, options = {}) {\n    if (!instance) {\n      if (!form) return;\n      const defaultOptions = {};\n      this.options = Object.assign(defaultOptions, options);\n      this.form = form instanceof HTMLElement ? form : document.querySelector(form);\n      this.validateFields(true);\n      this.init();\n      instance = this;\n    }\n    return instance;\n  }\n  init() {\n    // init the form ( options like beforeunload etc...)\n    this.form.addEventListener('submit', async (e) => {\n      console.log('----------------formsubmit', e)\n      const res = await this.submitForm();\n      if (!res) e.preventDefault();\n      return res;\n    });\n    // check if there is a password confirm input\n    this.form.querySelectorAll('input[data-match]').forEach(input => {\n      //\n      const match = input.dataset.match;\n      if (!match) return;\n      const target = document.getElementById(match);\n      if (!target) return;\n      const invalid = (input.dataset.matchinvalid) ? input.dataset.matchinvalid : \"no match\";\n      const label = input.closest('label');\n      const check_match = (item, itemtarget) => {\n        if (item.value !== itemtarget.value) {\n          item.setCustomValidity(invalid);\n          itemtarget.setCustomValidity(invalid);\n          if (input != item) {\n            if (label) label.classList.add(formcss.invalid);\n            input.classList.add(formcss.inputvalidate);\n          }\n        } else {\n          item.setCustomValidity(\"\");\n          itemtarget.setCustomValidity(\"\");\n          item.dataset.invalid = '';\n          itemtarget.dataset.invalid = '';\n          if (input != item) {\n            if (label) label.classList.remove(formcss.invalid);\n            input.classList.remove(formcss.inputvalidate);\n\n          }\n        }\n        item.reportValidity();\n        itemtarget.reportValidity();\n        item.focus();\n      };\n      [input, target].forEach(item => {\n        item.addEventListener('keyup', (e) => {\n          const itemtarget = (item === input) ? target : input;\n          check_match(item, itemtarget);\n        });\n      });\n\n    });\n  }\n\n  validateField(field) {\n\n    const get_message = (field) => {\n      let message = 'invalid';\n      if (field.required) message = (field.dataset.required) ? field.dataset.required : ((this.form.dataset.required) ? this.form.dataset.required : 'invalid');\n      if (message === 'invalid') message = (field.dataset.invalid) ? field.dataset.invalid : ((this.form.dataset.invalid) ? this.form.dataset.invalid : 'invalid input');\n      return message;\n    }\n\n\n    field.value = dompurify__WEBPACK_IMPORTED_MODULE_0___default().sanitize(field.value);\n    const rep = field.checkValidity();\n    const label = field.closest('.form-box') ? field.closest('.form-box').querySelector('label') : null;\n\n    if (rep && label) label.classList.remove(formcss.invalid);\n\n    else if (!rep) {\n      if (label) {\n        label.dataset.invalid = get_message(field);\n        label.classList.add(formcss.invalid);\n      }\n\n    }\n\n    if (field.classList.contains('tomselected') && field.nextElementSibling) {\n      field.nextElementSibling.classList.add(formcss.inputvalidate);\n    } else field.classList.add(formcss.inputvalidate);\n\n    return rep;\n  }\n\n  validateFields(init = false) {\n\n    // todo: complete validation foreach field type\n    let resp = true;\n\n    this.form.querySelectorAll('input,textarea, select').forEach(field => {\n      if (init === true) {\n        if (!field.dataset.listen) {\n          ['change', 'blur'].forEach(evt => {\n            field.addEventListener(evt, (e) => {\n              this.validateField(e.currentTarget);\n            });\n          });\n          field.dataset.listen = true;\n        }\n      } else {\n        const rep = this.validateField(field);\n        resp = (resp && rep);\n      }\n\n\n    });\n    return resp;\n  }\n  addHandler(handler) {\n    this.handlers.push(handler);\n  }\n  fieldEnable() {\n    this.form.querySelectorAll('input[data-sub=\"enable\"]').forEach(input => {\n      input.removeAttribute('disabled');\n    });\n  }\n  async submitHandler() {\n    if (!this.validateFields()) return false;\n    if (this.handlers.length === 0) return true;\n    let resp = true;\n    // series\n    /*  for (const handler of this.handlers) {\n          const rep = await handler()\n          resp = (resp && rep)\n      }*/\n    // concurrent\n    await Promise.all(this.handlers.map(async handler => {\n      const rep = await handler();\n      resp = (resp && rep);\n    }));\n    if (resp === true) this.handlers = [];\n    console.log('resp', resp)\n    return resp;\n  }\n  async submitForm() {\n    if (this.validateFields(false)) {\n      const yessubmit = await this.submitHandler();\n      if (yessubmit) {\n        this.fieldEnable();\n        this.form.submit();\n      } else return false;\n    } else return false;\n  }\n}//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvbW9kdWxlcy9mb3JtLXN1Ym1pdC5qcy5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7QUFBa0M7QUFDQTtBQUNsQztBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ087QUFDUDtBQUNBO0FBQ0E7QUFDQSxnQ0FBZ0M7QUFDaEM7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EsS0FBSztBQUNMO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSxVQUFVO0FBQ1Y7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7O0FBRUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSxTQUFTO0FBQ1QsT0FBTzs7QUFFUCxLQUFLO0FBQ0w7O0FBRUE7O0FBRUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOzs7QUFHQSxrQkFBa0IseURBQWtCO0FBQ3BDO0FBQ0E7O0FBRUE7O0FBRUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7QUFFQTs7QUFFQTtBQUNBO0FBQ0EsTUFBTTs7QUFFTjtBQUNBOztBQUVBOztBQUVBO0FBQ0E7O0FBRUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EsYUFBYTtBQUNiLFdBQVc7QUFDWDtBQUNBO0FBQ0EsUUFBUTtBQUNSO0FBQ0E7QUFDQTs7O0FBR0EsS0FBSztBQUNMO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSxLQUFLO0FBQ0w7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EsT0FBTztBQUNQO0FBQ0E7QUFDQTtBQUNBO0FBQ0EsS0FBSztBQUNMO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EsUUFBUTtBQUNSLE1BQU07QUFDTjtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vLy4vc3JjL21vZHVsZXMvZm9ybS1zdWJtaXQuanM/YzZiNyJdLCJzb3VyY2VzQ29udGVudCI6WyJpbXBvcnQgdmFsaWRhdG9yIGZyb20gJ3ZhbGlkYXRvcic7XG5pbXBvcnQgRE9NUHVyaWZ5IGZyb20gJ2RvbXB1cmlmeSc7XG5sZXQgaW5zdGFuY2UgPSBudWxsO1xuY29uc3QgZm9ybWNzcyA9IHtcbiAgaW52YWxpZDogJ2ludmFsaWQnLFxuICBpbnB1dHZhbGlkYXRlOiAnaW5wdXQtdmFsaWRhdGUnXG59XG5leHBvcnQgY2xhc3MgRm9ybVN1Ym1pdCB7XG4gIGhhbmRsZXJzID0gW107XG4gIGZvcm0gPSBudWxsO1xuICBsaXN0ZW5lciA9IG51bGw7XG4gIGNvbnN0cnVjdG9yKGZvcm0sIG9wdGlvbnMgPSB7fSkge1xuICAgIGlmICghaW5zdGFuY2UpIHtcbiAgICAgIGlmICghZm9ybSkgcmV0dXJuO1xuICAgICAgY29uc3QgZGVmYXVsdE9wdGlvbnMgPSB7fTtcbiAgICAgIHRoaXMub3B0aW9ucyA9IE9iamVjdC5hc3NpZ24oZGVmYXVsdE9wdGlvbnMsIG9wdGlvbnMpO1xuICAgICAgdGhpcy5mb3JtID0gZm9ybSBpbnN0YW5jZW9mIEhUTUxFbGVtZW50ID8gZm9ybSA6IGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3IoZm9ybSk7XG4gICAgICB0aGlzLnZhbGlkYXRlRmllbGRzKHRydWUpO1xuICAgICAgdGhpcy5pbml0KCk7XG4gICAgICBpbnN0YW5jZSA9IHRoaXM7XG4gICAgfVxuICAgIHJldHVybiBpbnN0YW5jZTtcbiAgfVxuICBpbml0KCkge1xuICAgIC8vIGluaXQgdGhlIGZvcm0gKCBvcHRpb25zIGxpa2UgYmVmb3JldW5sb2FkIGV0Yy4uLilcbiAgICB0aGlzLmZvcm0uYWRkRXZlbnRMaXN0ZW5lcignc3VibWl0JywgYXN5bmMgKGUpID0+IHtcbiAgICAgIGNvbnNvbGUubG9nKCctLS0tLS0tLS0tLS0tLS0tZm9ybXN1Ym1pdCcsIGUpXG4gICAgICBjb25zdCByZXMgPSBhd2FpdCB0aGlzLnN1Ym1pdEZvcm0oKTtcbiAgICAgIGlmICghcmVzKSBlLnByZXZlbnREZWZhdWx0KCk7XG4gICAgICByZXR1cm4gcmVzO1xuICAgIH0pO1xuICAgIC8vIGNoZWNrIGlmIHRoZXJlIGlzIGEgcGFzc3dvcmQgY29uZmlybSBpbnB1dFxuICAgIHRoaXMuZm9ybS5xdWVyeVNlbGVjdG9yQWxsKCdpbnB1dFtkYXRhLW1hdGNoXScpLmZvckVhY2goaW5wdXQgPT4ge1xuICAgICAgLy9cbiAgICAgIGNvbnN0IG1hdGNoID0gaW5wdXQuZGF0YXNldC5tYXRjaDtcbiAgICAgIGlmICghbWF0Y2gpIHJldHVybjtcbiAgICAgIGNvbnN0IHRhcmdldCA9IGRvY3VtZW50LmdldEVsZW1lbnRCeUlkKG1hdGNoKTtcbiAgICAgIGlmICghdGFyZ2V0KSByZXR1cm47XG4gICAgICBjb25zdCBpbnZhbGlkID0gKGlucHV0LmRhdGFzZXQubWF0Y2hpbnZhbGlkKSA/IGlucHV0LmRhdGFzZXQubWF0Y2hpbnZhbGlkIDogXCJubyBtYXRjaFwiO1xuICAgICAgY29uc3QgbGFiZWwgPSBpbnB1dC5jbG9zZXN0KCdsYWJlbCcpO1xuICAgICAgY29uc3QgY2hlY2tfbWF0Y2ggPSAoaXRlbSwgaXRlbXRhcmdldCkgPT4ge1xuICAgICAgICBpZiAoaXRlbS52YWx1ZSAhPT0gaXRlbXRhcmdldC52YWx1ZSkge1xuICAgICAgICAgIGl0ZW0uc2V0Q3VzdG9tVmFsaWRpdHkoaW52YWxpZCk7XG4gICAgICAgICAgaXRlbXRhcmdldC5zZXRDdXN0b21WYWxpZGl0eShpbnZhbGlkKTtcbiAgICAgICAgICBpZiAoaW5wdXQgIT0gaXRlbSkge1xuICAgICAgICAgICAgaWYgKGxhYmVsKSBsYWJlbC5jbGFzc0xpc3QuYWRkKGZvcm1jc3MuaW52YWxpZCk7XG4gICAgICAgICAgICBpbnB1dC5jbGFzc0xpc3QuYWRkKGZvcm1jc3MuaW5wdXR2YWxpZGF0ZSk7XG4gICAgICAgICAgfVxuICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgIGl0ZW0uc2V0Q3VzdG9tVmFsaWRpdHkoXCJcIik7XG4gICAgICAgICAgaXRlbXRhcmdldC5zZXRDdXN0b21WYWxpZGl0eShcIlwiKTtcbiAgICAgICAgICBpdGVtLmRhdGFzZXQuaW52YWxpZCA9ICcnO1xuICAgICAgICAgIGl0ZW10YXJnZXQuZGF0YXNldC5pbnZhbGlkID0gJyc7XG4gICAgICAgICAgaWYgKGlucHV0ICE9IGl0ZW0pIHtcbiAgICAgICAgICAgIGlmIChsYWJlbCkgbGFiZWwuY2xhc3NMaXN0LnJlbW92ZShmb3JtY3NzLmludmFsaWQpO1xuICAgICAgICAgICAgaW5wdXQuY2xhc3NMaXN0LnJlbW92ZShmb3JtY3NzLmlucHV0dmFsaWRhdGUpO1xuXG4gICAgICAgICAgfVxuICAgICAgICB9XG4gICAgICAgIGl0ZW0ucmVwb3J0VmFsaWRpdHkoKTtcbiAgICAgICAgaXRlbXRhcmdldC5yZXBvcnRWYWxpZGl0eSgpO1xuICAgICAgICBpdGVtLmZvY3VzKCk7XG4gICAgICB9O1xuICAgICAgW2lucHV0LCB0YXJnZXRdLmZvckVhY2goaXRlbSA9PiB7XG4gICAgICAgIGl0ZW0uYWRkRXZlbnRMaXN0ZW5lcigna2V5dXAnLCAoZSkgPT4ge1xuICAgICAgICAgIGNvbnN0IGl0ZW10YXJnZXQgPSAoaXRlbSA9PT0gaW5wdXQpID8gdGFyZ2V0IDogaW5wdXQ7XG4gICAgICAgICAgY2hlY2tfbWF0Y2goaXRlbSwgaXRlbXRhcmdldCk7XG4gICAgICAgIH0pO1xuICAgICAgfSk7XG5cbiAgICB9KTtcbiAgfVxuXG4gIHZhbGlkYXRlRmllbGQoZmllbGQpIHtcblxuICAgIGNvbnN0IGdldF9tZXNzYWdlID0gKGZpZWxkKSA9PiB7XG4gICAgICBsZXQgbWVzc2FnZSA9ICdpbnZhbGlkJztcbiAgICAgIGlmIChmaWVsZC5yZXF1aXJlZCkgbWVzc2FnZSA9IChmaWVsZC5kYXRhc2V0LnJlcXVpcmVkKSA/IGZpZWxkLmRhdGFzZXQucmVxdWlyZWQgOiAoKHRoaXMuZm9ybS5kYXRhc2V0LnJlcXVpcmVkKSA/IHRoaXMuZm9ybS5kYXRhc2V0LnJlcXVpcmVkIDogJ2ludmFsaWQnKTtcbiAgICAgIGlmIChtZXNzYWdlID09PSAnaW52YWxpZCcpIG1lc3NhZ2UgPSAoZmllbGQuZGF0YXNldC5pbnZhbGlkKSA/IGZpZWxkLmRhdGFzZXQuaW52YWxpZCA6ICgodGhpcy5mb3JtLmRhdGFzZXQuaW52YWxpZCkgPyB0aGlzLmZvcm0uZGF0YXNldC5pbnZhbGlkIDogJ2ludmFsaWQgaW5wdXQnKTtcbiAgICAgIHJldHVybiBtZXNzYWdlO1xuICAgIH1cblxuXG4gICAgZmllbGQudmFsdWUgPSBET01QdXJpZnkuc2FuaXRpemUoZmllbGQudmFsdWUpO1xuICAgIGNvbnN0IHJlcCA9IGZpZWxkLmNoZWNrVmFsaWRpdHkoKTtcbiAgICBjb25zdCBsYWJlbCA9IGZpZWxkLmNsb3Nlc3QoJy5mb3JtLWJveCcpID8gZmllbGQuY2xvc2VzdCgnLmZvcm0tYm94JykucXVlcnlTZWxlY3RvcignbGFiZWwnKSA6IG51bGw7XG5cbiAgICBpZiAocmVwICYmIGxhYmVsKSBsYWJlbC5jbGFzc0xpc3QucmVtb3ZlKGZvcm1jc3MuaW52YWxpZCk7XG5cbiAgICBlbHNlIGlmICghcmVwKSB7XG4gICAgICBpZiAobGFiZWwpIHtcbiAgICAgICAgbGFiZWwuZGF0YXNldC5pbnZhbGlkID0gZ2V0X21lc3NhZ2UoZmllbGQpO1xuICAgICAgICBsYWJlbC5jbGFzc0xpc3QuYWRkKGZvcm1jc3MuaW52YWxpZCk7XG4gICAgICB9XG5cbiAgICB9XG5cbiAgICBpZiAoZmllbGQuY2xhc3NMaXN0LmNvbnRhaW5zKCd0b21zZWxlY3RlZCcpICYmIGZpZWxkLm5leHRFbGVtZW50U2libGluZykge1xuICAgICAgZmllbGQubmV4dEVsZW1lbnRTaWJsaW5nLmNsYXNzTGlzdC5hZGQoZm9ybWNzcy5pbnB1dHZhbGlkYXRlKTtcbiAgICB9IGVsc2UgZmllbGQuY2xhc3NMaXN0LmFkZChmb3JtY3NzLmlucHV0dmFsaWRhdGUpO1xuXG4gICAgcmV0dXJuIHJlcDtcbiAgfVxuXG4gIHZhbGlkYXRlRmllbGRzKGluaXQgPSBmYWxzZSkge1xuXG4gICAgLy8gdG9kbzogY29tcGxldGUgdmFsaWRhdGlvbiBmb3JlYWNoIGZpZWxkIHR5cGVcbiAgICBsZXQgcmVzcCA9IHRydWU7XG5cbiAgICB0aGlzLmZvcm0ucXVlcnlTZWxlY3RvckFsbCgnaW5wdXQsdGV4dGFyZWEsIHNlbGVjdCcpLmZvckVhY2goZmllbGQgPT4ge1xuICAgICAgaWYgKGluaXQgPT09IHRydWUpIHtcbiAgICAgICAgaWYgKCFmaWVsZC5kYXRhc2V0Lmxpc3Rlbikge1xuICAgICAgICAgIFsnY2hhbmdlJywgJ2JsdXInXS5mb3JFYWNoKGV2dCA9PiB7XG4gICAgICAgICAgICBmaWVsZC5hZGRFdmVudExpc3RlbmVyKGV2dCwgKGUpID0+IHtcbiAgICAgICAgICAgICAgdGhpcy52YWxpZGF0ZUZpZWxkKGUuY3VycmVudFRhcmdldCk7XG4gICAgICAgICAgICB9KTtcbiAgICAgICAgICB9KTtcbiAgICAgICAgICBmaWVsZC5kYXRhc2V0Lmxpc3RlbiA9IHRydWU7XG4gICAgICAgIH1cbiAgICAgIH0gZWxzZSB7XG4gICAgICAgIGNvbnN0IHJlcCA9IHRoaXMudmFsaWRhdGVGaWVsZChmaWVsZCk7XG4gICAgICAgIHJlc3AgPSAocmVzcCAmJiByZXApO1xuICAgICAgfVxuXG5cbiAgICB9KTtcbiAgICByZXR1cm4gcmVzcDtcbiAgfVxuICBhZGRIYW5kbGVyKGhhbmRsZXIpIHtcbiAgICB0aGlzLmhhbmRsZXJzLnB1c2goaGFuZGxlcik7XG4gIH1cbiAgZmllbGRFbmFibGUoKSB7XG4gICAgdGhpcy5mb3JtLnF1ZXJ5U2VsZWN0b3JBbGwoJ2lucHV0W2RhdGEtc3ViPVwiZW5hYmxlXCJdJykuZm9yRWFjaChpbnB1dCA9PiB7XG4gICAgICBpbnB1dC5yZW1vdmVBdHRyaWJ1dGUoJ2Rpc2FibGVkJyk7XG4gICAgfSk7XG4gIH1cbiAgYXN5bmMgc3VibWl0SGFuZGxlcigpIHtcbiAgICBpZiAoIXRoaXMudmFsaWRhdGVGaWVsZHMoKSkgcmV0dXJuIGZhbHNlO1xuICAgIGlmICh0aGlzLmhhbmRsZXJzLmxlbmd0aCA9PT0gMCkgcmV0dXJuIHRydWU7XG4gICAgbGV0IHJlc3AgPSB0cnVlO1xuICAgIC8vIHNlcmllc1xuICAgIC8qICBmb3IgKGNvbnN0IGhhbmRsZXIgb2YgdGhpcy5oYW5kbGVycykge1xuICAgICAgICAgIGNvbnN0IHJlcCA9IGF3YWl0IGhhbmRsZXIoKVxuICAgICAgICAgIHJlc3AgPSAocmVzcCAmJiByZXApXG4gICAgICB9Ki9cbiAgICAvLyBjb25jdXJyZW50XG4gICAgYXdhaXQgUHJvbWlzZS5hbGwodGhpcy5oYW5kbGVycy5tYXAoYXN5bmMgaGFuZGxlciA9PiB7XG4gICAgICBjb25zdCByZXAgPSBhd2FpdCBoYW5kbGVyKCk7XG4gICAgICByZXNwID0gKHJlc3AgJiYgcmVwKTtcbiAgICB9KSk7XG4gICAgaWYgKHJlc3AgPT09IHRydWUpIHRoaXMuaGFuZGxlcnMgPSBbXTtcbiAgICBjb25zb2xlLmxvZygncmVzcCcsIHJlc3ApXG4gICAgcmV0dXJuIHJlc3A7XG4gIH1cbiAgYXN5bmMgc3VibWl0Rm9ybSgpIHtcbiAgICBpZiAodGhpcy52YWxpZGF0ZUZpZWxkcyhmYWxzZSkpIHtcbiAgICAgIGNvbnN0IHllc3N1Ym1pdCA9IGF3YWl0IHRoaXMuc3VibWl0SGFuZGxlcigpO1xuICAgICAgaWYgKHllc3N1Ym1pdCkge1xuICAgICAgICB0aGlzLmZpZWxkRW5hYmxlKCk7XG4gICAgICAgIHRoaXMuZm9ybS5zdWJtaXQoKTtcbiAgICAgIH0gZWxzZSByZXR1cm4gZmFsc2U7XG4gICAgfSBlbHNlIHJldHVybiBmYWxzZTtcbiAgfVxufSJdLCJuYW1lcyI6W10sInNvdXJjZVJvb3QiOiIifQ==\n//# sourceURL=webpack-internal:///./src/modules/form-submit.js\n")}}]);