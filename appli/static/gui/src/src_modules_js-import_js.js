/*! For license information please see src_modules_js-import_js.js.LICENSE.txt */
"use strict";(self.webpackChunk=self.webpackChunk||[]).push([["src_modules_js-import_js"],{"./src/modules/form-submit.js":(__unused_webpack_module,__webpack_exports__,__webpack_require__)=>{eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   FormSubmit: () => (/* binding */ FormSubmit)\n/* harmony export */ });\n/* harmony import */ var dompurify__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! dompurify */ \"./node_modules/dompurify/dist/purify.js\");\n/* harmony import */ var dompurify__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(dompurify__WEBPACK_IMPORTED_MODULE_0__);\n/* harmony import */ var _modules_utils_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../modules/utils.js */ \"./src/modules/utils.js\");\n\n\nconst formcss = {\n  invalid: 'input-invalid',\n  inputvalidate: 'input-valid',\n}\nconst domselectors = {\n  captcha: '.js-captcha'\n}\n;\n\nclass FormSubmit {\n  handlers = [];\n  form = null;\n  listener = null;\n  constructor(form, options = {}) {\n    if (!form.formsubmit) {\n      if (!form) return;\n      this.form = form instanceof HTMLElement ? form : document.querySelector(form);\n      const defaultOptions = {\n        fetch: null,\n      };\n      options = Object.assign(options, this.form.dataset);\n      this.options = Object.assign(defaultOptions, options);\n      if (!this.form) return;\n      this.validateFields(true);\n      this.init();\n      form.formsubmit = this;\n    }\n    return form.formsubmit;\n  }\n  init() {\n    // init the form ( options like beforeunload etc...)\n\n    this.form.addEventListener('submit', async (e) => {\n      e.preventDefault();\n      const res = await this.submitForm();\n      return res;\n    });\n    this.specialFields();\n  }\n  specialFields() {\n    // check if there is a password confirm input\n    // add show text for password fields\n\n    this.form.querySelectorAll('input[data-match]').forEach(input => {\n      //\n      const match = input.dataset.match;\n      if (!match) return;\n      const target = document.getElementById(match);\n      if (!target) return;\n      const invalid = (input.dataset.matchinvalid) ? input.dataset.matchinvalid : \"no match\";\n      const check_match = (item, itemtarget) => {\n        const label = (input.previousElementSibling && input.previousElementSibling.tagName.toLowerCase() == 'label') ? input.previousElementSibling : null;\n        const labeltarget = (target.previousElementSibling && target.previousElementSibling.tagName.toLowerCase() == 'label') ? target.previousElementSibling : null;\n        const {\n          patternMismatch = false\n        } = item.validity;\n        const customvalidity = (patternMismatch) ?\n          this.get_message(item, 'invalid') : '';\n        if (item.checkValidity() === true) {\n          item.dataset.invalid = '';\n          item.setCustomValidity(\"\");\n          if (item == input && label !== null) label.classList.remove(formcss.invalid);\n          else if (labeltarget !== null) labeltarget.classList.remove(formcss.invalid);\n          item.classList.remove(formcss.inputvalidate);\n          if (item.value !== itemtarget.value) {\n            input.setCustomValidity(invalid);\n            input.dataset.invalid = invalid;\n            if (label) label.classList.add(formcss.invalid);\n            input.classList.add(formcss.inputvalidate);\n          } else {\n            input.setCustomValidity(\"\");\n            input.dataset.invalid = \"\";\n            if (label) label.classList.remove(formcss.invalid);\n            input.classList.remove(formcss.inputvalidate);\n          }\n        } else {\n          item.setCustomValidity(customvalidity);\n          item.dataset.invalid = customvalidity;\n          if (label) label.classList.add(formcss.invalid);\n          item.classList.add(formcss.inputvalidate);\n        }\n        item.focus();\n      };\n      [input, target].forEach(item => {\n        item.addEventListener('keyup', (e) => {\n          const itemtarget = (item === input) ? target : input;\n          check_match(item, itemtarget);\n        });\n      });\n\n    });\n  }\n  get_message(field, type = 'invalid') {\n    if (field.checkValidity() == false) {\n      const {\n        valueMissing = true\n      } = field.validity;\n      if (valueMissing) return (field.dataset.required) ? field.dataset.required : ((this.form.dataset.required) ? this.form.dataset.required : 'required');\n      else return (field.dataset[type]) ? field.dataset[type] : 'input invalid';\n    } else return '';\n  }\n\n  validateField(field, init = false) {\n\n\n\n    if (['textarea', 'input'].indexOf(field.tagName.toLowerCase()) >= 0) {\n\n    }\n\n    if (['select', 'input[type=\"checkbox\"]'].indexOf(field.tagName.toLowerCase()) >= 0) {\n      field.querySelectorAll('option:checked').forEach(option => {\n        option.value = (0,_modules_utils_js__WEBPACK_IMPORTED_MODULE_1__.decode_HTMLEntities)(dompurify__WEBPACK_IMPORTED_MODULE_0___default().sanitize(option.value));\n      });\n\n    } else field.value = (0,_modules_utils_js__WEBPACK_IMPORTED_MODULE_1__.decode_HTMLEntities)(dompurify__WEBPACK_IMPORTED_MODULE_0___default().sanitize(field.value));\n\n    const rep = field.checkValidity();\n\n    /*  if (field.classList.contains('select-one')) {\n\n    }*/\n    const label = field.closest('.form-box') ? field.closest('.form-box').querySelector('label') : null;\n\n    if (rep && label) {\n      label.classList.remove(formcss.invalid);\n    } else if (!rep) {\n      if (label) {\n        label.dataset.invalid = this.get_message(field);\n        label.classList.add(formcss.invalid);\n        window.scrollTo({\n          top: parseInt(label.offsetTop),\n          left: parseInt(label.offsetLeft),\n          behavior: 'smooth'\n        });\n      }\n    }\n    return rep;\n  }\n\n  validateFields(init = false) {\n    //todo: complete validation foreach field type\n    let resp = true;\n    // .required input for tom-select component\n\n    [...this.form.elements].forEach(field => {\n      if (field.name) {\n\n        if (init === true) {\n\n          if (!field.dataset.listen) {\n            if (field.hasAttribute('required') && field.required) {\n              const label = field.closest('.form-box') ? field.closest('.form-box').querySelector('label') : field.parentElement.querySelector('label');\n              if (label) label.classList.add('required');\n            }\n\n            ['change', 'blur'].forEach(evt => {\n              field.addEventListener(evt, (e) => {\n                this.validateField(e.currentTarget, init);\n              });\n            });\n            field.dataset.listen = true;\n          }\n        } else resp = (resp && this.validateField(field, init));\n      }\n    });\n    return resp;\n  }\n\n  addHandler(handler) {\n    this.handlers.push(handler);\n  }\n  fieldEnable(enable = true) {\n    this.form.querySelectorAll('input[data-sub=\"enable\"]').forEach(input => {\n      if (enable === true) {\n        input.removeAttribute(\"disabled\");\n      } else input.disabled = true;\n    });\n  }\n\n  async submitHandler() {\n    if (!this.validateFields()) return false;\n\n    if (this.handlers.length === 0) return true;\n    let resp = true;\n    // series\n    /*  for (const handler of this.handlers) {\n          const rep = await handler()\n          resp = (resp && rep)\n      }*/\n    // concurrent\n    await Promise.all(this.handlers.map(async handler => {\n      const rep = await handler();\n      resp = (resp && rep);\n    }));\n    if (resp === true) this.handlers = [];\n    return resp;\n  }\n  // no redirection when using data-fetch\n  formFetch(format = null) {\n    const formdata = new FormData(this.form);\n    formdata[\"fetch\"] = true;\n    fetch(this.form.action, (0,_modules_utils_js__WEBPACK_IMPORTED_MODULE_1__.fetchSettings)({\n        method: 'POST',\n        body: formdata,\n      }))\n      .then(response => {\n        switch (format) {\n          case \"text\":\n          case \"html\":\n            return response.text();\n            break;\n          default:\n            return response.json();\n        }\n      })\n      .then(response => {\n        this.displayResponse(response);\n      })\n      .catch(err => {\n        this.displayResponse(err, true)\n      }).finally(response => {\n        this.form.disabled = true;\n      });\n    return false;\n  }\n\n  async submitForm() {\n    this.fieldEnable();\n    if (this.validateFields(false)) {\n      const isbot = (this.form.querySelector(domselectors.captcha)) ? (this.form.dataset.isbot ? (this.form.dataset.isbot === true) : true) : false;\n      if (isbot === true) return false;\n      const yessubmit = await this.submitHandler();\n      if (yessubmit) {\n        if (this.options.fetch) this.formFetch(this.options.fetch);\n        else this.form.submit();\n        this.form.disabled = true;\n        return true;\n      } else return false;\n    } else return false;\n  }\n\n  displayResponse(response, error = false) {\n    const el = document.createElement('div');\n    el.insertAdjacentHTML('afterbegin', response);\n    if (error !== false) el.classList.add('is-error');\n    this.form.parentElement.insertBefore(el, this.form);\n    this.form.remove();\n  }\n}//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvbW9kdWxlcy9mb3JtLXN1Ym1pdC5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7O0FBQWtDO0FBQ0E7QUFDbEM7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSxDQUc2Qjs7QUFFdEI7QUFDUDtBQUNBO0FBQ0E7QUFDQSxnQ0FBZ0M7QUFDaEM7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7QUFFQTtBQUNBO0FBQ0E7QUFDQTtBQUNBLEtBQUs7QUFDTDtBQUNBO0FBQ0E7QUFDQTtBQUNBOztBQUVBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBLFVBQVU7QUFDVjtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBLFlBQVk7QUFDWjtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EsVUFBVTtBQUNWO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSxTQUFTO0FBQ1QsT0FBTzs7QUFFUCxLQUFLO0FBQ0w7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBLFFBQVE7QUFDUjtBQUNBO0FBQ0EsTUFBTTtBQUNOOztBQUVBOzs7O0FBSUE7O0FBRUE7O0FBRUE7QUFDQTtBQUNBLHVCQUF1QixzRUFBbUIsQ0FBQyx5REFBa0I7QUFDN0QsT0FBTzs7QUFFUCxNQUFNLG1CQUFtQixzRUFBbUIsQ0FBQyx5REFBa0I7O0FBRS9EOztBQUVBOztBQUVBLEtBQUs7QUFDTDs7QUFFQTtBQUNBO0FBQ0EsTUFBTTtBQUNOO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EsU0FBUztBQUNUO0FBQ0E7QUFDQTtBQUNBOztBQUVBO0FBQ0E7QUFDQTtBQUNBOztBQUVBO0FBQ0E7O0FBRUE7O0FBRUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7QUFFQTtBQUNBO0FBQ0E7QUFDQSxlQUFlO0FBQ2YsYUFBYTtBQUNiO0FBQ0E7QUFDQSxVQUFVO0FBQ1Y7QUFDQSxLQUFLO0FBQ0w7QUFDQTs7QUFFQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBLFFBQVE7QUFDUixLQUFLO0FBQ0w7O0FBRUE7QUFDQTs7QUFFQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSxPQUFPO0FBQ1A7QUFDQTtBQUNBO0FBQ0E7QUFDQSxLQUFLO0FBQ0w7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSw0QkFBNEIsZ0VBQWE7QUFDekM7QUFDQTtBQUNBLE9BQU87QUFDUDtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSxPQUFPO0FBQ1A7QUFDQTtBQUNBLE9BQU87QUFDUDtBQUNBO0FBQ0EsT0FBTztBQUNQO0FBQ0EsT0FBTztBQUNQO0FBQ0E7O0FBRUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBLFFBQVE7QUFDUixNQUFNO0FBQ047O0FBRUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovLy8uL3NyYy9tb2R1bGVzL2Zvcm0tc3VibWl0LmpzP2M2YjciXSwic291cmNlc0NvbnRlbnQiOlsiaW1wb3J0IHZhbGlkYXRvciBmcm9tICd2YWxpZGF0b3InO1xuaW1wb3J0IERPTVB1cmlmeSBmcm9tICdkb21wdXJpZnknO1xuY29uc3QgZm9ybWNzcyA9IHtcbiAgaW52YWxpZDogJ2lucHV0LWludmFsaWQnLFxuICBpbnB1dHZhbGlkYXRlOiAnaW5wdXQtdmFsaWQnLFxufVxuY29uc3QgZG9tc2VsZWN0b3JzID0ge1xuICBjYXB0Y2hhOiAnLmpzLWNhcHRjaGEnXG59XG5pbXBvcnQge1xuICBmZXRjaFNldHRpbmdzLFxuICBkZWNvZGVfSFRNTEVudGl0aWVzXG59IGZyb20gJy4uL21vZHVsZXMvdXRpbHMuanMnO1xuXG5leHBvcnQgY2xhc3MgRm9ybVN1Ym1pdCB7XG4gIGhhbmRsZXJzID0gW107XG4gIGZvcm0gPSBudWxsO1xuICBsaXN0ZW5lciA9IG51bGw7XG4gIGNvbnN0cnVjdG9yKGZvcm0sIG9wdGlvbnMgPSB7fSkge1xuICAgIGlmICghZm9ybS5mb3Jtc3VibWl0KSB7XG4gICAgICBpZiAoIWZvcm0pIHJldHVybjtcbiAgICAgIHRoaXMuZm9ybSA9IGZvcm0gaW5zdGFuY2VvZiBIVE1MRWxlbWVudCA/IGZvcm0gOiBkb2N1bWVudC5xdWVyeVNlbGVjdG9yKGZvcm0pO1xuICAgICAgY29uc3QgZGVmYXVsdE9wdGlvbnMgPSB7XG4gICAgICAgIGZldGNoOiBudWxsLFxuICAgICAgfTtcbiAgICAgIG9wdGlvbnMgPSBPYmplY3QuYXNzaWduKG9wdGlvbnMsIHRoaXMuZm9ybS5kYXRhc2V0KTtcbiAgICAgIHRoaXMub3B0aW9ucyA9IE9iamVjdC5hc3NpZ24oZGVmYXVsdE9wdGlvbnMsIG9wdGlvbnMpO1xuICAgICAgaWYgKCF0aGlzLmZvcm0pIHJldHVybjtcbiAgICAgIHRoaXMudmFsaWRhdGVGaWVsZHModHJ1ZSk7XG4gICAgICB0aGlzLmluaXQoKTtcbiAgICAgIGZvcm0uZm9ybXN1Ym1pdCA9IHRoaXM7XG4gICAgfVxuICAgIHJldHVybiBmb3JtLmZvcm1zdWJtaXQ7XG4gIH1cbiAgaW5pdCgpIHtcbiAgICAvLyBpbml0IHRoZSBmb3JtICggb3B0aW9ucyBsaWtlIGJlZm9yZXVubG9hZCBldGMuLi4pXG5cbiAgICB0aGlzLmZvcm0uYWRkRXZlbnRMaXN0ZW5lcignc3VibWl0JywgYXN5bmMgKGUpID0+IHtcbiAgICAgIGUucHJldmVudERlZmF1bHQoKTtcbiAgICAgIGNvbnN0IHJlcyA9IGF3YWl0IHRoaXMuc3VibWl0Rm9ybSgpO1xuICAgICAgcmV0dXJuIHJlcztcbiAgICB9KTtcbiAgICB0aGlzLnNwZWNpYWxGaWVsZHMoKTtcbiAgfVxuICBzcGVjaWFsRmllbGRzKCkge1xuICAgIC8vIGNoZWNrIGlmIHRoZXJlIGlzIGEgcGFzc3dvcmQgY29uZmlybSBpbnB1dFxuICAgIC8vIGFkZCBzaG93IHRleHQgZm9yIHBhc3N3b3JkIGZpZWxkc1xuXG4gICAgdGhpcy5mb3JtLnF1ZXJ5U2VsZWN0b3JBbGwoJ2lucHV0W2RhdGEtbWF0Y2hdJykuZm9yRWFjaChpbnB1dCA9PiB7XG4gICAgICAvL1xuICAgICAgY29uc3QgbWF0Y2ggPSBpbnB1dC5kYXRhc2V0Lm1hdGNoO1xuICAgICAgaWYgKCFtYXRjaCkgcmV0dXJuO1xuICAgICAgY29uc3QgdGFyZ2V0ID0gZG9jdW1lbnQuZ2V0RWxlbWVudEJ5SWQobWF0Y2gpO1xuICAgICAgaWYgKCF0YXJnZXQpIHJldHVybjtcbiAgICAgIGNvbnN0IGludmFsaWQgPSAoaW5wdXQuZGF0YXNldC5tYXRjaGludmFsaWQpID8gaW5wdXQuZGF0YXNldC5tYXRjaGludmFsaWQgOiBcIm5vIG1hdGNoXCI7XG4gICAgICBjb25zdCBjaGVja19tYXRjaCA9IChpdGVtLCBpdGVtdGFyZ2V0KSA9PiB7XG4gICAgICAgIGNvbnN0IGxhYmVsID0gKGlucHV0LnByZXZpb3VzRWxlbWVudFNpYmxpbmcgJiYgaW5wdXQucHJldmlvdXNFbGVtZW50U2libGluZy50YWdOYW1lLnRvTG93ZXJDYXNlKCkgPT0gJ2xhYmVsJykgPyBpbnB1dC5wcmV2aW91c0VsZW1lbnRTaWJsaW5nIDogbnVsbDtcbiAgICAgICAgY29uc3QgbGFiZWx0YXJnZXQgPSAodGFyZ2V0LnByZXZpb3VzRWxlbWVudFNpYmxpbmcgJiYgdGFyZ2V0LnByZXZpb3VzRWxlbWVudFNpYmxpbmcudGFnTmFtZS50b0xvd2VyQ2FzZSgpID09ICdsYWJlbCcpID8gdGFyZ2V0LnByZXZpb3VzRWxlbWVudFNpYmxpbmcgOiBudWxsO1xuICAgICAgICBjb25zdCB7XG4gICAgICAgICAgcGF0dGVybk1pc21hdGNoID0gZmFsc2VcbiAgICAgICAgfSA9IGl0ZW0udmFsaWRpdHk7XG4gICAgICAgIGNvbnN0IGN1c3RvbXZhbGlkaXR5ID0gKHBhdHRlcm5NaXNtYXRjaCkgP1xuICAgICAgICAgIHRoaXMuZ2V0X21lc3NhZ2UoaXRlbSwgJ2ludmFsaWQnKSA6ICcnO1xuICAgICAgICBpZiAoaXRlbS5jaGVja1ZhbGlkaXR5KCkgPT09IHRydWUpIHtcbiAgICAgICAgICBpdGVtLmRhdGFzZXQuaW52YWxpZCA9ICcnO1xuICAgICAgICAgIGl0ZW0uc2V0Q3VzdG9tVmFsaWRpdHkoXCJcIik7XG4gICAgICAgICAgaWYgKGl0ZW0gPT0gaW5wdXQgJiYgbGFiZWwgIT09IG51bGwpIGxhYmVsLmNsYXNzTGlzdC5yZW1vdmUoZm9ybWNzcy5pbnZhbGlkKTtcbiAgICAgICAgICBlbHNlIGlmIChsYWJlbHRhcmdldCAhPT0gbnVsbCkgbGFiZWx0YXJnZXQuY2xhc3NMaXN0LnJlbW92ZShmb3JtY3NzLmludmFsaWQpO1xuICAgICAgICAgIGl0ZW0uY2xhc3NMaXN0LnJlbW92ZShmb3JtY3NzLmlucHV0dmFsaWRhdGUpO1xuICAgICAgICAgIGlmIChpdGVtLnZhbHVlICE9PSBpdGVtdGFyZ2V0LnZhbHVlKSB7XG4gICAgICAgICAgICBpbnB1dC5zZXRDdXN0b21WYWxpZGl0eShpbnZhbGlkKTtcbiAgICAgICAgICAgIGlucHV0LmRhdGFzZXQuaW52YWxpZCA9IGludmFsaWQ7XG4gICAgICAgICAgICBpZiAobGFiZWwpIGxhYmVsLmNsYXNzTGlzdC5hZGQoZm9ybWNzcy5pbnZhbGlkKTtcbiAgICAgICAgICAgIGlucHV0LmNsYXNzTGlzdC5hZGQoZm9ybWNzcy5pbnB1dHZhbGlkYXRlKTtcbiAgICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgICAgaW5wdXQuc2V0Q3VzdG9tVmFsaWRpdHkoXCJcIik7XG4gICAgICAgICAgICBpbnB1dC5kYXRhc2V0LmludmFsaWQgPSBcIlwiO1xuICAgICAgICAgICAgaWYgKGxhYmVsKSBsYWJlbC5jbGFzc0xpc3QucmVtb3ZlKGZvcm1jc3MuaW52YWxpZCk7XG4gICAgICAgICAgICBpbnB1dC5jbGFzc0xpc3QucmVtb3ZlKGZvcm1jc3MuaW5wdXR2YWxpZGF0ZSk7XG4gICAgICAgICAgfVxuICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgIGl0ZW0uc2V0Q3VzdG9tVmFsaWRpdHkoY3VzdG9tdmFsaWRpdHkpO1xuICAgICAgICAgIGl0ZW0uZGF0YXNldC5pbnZhbGlkID0gY3VzdG9tdmFsaWRpdHk7XG4gICAgICAgICAgaWYgKGxhYmVsKSBsYWJlbC5jbGFzc0xpc3QuYWRkKGZvcm1jc3MuaW52YWxpZCk7XG4gICAgICAgICAgaXRlbS5jbGFzc0xpc3QuYWRkKGZvcm1jc3MuaW5wdXR2YWxpZGF0ZSk7XG4gICAgICAgIH1cbiAgICAgICAgaXRlbS5mb2N1cygpO1xuICAgICAgfTtcbiAgICAgIFtpbnB1dCwgdGFyZ2V0XS5mb3JFYWNoKGl0ZW0gPT4ge1xuICAgICAgICBpdGVtLmFkZEV2ZW50TGlzdGVuZXIoJ2tleXVwJywgKGUpID0+IHtcbiAgICAgICAgICBjb25zdCBpdGVtdGFyZ2V0ID0gKGl0ZW0gPT09IGlucHV0KSA/IHRhcmdldCA6IGlucHV0O1xuICAgICAgICAgIGNoZWNrX21hdGNoKGl0ZW0sIGl0ZW10YXJnZXQpO1xuICAgICAgICB9KTtcbiAgICAgIH0pO1xuXG4gICAgfSk7XG4gIH1cbiAgZ2V0X21lc3NhZ2UoZmllbGQsIHR5cGUgPSAnaW52YWxpZCcpIHtcbiAgICBpZiAoZmllbGQuY2hlY2tWYWxpZGl0eSgpID09IGZhbHNlKSB7XG4gICAgICBjb25zdCB7XG4gICAgICAgIHZhbHVlTWlzc2luZyA9IHRydWVcbiAgICAgIH0gPSBmaWVsZC52YWxpZGl0eTtcbiAgICAgIGlmICh2YWx1ZU1pc3NpbmcpIHJldHVybiAoZmllbGQuZGF0YXNldC5yZXF1aXJlZCkgPyBmaWVsZC5kYXRhc2V0LnJlcXVpcmVkIDogKCh0aGlzLmZvcm0uZGF0YXNldC5yZXF1aXJlZCkgPyB0aGlzLmZvcm0uZGF0YXNldC5yZXF1aXJlZCA6ICdyZXF1aXJlZCcpO1xuICAgICAgZWxzZSByZXR1cm4gKGZpZWxkLmRhdGFzZXRbdHlwZV0pID8gZmllbGQuZGF0YXNldFt0eXBlXSA6ICdpbnB1dCBpbnZhbGlkJztcbiAgICB9IGVsc2UgcmV0dXJuICcnO1xuICB9XG5cbiAgdmFsaWRhdGVGaWVsZChmaWVsZCwgaW5pdCA9IGZhbHNlKSB7XG5cblxuXG4gICAgaWYgKFsndGV4dGFyZWEnLCAnaW5wdXQnXS5pbmRleE9mKGZpZWxkLnRhZ05hbWUudG9Mb3dlckNhc2UoKSkgPj0gMCkge1xuXG4gICAgfVxuXG4gICAgaWYgKFsnc2VsZWN0JywgJ2lucHV0W3R5cGU9XCJjaGVja2JveFwiXSddLmluZGV4T2YoZmllbGQudGFnTmFtZS50b0xvd2VyQ2FzZSgpKSA+PSAwKSB7XG4gICAgICBmaWVsZC5xdWVyeVNlbGVjdG9yQWxsKCdvcHRpb246Y2hlY2tlZCcpLmZvckVhY2gob3B0aW9uID0+IHtcbiAgICAgICAgb3B0aW9uLnZhbHVlID0gZGVjb2RlX0hUTUxFbnRpdGllcyhET01QdXJpZnkuc2FuaXRpemUob3B0aW9uLnZhbHVlKSk7XG4gICAgICB9KTtcblxuICAgIH0gZWxzZSBmaWVsZC52YWx1ZSA9IGRlY29kZV9IVE1MRW50aXRpZXMoRE9NUHVyaWZ5LnNhbml0aXplKGZpZWxkLnZhbHVlKSk7XG5cbiAgICBjb25zdCByZXAgPSBmaWVsZC5jaGVja1ZhbGlkaXR5KCk7XG5cbiAgICAvKiAgaWYgKGZpZWxkLmNsYXNzTGlzdC5jb250YWlucygnc2VsZWN0LW9uZScpKSB7XG5cbiAgICB9Ki9cbiAgICBjb25zdCBsYWJlbCA9IGZpZWxkLmNsb3Nlc3QoJy5mb3JtLWJveCcpID8gZmllbGQuY2xvc2VzdCgnLmZvcm0tYm94JykucXVlcnlTZWxlY3RvcignbGFiZWwnKSA6IG51bGw7XG5cbiAgICBpZiAocmVwICYmIGxhYmVsKSB7XG4gICAgICBsYWJlbC5jbGFzc0xpc3QucmVtb3ZlKGZvcm1jc3MuaW52YWxpZCk7XG4gICAgfSBlbHNlIGlmICghcmVwKSB7XG4gICAgICBpZiAobGFiZWwpIHtcbiAgICAgICAgbGFiZWwuZGF0YXNldC5pbnZhbGlkID0gdGhpcy5nZXRfbWVzc2FnZShmaWVsZCk7XG4gICAgICAgIGxhYmVsLmNsYXNzTGlzdC5hZGQoZm9ybWNzcy5pbnZhbGlkKTtcbiAgICAgICAgd2luZG93LnNjcm9sbFRvKHtcbiAgICAgICAgICB0b3A6IHBhcnNlSW50KGxhYmVsLm9mZnNldFRvcCksXG4gICAgICAgICAgbGVmdDogcGFyc2VJbnQobGFiZWwub2Zmc2V0TGVmdCksXG4gICAgICAgICAgYmVoYXZpb3I6ICdzbW9vdGgnXG4gICAgICAgIH0pO1xuICAgICAgfVxuICAgIH1cbiAgICByZXR1cm4gcmVwO1xuICB9XG5cbiAgdmFsaWRhdGVGaWVsZHMoaW5pdCA9IGZhbHNlKSB7XG4gICAgLy90b2RvOiBjb21wbGV0ZSB2YWxpZGF0aW9uIGZvcmVhY2ggZmllbGQgdHlwZVxuICAgIGxldCByZXNwID0gdHJ1ZTtcbiAgICAvLyAucmVxdWlyZWQgaW5wdXQgZm9yIHRvbS1zZWxlY3QgY29tcG9uZW50XG5cbiAgICBbLi4udGhpcy5mb3JtLmVsZW1lbnRzXS5mb3JFYWNoKGZpZWxkID0+IHtcbiAgICAgIGlmIChmaWVsZC5uYW1lKSB7XG5cbiAgICAgICAgaWYgKGluaXQgPT09IHRydWUpIHtcblxuICAgICAgICAgIGlmICghZmllbGQuZGF0YXNldC5saXN0ZW4pIHtcbiAgICAgICAgICAgIGlmIChmaWVsZC5oYXNBdHRyaWJ1dGUoJ3JlcXVpcmVkJykgJiYgZmllbGQucmVxdWlyZWQpIHtcbiAgICAgICAgICAgICAgY29uc3QgbGFiZWwgPSBmaWVsZC5jbG9zZXN0KCcuZm9ybS1ib3gnKSA/IGZpZWxkLmNsb3Nlc3QoJy5mb3JtLWJveCcpLnF1ZXJ5U2VsZWN0b3IoJ2xhYmVsJykgOiBmaWVsZC5wYXJlbnRFbGVtZW50LnF1ZXJ5U2VsZWN0b3IoJ2xhYmVsJyk7XG4gICAgICAgICAgICAgIGlmIChsYWJlbCkgbGFiZWwuY2xhc3NMaXN0LmFkZCgncmVxdWlyZWQnKTtcbiAgICAgICAgICAgIH1cblxuICAgICAgICAgICAgWydjaGFuZ2UnLCAnYmx1ciddLmZvckVhY2goZXZ0ID0+IHtcbiAgICAgICAgICAgICAgZmllbGQuYWRkRXZlbnRMaXN0ZW5lcihldnQsIChlKSA9PiB7XG4gICAgICAgICAgICAgICAgdGhpcy52YWxpZGF0ZUZpZWxkKGUuY3VycmVudFRhcmdldCwgaW5pdCk7XG4gICAgICAgICAgICAgIH0pO1xuICAgICAgICAgICAgfSk7XG4gICAgICAgICAgICBmaWVsZC5kYXRhc2V0Lmxpc3RlbiA9IHRydWU7XG4gICAgICAgICAgfVxuICAgICAgICB9IGVsc2UgcmVzcCA9IChyZXNwICYmIHRoaXMudmFsaWRhdGVGaWVsZChmaWVsZCwgaW5pdCkpO1xuICAgICAgfVxuICAgIH0pO1xuICAgIHJldHVybiByZXNwO1xuICB9XG5cbiAgYWRkSGFuZGxlcihoYW5kbGVyKSB7XG4gICAgdGhpcy5oYW5kbGVycy5wdXNoKGhhbmRsZXIpO1xuICB9XG4gIGZpZWxkRW5hYmxlKGVuYWJsZSA9IHRydWUpIHtcbiAgICB0aGlzLmZvcm0ucXVlcnlTZWxlY3RvckFsbCgnaW5wdXRbZGF0YS1zdWI9XCJlbmFibGVcIl0nKS5mb3JFYWNoKGlucHV0ID0+IHtcbiAgICAgIGlmIChlbmFibGUgPT09IHRydWUpIHtcbiAgICAgICAgaW5wdXQucmVtb3ZlQXR0cmlidXRlKFwiZGlzYWJsZWRcIik7XG4gICAgICB9IGVsc2UgaW5wdXQuZGlzYWJsZWQgPSB0cnVlO1xuICAgIH0pO1xuICB9XG5cbiAgYXN5bmMgc3VibWl0SGFuZGxlcigpIHtcbiAgICBpZiAoIXRoaXMudmFsaWRhdGVGaWVsZHMoKSkgcmV0dXJuIGZhbHNlO1xuXG4gICAgaWYgKHRoaXMuaGFuZGxlcnMubGVuZ3RoID09PSAwKSByZXR1cm4gdHJ1ZTtcbiAgICBsZXQgcmVzcCA9IHRydWU7XG4gICAgLy8gc2VyaWVzXG4gICAgLyogIGZvciAoY29uc3QgaGFuZGxlciBvZiB0aGlzLmhhbmRsZXJzKSB7XG4gICAgICAgICAgY29uc3QgcmVwID0gYXdhaXQgaGFuZGxlcigpXG4gICAgICAgICAgcmVzcCA9IChyZXNwICYmIHJlcClcbiAgICAgIH0qL1xuICAgIC8vIGNvbmN1cnJlbnRcbiAgICBhd2FpdCBQcm9taXNlLmFsbCh0aGlzLmhhbmRsZXJzLm1hcChhc3luYyBoYW5kbGVyID0+IHtcbiAgICAgIGNvbnN0IHJlcCA9IGF3YWl0IGhhbmRsZXIoKTtcbiAgICAgIHJlc3AgPSAocmVzcCAmJiByZXApO1xuICAgIH0pKTtcbiAgICBpZiAocmVzcCA9PT0gdHJ1ZSkgdGhpcy5oYW5kbGVycyA9IFtdO1xuICAgIHJldHVybiByZXNwO1xuICB9XG4gIC8vIG5vIHJlZGlyZWN0aW9uIHdoZW4gdXNpbmcgZGF0YS1mZXRjaFxuICBmb3JtRmV0Y2goZm9ybWF0ID0gbnVsbCkge1xuICAgIGNvbnN0IGZvcm1kYXRhID0gbmV3IEZvcm1EYXRhKHRoaXMuZm9ybSk7XG4gICAgZm9ybWRhdGFbXCJmZXRjaFwiXSA9IHRydWU7XG4gICAgZmV0Y2godGhpcy5mb3JtLmFjdGlvbiwgZmV0Y2hTZXR0aW5ncyh7XG4gICAgICAgIG1ldGhvZDogJ1BPU1QnLFxuICAgICAgICBib2R5OiBmb3JtZGF0YSxcbiAgICAgIH0pKVxuICAgICAgLnRoZW4ocmVzcG9uc2UgPT4ge1xuICAgICAgICBzd2l0Y2ggKGZvcm1hdCkge1xuICAgICAgICAgIGNhc2UgXCJ0ZXh0XCI6XG4gICAgICAgICAgY2FzZSBcImh0bWxcIjpcbiAgICAgICAgICAgIHJldHVybiByZXNwb25zZS50ZXh0KCk7XG4gICAgICAgICAgICBicmVhaztcbiAgICAgICAgICBkZWZhdWx0OlxuICAgICAgICAgICAgcmV0dXJuIHJlc3BvbnNlLmpzb24oKTtcbiAgICAgICAgfVxuICAgICAgfSlcbiAgICAgIC50aGVuKHJlc3BvbnNlID0+IHtcbiAgICAgICAgdGhpcy5kaXNwbGF5UmVzcG9uc2UocmVzcG9uc2UpO1xuICAgICAgfSlcbiAgICAgIC5jYXRjaChlcnIgPT4ge1xuICAgICAgICB0aGlzLmRpc3BsYXlSZXNwb25zZShlcnIsIHRydWUpXG4gICAgICB9KS5maW5hbGx5KHJlc3BvbnNlID0+IHtcbiAgICAgICAgdGhpcy5mb3JtLmRpc2FibGVkID0gdHJ1ZTtcbiAgICAgIH0pO1xuICAgIHJldHVybiBmYWxzZTtcbiAgfVxuXG4gIGFzeW5jIHN1Ym1pdEZvcm0oKSB7XG4gICAgdGhpcy5maWVsZEVuYWJsZSgpO1xuICAgIGlmICh0aGlzLnZhbGlkYXRlRmllbGRzKGZhbHNlKSkge1xuICAgICAgY29uc3QgaXNib3QgPSAodGhpcy5mb3JtLnF1ZXJ5U2VsZWN0b3IoZG9tc2VsZWN0b3JzLmNhcHRjaGEpKSA/ICh0aGlzLmZvcm0uZGF0YXNldC5pc2JvdCA/ICh0aGlzLmZvcm0uZGF0YXNldC5pc2JvdCA9PT0gdHJ1ZSkgOiB0cnVlKSA6IGZhbHNlO1xuICAgICAgaWYgKGlzYm90ID09PSB0cnVlKSByZXR1cm4gZmFsc2U7XG4gICAgICBjb25zdCB5ZXNzdWJtaXQgPSBhd2FpdCB0aGlzLnN1Ym1pdEhhbmRsZXIoKTtcbiAgICAgIGlmICh5ZXNzdWJtaXQpIHtcbiAgICAgICAgaWYgKHRoaXMub3B0aW9ucy5mZXRjaCkgdGhpcy5mb3JtRmV0Y2godGhpcy5vcHRpb25zLmZldGNoKTtcbiAgICAgICAgZWxzZSB0aGlzLmZvcm0uc3VibWl0KCk7XG4gICAgICAgIHRoaXMuZm9ybS5kaXNhYmxlZCA9IHRydWU7XG4gICAgICAgIHJldHVybiB0cnVlO1xuICAgICAgfSBlbHNlIHJldHVybiBmYWxzZTtcbiAgICB9IGVsc2UgcmV0dXJuIGZhbHNlO1xuICB9XG5cbiAgZGlzcGxheVJlc3BvbnNlKHJlc3BvbnNlLCBlcnJvciA9IGZhbHNlKSB7XG4gICAgY29uc3QgZWwgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCdkaXYnKTtcbiAgICBlbC5pbnNlcnRBZGphY2VudEhUTUwoJ2FmdGVyYmVnaW4nLCByZXNwb25zZSk7XG4gICAgaWYgKGVycm9yICE9PSBmYWxzZSkgZWwuY2xhc3NMaXN0LmFkZCgnaXMtZXJyb3InKTtcbiAgICB0aGlzLmZvcm0ucGFyZW50RWxlbWVudC5pbnNlcnRCZWZvcmUoZWwsIHRoaXMuZm9ybSk7XG4gICAgdGhpcy5mb3JtLnJlbW92ZSgpO1xuICB9XG59Il0sIm5hbWVzIjpbXSwic291cmNlUm9vdCI6IiJ9\n//# sourceURL=webpack-internal:///./src/modules/form-submit.js\n")},"./src/modules/js-import.js":(__unused_webpack_module,__webpack_exports__,__webpack_require__)=>{eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   JsImport: () => (/* binding */ JsImport)\n/* harmony export */ });\n/* harmony import */ var dompurify__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! dompurify */ \"./node_modules/dompurify/dist/purify.js\");\n/* harmony import */ var dompurify__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(dompurify__WEBPACK_IMPORTED_MODULE_0__);\n/* harmony import */ var _modules_form_submit_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../modules/form-submit.js */ \"./src/modules/form-submit.js\");\n/* harmony import */ var _modules_utils_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../modules/utils.js */ \"./src/modules/utils.js\");\n/* harmony import */ var _modules_modules_config_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../modules/modules-config.js */ \"./src/modules/modules-config.js\");\n\n\n\n\n\n\nclass JsImport {\n  typeimport;\n  myFiles;\n  constructor(container, options = {}) {\n    container = (container instanceof HTMLElement) ? container : document.querySelector(container);\n    if (!container) return;\n    this.container = container;\n    const defaultOptions = {\n      selector: {\n        displayresult: 'results',\n        typeimport: \"typeimport\",\n        importzone: \"file_to_load\",\n        showfiles: \".showfiles\",\n        displayselection: \"dirlist\"\n      }\n    };\n\n    this.options = Object.assign(defaultOptions, options);\n\n    this.init();\n  }\n\n  init() {\n    // init steps to display import sequence\n    this.container.querySelectorAll('input[name=\"' + this.options.selector.typeimport + '\"]').forEach(typeimport => {\n      typeimport.addEventListener('change', (e) => {\n        if (e.currentTarget.checked) {\n          console.log(e.currentTarget)\n          this.typeimport = e.currentTarget.value;\n          this.showSelection(true);\n        }\n      })\n    });\n    this.showSelection();\n  }\n  async showSelection(refresh = false) {\n    const apply_filters = () => {\n      let filters = this.typeimport.split('-');\n      filters = filters.map(filter => {\n        return new Set([...(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_3__.filter_files[filter] ? _modules_modules_config_js__WEBPACK_IMPORTED_MODULE_3__.filter_files[filter] : [])]);\n      });\n      this.myFiles.container.querySelectorAll('[data-ftype]').forEach(entry => {\n        if (filters.has(entry.dataset.ftype)) entry.classList.remove('disabled');\n        else entry.classList.add('disabled');\n      });\n    }\n    const displayselection = document.getElementById(this.options.selector.displayselection);\n    const displayresult = document.getElementById(this.options.selector.displayresult);\n    if (!displayselection || !displayresult) return;\n    if (!this.myFiles) {\n      const {\n        JsMyFiles\n      } =\n      await __webpack_require__.e(/*! import() */ \"src_modules_js-my-files_js\").then(__webpack_require__.bind(__webpack_require__, /*! ../modules/js-my-files.js */ \"./src/modules/js-my-files.js\"));\n      this.myFiles = new JsMyFiles(displayselection, {\n        enableupload: true,\n        enablestore: true,\n        btnfilelist: this.options.showfiles,\n        upload: {\n          label: (displayselection.dataset.uploadlabel) ? (displayselection.dataset.uploadlabel) : 'upload',\n          callback: () => {\n            this.addImportPath('/tmp/ecotaxa_user.760/ecotaxa_import');\n            this.showSubmit();\n          }\n        }\n      });\n    }\n\n    if (refresh === true) apply_filters();\n\n  }\n  addImportPath(value) {\n    document.getElementById(this.options.selector.importzone).value = value;\n    const displayresult = document.getElementById(this.options.selector.displayresult);\n    if (displayresult) displayresult.innerHTML = `<li>${value.split('/').pop()}</li>`;\n    const options = this.container.querySelector('#' + this.options.selector.importoptions);\n  }\n\n  showSubmit(show = true) {\n    const submit = this.container.querySelector('[type=\"submit\"]');\n    console.log('sub', submit)\n    if (show) {\n      submit.classList.remove('hide');\n      submit.disabled = false;\n    } else submit.disabled = true;\n  }\n}//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvbW9kdWxlcy9qcy1pbXBvcnQuanMiLCJtYXBwaW5ncyI6Ijs7Ozs7Ozs7O0FBQWtDOztBQUlDO0FBR047QUFJUzs7QUFFL0I7QUFDUDtBQUNBO0FBQ0EscUNBQXFDO0FBQ3JDO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7QUFFQTs7QUFFQTtBQUNBOztBQUVBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBLE9BQU87QUFDUCxLQUFLO0FBQ0w7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EsNEJBQTRCLG9FQUFZLFdBQVcsb0VBQVk7QUFDL0QsT0FBTztBQUNQO0FBQ0E7QUFDQTtBQUNBLE9BQU87QUFDUDtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBLFFBQVE7QUFDUixZQUFZLHdMQUFtQztBQUMvQztBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EsT0FBTztBQUNQOztBQUVBOztBQUVBO0FBQ0E7QUFDQTtBQUNBO0FBQ0Esd0RBQXdELHVCQUF1QjtBQUMvRTtBQUNBOztBQUVBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBLE1BQU07QUFDTjtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vLy4vc3JjL21vZHVsZXMvanMtaW1wb3J0LmpzPzYwMjMiXSwic291cmNlc0NvbnRlbnQiOlsiaW1wb3J0IERPTVB1cmlmeSBmcm9tICdkb21wdXJpZnknO1xuXG5pbXBvcnQge1xuICBGb3JtU3VibWl0XG59IGZyb20gJy4uL21vZHVsZXMvZm9ybS1zdWJtaXQuanMnO1xuaW1wb3J0IHtcbiAgZmV0Y2hTZXR0aW5ncyxcbn0gZnJvbSAnLi4vbW9kdWxlcy91dGlscy5qcyc7XG5pbXBvcnQge1xuICBjc3MsXG4gIGZpbHRlcl9maWxlc1xufSBmcm9tICcuLi9tb2R1bGVzL21vZHVsZXMtY29uZmlnLmpzJztcblxuZXhwb3J0IGNsYXNzIEpzSW1wb3J0IHtcbiAgdHlwZWltcG9ydDtcbiAgbXlGaWxlcztcbiAgY29uc3RydWN0b3IoY29udGFpbmVyLCBvcHRpb25zID0ge30pIHtcbiAgICBjb250YWluZXIgPSAoY29udGFpbmVyIGluc3RhbmNlb2YgSFRNTEVsZW1lbnQpID8gY29udGFpbmVyIDogZG9jdW1lbnQucXVlcnlTZWxlY3Rvcihjb250YWluZXIpO1xuICAgIGlmICghY29udGFpbmVyKSByZXR1cm47XG4gICAgdGhpcy5jb250YWluZXIgPSBjb250YWluZXI7XG4gICAgY29uc3QgZGVmYXVsdE9wdGlvbnMgPSB7XG4gICAgICBzZWxlY3Rvcjoge1xuICAgICAgICBkaXNwbGF5cmVzdWx0OiAncmVzdWx0cycsXG4gICAgICAgIHR5cGVpbXBvcnQ6IFwidHlwZWltcG9ydFwiLFxuICAgICAgICBpbXBvcnR6b25lOiBcImZpbGVfdG9fbG9hZFwiLFxuICAgICAgICBzaG93ZmlsZXM6IFwiLnNob3dmaWxlc1wiLFxuICAgICAgICBkaXNwbGF5c2VsZWN0aW9uOiBcImRpcmxpc3RcIlxuICAgICAgfVxuICAgIH07XG5cbiAgICB0aGlzLm9wdGlvbnMgPSBPYmplY3QuYXNzaWduKGRlZmF1bHRPcHRpb25zLCBvcHRpb25zKTtcblxuICAgIHRoaXMuaW5pdCgpO1xuICB9XG5cbiAgaW5pdCgpIHtcbiAgICAvLyBpbml0IHN0ZXBzIHRvIGRpc3BsYXkgaW1wb3J0IHNlcXVlbmNlXG4gICAgdGhpcy5jb250YWluZXIucXVlcnlTZWxlY3RvckFsbCgnaW5wdXRbbmFtZT1cIicgKyB0aGlzLm9wdGlvbnMuc2VsZWN0b3IudHlwZWltcG9ydCArICdcIl0nKS5mb3JFYWNoKHR5cGVpbXBvcnQgPT4ge1xuICAgICAgdHlwZWltcG9ydC5hZGRFdmVudExpc3RlbmVyKCdjaGFuZ2UnLCAoZSkgPT4ge1xuICAgICAgICBpZiAoZS5jdXJyZW50VGFyZ2V0LmNoZWNrZWQpIHtcbiAgICAgICAgICBjb25zb2xlLmxvZyhlLmN1cnJlbnRUYXJnZXQpXG4gICAgICAgICAgdGhpcy50eXBlaW1wb3J0ID0gZS5jdXJyZW50VGFyZ2V0LnZhbHVlO1xuICAgICAgICAgIHRoaXMuc2hvd1NlbGVjdGlvbih0cnVlKTtcbiAgICAgICAgfVxuICAgICAgfSlcbiAgICB9KTtcbiAgICB0aGlzLnNob3dTZWxlY3Rpb24oKTtcbiAgfVxuICBhc3luYyBzaG93U2VsZWN0aW9uKHJlZnJlc2ggPSBmYWxzZSkge1xuICAgIGNvbnN0IGFwcGx5X2ZpbHRlcnMgPSAoKSA9PiB7XG4gICAgICBsZXQgZmlsdGVycyA9IHRoaXMudHlwZWltcG9ydC5zcGxpdCgnLScpO1xuICAgICAgZmlsdGVycyA9IGZpbHRlcnMubWFwKGZpbHRlciA9PiB7XG4gICAgICAgIHJldHVybiBuZXcgU2V0KFsuLi4oZmlsdGVyX2ZpbGVzW2ZpbHRlcl0gPyBmaWx0ZXJfZmlsZXNbZmlsdGVyXSA6IFtdKV0pO1xuICAgICAgfSk7XG4gICAgICB0aGlzLm15RmlsZXMuY29udGFpbmVyLnF1ZXJ5U2VsZWN0b3JBbGwoJ1tkYXRhLWZ0eXBlXScpLmZvckVhY2goZW50cnkgPT4ge1xuICAgICAgICBpZiAoZmlsdGVycy5oYXMoZW50cnkuZGF0YXNldC5mdHlwZSkpIGVudHJ5LmNsYXNzTGlzdC5yZW1vdmUoJ2Rpc2FibGVkJyk7XG4gICAgICAgIGVsc2UgZW50cnkuY2xhc3NMaXN0LmFkZCgnZGlzYWJsZWQnKTtcbiAgICAgIH0pO1xuICAgIH1cbiAgICBjb25zdCBkaXNwbGF5c2VsZWN0aW9uID0gZG9jdW1lbnQuZ2V0RWxlbWVudEJ5SWQodGhpcy5vcHRpb25zLnNlbGVjdG9yLmRpc3BsYXlzZWxlY3Rpb24pO1xuICAgIGNvbnN0IGRpc3BsYXlyZXN1bHQgPSBkb2N1bWVudC5nZXRFbGVtZW50QnlJZCh0aGlzLm9wdGlvbnMuc2VsZWN0b3IuZGlzcGxheXJlc3VsdCk7XG4gICAgaWYgKCFkaXNwbGF5c2VsZWN0aW9uIHx8ICFkaXNwbGF5cmVzdWx0KSByZXR1cm47XG4gICAgaWYgKCF0aGlzLm15RmlsZXMpIHtcbiAgICAgIGNvbnN0IHtcbiAgICAgICAgSnNNeUZpbGVzXG4gICAgICB9ID1cbiAgICAgIGF3YWl0IGltcG9ydCgnLi4vbW9kdWxlcy9qcy1teS1maWxlcy5qcycpO1xuICAgICAgdGhpcy5teUZpbGVzID0gbmV3IEpzTXlGaWxlcyhkaXNwbGF5c2VsZWN0aW9uLCB7XG4gICAgICAgIGVuYWJsZXVwbG9hZDogdHJ1ZSxcbiAgICAgICAgZW5hYmxlc3RvcmU6IHRydWUsXG4gICAgICAgIGJ0bmZpbGVsaXN0OiB0aGlzLm9wdGlvbnMuc2hvd2ZpbGVzLFxuICAgICAgICB1cGxvYWQ6IHtcbiAgICAgICAgICBsYWJlbDogKGRpc3BsYXlzZWxlY3Rpb24uZGF0YXNldC51cGxvYWRsYWJlbCkgPyAoZGlzcGxheXNlbGVjdGlvbi5kYXRhc2V0LnVwbG9hZGxhYmVsKSA6ICd1cGxvYWQnLFxuICAgICAgICAgIGNhbGxiYWNrOiAoKSA9PiB7XG4gICAgICAgICAgICB0aGlzLmFkZEltcG9ydFBhdGgoJy90bXAvZWNvdGF4YV91c2VyLjc2MC9lY290YXhhX2ltcG9ydCcpO1xuICAgICAgICAgICAgdGhpcy5zaG93U3VibWl0KCk7XG4gICAgICAgICAgfVxuICAgICAgICB9XG4gICAgICB9KTtcbiAgICB9XG5cbiAgICBpZiAocmVmcmVzaCA9PT0gdHJ1ZSkgYXBwbHlfZmlsdGVycygpO1xuXG4gIH1cbiAgYWRkSW1wb3J0UGF0aCh2YWx1ZSkge1xuICAgIGRvY3VtZW50LmdldEVsZW1lbnRCeUlkKHRoaXMub3B0aW9ucy5zZWxlY3Rvci5pbXBvcnR6b25lKS52YWx1ZSA9IHZhbHVlO1xuICAgIGNvbnN0IGRpc3BsYXlyZXN1bHQgPSBkb2N1bWVudC5nZXRFbGVtZW50QnlJZCh0aGlzLm9wdGlvbnMuc2VsZWN0b3IuZGlzcGxheXJlc3VsdCk7XG4gICAgaWYgKGRpc3BsYXlyZXN1bHQpIGRpc3BsYXlyZXN1bHQuaW5uZXJIVE1MID0gYDxsaT4ke3ZhbHVlLnNwbGl0KCcvJykucG9wKCl9PC9saT5gO1xuICAgIGNvbnN0IG9wdGlvbnMgPSB0aGlzLmNvbnRhaW5lci5xdWVyeVNlbGVjdG9yKCcjJyArIHRoaXMub3B0aW9ucy5zZWxlY3Rvci5pbXBvcnRvcHRpb25zKTtcbiAgfVxuXG4gIHNob3dTdWJtaXQoc2hvdyA9IHRydWUpIHtcbiAgICBjb25zdCBzdWJtaXQgPSB0aGlzLmNvbnRhaW5lci5xdWVyeVNlbGVjdG9yKCdbdHlwZT1cInN1Ym1pdFwiXScpO1xuICAgIGNvbnNvbGUubG9nKCdzdWInLCBzdWJtaXQpXG4gICAgaWYgKHNob3cpIHtcbiAgICAgIHN1Ym1pdC5jbGFzc0xpc3QucmVtb3ZlKCdoaWRlJyk7XG4gICAgICBzdWJtaXQuZGlzYWJsZWQgPSBmYWxzZTtcbiAgICB9IGVsc2Ugc3VibWl0LmRpc2FibGVkID0gdHJ1ZTtcbiAgfVxufSJdLCJuYW1lcyI6W10sInNvdXJjZVJvb3QiOiIifQ==\n//# sourceURL=webpack-internal:///./src/modules/js-import.js\n")}}]);