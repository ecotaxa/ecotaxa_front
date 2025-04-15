//from css tricks
// used in tables about project stats details
// used in tables imports when cells contains lots of data
// apply mostly to details tags
import {
  css
} from '../modules/modules-config.js';
css.open = 'open';

function createJsAccordion() {
  let options = {
    shrink: {
      opacity: [100, 0],
      scaleY: [1, 0]
    },
    expand: {
      opacity: [0, 100],
      scaleY: [0, 1]
    }
  }
  let activitem = null;
  let currentitem = null;
  let callbackopen = null;
  let callbackclose = null;

  function applyTo(item, open = null, close = null, content = null, opts = {}) {
    options = { ...options,
      ...opts
    };
    Object.freeze(options);
    callbackopen = open;
    callbackclose = close;
    const details = (item instanceof HTMLElement) ? item.querySelectorAll(((item.dataset && item.dataset.detail) ? item.dataset.detail : item.querySelector('details'))) : item;
    details.forEach(el => {
      const summary = (el.dataset && el.dataset.summary) ? el : ((item.dataset && item.dataset.summary) ? el.querySelector(item.dataset.summary) : el.querySelector('summary'));
      const elcontent = (content) ? content : ((el.dataset && el.dataset.content) ? item.querySelector(el.dataset.content) : null);
      initItem(el, summary, elcontent);
    });
  }
  // animation and specific display on accordions list / details tag open
  function initItem(el, elsummary = null, elcontent = null) {
    // Store the <details> element
    const element = (el instanceof HTMLElement) ? el : el.querySelector(el);
    if (!element) return;
    const summary = (elsummary) ? ((elsummary instanceof HTMLElement) ? elsummary : el.querySelector(elsummary)) : ((el.querySelector('summary')) ? el.querySelector('summary') : el);
    if (!summary) return;
    const content = (elcontent) ? ((elcontent instanceof HTMLElement) ? elcontent : el.querySelector(elcontent)) : element.nextElementSibling;
    if (!content) return;
    summary.addEventListener('click', (e) => {
      if (currentitem === null || currentitem.element !== element) currentitem = setItem(element, summary, content);
      onClick(e);
    });

    function isOpen(current = currentitem) {
      return (element.tagName.toLowerCase() === 'details') ? element.open : ((content.classList.contains(css.hide)) ? false : true);
    }

    function setItem(element, summary, content) {
      return {
        animation: null,
        element: element,
        summary: summary,
        content: content,
        isclosing: false,
        isexpanding: false
      }
    }

    function onClick(e, current = currentitem) {
      e.preventDefault();
      // Check if the element is being closed or is already closed

      if (current.isclosing || !isOpen(current)) {

        // for fetching data or other op.
        if (callbackopen) {
          callbackopen(current.element, () => {
            open(current);
          });
        } else open(current);
        if (activitem !== null)  shrink(activitem);
        activitem = current;
        // Check if the element is being openned or is already open
      } else if (current.isexpanding || isOpen(current)) {
        shrink(current);
        activitem = null;
      }
    }
    // close the content with an animation
    function shrink(current = currentitem) {
    //close previous item
      if (current.summary.emitevent) current.summary.emitevent();
      current.isclosing = true;
      if (current.animation) current.animation.cancel();
      // Start a WAAPI animation
      current.animation = current.content.animate(options.shrink, {
        duration: 400,
        easing: 'ease-out'
      });
      current.animation.onfinish = () => onAnimationFinish(false, current);
      current.animation.oncancel = () => current.isclosing = false;
      if (callbackclose) callbackclose(current.element);
    }

    function toggleElement(open, current = currentitem) {
      if (current.element.tagName.toLowerCase() === 'details') current.element.open = open;
      else {
        if (open) {
          current.content.classList.remove(css.hide);
          current.summary.classList.add(css.open);
        } else {
          current.content.classList.add(css.hide);
          current.summary.classList.remove(css.open);
        }
      }
    }

    function open(current = currentitem) {
      toggleElement(true, current);
      requestAnimationFrame(() => expand(current));
    }

    function expand(current = currentitem) {
      current.isexpanding = true;
      if (current.animation) current.animation.cancel();
      // Start a WAAPI animation
      current.animation = current.content.animate(options.expand, {
        duration: 400,
        easing: 'ease-out'
      });
      current.animation.onfinish = () => onAnimationFinish(true, current);
      current.animation.oncancel = () => current.isexpanding = false;
    }

    function onAnimationFinish(open, current = currentitem) {
      toggleElement(open, current);
      current.animation = null;
      current.isclosing = false;
      current.isexpanding = false;
    }
  }
  return {
    applyTo
  }
}
const JsAccordion = createJsAccordion();
export {
  JsAccordion
}