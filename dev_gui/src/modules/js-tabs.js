import DOMPurify from 'dompurify';
import {
  css,
  domselectors
} from '../modules/modules-config.js';
domselectors.shared = '[data-shared]';

function createJsTabs() {
  let togglewhat, toggledisable, toggleshared;

  function applyTo(item) {
    if (!item.jstabs) {
      let btns = item.querySelectorAll(domselectors.component.tabs.tabcontrol);
      if (btns.length === 0) {
        btns = item.querySelectorAll(((item.dataset.selector) ? item.dataset.selector : 'legend'));

      }
      toggledisable = (item.dataset.toggledisable) ? true : false;
      togglewhat = (item.dataset.togglewhat) ? item.dataset.togglewhat : null;
      toggleshared = (item.dataset.toggleshared) ? true : false;
      let l = 0;
      btns.forEach((btn, index) => {
        const target = (btn.dataset.target) ? item.querySelector('#' + btn.dataset.target) : btn.closest(domselectors.component.tabs.tab);
        if (!target) return;
        const ev = (item.dataset.event) ? item.dataset.event : 'click';
        btn.style.left = l + 'px';


        l += parseInt(btn.offsetWidth) + 20;
        btn.addEventListener(ev, (e) => {
          if (e.currentTarget.disabled === true) {
            e.preventDefault();
            return;
          }
          const oldactive = item.dataset.selector ? target.parentElement.querySelector('.' + css.active) : item.querySelector(domselectors.component.tabs.tab + '.' + css.active);
          if (oldactive !== null) {
            oldactive.classList.remove(css.active);
            toggleTab(oldactive, false);
          }
          target.classList.add(css.active);
          toggleTab(target, true);
        });
        if ((index === 0 && target.parentElement.querySelectorAll('.' + css.active).length === 0) || target.classList.contains(css.active)) {
          target.classList.add(css.active);
          toggleTab(target, true);
        } else {
          target.classList.remove(css.active);
          toggleTab(target, false);
        }
      });
      if (!item.dataset.toggle) toggleDisplayListener(item, btns);
      item.jstabs = true;
    }
  }

  function toggleTab(tab, show) {
    let what = (togglewhat) ? document.getElementById(togglewhat) : null;
    let tabcontents = tab.querySelectorAll(domselectors.component.tabs.tabcontent);
    if (tabcontents.length === 0) tabcontents = [tab];
    tabcontents.forEach(tabcontent => {
      if (show === true) tabcontent.classList.remove(css.hide);
      else if (!tab.classList.contains(css.active)) tabcontent.classList.add(css.hide);
      if (toggledisable === true) {
        tabcontent.querySelectorAll('input, select, button, textarea').forEach(el => {
          if (show) {
            el.disabled = false;
            if (el.dataset.checked) {
              el.checked = el.dataset.checked;
              delete el.dataset.checked;
            }
          } else {
            el.disabled = true;
            if (el.checked) {
              el.dataset.checked = el.checked;
              el.removeAttribute('checked');
            }
          }
        });
        if (what) what.value = tabcontent.dataset.what;
        if (show) {
          const form = tab.closest('form');
          if (tabcontent.dataset.path && form !== null) {
            form.setAttribute('action', tabcontent.dataset.path);
            // only used in export - to do  generic

            window.history.replaceState({
              additionalInformation: 'Updated by jsTabs'
            }, document.title, window.location.origin + tabcontent.dataset.path + window.location.search);
          }
          if (toggleshared) {
            // for elements shared between tabs and displayed on tab activation
            tab.querySelectorAll(domselectors.shared).forEach(shared => {
              const sharedcontent = tab.parentElement.querySelector('#' + shared.dataset.shared);
              sharedcontent.parent = sharedcontent.parentElement;

              if (show) {
                sharedcontent.classList.remove(css.hide);
                shared.append(sharedcontent);
                replaceLabels(shared, sharedcontent);
              } else {
                sharedcontent.classList.add(css.hide);
                if (sharedcontent.parent) {
                  sharedcontent.parent.append(sharedcontent);
                  delete sharedcontent.parent;
                }
              }
            });
          }
        }
      }
    });
  }

  function replaceLabels(shared, sharedcontent) {
    // sort of a hack to set every option and label in import my files
    const separator = '|';
    const replaces = (shared.dataset.replaces) ? shared.dataset.replaces.split(separator) : null;
    const values = (shared.dataset.values) ? shared.dataset.values.split(separator) : null;
    if (replaces !== null && values !== null) {
      replaces.forEach((rep, index) => {
        let target = sharedcontent.querySelector(rep);
        if (target) target.innerHTML = DOMPurify.sanitize(values[index]);
        else {
          target = sharedcontent.querySelector('[data-' + rep + ']');
          if (target) target.dataset[rep] = DOMPurify.sanitize(values[index]);
        }
      });
    }
  }

  function toggleDisplayListener(item, btns) {
    // flat/ tabs display
    const dismiss = item.querySelector('[data-dismiss="tabs"]');
    const toggle_tab = ((index, btn, show) => {
      btn.disabled = show;
      toggleTab(btn.closest(domselectors.component.tabs.tab), show);
    })
    if (dismiss) dismiss.addEventListener('click', (e) => {
      const icon = item.querySelector('.tabs-display');
      btns.forEach((btn, index) => toggle_tab(index, btn, (item.classList.contains(css.component.tabs.name))));
      item.classList.toggle(css.component.tabs.name);
      icon.classList.toggle('expand');
      icon.classList.toggle('shrink');
    });
  }
  return {
    applyTo
  }
}
const JsTabs = createJsTabs();
export {
  JsTabs
}