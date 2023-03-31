/*! For license information please see src_modules_js-detail_js.js.LICENSE.txt */
"use strict";(self.webpackChunk=self.webpackChunk||[]).push([["src_modules_js-detail_js"],{"./src/modules/js-detail.js":(__unused_webpack_module,__webpack_exports__,__webpack_require__)=>{eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"JsDetail\": () => (/* binding */ JsDetail)\n/* harmony export */ });\n/* harmony import */ var dompurify__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! dompurify */ \"./node_modules/dompurify/dist/purify.js\");\n/* harmony import */ var dompurify__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(dompurify__WEBPACK_IMPORTED_MODULE_0__);\n/* harmony import */ var _modules_modules_config_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../modules/modules-config.js */ \"./src/modules/modules-config.js\");\n\n\nlet instance = null;\n//special details info - about in project lists\nclass JsDetail {\n  current = null; // this.current item - only one this.current at a time  / toggle when accordion style\n  constructor(detail, wrapper, options = {}) {\n    if (instance === null) {\n      const defaultOptions = {\n        istable: true, //called by element in table cell\n        over: false, // display over or \"inline vertical\"\n        waitdiv: null\n      }\n      this.options = Object.assign(defaultOptions, options);\n      Object.freeze(this.options);\n      this.wrapper = wrapper;\n      this.detail = detail;\n      this.init();\n      instance = this;\n    }\n    return instance;\n  }\n  init() {\n    if (this.detail instanceof HTMLElement) return;\n    const detail = document.createElement('div');\n    detail.id = this.detail;\n    detail.classList.add(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_1__.css.hide);\n    if (this.options.waitdiv) {\n      this.options.waitdiv.textContent = (this.options.waitdiv.dataset.wait) ? this.options.waitdiv.dataset.wait : _modules_modules_config_js__WEBPACK_IMPORTED_MODULE_1__.default_messages.wait;\n      detail.append(this.options.waitdiv);\n    }\n    detail.append(document.createElement('div'));\n    this.detail = detail;\n    this.wrapper.classList.add('relative');\n    this.wrapper.append(this.detail);\n    // todo : listener window resize\n  }\n\n  expandDetail(el, html = null) {\n    // illusion of row expanding\n    if (this.current && this.current !== el) this.shrinkDetail(this.current);\n    this.current = el;\n    if (this.options.waitdiv) this.options.waitdiv.classList.add(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_1__.css.hide);\n    if (html !== null) this.detail.lastElementChild.innerHTML = dompurify__WEBPACK_IMPORTED_MODULE_0___default().sanitize(html);\n    const padding = 6;\n    const cell = (this.options.istable) ? el.closest('td') : el;\n    const t = (this.options.istable) ? parseInt(this.wrapper.querySelector('table').offsetTop) : 0;\n    const h = parseInt(cell.offsetHeight) + parseInt(this.detail.offsetHeight) + padding;\n    const w = parseInt(this.wrapper.offsetWidth);\n    this.detail.style.minWidth = this.detail.style.width = w + 'px';\n    cell.style.overflow = el.style.overflowX = 'visible';\n    this.detail.style.top = t + parseInt(cell.offsetTop) + parseInt(el.offsetHeight) + padding + 'px';\n    cell.style.minHeight = cell.style.height = h + 'px';\n\n  }\n  shrinkDetail(el) {\n    // illusion of row shrink\n    const cell = (this.options.istable) ? el.closest('td') : el;\n    //cell.style.maxHeight = cell.dataset.maxh;\n    const ellipsis = el.closest('.overflow');\n    if (ellipsis) {\n      ellipsis.classList.remove('overflow');\n      ellipsis.style.maxWidth = ellipsis.dataset.maxw;\n    }\n    cell.style.minHeight = 'none';\n    cell.style.height = 'auto';\n    cell.style.overflow = el.style.overflowX = el.parentElement.style.overflowX = 'hidden';\n    this.detail.classList.add(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_1__.css.hide);\n    this.wrapper.append(this.detail);\n    this.current = null;\n\n  }\n  activeDetail(activ, clear = false) {\n    if (activ === true) {\n      this.detail.lastElementChild.innerHTML = ``;\n      this.detail.classList.remove(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_1__.css.hide);\n      if (this.options.waitdiv) this.options.waitdiv.classList.remove(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_1__.css.hide);\n\n    } else {\n      this.detail.classList.add(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_1__.css.hide);\n      if (this.options.waitdiv) this.options.waitdiv.classList.add(_modules_modules_config_js__WEBPACK_IMPORTED_MODULE_1__.css.hide);\n      if (this.current) this.shrinkDetail(this.current);\n      if (clear === true) this.detail.lastElementChild.innerHTML = ``;\n      this.current = null;\n    }\n  }\n\n}//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvbW9kdWxlcy9qcy1kZXRhaWwuanMuanMiLCJtYXBwaW5ncyI6Ijs7Ozs7OztBQUFrQztBQUlJO0FBQ3RDO0FBQ0E7QUFDTztBQUNQLGtCQUFrQjtBQUNsQiwyQ0FBMkM7QUFDM0M7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSx5QkFBeUIsZ0VBQVE7QUFDakM7QUFDQSxtSEFBbUgsNkVBQXFCO0FBQ3hJO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7O0FBRUE7QUFDQTtBQUNBO0FBQ0E7QUFDQSxpRUFBaUUsZ0VBQVE7QUFDekUsZ0VBQWdFLHlEQUFrQjtBQUNsRjtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7O0FBRUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSw4QkFBOEIsZ0VBQVE7QUFDdEM7QUFDQTs7QUFFQTtBQUNBO0FBQ0E7QUFDQTtBQUNBLG1DQUFtQyxnRUFBUTtBQUMzQyxzRUFBc0UsZ0VBQVE7O0FBRTlFLE1BQU07QUFDTixnQ0FBZ0MsZ0VBQVE7QUFDeEMsbUVBQW1FLGdFQUFRO0FBQzNFO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7O0FBRUEiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly8vLi9zcmMvbW9kdWxlcy9qcy1kZXRhaWwuanM/ZGM1YyJdLCJzb3VyY2VzQ29udGVudCI6WyJpbXBvcnQgRE9NUHVyaWZ5IGZyb20gJ2RvbXB1cmlmeSc7XG5pbXBvcnQge1xuICBjc3MsXG4gIGRlZmF1bHRfbWVzc2FnZXNcbn0gZnJvbSAnLi4vbW9kdWxlcy9tb2R1bGVzLWNvbmZpZy5qcyc7XG5sZXQgaW5zdGFuY2UgPSBudWxsO1xuLy9zcGVjaWFsIGRldGFpbHMgaW5mbyAtIGFib3V0IGluIHByb2plY3QgbGlzdHNcbmV4cG9ydCBjbGFzcyBKc0RldGFpbCB7XG4gIGN1cnJlbnQgPSBudWxsOyAvLyB0aGlzLmN1cnJlbnQgaXRlbSAtIG9ubHkgb25lIHRoaXMuY3VycmVudCBhdCBhIHRpbWUgIC8gdG9nZ2xlIHdoZW4gYWNjb3JkaW9uIHN0eWxlXG4gIGNvbnN0cnVjdG9yKGRldGFpbCwgd3JhcHBlciwgb3B0aW9ucyA9IHt9KSB7XG4gICAgaWYgKGluc3RhbmNlID09PSBudWxsKSB7XG4gICAgICBjb25zdCBkZWZhdWx0T3B0aW9ucyA9IHtcbiAgICAgICAgaXN0YWJsZTogdHJ1ZSwgLy9jYWxsZWQgYnkgZWxlbWVudCBpbiB0YWJsZSBjZWxsXG4gICAgICAgIG92ZXI6IGZhbHNlLCAvLyBkaXNwbGF5IG92ZXIgb3IgXCJpbmxpbmUgdmVydGljYWxcIlxuICAgICAgICB3YWl0ZGl2OiBudWxsXG4gICAgICB9XG4gICAgICB0aGlzLm9wdGlvbnMgPSBPYmplY3QuYXNzaWduKGRlZmF1bHRPcHRpb25zLCBvcHRpb25zKTtcbiAgICAgIE9iamVjdC5mcmVlemUodGhpcy5vcHRpb25zKTtcbiAgICAgIHRoaXMud3JhcHBlciA9IHdyYXBwZXI7XG4gICAgICB0aGlzLmRldGFpbCA9IGRldGFpbDtcbiAgICAgIHRoaXMuaW5pdCgpO1xuICAgICAgaW5zdGFuY2UgPSB0aGlzO1xuICAgIH1cbiAgICByZXR1cm4gaW5zdGFuY2U7XG4gIH1cbiAgaW5pdCgpIHtcbiAgICBpZiAodGhpcy5kZXRhaWwgaW5zdGFuY2VvZiBIVE1MRWxlbWVudCkgcmV0dXJuO1xuICAgIGNvbnN0IGRldGFpbCA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoJ2RpdicpO1xuICAgIGRldGFpbC5pZCA9IHRoaXMuZGV0YWlsO1xuICAgIGRldGFpbC5jbGFzc0xpc3QuYWRkKGNzcy5oaWRlKTtcbiAgICBpZiAodGhpcy5vcHRpb25zLndhaXRkaXYpIHtcbiAgICAgIHRoaXMub3B0aW9ucy53YWl0ZGl2LnRleHRDb250ZW50ID0gKHRoaXMub3B0aW9ucy53YWl0ZGl2LmRhdGFzZXQud2FpdCkgPyB0aGlzLm9wdGlvbnMud2FpdGRpdi5kYXRhc2V0LndhaXQgOiBkZWZhdWx0X21lc3NhZ2VzLndhaXQ7XG4gICAgICBkZXRhaWwuYXBwZW5kKHRoaXMub3B0aW9ucy53YWl0ZGl2KTtcbiAgICB9XG4gICAgZGV0YWlsLmFwcGVuZChkb2N1bWVudC5jcmVhdGVFbGVtZW50KCdkaXYnKSk7XG4gICAgdGhpcy5kZXRhaWwgPSBkZXRhaWw7XG4gICAgdGhpcy53cmFwcGVyLmNsYXNzTGlzdC5hZGQoJ3JlbGF0aXZlJyk7XG4gICAgdGhpcy53cmFwcGVyLmFwcGVuZCh0aGlzLmRldGFpbCk7XG4gICAgLy8gdG9kbyA6IGxpc3RlbmVyIHdpbmRvdyByZXNpemVcbiAgfVxuXG4gIGV4cGFuZERldGFpbChlbCwgaHRtbCA9IG51bGwpIHtcbiAgICAvLyBpbGx1c2lvbiBvZiByb3cgZXhwYW5kaW5nXG4gICAgaWYgKHRoaXMuY3VycmVudCAmJiB0aGlzLmN1cnJlbnQgIT09IGVsKSB0aGlzLnNocmlua0RldGFpbCh0aGlzLmN1cnJlbnQpO1xuICAgIHRoaXMuY3VycmVudCA9IGVsO1xuICAgIGlmICh0aGlzLm9wdGlvbnMud2FpdGRpdikgdGhpcy5vcHRpb25zLndhaXRkaXYuY2xhc3NMaXN0LmFkZChjc3MuaGlkZSk7XG4gICAgaWYgKGh0bWwgIT09IG51bGwpIHRoaXMuZGV0YWlsLmxhc3RFbGVtZW50Q2hpbGQuaW5uZXJIVE1MID0gRE9NUHVyaWZ5LnNhbml0aXplKGh0bWwpO1xuICAgIGNvbnN0IHBhZGRpbmcgPSA2O1xuICAgIGNvbnN0IGNlbGwgPSAodGhpcy5vcHRpb25zLmlzdGFibGUpID8gZWwuY2xvc2VzdCgndGQnKSA6IGVsO1xuICAgIGNvbnN0IHQgPSAodGhpcy5vcHRpb25zLmlzdGFibGUpID8gcGFyc2VJbnQodGhpcy53cmFwcGVyLnF1ZXJ5U2VsZWN0b3IoJ3RhYmxlJykub2Zmc2V0VG9wKSA6IDA7XG4gICAgY29uc3QgaCA9IHBhcnNlSW50KGNlbGwub2Zmc2V0SGVpZ2h0KSArIHBhcnNlSW50KHRoaXMuZGV0YWlsLm9mZnNldEhlaWdodCkgKyBwYWRkaW5nO1xuICAgIGNvbnN0IHcgPSBwYXJzZUludCh0aGlzLndyYXBwZXIub2Zmc2V0V2lkdGgpO1xuICAgIHRoaXMuZGV0YWlsLnN0eWxlLm1pbldpZHRoID0gdGhpcy5kZXRhaWwuc3R5bGUud2lkdGggPSB3ICsgJ3B4JztcbiAgICBjZWxsLnN0eWxlLm92ZXJmbG93ID0gZWwuc3R5bGUub3ZlcmZsb3dYID0gJ3Zpc2libGUnO1xuICAgIHRoaXMuZGV0YWlsLnN0eWxlLnRvcCA9IHQgKyBwYXJzZUludChjZWxsLm9mZnNldFRvcCkgKyBwYXJzZUludChlbC5vZmZzZXRIZWlnaHQpICsgcGFkZGluZyArICdweCc7XG4gICAgY2VsbC5zdHlsZS5taW5IZWlnaHQgPSBjZWxsLnN0eWxlLmhlaWdodCA9IGggKyAncHgnO1xuXG4gIH1cbiAgc2hyaW5rRGV0YWlsKGVsKSB7XG4gICAgLy8gaWxsdXNpb24gb2Ygcm93IHNocmlua1xuICAgIGNvbnN0IGNlbGwgPSAodGhpcy5vcHRpb25zLmlzdGFibGUpID8gZWwuY2xvc2VzdCgndGQnKSA6IGVsO1xuICAgIC8vY2VsbC5zdHlsZS5tYXhIZWlnaHQgPSBjZWxsLmRhdGFzZXQubWF4aDtcbiAgICBjb25zdCBlbGxpcHNpcyA9IGVsLmNsb3Nlc3QoJy5vdmVyZmxvdycpO1xuICAgIGlmIChlbGxpcHNpcykge1xuICAgICAgZWxsaXBzaXMuY2xhc3NMaXN0LnJlbW92ZSgnb3ZlcmZsb3cnKTtcbiAgICAgIGVsbGlwc2lzLnN0eWxlLm1heFdpZHRoID0gZWxsaXBzaXMuZGF0YXNldC5tYXh3O1xuICAgIH1cbiAgICBjZWxsLnN0eWxlLm1pbkhlaWdodCA9ICdub25lJztcbiAgICBjZWxsLnN0eWxlLmhlaWdodCA9ICdhdXRvJztcbiAgICBjZWxsLnN0eWxlLm92ZXJmbG93ID0gZWwuc3R5bGUub3ZlcmZsb3dYID0gZWwucGFyZW50RWxlbWVudC5zdHlsZS5vdmVyZmxvd1ggPSAnaGlkZGVuJztcbiAgICB0aGlzLmRldGFpbC5jbGFzc0xpc3QuYWRkKGNzcy5oaWRlKTtcbiAgICB0aGlzLndyYXBwZXIuYXBwZW5kKHRoaXMuZGV0YWlsKTtcbiAgICB0aGlzLmN1cnJlbnQgPSBudWxsO1xuXG4gIH1cbiAgYWN0aXZlRGV0YWlsKGFjdGl2LCBjbGVhciA9IGZhbHNlKSB7XG4gICAgaWYgKGFjdGl2ID09PSB0cnVlKSB7XG4gICAgICB0aGlzLmRldGFpbC5sYXN0RWxlbWVudENoaWxkLmlubmVySFRNTCA9IGBgO1xuICAgICAgdGhpcy5kZXRhaWwuY2xhc3NMaXN0LnJlbW92ZShjc3MuaGlkZSk7XG4gICAgICBpZiAodGhpcy5vcHRpb25zLndhaXRkaXYpIHRoaXMub3B0aW9ucy53YWl0ZGl2LmNsYXNzTGlzdC5yZW1vdmUoY3NzLmhpZGUpO1xuXG4gICAgfSBlbHNlIHtcbiAgICAgIHRoaXMuZGV0YWlsLmNsYXNzTGlzdC5hZGQoY3NzLmhpZGUpO1xuICAgICAgaWYgKHRoaXMub3B0aW9ucy53YWl0ZGl2KSB0aGlzLm9wdGlvbnMud2FpdGRpdi5jbGFzc0xpc3QuYWRkKGNzcy5oaWRlKTtcbiAgICAgIGlmICh0aGlzLmN1cnJlbnQpIHRoaXMuc2hyaW5rRGV0YWlsKHRoaXMuY3VycmVudCk7XG4gICAgICBpZiAoY2xlYXIgPT09IHRydWUpIHRoaXMuZGV0YWlsLmxhc3RFbGVtZW50Q2hpbGQuaW5uZXJIVE1MID0gYGA7XG4gICAgICB0aGlzLmN1cnJlbnQgPSBudWxsO1xuICAgIH1cbiAgfVxuXG59Il0sIm5hbWVzIjpbXSwic291cmNlUm9vdCI6IiJ9\n//# sourceURL=webpack-internal:///./src/modules/js-detail.js\n")}}]);