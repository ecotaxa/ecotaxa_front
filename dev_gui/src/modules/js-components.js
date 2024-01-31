import DOMPurify from 'dompurify';
import {
  fetchSettings,
  format_license
} from '../modules/utils.js';
import {
  domselectors,
  css
} from '../modules/modules-config.js';

export class JsComponents {
  items = {};
  async applyTo(element = document) {
    if (!element) return;
    await this.activate(element);
  }
  async activate(element) {
    const items = element.querySelectorAll('.js');
    // dynamic import of necessary modules
    let dynamics = {};
    items.forEach(async item => {
      let actions = item.classList;
      actions.forEach(async (action) => {
        if (action.indexOf('js-') === 0) {
          switch (action) {
            case 'js-privacy':
              const opts = document.querySelectorAll('.RDOpt')
              opts.forEach(opt => opt.addEventListener('click', (e) => {

                fetch('/setprivacy/' + DOMPurify.sanitize(e.target.value), fetchSettings()).then(response => response.text()).then(text => {
                  window.location.reload(true);
                });
              }))

              break;

            case 'js-datatable':
              if (!dynamics.TableComponent) {
                const {
                  TableComponent
                } = await import('../modules/table-component.js');
                dynamics.TableComponent = TableComponent;
              }

              const tbl = new dynamics.TableComponent(item);
              break;
            case 'js-hierarchy':
              break;
            case 'js-autocomplete':
              if (!item.hasOwnProperty('tomselect')) {
                if (!dynamics.JsTomSelect) {
                  const {
                    JsTomSelect
                  } = await
                  import(`../modules/js-tom-select.js`);
                  dynamics.JsTomSelect = JsTomSelect;
                }
                const jsTomSelect = new dynamics.JsTomSelect();
                jsTomSelect.applyTo(item);
              }
              break;
            case 'js-privilege':
              if (!dynamics.ProjectPrivileges) {
                const {
                  ProjectPrivileges
                } = await import('../modules/project-privileges.js');
                dynamics.ProjectPrivileges = ProjectPrivileges;
              }
              const projectPrivileges = new dynamics.ProjectPrivileges();
              break;
            case 'js-tabs':
              if (!dynamics.JsTabs) {
                let {
                  JsTabs
                } = await
                import(`../modules/js-tabs.js`);
                dynamics.JsTabs = JsTabs;
              }
              const jsTabs = new dynamics.JsTabs(item);
              break;
            case 'js-nav':
              const location = window.location.href.split('?');
              const tag = (item.dataset.tag) ? item.dataset.tag : 'ul';
              const links = item.querySelectorAll(tag + ' a');
              links.forEach(link => {
                const href = link.href.split('?');
                if (href[0] === location[0]) {
                  link.parentElement.classList.add(css.active);
                  const root = link.closest('ul');
                  if (root && root.parentElement) {
                    if (root.parentElement.tagName === 'LI') root.parentElement.classList.add(css.active);
                  }
                  return;
                }

              });
              const burger = item.querySelector(domselectors.component.navigation.burgermenu);
              if (!burger) return;
              const target = (burger.dataset.target) ? document.getElementById(burger.dataset.target) : burger.nextElementSibling;
              if (!target) return;
              burger.addEventListener('click', (e) => {
                item.classList.toggle('open');
              });
              break;
            case 'js-import':
              if (!dynamics.JsImport) {
                const {
                  JsImport
                } = await
                import(`../modules/js-import.js`);
                dynamics.JsImport = JsImport;
              }
              const jsImport = new dynamics.JsImport(item);
              break;
            case 'js-my-files':
              if (!dynamics.JsMyFiles) {
                const {
                  JsMyFiles
                } = await
                import(`../modules/js-my-files.js`);
                dynamics.JsMyFiles = JsMyFiles;
              }
              const jsMyFiles = new dynamics.JsMyFiles(item);
              break;
            case 'js-upload':
              if (!dynamics.JsUpload) {
                let {
                  JsUpload
                } = await
                import(`../modules/js-upload.js`);
                dynamics.JsUpload = JsUpload;
              }
              const jsUpload = new dynamics.JsUpload(item);
              break;
            case "js-submit":
              if (!dynamics.FormSubmit) {
                let {
                  FormSubmit
                } = await
                import(`../modules/form-submit.js`);
                dynamics.FormSubmit = FormSubmit;
              }
              const formSubmit = new dynamics.FormSubmit(item);
              break;
            case 'js-captcha':
              if (!dynamics.JsCaptcha) {
                const {
                  JsCaptcha
                } = await import('../modules/js-captcha.js');
                dynamics.JsCaptcha = JsCaptcha;
              }
              const jsCaptcha = new dynamics.JsCaptcha(item);
              jsCaptcha.init();
              break;
            case 'js-alert':
              if (!item.dataset.message) return;
              if (!dynamics.AlertBox) {
                let {
                  AlertBox
                } = await
                import(`../modules/alert-boxes.js`);
                dynamics.AlertBox = AlertBox;
              }
              const alert = new dynamics.AlertBox().build(item);
              break;
            case 'js-notifications':
              const checkNotifs = (tim) => {
                fetch('/gui/jobssummary/', fetchSettings()).then(response => response.text()).then(html => {
                  item.innerHTML = DOMPurify.sanitize(html);
                  if (tim < 30000) tim = 30000;
                  //setTimeout(() => {checkNotifs(tim);}, tim);
                });
              };
              //checkNotifs(30000);
              setTimeout(() => {
                checkNotifs(30000);
              }, 2000);
              break;
            case 'js-accordion':
              if (!dynamics.JsAccordion) {
                let {
                  JsAccordion
                } = await
                import(`../modules/js-accordion.js`);
                dynamics.JsAccordion = JsAccordion;
              }
              item.querySelectorAll(((item.dataset.detail) ? item.dataset.detail : 'detail')).forEach(el => {
                const summary = el.querySelector(((item.dataset.summary) ? item.dataset.summary : 'summary'));
                const jsAccordion = new dynamics.JsAccordion(el, null, null, null, {}, summary);
              })
              break;
            case 'js-license':
              if (!dynamics.format_license) {
                let {
                  format_license
                } = await
                import(`../modules/utils.js`);
                dynamics.format_license = format_license;
              }
              item.innerHTML = dynamics.format_license(DOMPurify.sanitize(item.innerHTML), (item.dataset.withlink));
              break;
            case 'js-observer':
              /*  const observer = new MutationObserver(mutations => {
                  for (const mutation of mutations) {
                    for (let node of mutation.addedNodes) {
                      if (!(node instanceof HTMLElement)) continue;
                      const scripts = node.querySelectorAll('pre[class*="language-"],script');
                      if (scripts.length) {
                        console.log('script');
                        // remove all injected script
                        node.remove();
                      }

                    }

                  }
                  console.log('mutation', mutations)
                  if (mutations.length) this.init(item);
                });
              observer.observe(item, {
                childList: true,
                subtree: true
              });
              this.init(item);*/
              break;
            case 'js-addtags':

              break;
          }
        }
      })
    });
  }
}