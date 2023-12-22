/*! For license information please see src_modules_table-sample_js.js.LICENSE.txt */
"use strict";(self.webpackChunk=self.webpackChunk||[]).push([["src_modules_table-sample_js"],{"./src/modules/table-sample.js":(__unused_webpack_module,__webpack_exports__,__webpack_require__)=>{eval('__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   "default": () => (/* export default binding */ __WEBPACK_DEFAULT_EXPORT__)\n/* harmony export */ });\n/* harmony import */ var _modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../modules/modules-config.js */ "./src/modules/modules-config.js");\n\n/* harmony default export */ function __WEBPACK_DEFAULT_EXPORT__(state) {\n  return {\n    taxa: (value, rowIndex, cellIndex, td = {}) => {\n\n      if (!Array.isArray(value)) td.childNodes = [];\n      let html = [];\n      value.forEach(v => {\n        html.push(v[1]);\n      });\n      td.childnodes = [{\n        nodename: \'DIV\',\n        attributes: {\n          class: _modules_modules_config_js__WEBPACK_IMPORTED_MODULE_0__.css.component.table.tip,\n          "data-num": html.length\n        },\n        childnodes: [state.setTextNode(html.join(`, `))]\n      }];\n      return td;\n    }\n\n  }\n}//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvbW9kdWxlcy90YWJsZS1zYW1wbGUuanMiLCJtYXBwaW5ncyI6Ijs7Ozs7QUFFc0M7QUFDdEMsNkJBQWUsb0NBQVM7QUFDeEI7QUFDQSw4Q0FBOEM7O0FBRTlDO0FBQ0E7QUFDQTtBQUNBO0FBQ0EsT0FBTztBQUNQO0FBQ0E7QUFDQTtBQUNBLGlCQUFpQiwyREFBRztBQUNwQjtBQUNBLFNBQVM7QUFDVDtBQUNBLE9BQU87QUFDUDtBQUNBOztBQUVBO0FBQ0EiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly8vLi9zcmMvbW9kdWxlcy90YWJsZS1zYW1wbGUuanM/OTI3ZCJdLCJzb3VyY2VzQ29udGVudCI6WyJpbXBvcnQge1xuICBjc3Ncbn0gZnJvbSAnLi4vbW9kdWxlcy9tb2R1bGVzLWNvbmZpZy5qcyc7XG5leHBvcnQgZGVmYXVsdCBmdW5jdGlvbihzdGF0ZSkge1xuICByZXR1cm4ge1xuICAgIHRheGE6ICh2YWx1ZSwgcm93SW5kZXgsIGNlbGxJbmRleCwgdGQgPSB7fSkgPT4ge1xuXG4gICAgICBpZiAoIUFycmF5LmlzQXJyYXkodmFsdWUpKSB0ZC5jaGlsZE5vZGVzID0gW107XG4gICAgICBsZXQgaHRtbCA9IFtdO1xuICAgICAgdmFsdWUuZm9yRWFjaCh2ID0+IHtcbiAgICAgICAgaHRtbC5wdXNoKHZbMV0pO1xuICAgICAgfSk7XG4gICAgICB0ZC5jaGlsZG5vZGVzID0gW3tcbiAgICAgICAgbm9kZW5hbWU6ICdESVYnLFxuICAgICAgICBhdHRyaWJ1dGVzOiB7XG4gICAgICAgICAgY2xhc3M6IGNzcy5jb21wb25lbnQudGFibGUudGlwLFxuICAgICAgICAgIFwiZGF0YS1udW1cIjogaHRtbC5sZW5ndGhcbiAgICAgICAgfSxcbiAgICAgICAgY2hpbGRub2RlczogW3N0YXRlLnNldFRleHROb2RlKGh0bWwuam9pbihgLCBgKSldXG4gICAgICB9XTtcbiAgICAgIHJldHVybiB0ZDtcbiAgICB9XG5cbiAgfVxufSJdLCJuYW1lcyI6W10sInNvdXJjZVJvb3QiOiIifQ==\n//# sourceURL=webpack-internal:///./src/modules/table-sample.js\n')}}]);