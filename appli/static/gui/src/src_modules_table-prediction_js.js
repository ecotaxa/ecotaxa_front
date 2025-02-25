/*! For license information please see src_modules_table-prediction_js.js.LICENSE.txt */
"use strict";(self.webpackChunk=self.webpackChunk||[]).push([["src_modules_table-prediction_js"],{"./src/modules/table-prediction.js":(__unused_webpack_module,__webpack_exports__,__webpack_require__)=>{eval('__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   "default": () => (/* export default binding */ __WEBPACK_DEFAULT_EXPORT__)\n/* harmony export */ });\n/* harmony import */ var _modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../modules/modules-config.js */ "./src/modules/modules-config.js");\n\n/* harmony default export */ function __WEBPACK_DEFAULT_EXPORT__(state) {\n  console.log(\'fromid\', state.params.fromid)\n  if (state.params.fromid) {\n    state.afterLoad = () => {\n      const tocheck = state.dom.querySelector(\'input[name="\' + state.uuid + \'select[]"][value="\' + state.params.fromid + \'"]\');\n      if (tocheck) tocheck.checked = true;\n    }\n  }\n  return {\n    selectmultiple: (value, rowIndex, cellIndex, td = {}) => {\n      const column = state.grid.columns[cellIndex];\n      value = (isNaN(value)) ? ((column.hasOwnProperty(\'field\')) ? this.getCellData(rowIndex, column.field) : value) : value;\n      td.childnodes = [{\n        nodename: "INPUT",\n        attributes: {\n          type: "checkbox",\n          name: `${state.uuid}select[]`,\n          value: String(value)\n        }\n      }];\n      return td;\n    },\n\n  }\n}//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvbW9kdWxlcy90YWJsZS1wcmVkaWN0aW9uLmpzIiwibWFwcGluZ3MiOiI7Ozs7O0FBRXNDO0FBQ3RDLDZCQUFlLG9DQUFTO0FBQ3hCO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSx3REFBd0Q7QUFDeEQ7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EsbUJBQW1CLFdBQVc7QUFDOUI7QUFDQTtBQUNBLE9BQU87QUFDUDtBQUNBLEtBQUs7O0FBRUw7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovLy8uL3NyYy9tb2R1bGVzL3RhYmxlLXByZWRpY3Rpb24uanM/MjVmOCJdLCJzb3VyY2VzQ29udGVudCI6WyJpbXBvcnQge1xuICBjc3Ncbn0gZnJvbSAnLi4vbW9kdWxlcy9tb2R1bGVzLWNvbmZpZy5qcyc7XG5leHBvcnQgZGVmYXVsdCBmdW5jdGlvbihzdGF0ZSkge1xuICBjb25zb2xlLmxvZygnZnJvbWlkJywgc3RhdGUucGFyYW1zLmZyb21pZClcbiAgaWYgKHN0YXRlLnBhcmFtcy5mcm9taWQpIHtcbiAgICBzdGF0ZS5hZnRlckxvYWQgPSAoKSA9PiB7XG4gICAgICBjb25zdCB0b2NoZWNrID0gc3RhdGUuZG9tLnF1ZXJ5U2VsZWN0b3IoJ2lucHV0W25hbWU9XCInICsgc3RhdGUudXVpZCArICdzZWxlY3RbXVwiXVt2YWx1ZT1cIicgKyBzdGF0ZS5wYXJhbXMuZnJvbWlkICsgJ1wiXScpO1xuICAgICAgaWYgKHRvY2hlY2spIHRvY2hlY2suY2hlY2tlZCA9IHRydWU7XG4gICAgfVxuICB9XG4gIHJldHVybiB7XG4gICAgc2VsZWN0bXVsdGlwbGU6ICh2YWx1ZSwgcm93SW5kZXgsIGNlbGxJbmRleCwgdGQgPSB7fSkgPT4ge1xuICAgICAgY29uc3QgY29sdW1uID0gc3RhdGUuZ3JpZC5jb2x1bW5zW2NlbGxJbmRleF07XG4gICAgICB2YWx1ZSA9IChpc05hTih2YWx1ZSkpID8gKChjb2x1bW4uaGFzT3duUHJvcGVydHkoJ2ZpZWxkJykpID8gdGhpcy5nZXRDZWxsRGF0YShyb3dJbmRleCwgY29sdW1uLmZpZWxkKSA6IHZhbHVlKSA6IHZhbHVlO1xuICAgICAgdGQuY2hpbGRub2RlcyA9IFt7XG4gICAgICAgIG5vZGVuYW1lOiBcIklOUFVUXCIsXG4gICAgICAgIGF0dHJpYnV0ZXM6IHtcbiAgICAgICAgICB0eXBlOiBcImNoZWNrYm94XCIsXG4gICAgICAgICAgbmFtZTogYCR7c3RhdGUudXVpZH1zZWxlY3RbXWAsXG4gICAgICAgICAgdmFsdWU6IFN0cmluZyh2YWx1ZSlcbiAgICAgICAgfVxuICAgICAgfV07XG4gICAgICByZXR1cm4gdGQ7XG4gICAgfSxcblxuICB9XG59Il0sIm5hbWVzIjpbXSwic291cmNlUm9vdCI6IiJ9\n//# sourceURL=webpack-internal:///./src/modules/table-prediction.js\n')}}]);