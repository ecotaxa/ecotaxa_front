import DOMPurify from 'dompurify';
import {
  fetchSettings,
} from '../modules/utils.js';
import {
  domselectors,
  typeimport,
  models,
} from '../modules/modules-config.js';
let dynamics = {};
export class ActivRequest {
  applyTo(element = document) {
    element = (document || element instanceof HTMLElement) ? element : document.querySelector(element);
    if (!element) return;
    element.querySelectorAll('[data-request]').forEach(item => {
      const ev = item.dataset.event || 'click';
      if (ev === 'load') this.makeRequest(item);
      else item.addEventListener(ev, async (e) => {
        await this.makeRequest(item);
      });
    });

  }

  /* fetch data in a modal - contextual help or any other type */
  async callModal(item) {
    if (!dynamics || !dynamics.ModalContainer) {
      const {
        ModalContainer
      } = await import('../modules/modal-container.js');
      dynamics.ModalContainer = ModalContainer;
    }

    return new dynamics.ModalContainer(item);
  }
  async makeRequest(item) {
    let url, format = (item.dataset.format) ? item.dataset.format : 'html',
      modal,
      callback = null;

    switch (item.dataset.request) {
      case models.help:
        item.dataset.what = models.help;
        modal = await this.callModal(item);
        const modalbox = (modal) ? modal.modal : null;
        if (!modal) return;
        const file = (item.dataset.file) ? ((item.dataset.file !== modalbox.dataset.currentfile) ? item.dataset.file : null) : modalbox.dataset.file;
        const target = (item.dataset.target) ? document.querySelector('#' + item.dataset.target + ' article') : modalbox.querySelector(domselectors.component.modal.mainhelp + " article");
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
            this.applyTo(target);
            //open and open only the selected info
            if (item.dataset.for) modal.modalOpen(item);

          }
        } else if (!file) modal.openContent(item);
        break;

      case models.settings:
        modal = await this.callModal(item);
        if (!modal) return;
        const container = modal.modalcontent ? modal.modalcontent.querySelector('[data-import]') : null;
        if (!container || (item.dataset.key !== container.dataset.import || !container.dataset.table)) {
          url = '/gui/prj/importsettings?' + new URLSearchParams({
            prjid: ((item.dataset.projid) ? item.dataset.projid : ''),
            typeimport: ((item.dataset.key) ? item.dataset.key : typeimport.settings)
          });

          callback = async (html) => {
            const modalcontent = modal.setContent(html);
            if (!dynamics.JsComponents) {
              const {
                JsComponents
              } = await import('../modules/js-components.js');
              dynamics.JsComponents = JsComponents;
            }
            const jsComponents = new dynamics.JsComponents();
            jsComponents.applyTo(modalcontent, modal);

          }
        } else {
          callback = url = null;
        }
        break;

      case models.taxotree:
        modal = await this.callModal(item);
        if (!modal) return;
        /*
          url = '/gui/search/taxotreejson?' + new URLSearchParams({
            id: '#',
            targetid: ((item.dataset.targetid) ? item.dataset.targetid : '')
          })

          const modalcontent = modal.setContent('<h3>Hierarchy</h3><div></div>');

          format = 'json';
          callback = (json) => {
            //  modal.modalOpen();
          }*/
        url = '/search/taxotree?' + +new URLSearchParams({
          target: ((item.dataset.target) ? item.dataset.target : '')
        });
        callback = (response) => {
          console.log(response);
        }
        break;
      default:
        if (item.dataset.href) {
          url = item.dataset.href;
          if (url.substr(0, 1) === '?') {
            url = window.location.href.split('?');
            if (url.length > 1) url = url.join('?') + '&' + item.dataset.href.substr(1);
            else url = url[0] + item.dataset.href;
          }
          console.log('url', url)
          callback = (html) => {
            let content = item.nextElementSibling;
            if (!content) {
              content = document.createElement('div');
              item.parentElement.append(content);

            }
            content.innerHTML = html;
          }
        }
        break;
      case "monitor":
        if (!dynamics.jobMonitor) {
          const {
            jobMonitor
          } = await import('../modules/job-monitor.js');
          dynamics.jobMonitor = jobMonitor;
        }
        return dynamics.jobMonitor(item);
        break;
      case 'privacy':
        url = '/setprivacy/Y';
        callback = (response) => {
          let id = item.id;
          if (id) id = id.replace('Bt', 'Div');
          id = document.getElementById(id);
          if (id) id.remove();
        }
        break;
    }

    this.fetchRequest(format, url, callback);
  }

  makeCloseRequest(item) {
    item.addEventListener(ev, async (e) => {
      const modal = await this.callModal(item);
      if (modal) modal.dismissModal();
    });
  }
  fetchRequest(format, url, callback) {
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
      });
    }
  }


}