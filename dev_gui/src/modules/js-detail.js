import DOMPurify from 'dompurify';
import {
  css,
  default_messages
} from '../modules/modules-config.js';
let instance = null;
//special details info - about in project lists
export class JsDetail {
  current = null; // this.current item - only one this.current at a time  / toggle when accordion style
  constructor(detail, wrapper, options = {}) {
    if (instance === null) {
      const defaultOptions = {
        istable: true, //called by element in table cell
        over: false, // display over or "inline vertical"
        waitdiv: null
      }
      this.options = Object.assign(defaultOptions, options);
      Object.freeze(this.options);
      this.wrapper = wrapper;
      this.detail = detail;
      this.init();
      instance = this;
    }
    return instance;
  }
  init() {
    if (this.detail instanceof HTMLElement) return;
    const detail = document.createElement('div');
    detail.id = this.detail;
    detail.classList.add(css.hide);
    if (this.options.waitdiv) {
      this.options.waitdiv.textContent = (this.options.waitdiv.dataset.wait) ? this.options.waitdiv.dataset.wait : default_messages.wait;
      detail.append(this.options.waitdiv);
    }
    detail.append(document.createElement('div'));
    this.detail = detail;
    this.wrapper.classList.add('relative');
    this.wrapper.append(this.detail);
    // todo : listener window resize
  }

  expandDetail(el, html = null) {
    // illusion of row expanding
    if (this.current && this.current !== el) this.shrinkDetail(this.current);
    this.current = el;
    if (this.options.waitdiv) this.options.waitdiv.classList.add(css.hide);
    if (html !== null) this.detail.lastElementChild.innerHTML = DOMPurify.sanitize(html);
    const padding = 6;
    const cell = (this.options.istable) ? el.closest('td') : el;
    const t = (this.options.istable) ? parseInt(this.wrapper.querySelector('table').offsetTop) : 0;
    const h = parseInt(cell.offsetHeight) + parseInt(this.detail.offsetHeight) + padding;
    const w = parseInt(this.wrapper.offsetWidth);
    this.detail.style.minWidth = this.detail.style.width = w + 'px';
    cell.style.overflow = el.style.overflowX = 'visible';
    this.detail.style.top = t + parseInt(cell.offsetTop) + parseInt(el.offsetHeight) + padding + 'px';
    cell.style.minHeight = cell.style.height = h + 'px';

  }
  shrinkDetail(el) {
    // illusion of row shrink
    const cell = (this.options.istable) ? el.closest('td') : el;
    //cell.style.maxHeight = cell.dataset.maxh;
    const ellipsis = el.closest('.overflow');
    if (ellipsis) {
      ellipsis.classList.remove('overflow');
      ellipsis.style.maxWidth = ellipsis.dataset.maxw;
    }
    cell.style.minHeight = 'none';
    cell.style.height = 'auto';
    cell.style.overflow = el.style.overflowX = el.parentElement.style.overflowX = 'hidden';
    this.detail.classList.add(css.hide);
    this.wrapper.append(this.detail);
    this.current = null;

  }
  activeDetail(activ, clear = false) {
    if (activ === true) {
      this.detail.lastElementChild.innerHTML = ``;
      this.detail.classList.remove(css.hide);
      if (this.options.waitdiv) this.options.waitdiv.classList.remove(css.hide);

    } else {
      this.detail.classList.add(css.hide);
      if (this.options.waitdiv) this.options.waitdiv.classList.add(css.hide);
      if (this.current) this.shrinkDetail(this.current);
      if (clear === true) this.detail.lastElementChild.innerHTML = ``;
      this.current = null;
    }
  }

}