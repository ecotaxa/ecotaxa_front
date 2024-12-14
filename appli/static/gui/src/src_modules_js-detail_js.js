/*! For license information please see src_modules_js-detail_js.js.LICENSE.txt */
"use strict";(self.webpackChunk=self.webpackChunk||[]).push([["src_modules_js-detail_js"],{"./src/modules/js-detail.js":(__unused_webpack_module,__webpack_exports__,__webpack_require__)=>{eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   JsDetail: () => (/* binding */ JsDetail)\n/* harmony export */ });\n/* harmony import */ var dompurify__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! dompurify */ \"./node_modules/dompurify/dist/purify.js\");\n/* harmony import */ var dompurify__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(dompurify__WEBPACK_IMPORTED_MODULE_0__);\n/* harmony import */ var _modules_modules_config_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../modules/modules-config.js */ \"./src/modules/modules-config.js\");\n/* harmony import */ var _modules_utils_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../modules/utils.js */ \"./src/modules/utils.js\");\n\n\n\n//special details info - about in project lists\nfunction JsDetail(options) {\n  let current = null; // current item - only one this.current at a time  / toggle when accordion style\n  let wrapper, detail, content;\n  const defaultOptions = {\n    istable: true, //called by element in table cell\n    over: false, // display over or \"inline vertical\"\n    waitdiv: null\n  }\n  options = { ...defaultOptions,\n    ...options\n  };\n  Object.freeze(options);\n\n  function applyTo(item, container) {\n    if (!(container instanceof HTMLElement)) return;\n    wrapper = container;\n    wrapper.classList.add(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_1__.css.relative);\n    // item is either an id or the element\n    if (item instanceof HTMLElement) return;\n    detail = (0,_modules_utils_js__WEBPACK_IMPORTED_MODULE_2__.create_box)('div', {\n      id: item,\n      class: _modules_modules_config_js__WEBPACK_IMPORTED_MODULE_1__.css.hide\n    }, wrapper);\n    if (options.waitdiv) {\n      options.waitdiv.textContent = (options.waitdiv.dataset.wait) ? options.waitdiv.dataset.wait : _modules_modules_config_js__WEBPACK_IMPORTED_MODULE_1__.default_messages.wait;\n      detail.append(options.waitdiv);\n    }\n    content = (0,_modules_utils_js__WEBPACK_IMPORTED_MODULE_2__.create_box)('div', {}, detail);\n    // todo : listener window resize\n    return detail;\n  }\n\n  function expandDetail(el, html = null) {\n    // illusion of row expanding\n\n    if (current && current !== el) shrinkDetail(current);\n    current = el;\n    if (options.waitdiv) options.waitdiv.classList.add(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_1__.css.hide);\n    if (html !== null) content.innerHTML = dompurify__WEBPACK_IMPORTED_MODULE_0___default().sanitize(html);\n    el.append(detail);\n    const padding = 6;\n    const cell = (options.istable) ? el.closest('td') : el;\n    let t = (options.istable) ? parseInt(wrapper.querySelector('table').offsetTop) : 0;\n    t = t + (parseInt(cell.offsetTop) + parseInt(el.offsetHeight) + padding) + 'px';\n    const h = (parseInt(cell.offsetHeight) + parseInt(detail.offsetHeight) + padding) + 'px';\n    const w = (parseInt(wrapper.offsetWidth)) + 'px';\n    requestAnimationFrame(() => {\n      detail.style.minWidth = w;\n      detail.style.width = w;\n      cell.style.overflow = 'visible';\n      el.style.overflowX = 'visible';\n      detail.style.top = t;\n      cell.style.minHeight = h;\n      cell.style.height = h;\n    });\n    return current;\n  }\n\n  function shrinkDetail(el) {\n    // illusion of row shrink\n    const cell = (options.istable) ? el.closest('td') : el;\n    //cell.style.maxHeight = cell.dataset.maxh;\n    const ellipsis = el.closest('.overflow');\n    if (ellipsis) {\n      ellipsis.classList.remove('overflow');\n      ellipsis.style.maxWidth = ellipsis.dataset.maxw;\n    }\n    cell.style.minHeight = 'none';\n    cell.style.height = 'auto';\n    cell.style.overflow = el.style.overflowX = el.parentElement.style.overflowX = 'hidden';\n    detail.classList.add(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_1__.css.hide);\n    wrapper.append(detail);\n    current = null;\n    return current;\n  }\n\n  function activeDetail(activ, clear = false) {\n    if (activ === true) {\n      detail.lastElementChild.innerHTML = ``;\n      detail.classList.remove(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_1__.css.hide);\n      if (options.waitdiv) options.waitdiv.classList.remove(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_1__.css.hide);\n\n    } else {\n      detail.classList.add(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_1__.css.hide);\n      if (options.waitdiv) options.waitdiv.classList.add(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_1__.css.hide);\n      if (current) shrinkDetail(current);\n      if (clear === true) detail.lastElementChild.innerHTML = ``;\n      current = null;\n    }\n    return current;\n  }\n  return {\n    applyTo,\n    activeDetail,\n    expandDetail,\n  }\n}//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvbW9kdWxlcy9qcy1kZXRhaWwuanMiLCJtYXBwaW5ncyI6Ijs7Ozs7Ozs7QUFBa0M7QUFJSTtBQUdUO0FBQzdCO0FBQ087QUFDUCxzQkFBc0I7QUFDdEI7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EsY0FBYztBQUNkO0FBQ0E7QUFDQTs7QUFFQTtBQUNBO0FBQ0E7QUFDQSwwQkFBMEIsMkRBQUc7QUFDN0I7QUFDQTtBQUNBLGFBQWEsNkRBQVU7QUFDdkI7QUFDQSxhQUFhLDJEQUFHO0FBQ2hCLEtBQUs7QUFDTDtBQUNBLG9HQUFvRyx3RUFBZ0I7QUFDcEg7QUFDQTtBQUNBLGNBQWMsNkRBQVUsVUFBVTtBQUNsQztBQUNBO0FBQ0E7O0FBRUE7QUFDQTs7QUFFQTtBQUNBO0FBQ0EsdURBQXVELDJEQUFHO0FBQzFELDJDQUEyQyx5REFBa0I7QUFDN0Q7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EsS0FBSztBQUNMO0FBQ0E7O0FBRUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EseUJBQXlCLDJEQUFHO0FBQzVCO0FBQ0E7QUFDQTtBQUNBOztBQUVBO0FBQ0E7QUFDQTtBQUNBLDhCQUE4QiwyREFBRztBQUNqQyw0REFBNEQsMkRBQUc7O0FBRS9ELE1BQU07QUFDTiwyQkFBMkIsMkRBQUc7QUFDOUIseURBQXlELDJEQUFHO0FBQzVEO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovLy8uL3NyYy9tb2R1bGVzL2pzLWRldGFpbC5qcz9kYzVjIl0sInNvdXJjZXNDb250ZW50IjpbImltcG9ydCBET01QdXJpZnkgZnJvbSAnZG9tcHVyaWZ5JztcbmltcG9ydCB7XG4gIGNzcyxcbiAgZGVmYXVsdF9tZXNzYWdlc1xufSBmcm9tICcuLi9tb2R1bGVzL21vZHVsZXMtY29uZmlnLmpzJztcbmltcG9ydCB7XG4gIGNyZWF0ZV9ib3hcbn0gZnJvbSAnLi4vbW9kdWxlcy91dGlscy5qcyc7XG4vL3NwZWNpYWwgZGV0YWlscyBpbmZvIC0gYWJvdXQgaW4gcHJvamVjdCBsaXN0c1xuZXhwb3J0IGZ1bmN0aW9uIEpzRGV0YWlsKG9wdGlvbnMpIHtcbiAgbGV0IGN1cnJlbnQgPSBudWxsOyAvLyBjdXJyZW50IGl0ZW0gLSBvbmx5IG9uZSB0aGlzLmN1cnJlbnQgYXQgYSB0aW1lICAvIHRvZ2dsZSB3aGVuIGFjY29yZGlvbiBzdHlsZVxuICBsZXQgd3JhcHBlciwgZGV0YWlsLCBjb250ZW50O1xuICBjb25zdCBkZWZhdWx0T3B0aW9ucyA9IHtcbiAgICBpc3RhYmxlOiB0cnVlLCAvL2NhbGxlZCBieSBlbGVtZW50IGluIHRhYmxlIGNlbGxcbiAgICBvdmVyOiBmYWxzZSwgLy8gZGlzcGxheSBvdmVyIG9yIFwiaW5saW5lIHZlcnRpY2FsXCJcbiAgICB3YWl0ZGl2OiBudWxsXG4gIH1cbiAgb3B0aW9ucyA9IHsgLi4uZGVmYXVsdE9wdGlvbnMsXG4gICAgLi4ub3B0aW9uc1xuICB9O1xuICBPYmplY3QuZnJlZXplKG9wdGlvbnMpO1xuXG4gIGZ1bmN0aW9uIGFwcGx5VG8oaXRlbSwgY29udGFpbmVyKSB7XG4gICAgaWYgKCEoY29udGFpbmVyIGluc3RhbmNlb2YgSFRNTEVsZW1lbnQpKSByZXR1cm47XG4gICAgd3JhcHBlciA9IGNvbnRhaW5lcjtcbiAgICB3cmFwcGVyLmNsYXNzTGlzdC5hZGQoY3NzLnJlbGF0aXZlKTtcbiAgICAvLyBpdGVtIGlzIGVpdGhlciBhbiBpZCBvciB0aGUgZWxlbWVudFxuICAgIGlmIChpdGVtIGluc3RhbmNlb2YgSFRNTEVsZW1lbnQpIHJldHVybjtcbiAgICBkZXRhaWwgPSBjcmVhdGVfYm94KCdkaXYnLCB7XG4gICAgICBpZDogaXRlbSxcbiAgICAgIGNsYXNzOiBjc3MuaGlkZVxuICAgIH0sIHdyYXBwZXIpO1xuICAgIGlmIChvcHRpb25zLndhaXRkaXYpIHtcbiAgICAgIG9wdGlvbnMud2FpdGRpdi50ZXh0Q29udGVudCA9IChvcHRpb25zLndhaXRkaXYuZGF0YXNldC53YWl0KSA/IG9wdGlvbnMud2FpdGRpdi5kYXRhc2V0LndhaXQgOiBkZWZhdWx0X21lc3NhZ2VzLndhaXQ7XG4gICAgICBkZXRhaWwuYXBwZW5kKG9wdGlvbnMud2FpdGRpdik7XG4gICAgfVxuICAgIGNvbnRlbnQgPSBjcmVhdGVfYm94KCdkaXYnLCB7fSwgZGV0YWlsKTtcbiAgICAvLyB0b2RvIDogbGlzdGVuZXIgd2luZG93IHJlc2l6ZVxuICAgIHJldHVybiBkZXRhaWw7XG4gIH1cblxuICBmdW5jdGlvbiBleHBhbmREZXRhaWwoZWwsIGh0bWwgPSBudWxsKSB7XG4gICAgLy8gaWxsdXNpb24gb2Ygcm93IGV4cGFuZGluZ1xuXG4gICAgaWYgKGN1cnJlbnQgJiYgY3VycmVudCAhPT0gZWwpIHNocmlua0RldGFpbChjdXJyZW50KTtcbiAgICBjdXJyZW50ID0gZWw7XG4gICAgaWYgKG9wdGlvbnMud2FpdGRpdikgb3B0aW9ucy53YWl0ZGl2LmNsYXNzTGlzdC5hZGQoY3NzLmhpZGUpO1xuICAgIGlmIChodG1sICE9PSBudWxsKSBjb250ZW50LmlubmVySFRNTCA9IERPTVB1cmlmeS5zYW5pdGl6ZShodG1sKTtcbiAgICBlbC5hcHBlbmQoZGV0YWlsKTtcbiAgICBjb25zdCBwYWRkaW5nID0gNjtcbiAgICBjb25zdCBjZWxsID0gKG9wdGlvbnMuaXN0YWJsZSkgPyBlbC5jbG9zZXN0KCd0ZCcpIDogZWw7XG4gICAgbGV0IHQgPSAob3B0aW9ucy5pc3RhYmxlKSA/IHBhcnNlSW50KHdyYXBwZXIucXVlcnlTZWxlY3RvcigndGFibGUnKS5vZmZzZXRUb3ApIDogMDtcbiAgICB0ID0gdCArIChwYXJzZUludChjZWxsLm9mZnNldFRvcCkgKyBwYXJzZUludChlbC5vZmZzZXRIZWlnaHQpICsgcGFkZGluZykgKyAncHgnO1xuICAgIGNvbnN0IGggPSAocGFyc2VJbnQoY2VsbC5vZmZzZXRIZWlnaHQpICsgcGFyc2VJbnQoZGV0YWlsLm9mZnNldEhlaWdodCkgKyBwYWRkaW5nKSArICdweCc7XG4gICAgY29uc3QgdyA9IChwYXJzZUludCh3cmFwcGVyLm9mZnNldFdpZHRoKSkgKyAncHgnO1xuICAgIHJlcXVlc3RBbmltYXRpb25GcmFtZSgoKSA9PiB7XG4gICAgICBkZXRhaWwuc3R5bGUubWluV2lkdGggPSB3O1xuICAgICAgZGV0YWlsLnN0eWxlLndpZHRoID0gdztcbiAgICAgIGNlbGwuc3R5bGUub3ZlcmZsb3cgPSAndmlzaWJsZSc7XG4gICAgICBlbC5zdHlsZS5vdmVyZmxvd1ggPSAndmlzaWJsZSc7XG4gICAgICBkZXRhaWwuc3R5bGUudG9wID0gdDtcbiAgICAgIGNlbGwuc3R5bGUubWluSGVpZ2h0ID0gaDtcbiAgICAgIGNlbGwuc3R5bGUuaGVpZ2h0ID0gaDtcbiAgICB9KTtcbiAgICByZXR1cm4gY3VycmVudDtcbiAgfVxuXG4gIGZ1bmN0aW9uIHNocmlua0RldGFpbChlbCkge1xuICAgIC8vIGlsbHVzaW9uIG9mIHJvdyBzaHJpbmtcbiAgICBjb25zdCBjZWxsID0gKG9wdGlvbnMuaXN0YWJsZSkgPyBlbC5jbG9zZXN0KCd0ZCcpIDogZWw7XG4gICAgLy9jZWxsLnN0eWxlLm1heEhlaWdodCA9IGNlbGwuZGF0YXNldC5tYXhoO1xuICAgIGNvbnN0IGVsbGlwc2lzID0gZWwuY2xvc2VzdCgnLm92ZXJmbG93Jyk7XG4gICAgaWYgKGVsbGlwc2lzKSB7XG4gICAgICBlbGxpcHNpcy5jbGFzc0xpc3QucmVtb3ZlKCdvdmVyZmxvdycpO1xuICAgICAgZWxsaXBzaXMuc3R5bGUubWF4V2lkdGggPSBlbGxpcHNpcy5kYXRhc2V0Lm1heHc7XG4gICAgfVxuICAgIGNlbGwuc3R5bGUubWluSGVpZ2h0ID0gJ25vbmUnO1xuICAgIGNlbGwuc3R5bGUuaGVpZ2h0ID0gJ2F1dG8nO1xuICAgIGNlbGwuc3R5bGUub3ZlcmZsb3cgPSBlbC5zdHlsZS5vdmVyZmxvd1ggPSBlbC5wYXJlbnRFbGVtZW50LnN0eWxlLm92ZXJmbG93WCA9ICdoaWRkZW4nO1xuICAgIGRldGFpbC5jbGFzc0xpc3QuYWRkKGNzcy5oaWRlKTtcbiAgICB3cmFwcGVyLmFwcGVuZChkZXRhaWwpO1xuICAgIGN1cnJlbnQgPSBudWxsO1xuICAgIHJldHVybiBjdXJyZW50O1xuICB9XG5cbiAgZnVuY3Rpb24gYWN0aXZlRGV0YWlsKGFjdGl2LCBjbGVhciA9IGZhbHNlKSB7XG4gICAgaWYgKGFjdGl2ID09PSB0cnVlKSB7XG4gICAgICBkZXRhaWwubGFzdEVsZW1lbnRDaGlsZC5pbm5lckhUTUwgPSBgYDtcbiAgICAgIGRldGFpbC5jbGFzc0xpc3QucmVtb3ZlKGNzcy5oaWRlKTtcbiAgICAgIGlmIChvcHRpb25zLndhaXRkaXYpIG9wdGlvbnMud2FpdGRpdi5jbGFzc0xpc3QucmVtb3ZlKGNzcy5oaWRlKTtcblxuICAgIH0gZWxzZSB7XG4gICAgICBkZXRhaWwuY2xhc3NMaXN0LmFkZChjc3MuaGlkZSk7XG4gICAgICBpZiAob3B0aW9ucy53YWl0ZGl2KSBvcHRpb25zLndhaXRkaXYuY2xhc3NMaXN0LmFkZChjc3MuaGlkZSk7XG4gICAgICBpZiAoY3VycmVudCkgc2hyaW5rRGV0YWlsKGN1cnJlbnQpO1xuICAgICAgaWYgKGNsZWFyID09PSB0cnVlKSBkZXRhaWwubGFzdEVsZW1lbnRDaGlsZC5pbm5lckhUTUwgPSBgYDtcbiAgICAgIGN1cnJlbnQgPSBudWxsO1xuICAgIH1cbiAgICByZXR1cm4gY3VycmVudDtcbiAgfVxuICByZXR1cm4ge1xuICAgIGFwcGx5VG8sXG4gICAgYWN0aXZlRGV0YWlsLFxuICAgIGV4cGFuZERldGFpbCxcbiAgfVxufSJdLCJuYW1lcyI6W10sInNvdXJjZVJvb3QiOiIifQ==\n//# sourceURL=webpack-internal:///./src/modules/js-detail.js\n")}}]);