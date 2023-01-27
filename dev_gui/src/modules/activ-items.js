import DOMPurify from 'dompurify';
import {
  alertconfig,
  AlertBox
} from "../modules/alert-boxes.js";
import {
  ModalContainer
} from "../modules/modal-container.js";
import {
  FormSubmit
} from "../modules/form-submit.js";

import {
  JsComponents
} from '../modules/js-components.js';
import {
  fetchSettings,
  className
} from '../modules/utils.js';
import {
  models
} from '../modules/modules-config.js';
export class ActivItems {
  /* apply activate functions */
  apply(element = document) {
    if (!element) return;
    let items;
    items = element.querySelectorAll('[data-action]');
    this.activateActions(items);
    // alerts
    items = element.querySelectorAll(alertconfig.selector + ' ' + alertconfig.dismiss_selector, alertconfig.confirm_selector);
    this.activateDismisses(items);
  }

  async activateActions(items) {
    let modal;
    items.forEach(async (item) => {
      const ev = item.dataset.event || 'click';

      //e.stopPropagation();
      const action = item.dataset.action;
      switch (action) {
        case 'submit':
          item.addEventListener(ev, async (e) => {
            e.preventDefault();
            let form = (item.dataset.target) ? document.querySelector(item.dataset.target) : item.closest('form');
            if (!form) return;
            const formSubmit = new FormSubmit(form);
            const yessubmit = await formSubmit.submitHandler();
            if (formSubmit && yessubmit) form.submit();
          });
          break;
        case 'gotop':
          item.addEventListener(ev, async (e) => {
            e.preventDefault();
            let box = (item.dataset.target) ? document.querySelector('#' + item.dataset.target) : window;
            if (box !== window && box.classList.contains('modal')) box = box.querySelector('.modal-content');
            if (box !== null) box.scrollTo({
              top: 0,
              behavior: 'smooth'
            });
          });
          break;
        case 'dismiss':
          item.addEventListener(ev, async (e) => {
            e.preventDefault();
            const todismiss = (item.dataset.target) ? item.closest(item.dataset.target) : item.parentElement;
            if (todismiss) todismiss.remove();
          });
          break;
        case 'add-filters':
          item.addEventListener(ev, async (e) => {
            let inputs = item.closest('.ghost-form');
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
        case 'close-request':
          item.addEventListener(ev, async (e) => {
            modal = new ModalContainer(item);
            if (modal) modal.dismissModal();
          });
          break;
        case 'request':
          const make_request = (e, item) => {
            let url, format = (item.dataset.format) ? item.dataset.format : 'html',
              callback = null;
            switch (item.dataset.what) {
              case models.help:
                modal = new ModalContainer(item);
                const modalbox = modal.modal;
                if (!modalbox) return;
                const file = (item.dataset.file) ? ((item.dataset.file !== modalbox.dataset.currentfile) ? item.dataset.file : null) : modalbox.dataset.file;
                const target = (item.dataset.target) ? document.querySelector('#' + item.dataset.target + ' article') : ((modal) ? modal.getBySelector("#main-help article") : ((item.closest('.modal-help')) ? item.closest('.modal-help').querySelector('#main-help article') : null));
                if (!target) return;
                if (target && file) {
                  url = '/gui/help/' + file + '?' +
                    new URLSearchParams({
                      partial: true
                    });
                  callback = (html) => {
                    html = html instanceof HTMLElement ? html.outerHTML : html;
                    modalbox.dataset.currentfile = file;
                    target.innerHTML = html;
                    this.apply(target);
                    //open and open only the selected info
                    if (item.dataset.for) modal.modalOpen(item);

                  }
                } else if (file === null) modal.openContent(item);
                break;
              case models.settings:
                modal = new ModalContainer(item);
                const container = modal.modalcontent ? modal.modalcontent.querySelector('[data-import]') : null;

                if (!container || (item.dataset.key !== container.dataset.import || !container.dataset.table)) {
                  url = '/gui/prj/importsettings?' + new URLSearchParams({
                    prjid: ((item.dataset.projid) ? item.dataset.projid : ''),
                    typeimport: ((item.dataset.key) ? item.dataset.key : 'settings')
                  });

                  callback = (html) => {
                    const modalcontent = modal.setContent(html);
                    const jsComponents = new JsComponents();
                    jsComponents.apply(modalcontent, modal);
                  }
                } else {
                  callback = url = null;
                }
                break;
              case models.taxo:
                modal = new ModalContainer(item);
                e.preventDefault();
                url = '/gui/search/taxotreejson?' + new URLSearchParams({
                  id: '#',
                  targetid: ((item.dataset.targetid) ? item.dataset.targetid : '')
                })

                const modalcontent = modal.setContent('<h3>Hierarchy</h3><div></div>');

                format = 'json';
                callback = (json) => {
                  //  modal.modalOpen();
                }
                break;

            }
            if (!callback) return;

            if (format === 'json') {
              fetch(url, fetchSettings()).then(response => response.json()).then(json => {
                callback(json);
              });
            } else {
              fetch(url, fetchSettings()).then(response => response.text()).then(html => {
                html = DOMPurify.sanitize(html);
                callback(html);
              }).catch(err => {
                console.log('request', err);
              })
            }
          }
          item.addEventListener(ev, (e) => {
            make_request(e, item);
          });
          break;
        case 'alert-confirm':
          item.addEventListener(ev, () => {
            const alert = new AlertBox().build((item.dataset.message ? item.dataset.message : alertconfig.warning), 'confirm', (item.id ? item.id : null), {
              dismissible: true,
              callback: () => {
                if (item.dataset.unlock && item.dataset.unlock === true) item.disabled = false;
              }
            });
          });
          break;
      }
    });
  }
  /* dismissable alerts */
  activateDismisses(items) {
    if (items.length === 0) return;
    items.forEach(item => {
      item = item.closest(alertconfig.selector);
      if (item) {
        item = new AlertBox(item);
        if (item.box.classList.contains(className(alertconfig.confirm_selector))) item.waitForAnswer();
        else item.dismissListener();
      }
    });
  }

}