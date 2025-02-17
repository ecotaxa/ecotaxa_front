import DOMPurify from 'dompurify';
import {
  AlertBox
} from '../modules/alert-box.js';
import {
  models,
  domselectors,
  css
} from '../modules/modules-config.js';
import {
  fetchSettings,
  get_catcha_reponse,
  decode_HTMLEntities
} from '../modules/utils.js';
import {
  export_html2word
} from '../modules/export-html2word.js';
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

function createActivItems() {
  /*  activate function */
  function applyTo(element = document) {
    element = (document || element instanceof HTMLElement) ? element : document.querySelector(element);
    if (!element) return;
    element.querySelectorAll('[data-action]').forEach(async (item) => {
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
          item.classList.add(css.disabled);
          break;
        case 'discard':
          const inputs = (item.dataset.target) ? item.dataset.target.split(',') : null;
          if (inputs === null) return;
          const triggers = (item.dataset.trigger) ? item.parentElement.querySelectorAll('[name="' + item.dataset.trigger + '"]') : null;
          if (triggers === null) return;
          triggers.forEach(trigger => trigger.addEventListener('change', (e) => {
            const targetvalue = parseInt(e.target.value);
            inputs.forEach(input => {
              input = input.split('|');
              const value = (input.length) ? input[1] : 0;
              input = input[0];
              item.closest('fieldset').querySelectorAll('[data-name="' + input + '"]').forEach(box => {
                const els = box.querySelectorAll('input[name="' + input + '"]');
                if (targetvalue === 1 && e.target.checked) {
                  box.dataset.keep = (box.querySelector('input[name="' + input + '"]:checked')) ? box.querySelector('input[name="' + input + '"]:checked').value : null;
                  box.classList.add(css.disabled);
                  els.forEach(el => {
                    if (el.value === value) el.checked = true;
                    else el.checked = false;
                  });
                } else if (box.classList.contains(css.disabled)) {
                  box.classList.remove(css.disabled);
                  els.forEach(el => {
                    if (box.dataset.keep === el.value) el.checked = true;
                    else if (box.dataset.keep) el.checked = false;
                  });
                }

              });
            });
          }));
          break;
        case 'confirm':
          item.addEventListener((item.dataset.event) ? item.dataset.event : 'click', async (e) => {
            e.preventDefault();
            let rep = false;
            const message = (item.dataset.content) ? item.dataset.content : `Do you really want to ` + item.textContent + '?';
            const options = (item.href) ? {
              href: item.href
            } : {};
            rep = await AlertBox.addConfirm(message, options);
            if (rep === true && item.form) {
              if (item.form.formsubmit) {
                item.form.formsubmit.submitForm();
              } else item.form.submit();
            }
            return rep;
          });
          break;
        case 'astext':
          const article = (item.dataset.target) ? document.getElementById(item.dataset.target) : item.parentElement.querySelector('article');
          if (article) {
            item.addEventListener((item.dataset.event) ? item.dataset.event : 'click', (e) => {
              export_html2word(article, item.parentElement);
            });
          }
          break;
      }

    });
  }
  return {
    applyTo
  }

}
const ActivItems = createActivItems();
export {
  ActivItems
}