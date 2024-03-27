/*! For license information please see src_modules_js-taxomapping_js.js.LICENSE.txt */
"use strict";(self.webpackChunk=self.webpackChunk||[]).push([["src_modules_js-taxomapping_js"],{"./src/modules/js-taxomapping.js":(__unused_webpack_module,__webpack_exports__,__webpack_require__)=>{eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   TaxoMapping: () => (/* binding */ TaxoMapping)\n/* harmony export */ });\n/* harmony import */ var dompurify__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! dompurify */ \"./node_modules/dompurify/dist/purify.js\");\n/* harmony import */ var dompurify__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(dompurify__WEBPACK_IMPORTED_MODULE_0__);\n//from css tricks\n// used in tables about project stats details\n// used in tables imports when cells contains lots of data\n// apply mostly to details tags\n\nconst css = {\n  line: 'taxoline',\n  mapline: 'mapping-line',\n  cancel: 'cancel-line',\n};\nclass TaxoMapping {\n  // animation and specific display on accordions list / details tag open\n  numlines = 0;\n\n  constructor(line) {\n    if (!line instanceof HTMLElement) return;\n    if (!line.taxomapping) {\n      const keepname = (line.dataset.name) ? line.dataset.name : null;\n      if (keepname === null) return null;\n      this.keepname = keepname;\n      this.init(line);\n      line.taxomapping = this;\n\n    }\n    return line.taxomapping;\n  }\n\n\n  init(line) {\n    if (line.dataset.addline) {\n      let controls = {};\n      ['select', 'replace'].forEach(selector => {\n        controls[selector] = line.querySelector('[name=\"item-' + selector + '\"]');\n      });\n      this.linecontrols = controls;\n      controls = null;\n      let btn = line.querySelector('.' + line.dataset.addline);\n      btn = (btn === null) ? this.createBtn(line) : btn;\n      btn.addEventListener('click', (e) => {\n        this.addLine(line);\n      });\n      this.btn = btn;\n    }\n    // adjust historyback\n    window.addEventListener(\"pageshow\", (e) => {\n      const historytraversal = event.persisted ||\n        (typeof window.performance != \"undefined\" &&\n          window.performance.navigation.type === 2);\n      if (historytraversal) {\n        this.beforeSubmit(line);\n      }\n    });\n    this.beforeSubmit(line);\n  }\n\n  createBtn(line) {\n    const btn = document.createElement('div');\n    btn.classList.add(line.dataset.addline);\n    btn.insertAdjacentHTML('afterbegin', `<i class=\"icon icon-plus-sm block mx-auto\"></i>`);\n    btn.textContent = (line.dataset.addtext) ? dompurify__WEBPACK_IMPORTED_MODULE_0___default()(line.dataset.addtext).sanitize() : 'Add';\n    line.append(btn);\n    return btn;\n  }\n\n  addLine(line) {\n    // verify values not \"\" for select and replace inputs\n    let cando = true;\n    Object.values(this.linecontrols).forEach(input => {\n      const inputvalue = (input.tomselect) ? ((input.tomselect.items.length) ? input.tomselect.items[0] : '') : new String(input.value);\n      cando = cando && (inputvalue.length > 0);\n    });\n    if (cando === false) {\n      this.btn.dataset.title = (line.dataset.notselected) ? line.dataset.notselected : 'select values to replace';\n      return;\n    } else if (this.btn.dataset.title) delete this.btn.dataset.title;\n    const newline = document.createElement('div');\n    newline.classList.add(css.line);\n    newline.classList.add('pb-2');\n    this.numlines++;\n\n    Object.values(this.linecontrols).forEach(input => {\n      const keep = document.createElement('div');\n      keep.classList.add(css.mapline);\n      keep.classList.add('mr-2');\n      if (input.tomselect) {\n        const tsinput = line.querySelector('.ts-control > div');\n        keep.dataset.value = input.value;\n        keep.textContent = tsinput.textContent;\n        keep.dataset.replace = this.numlines;\n        input.tomselect.clear(true);\n      } else {\n        keep.dataset.value = input.options[input.selectedIndex].value;\n        keep.textContent = input.options[input.selectedIndex].text;\n        newline.dataset.index = input.selectedIndex;\n        keep.dataset.select = this.numlines;\n        input.options[input.selectedIndex].disabled = true;\n        input.selectedIndex = -1;\n      }\n      input.parentElement.insertBefore(keep, input);\n      newline.append(keep);\n    });\n    this.btnCancel(newline, (line.dataset.cancel) ? line.dataset.cancel : 'cancel');\n    line.parentElement.insertBefore(newline, line);\n  }\n\n  btnCancel(item, text) {\n    const cancel = document.createElement('div');\n    cancel.id = 'cancel_' + this.numlines;\n    cancel.classList.add(css.cancel);\n    ['action', 'name'].forEach(data => {\n      delete cancel.dataset[data];\n    });\n    item.append(cancel);\n    cancel.insertAdjacentHTML('afterbegin', `<i class=\"icon icon-cancel absolute centered\"></i>`);\n    cancel.addEventListener('click', (e) => {\n      this.linecontrols.select.options[item.dataset.index].disabled = false;\n      item.remove();\n    });\n  }\n\n  beforeSubmit(item) {\n    const form = item.closest('form');\n    if (form === null) return;\n    const format_mapping_field = () => {\n      let keephidden = form.querySelector('input[name=\"' + this.keepname + '\"]');\n      if (keephidden !== null) keephidden.remove();\n      keephidden = document.createElement('input');\n      keephidden.type = 'hidden';\n      keephidden.name = this.keepname;\n      let mapping = {};\n      form.querySelectorAll('[data-select]').forEach(el => {\n        const replace = el.parentElement.querySelector('[data-replace=\"' + el.dataset.select + '\"]');\n        if (replace !== null) mapping[el.dataset.value] = replace.dataset.value;\n      });\n      form.append(keephidden);\n      keephidden.value = JSON.stringify(mapping);\n      return true;\n    };\n    if (form.formsubmit) {\n      form.formsubmit.addHandler('submit', format_mapping_field);\n\n    } else form.addEventListener('submit', (e) => {\n      format_mapping_field();\n    });\n  }\n\n}//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvbW9kdWxlcy9qcy10YXhvbWFwcGluZy5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNrQztBQUNsQztBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ087QUFDUDtBQUNBOztBQUVBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7O0FBRUE7QUFDQTtBQUNBOzs7QUFHQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EsT0FBTztBQUNQO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBLE9BQU87QUFDUDtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBLEtBQUs7QUFDTDtBQUNBOztBQUVBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EsK0NBQStDLGdEQUFTO0FBQ3hEO0FBQ0E7QUFDQTs7QUFFQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSxLQUFLO0FBQ0w7QUFDQTtBQUNBO0FBQ0EsTUFBTTtBQUNOO0FBQ0E7QUFDQTtBQUNBOztBQUVBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EsUUFBUTtBQUNSO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBLEtBQUs7QUFDTDtBQUNBO0FBQ0E7O0FBRUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EsS0FBSztBQUNMO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSxLQUFLO0FBQ0w7O0FBRUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSxPQUFPO0FBQ1A7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOztBQUVBLE1BQU07QUFDTjtBQUNBLEtBQUs7QUFDTDs7QUFFQSIsInNvdXJjZXMiOlsid2VicGFjazovLy8uL3NyYy9tb2R1bGVzL2pzLXRheG9tYXBwaW5nLmpzP2JhNTIiXSwic291cmNlc0NvbnRlbnQiOlsiLy9mcm9tIGNzcyB0cmlja3Ncbi8vIHVzZWQgaW4gdGFibGVzIGFib3V0IHByb2plY3Qgc3RhdHMgZGV0YWlsc1xuLy8gdXNlZCBpbiB0YWJsZXMgaW1wb3J0cyB3aGVuIGNlbGxzIGNvbnRhaW5zIGxvdHMgb2YgZGF0YVxuLy8gYXBwbHkgbW9zdGx5IHRvIGRldGFpbHMgdGFnc1xuaW1wb3J0IERPTVB1cmlmeSBmcm9tICdkb21wdXJpZnknO1xuY29uc3QgY3NzID0ge1xuICBsaW5lOiAndGF4b2xpbmUnLFxuICBtYXBsaW5lOiAnbWFwcGluZy1saW5lJyxcbiAgY2FuY2VsOiAnY2FuY2VsLWxpbmUnLFxufTtcbmV4cG9ydCBjbGFzcyBUYXhvTWFwcGluZyB7XG4gIC8vIGFuaW1hdGlvbiBhbmQgc3BlY2lmaWMgZGlzcGxheSBvbiBhY2NvcmRpb25zIGxpc3QgLyBkZXRhaWxzIHRhZyBvcGVuXG4gIG51bWxpbmVzID0gMDtcblxuICBjb25zdHJ1Y3RvcihsaW5lKSB7XG4gICAgaWYgKCFsaW5lIGluc3RhbmNlb2YgSFRNTEVsZW1lbnQpIHJldHVybjtcbiAgICBpZiAoIWxpbmUudGF4b21hcHBpbmcpIHtcbiAgICAgIGNvbnN0IGtlZXBuYW1lID0gKGxpbmUuZGF0YXNldC5uYW1lKSA/IGxpbmUuZGF0YXNldC5uYW1lIDogbnVsbDtcbiAgICAgIGlmIChrZWVwbmFtZSA9PT0gbnVsbCkgcmV0dXJuIG51bGw7XG4gICAgICB0aGlzLmtlZXBuYW1lID0ga2VlcG5hbWU7XG4gICAgICB0aGlzLmluaXQobGluZSk7XG4gICAgICBsaW5lLnRheG9tYXBwaW5nID0gdGhpcztcblxuICAgIH1cbiAgICByZXR1cm4gbGluZS50YXhvbWFwcGluZztcbiAgfVxuXG5cbiAgaW5pdChsaW5lKSB7XG4gICAgaWYgKGxpbmUuZGF0YXNldC5hZGRsaW5lKSB7XG4gICAgICBsZXQgY29udHJvbHMgPSB7fTtcbiAgICAgIFsnc2VsZWN0JywgJ3JlcGxhY2UnXS5mb3JFYWNoKHNlbGVjdG9yID0+IHtcbiAgICAgICAgY29udHJvbHNbc2VsZWN0b3JdID0gbGluZS5xdWVyeVNlbGVjdG9yKCdbbmFtZT1cIml0ZW0tJyArIHNlbGVjdG9yICsgJ1wiXScpO1xuICAgICAgfSk7XG4gICAgICB0aGlzLmxpbmVjb250cm9scyA9IGNvbnRyb2xzO1xuICAgICAgY29udHJvbHMgPSBudWxsO1xuICAgICAgbGV0IGJ0biA9IGxpbmUucXVlcnlTZWxlY3RvcignLicgKyBsaW5lLmRhdGFzZXQuYWRkbGluZSk7XG4gICAgICBidG4gPSAoYnRuID09PSBudWxsKSA/IHRoaXMuY3JlYXRlQnRuKGxpbmUpIDogYnRuO1xuICAgICAgYnRuLmFkZEV2ZW50TGlzdGVuZXIoJ2NsaWNrJywgKGUpID0+IHtcbiAgICAgICAgdGhpcy5hZGRMaW5lKGxpbmUpO1xuICAgICAgfSk7XG4gICAgICB0aGlzLmJ0biA9IGJ0bjtcbiAgICB9XG4gICAgLy8gYWRqdXN0IGhpc3RvcnliYWNrXG4gICAgd2luZG93LmFkZEV2ZW50TGlzdGVuZXIoXCJwYWdlc2hvd1wiLCAoZSkgPT4ge1xuICAgICAgY29uc3QgaGlzdG9yeXRyYXZlcnNhbCA9IGV2ZW50LnBlcnNpc3RlZCB8fFxuICAgICAgICAodHlwZW9mIHdpbmRvdy5wZXJmb3JtYW5jZSAhPSBcInVuZGVmaW5lZFwiICYmXG4gICAgICAgICAgd2luZG93LnBlcmZvcm1hbmNlLm5hdmlnYXRpb24udHlwZSA9PT0gMik7XG4gICAgICBpZiAoaGlzdG9yeXRyYXZlcnNhbCkge1xuICAgICAgICB0aGlzLmJlZm9yZVN1Ym1pdChsaW5lKTtcbiAgICAgIH1cbiAgICB9KTtcbiAgICB0aGlzLmJlZm9yZVN1Ym1pdChsaW5lKTtcbiAgfVxuXG4gIGNyZWF0ZUJ0bihsaW5lKSB7XG4gICAgY29uc3QgYnRuID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgnZGl2Jyk7XG4gICAgYnRuLmNsYXNzTGlzdC5hZGQobGluZS5kYXRhc2V0LmFkZGxpbmUpO1xuICAgIGJ0bi5pbnNlcnRBZGphY2VudEhUTUwoJ2FmdGVyYmVnaW4nLCBgPGkgY2xhc3M9XCJpY29uIGljb24tcGx1cy1zbSBibG9jayBteC1hdXRvXCI+PC9pPmApO1xuICAgIGJ0bi50ZXh0Q29udGVudCA9IChsaW5lLmRhdGFzZXQuYWRkdGV4dCkgPyBET01QdXJpZnkobGluZS5kYXRhc2V0LmFkZHRleHQpLnNhbml0aXplKCkgOiAnQWRkJztcbiAgICBsaW5lLmFwcGVuZChidG4pO1xuICAgIHJldHVybiBidG47XG4gIH1cblxuICBhZGRMaW5lKGxpbmUpIHtcbiAgICAvLyB2ZXJpZnkgdmFsdWVzIG5vdCBcIlwiIGZvciBzZWxlY3QgYW5kIHJlcGxhY2UgaW5wdXRzXG4gICAgbGV0IGNhbmRvID0gdHJ1ZTtcbiAgICBPYmplY3QudmFsdWVzKHRoaXMubGluZWNvbnRyb2xzKS5mb3JFYWNoKGlucHV0ID0+IHtcbiAgICAgIGNvbnN0IGlucHV0dmFsdWUgPSAoaW5wdXQudG9tc2VsZWN0KSA/ICgoaW5wdXQudG9tc2VsZWN0Lml0ZW1zLmxlbmd0aCkgPyBpbnB1dC50b21zZWxlY3QuaXRlbXNbMF0gOiAnJykgOiBuZXcgU3RyaW5nKGlucHV0LnZhbHVlKTtcbiAgICAgIGNhbmRvID0gY2FuZG8gJiYgKGlucHV0dmFsdWUubGVuZ3RoID4gMCk7XG4gICAgfSk7XG4gICAgaWYgKGNhbmRvID09PSBmYWxzZSkge1xuICAgICAgdGhpcy5idG4uZGF0YXNldC50aXRsZSA9IChsaW5lLmRhdGFzZXQubm90c2VsZWN0ZWQpID8gbGluZS5kYXRhc2V0Lm5vdHNlbGVjdGVkIDogJ3NlbGVjdCB2YWx1ZXMgdG8gcmVwbGFjZSc7XG4gICAgICByZXR1cm47XG4gICAgfSBlbHNlIGlmICh0aGlzLmJ0bi5kYXRhc2V0LnRpdGxlKSBkZWxldGUgdGhpcy5idG4uZGF0YXNldC50aXRsZTtcbiAgICBjb25zdCBuZXdsaW5lID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgnZGl2Jyk7XG4gICAgbmV3bGluZS5jbGFzc0xpc3QuYWRkKGNzcy5saW5lKTtcbiAgICBuZXdsaW5lLmNsYXNzTGlzdC5hZGQoJ3BiLTInKTtcbiAgICB0aGlzLm51bWxpbmVzKys7XG5cbiAgICBPYmplY3QudmFsdWVzKHRoaXMubGluZWNvbnRyb2xzKS5mb3JFYWNoKGlucHV0ID0+IHtcbiAgICAgIGNvbnN0IGtlZXAgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCdkaXYnKTtcbiAgICAgIGtlZXAuY2xhc3NMaXN0LmFkZChjc3MubWFwbGluZSk7XG4gICAgICBrZWVwLmNsYXNzTGlzdC5hZGQoJ21yLTInKTtcbiAgICAgIGlmIChpbnB1dC50b21zZWxlY3QpIHtcbiAgICAgICAgY29uc3QgdHNpbnB1dCA9IGxpbmUucXVlcnlTZWxlY3RvcignLnRzLWNvbnRyb2wgPiBkaXYnKTtcbiAgICAgICAga2VlcC5kYXRhc2V0LnZhbHVlID0gaW5wdXQudmFsdWU7XG4gICAgICAgIGtlZXAudGV4dENvbnRlbnQgPSB0c2lucHV0LnRleHRDb250ZW50O1xuICAgICAgICBrZWVwLmRhdGFzZXQucmVwbGFjZSA9IHRoaXMubnVtbGluZXM7XG4gICAgICAgIGlucHV0LnRvbXNlbGVjdC5jbGVhcih0cnVlKTtcbiAgICAgIH0gZWxzZSB7XG4gICAgICAgIGtlZXAuZGF0YXNldC52YWx1ZSA9IGlucHV0Lm9wdGlvbnNbaW5wdXQuc2VsZWN0ZWRJbmRleF0udmFsdWU7XG4gICAgICAgIGtlZXAudGV4dENvbnRlbnQgPSBpbnB1dC5vcHRpb25zW2lucHV0LnNlbGVjdGVkSW5kZXhdLnRleHQ7XG4gICAgICAgIG5ld2xpbmUuZGF0YXNldC5pbmRleCA9IGlucHV0LnNlbGVjdGVkSW5kZXg7XG4gICAgICAgIGtlZXAuZGF0YXNldC5zZWxlY3QgPSB0aGlzLm51bWxpbmVzO1xuICAgICAgICBpbnB1dC5vcHRpb25zW2lucHV0LnNlbGVjdGVkSW5kZXhdLmRpc2FibGVkID0gdHJ1ZTtcbiAgICAgICAgaW5wdXQuc2VsZWN0ZWRJbmRleCA9IC0xO1xuICAgICAgfVxuICAgICAgaW5wdXQucGFyZW50RWxlbWVudC5pbnNlcnRCZWZvcmUoa2VlcCwgaW5wdXQpO1xuICAgICAgbmV3bGluZS5hcHBlbmQoa2VlcCk7XG4gICAgfSk7XG4gICAgdGhpcy5idG5DYW5jZWwobmV3bGluZSwgKGxpbmUuZGF0YXNldC5jYW5jZWwpID8gbGluZS5kYXRhc2V0LmNhbmNlbCA6ICdjYW5jZWwnKTtcbiAgICBsaW5lLnBhcmVudEVsZW1lbnQuaW5zZXJ0QmVmb3JlKG5ld2xpbmUsIGxpbmUpO1xuICB9XG5cbiAgYnRuQ2FuY2VsKGl0ZW0sIHRleHQpIHtcbiAgICBjb25zdCBjYW5jZWwgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCdkaXYnKTtcbiAgICBjYW5jZWwuaWQgPSAnY2FuY2VsXycgKyB0aGlzLm51bWxpbmVzO1xuICAgIGNhbmNlbC5jbGFzc0xpc3QuYWRkKGNzcy5jYW5jZWwpO1xuICAgIFsnYWN0aW9uJywgJ25hbWUnXS5mb3JFYWNoKGRhdGEgPT4ge1xuICAgICAgZGVsZXRlIGNhbmNlbC5kYXRhc2V0W2RhdGFdO1xuICAgIH0pO1xuICAgIGl0ZW0uYXBwZW5kKGNhbmNlbCk7XG4gICAgY2FuY2VsLmluc2VydEFkamFjZW50SFRNTCgnYWZ0ZXJiZWdpbicsIGA8aSBjbGFzcz1cImljb24gaWNvbi1jYW5jZWwgYWJzb2x1dGUgY2VudGVyZWRcIj48L2k+YCk7XG4gICAgY2FuY2VsLmFkZEV2ZW50TGlzdGVuZXIoJ2NsaWNrJywgKGUpID0+IHtcbiAgICAgIHRoaXMubGluZWNvbnRyb2xzLnNlbGVjdC5vcHRpb25zW2l0ZW0uZGF0YXNldC5pbmRleF0uZGlzYWJsZWQgPSBmYWxzZTtcbiAgICAgIGl0ZW0ucmVtb3ZlKCk7XG4gICAgfSk7XG4gIH1cblxuICBiZWZvcmVTdWJtaXQoaXRlbSkge1xuICAgIGNvbnN0IGZvcm0gPSBpdGVtLmNsb3Nlc3QoJ2Zvcm0nKTtcbiAgICBpZiAoZm9ybSA9PT0gbnVsbCkgcmV0dXJuO1xuICAgIGNvbnN0IGZvcm1hdF9tYXBwaW5nX2ZpZWxkID0gKCkgPT4ge1xuICAgICAgbGV0IGtlZXBoaWRkZW4gPSBmb3JtLnF1ZXJ5U2VsZWN0b3IoJ2lucHV0W25hbWU9XCInICsgdGhpcy5rZWVwbmFtZSArICdcIl0nKTtcbiAgICAgIGlmIChrZWVwaGlkZGVuICE9PSBudWxsKSBrZWVwaGlkZGVuLnJlbW92ZSgpO1xuICAgICAga2VlcGhpZGRlbiA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoJ2lucHV0Jyk7XG4gICAgICBrZWVwaGlkZGVuLnR5cGUgPSAnaGlkZGVuJztcbiAgICAgIGtlZXBoaWRkZW4ubmFtZSA9IHRoaXMua2VlcG5hbWU7XG4gICAgICBsZXQgbWFwcGluZyA9IHt9O1xuICAgICAgZm9ybS5xdWVyeVNlbGVjdG9yQWxsKCdbZGF0YS1zZWxlY3RdJykuZm9yRWFjaChlbCA9PiB7XG4gICAgICAgIGNvbnN0IHJlcGxhY2UgPSBlbC5wYXJlbnRFbGVtZW50LnF1ZXJ5U2VsZWN0b3IoJ1tkYXRhLXJlcGxhY2U9XCInICsgZWwuZGF0YXNldC5zZWxlY3QgKyAnXCJdJyk7XG4gICAgICAgIGlmIChyZXBsYWNlICE9PSBudWxsKSBtYXBwaW5nW2VsLmRhdGFzZXQudmFsdWVdID0gcmVwbGFjZS5kYXRhc2V0LnZhbHVlO1xuICAgICAgfSk7XG4gICAgICBmb3JtLmFwcGVuZChrZWVwaGlkZGVuKTtcbiAgICAgIGtlZXBoaWRkZW4udmFsdWUgPSBKU09OLnN0cmluZ2lmeShtYXBwaW5nKTtcbiAgICAgIHJldHVybiB0cnVlO1xuICAgIH07XG4gICAgaWYgKGZvcm0uZm9ybXN1Ym1pdCkge1xuICAgICAgZm9ybS5mb3Jtc3VibWl0LmFkZEhhbmRsZXIoJ3N1Ym1pdCcsIGZvcm1hdF9tYXBwaW5nX2ZpZWxkKTtcblxuICAgIH0gZWxzZSBmb3JtLmFkZEV2ZW50TGlzdGVuZXIoJ3N1Ym1pdCcsIChlKSA9PiB7XG4gICAgICBmb3JtYXRfbWFwcGluZ19maWVsZCgpO1xuICAgIH0pO1xuICB9XG5cbn0iXSwibmFtZXMiOltdLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///./src/modules/js-taxomapping.js\n")}}]);