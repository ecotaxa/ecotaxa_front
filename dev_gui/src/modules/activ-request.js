import DOMPurify from 'dompurify';
import {
  fetchSettings,
  unescape_html,
  create_box
} from '../modules/utils.js';
import {
  domselectors,
  typeimport,
  models,css
} from '../modules/modules-config.js';
let dynamics = {};
import {
  ModuleEventEmitter
} from '../modules/module-event-emitter.js';
function createActivRequest() {
  function applyTo(element = document) {
    element = (document || element instanceof HTMLElement) ? element : document.querySelector(element);
    if (!element) return;
    element.querySelectorAll('[data-request]').forEach(item => {
      const ev = item.dataset.event || 'click';
      if (ev === 'load') makeRequest(item);
      else item.addEventListener(ev, async (e) => {
        if (item.tagName.toLowerCase() === "a") e.preventDefault();
        await makeRequest(item);
      });
    });

  }
  /* fetch data in a modal - contextual help or any other type */
  async function callModal(item) {
    if (!dynamics || !dynamics.ModalContainer) {
      const {
        ModalContainer
      } = await import('../modules/modal-container.js');
      dynamics.ModalContainer = ModalContainer;
    }

    return new dynamics.ModalContainer(item);
  }
  async function makeRequest(item) {
    let url, format = (item.dataset.format) ? item.dataset.format : 'html',
      modal,
      callback = null;

    switch (item.dataset.request) {
      case models.help:
        item.dataset.what = models.help;
        modal = await callModal(item);
        const modalbox = (modal) ? modal.modal : null;
        if (!modal || !modalbox) return;
        if (item.dataset.close) return;
        const file = (item.dataset.file) ? ((item.dataset.file !== modalbox.dataset.currentfile) ? item.dataset.file : null) : modalbox.dataset.file;
        const target = (item.dataset.target) ? document.getElementById(item.dataset.target) : modalbox.querySelector(domselectors.component.modal.mainhelp + ' > div');
        if (!target) return;
        if (target && file) {
          if (!dynamics.ActivItems) {
            const {
              ActivItems
            } = await import('../modules/activ-items.js');
            dynamics.ActivItems = ActivItems;
          }
          const params = {
            partial: true,
            title: (item.dataset.title && item.dataset.title!=='')?item.dataset.title: item.textContent,
          };
          url = '/gui/help/' + file + '?' +
            new URLSearchParams(params);
          callback = (html) => {
            html = html instanceof HTMLElement ? html.outerHTML : html;
            modalbox.dataset.currentfile = file;
            target.innerHTML = html;
            applyTo(target);
            dynamics.ActivItems.applyTo(target);
            //open and open only the selected info
            if (item.dataset.for) modal.modalOpen(item);
          }
        } else if (!file || file === undefined) {
          if (item.dataset.for) modal.modalOpen(item);
        }
        break;

      case models.settings:
        modal = await callModal(item);
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
            dynamics.JsComponents.applyTo(modalcontent);

          }
        } else {
          callback = url = null;
        }
        break;
      case models.taxotree:
        modal = await callModal(item);
      case models.commonserver:
        modal = (modal) ? modal : (item.dataset && item.dataset.where) ? document.getElementById(item.dataset.where) : null;
        if (!modal) return;
        const modalcontent = (modal.modalcontent) ? modal.modalcontent : modal;
        let options = JSON.parse(JSON.stringify(item.dataset));
        if (item.dataset.request === models.commonserver) {
          options.api_parameters = {
            rootname: (options.rootname) ? options.rootname : 'Server'
          };
          options.entry = {
            icons: {
              image: 'img',
              document: 'doc'
            },
          };
          item.dataset.import = true;

        } else options.trigger = modal.trigger;
        delete options.request;
        if (!dynamics.jsTree) {
          let {
            JsTree
          } = await
          import(`../modules/js-tree.js`);
          dynamics.JsTree = JsTree;
        }
        item.jstree = dynamics.JsTree(modalcontent, options);
        callback = null;
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
      case "taxolineage":
        url = "/api/taxon_set/query?ids=" + item.dataset.value;

        callback = (response) => {
          const lineage = response[0].lineage;
          const id_lineage = response[0].id_lineage;
          /* var click_lineage = lineage.map(function (txo, i) {
               if (i > 0) {
                   return "<a href='#' data-tgt='" + taxoid + "' data-txoid='" + id_lineage[i] + "' >" + txo + "</a>";
               } else {
                   // The base taxon itself, no use making it selectable
                   return txo;
               }
           });*/
        }

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
      default:
        if (item.dataset.href) {
          url = item.dataset.href;
          if (url.substr(0, 1) === '?') {
            url = window.location.href.split('?');
            if (url.length > 1) url = url.join('?') + '&' + item.dataset.href.substr(1);
            else url = url[0] + item.dataset.href;
          } let content =item.nextElementSibling;
            if (!content) {
           content = document.createElement('div');
            item.parentElement.append(content);            }
            else content.innerHTML="";
            content.classList.add(css.wait);
            const tab=item.closest(domselectors.component.tabs.tab);
          callback = async (html) => {
            content.classList.remove(css.wait);
            content.innerHTML = html;
             if(tab) tab.classList.remove(css.hide);
              if (!dynamics.JsComponents) {
              const {
                JsComponents
              } = await import('../modules/js-components.js');
              dynamics.JsComponents = JsComponents;
            }
             dynamics.JsComponents.applyTo(content);
             item.classList.add(css.hide);
        }}
        break;

    }

    fetchRequest(format, url, callback);
  }

  function makeCloseRequest(item) {
    item.addEventListener(ev, async (e) => {
      const modal = await callModal(item);
      if (modal) modal.dismissModal();
    });
  }

  function fetchRequest(format, url, callback) {
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
  return {
    applyTo,
    makeRequest
  }
}
const ActivRequest = createActivRequest();
export {
  ActivRequest
};