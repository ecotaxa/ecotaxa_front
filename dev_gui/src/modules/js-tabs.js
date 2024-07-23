import {
  css,
  domselectors
} from '../modules/modules-config.js';
export class JsTabs {
  constructor(item, options = {}) {
    if (!item.jstabs) {
      let btns = item.querySelectorAll(domselectors.component.tabs.tabcontrol);
      if (btns.length === 0) {
        btns = item.querySelectorAll(((item.dataset.selector) ? item.dataset.selector : 'legend'));

      }

      this.toggledisable = (item.dataset.toggledisable) ? true : false;
      this.togglewhat = (item.dataset.togglewhat) ? item.dataset.togglewhat : null;
      let l = 0;
      btns.forEach((btn, index) => {
        const target = (btn.dataset.target) ? item.querySelector('#' + btn.dataset.target) : btn.closest(domselectors.component.tabs.tab);
        if (!target) return;
        const ev = (item.dataset.event) ? item.dataset.event : 'click';
        btn.style.left = l + 'px';
        if (index === 0 && target.parentElement.querySelectorAll('.' + css.active).length === 0) {
          target.classList.add(css.active);
          this.toggleTab(target, true);

        } else this.toggleTab(target, target.classList.contains(css.active));
        l += parseInt(btn.offsetWidth) + 20;
        btn.addEventListener(ev, (e) => {
          if (e.currentTarget.disabled === true) {
            e.preventDefault();
            return;
          }
          const oldactive = item.dataset.selector ? target.parentElement.querySelector('.' + css.active) : item.querySelector(domselectors.component.tabs.tab + '.' + css.active);
          if (oldactive !== null) {
            oldactive.classList.remove(css.active);
            this.toggleTab(oldactive, false);
          }
          target.classList.add(css.active);
          this.toggleTab(target, true);
        });
      })
      if (!item.dataset.toggle) this.toggleDisplayListener(item, btns);
      item.jstabs = this;
    }
    return item.jstabs;
  }

  toggleTab(tab, show) {
    let what = (this.togglewhat) ? document.getElementById(this.togglewhat) : null;

    let tabcontents = tab.querySelectorAll(domselectors.component.tabs.tabcontent);
    if (tabcontents.length === 0) tabcontents = [tab];
    tabcontents.forEach(tabcontent => {
      if (show === true) tabcontent.classList.remove(css.hide);
      else if (!tab.classList.contains(css.active)) tabcontent.classList.add(css.hide);
      if (this.toggledisable === true) {
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
        }
      }
    });
  }
  toggleDisplayListener(item, btns) {
    // flat/ tabs display
    const dismiss = item.querySelector('[data-dismiss="tabs"]');
    const toggle_tab = ((index, btn, show) => {
      btn.disabled = show;
      this.toggleTab(btn.closest(domselectors.component.tabs.tab), show);
    })
    if (dismiss) dismiss.addEventListener('click', (e) => {
      const icon = item.querySelector('.tabs-display');
      btns.forEach((btn, index) => toggle_tab(index, btn, (item.classList.contains(css.component.tabs.name))));
      item.classList.toggle(css.component.tabs.name);
      icon.classList.toggle('expand');
      icon.classList.toggle('shrink');
    });
  }
}