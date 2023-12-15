import DOMPurify from 'dompurify';
import {
  models,
  alertconfig,
  domselectors,
  css
} from '../modules/modules-config.js';
import {
  fetchSettings,
  get_catcha_reponse
} from '../modules/utils.js';
const localcss = {
  trigger: {
    show: 'triggershow',
    hide: 'triggerhide'
  },
  icon: 'icon',
  iconeyeslash: 'icon-eye-dark-slash',
  iconeye: 'icon-eye-dark',
  wrap: 'password-wrapper'
};
export class ActivItems {
  /*  activate functions */
  constructor(element = document) {
    if (!element) return;
    let items;
    items = element.querySelectorAll('[data-action]');
    this.activateActions(items);

  }

  async activateActions(items) {
    items.forEach(async (item) => {
      const ev = item.dataset.event || 'click';
      const action = item.dataset.action;
      switch (action) {
        case 'toggle':
          const targets = (item.dataset.target) ? document.querySelectorAll(item.dataset.target) : ((item.nextElementSibling) ? [item.nextElementSibling] : null);
          if (!targets) return;
          const what = item.dataset.what ? item.dataset.what : css.hide;
          const disabled = item.dataset.disabled ? item.dataset.disabled : null;
          const toggle_target = (t) => {
            t.classList.toggle(what);
            if (disabled) {
              t.querySelectorAll(disabled).forEach(el => {
                if (el.disabled) el.removeAttribute('disabled');
                else el.disabled = true;
              });
            };
          }
          item.addEventListener(ev, (e) => {
            targets.forEach(t => {
              toggle_target(t);
            });

            item.classList.toggle(localcss.trigger.show);
            item.classList.toggle(localcss.trigger.hide);
            item.querySelectorAll('i[data-toggle]').forEach(ico => {
              ico.dataset.toggle.split(',').forEach(cl => {
                cl = cl.trim();
                if (cl !== ``) ico.classList.toggle(cl);
              });

            })
          });
          targets.forEach(t => {
            toggle_target(t);
          });
          break;
        case 'gotop':
          item.addEventListener(ev, (e) => {
            e.preventDefault();
            let box = (item.dataset.target) ? document.getElementById(item.dataset.target) : window;
            if (box !== window && box.classList.contains(css.modal)) box = box.querySelector(domselectors.component.modal.modalcontent);
            if (box !== null) box.scrollTo({
              top: 0,
              behavior: 'smooth'
            });
          });
          break;
        case 'wrapeye':
          const wrap = document.createElement('div');
          wrap.classList.add(localcss.wrap);
          const view = document.createElement('i');
          view.classList.add(localcss.icon);
          view.classList.add(localcss.iconeyeslash);
          item.parentNode.insertBefore(wrap, item);
          wrap.append(item);
          wrap.append(view);
          view.addEventListener('click', () => {
            let icoadd, icorem;
            if (item.type === "password") {
              item.type = "text";
              icoadd = localcss.iconeye;
              icorem = localcss.iconeyeslash;
            } else {
              item.type = "password";
              icoadd = localcss.iconeyeslash;
              icorem = localcss.iconeye;
            }
            view.classList.remove(icorem);
            view.classList.add(icoadd);
          })
          break;
        case 'setvalue':
          if (!item.dataset.what || !item.dataset.target) return;
          const dest = (item.dataset.target) ? document.getElementById(item.dataset.target) : null;
          if (!dest) return;
          item.addEventListener(ev, (e) => {
            dest.value = item.dataset.what;
          });
          break;

        case 'add-filters':
          item.addEventListener(ev, async (e) => {
            let inputs = item.closest('.ghost-form');
            if (!inputs) return;
            inputs = inputs.querySelectorAll('input');
            let href = item.href;
            href = href.split('?');
            href[1] = [];
            inputs.forEach(input => {
              if (input.checked) href[1].push(input.name + '=' + input.value);
            });
            item.href = href[0] + '?' + href[1].join('&');
            return true;
          });
          break;
        case 'getfile':
          if (item.dataset.contentlength) return item.dataset.contentlength;
          const enable_link = () => {
            item.classList.remove(css.disabled);
          }
          item.addEventListener('click', (e) => {

            if (item.classList.contains(css.disabled)) {
              e.preventDefault();
              return;
            }
            item.classList.add(css.disabled);

            setTimeout(enable_link, 4000);
            /*response.headers.forEach(function(val, key) {
              console.log(key + ' -> ' + val);
            });
            console.log('resp', response.headers.get('Content-Length'));
            item.dataset.contentlength = response.headers.get('Content-Length');*/
          });
          break;
        case 'dismisscook':
          item.addEventListener('click', (e) => {
            if (item.dataset.cook && item.dataset.value != undefined) {
              const params = new FormData();
              params.append("name", item.dataset.cook);
              params.append("value", item.dataset.value);
              fetch('/gui/setmsgcookie', fetchSettings({
                method: "POST",
                body: params
              }));
            }
            if (item.dataset.dismiss) {
              const target = document.getElementById(item.dataset.dismiss);
              if (target) target.remove();
            }
          });
          break;
        case 'togglecheckall':
          if (!item.dataset.target) return;
          item.addEventListener(((item.dataset.event) ? item.dataset.event : 'change'), (e) => {
            document.querySelectorAll(item.dataset.target).forEach(el => {
              el.toggleAttribute('checked', item.checked);
            });
          });
          break;
        case 'disabled':
          item.addEventListener(((item.dataset.event) ? item.dataset.event : 'click'), (e) => {
            e.preventDefault();
          });
          item.classList.add('disabled');
          break;
        case 'viewall':
          const target = item.closest(item.dataset.target);
          if (target === null) return;
          item.addEventListener('click', (e) => {
            if (!target.classList.contains('viewall') && target.firstChild.offsetHeight <= target.offsetHeight) return;
            target.classList.toggle('viewall');
          })
          break;
      }
    });
  }


}