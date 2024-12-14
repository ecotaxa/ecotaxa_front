import DOMPurify from 'dompurify';
import {
  css,
  default_messages
} from '../modules/modules-config.js';
import {
  create_box
} from '../modules/utils.js';
//special details info - about in project lists
export function JsDetail(options) {
  let current = null; // current item - only one this.current at a time  / toggle when accordion style
  let wrapper, detail, content;
  const defaultOptions = {
    istable: true, //called by element in table cell
    over: false, // display over or "inline vertical"
    waitdiv: null
  }
  options = { ...defaultOptions,
    ...options
  };
  Object.freeze(options);

  function applyTo(item, container) {
    if (!(container instanceof HTMLElement)) return;
    wrapper = container;
    wrapper.classList.add(css.relative);
    // item is either an id or the element
    if (item instanceof HTMLElement) return;
    detail = create_box('div', {
      id: item,
      class: css.hide
    }, wrapper);
    if (options.waitdiv) {
      options.waitdiv.textContent = (options.waitdiv.dataset.wait) ? options.waitdiv.dataset.wait : default_messages.wait;
      detail.append(options.waitdiv);
    }
    content = create_box('div', {}, detail);
    // todo : listener window resize
    return detail;
  }

  function expandDetail(el, html = null) {
    // illusion of row expanding

    if (current && current !== el) shrinkDetail(current);
    current = el;
    if (options.waitdiv) options.waitdiv.classList.add(css.hide);
    if (html !== null) content.innerHTML = DOMPurify.sanitize(html);
    el.append(detail);
    const padding = 6;
    const cell = (options.istable) ? el.closest('td') : el;
    let t = (options.istable) ? parseInt(wrapper.querySelector('table').offsetTop) : 0;
    t = t + (parseInt(cell.offsetTop) + parseInt(el.offsetHeight) + padding) + 'px';
    const h = (parseInt(cell.offsetHeight) + parseInt(detail.offsetHeight) + padding) + 'px';
    const w = (parseInt(wrapper.offsetWidth)) + 'px';
    requestAnimationFrame(() => {
      detail.style.minWidth = w;
      detail.style.width = w;
      cell.style.overflow = 'visible';
      el.style.overflowX = 'visible';
      detail.style.top = t;
      cell.style.minHeight = h;
      cell.style.height = h;
    });
    return current;
  }

  function shrinkDetail(el) {
    // illusion of row shrink
    const cell = (options.istable) ? el.closest('td') : el;
    //cell.style.maxHeight = cell.dataset.maxh;
    const ellipsis = el.closest('.overflow');
    if (ellipsis) {
      ellipsis.classList.remove('overflow');
      ellipsis.style.maxWidth = ellipsis.dataset.maxw;
    }
    cell.style.minHeight = 'none';
    cell.style.height = 'auto';
    cell.style.overflow = el.style.overflowX = el.parentElement.style.overflowX = 'hidden';
    detail.classList.add(css.hide);
    wrapper.append(detail);
    current = null;
    return current;
  }

  function activeDetail(activ, clear = false) {
    if (activ === true) {
      detail.lastElementChild.innerHTML = ``;
      detail.classList.remove(css.hide);
      if (options.waitdiv) options.waitdiv.classList.remove(css.hide);

    } else {
      detail.classList.add(css.hide);
      if (options.waitdiv) options.waitdiv.classList.add(css.hide);
      if (current) shrinkDetail(current);
      if (clear === true) detail.lastElementChild.innerHTML = ``;
      current = null;
    }
    return current;
  }
  return {
    applyTo,
    activeDetail,
    expandDetail,
  }
}