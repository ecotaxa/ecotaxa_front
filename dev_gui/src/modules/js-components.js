import DOMPurify from 'dompurify';
import {
  AlertBox
} from "../modules/alert-boxes.js";
import {
  ProjectPrivileges
} from "../modules/project-privileges.js";

import {
  TableComponent
} from '../modules/table-component.js';

import {
  JsTomSelect
} from "../modules/js-tom-select.js";

import {
  FormSubmit,
} from "../modules/form-submit.js";
import {
  fetchSettings
} from '../modules/utils.js';
export class JsComponents {
  async apply(element = document) {
    if (!element) return;
    await this.activate(element);
  }
  async activate(element) {
    const items = element.querySelectorAll('.js');

    items.forEach(async item => {
      let actions = item.classList;
      actions.forEach(async (action) => {
        if (action.indexOf('js-') === 0) {
          switch (action) {
            /*case "js-redir":
              if (document.querySelector('form')) document.querySelector('form').disabled = true;
              setTimeout(() => {
                const url = DOMPurify.sanitize(item.dataset.redir);
                history.replaceState(null, document.title, window.location.href);
                window.location.href = url;
              }, 3000);
              break;*/
            case 'js-privacy':
              const opts = document.querySelectorAll('.RDOpt')
              opts.forEach(opt => opt.addEventListener('click', (e) => {
                fetch('/setprivacy/' + DOMPurify.sanitize(e.target.value), fethSettings()).then(response => response.text()).then(text => {
                  //text = DOMPurify.sanitize(text);
                  location.reload(true)
                })
              }))
              break;
            case 'js-datatable':
              const tbl = new TableComponent(item);
              break;

            case 'js-hierarchy':
              break;
            case 'js-snap':
              // init modalcontainer with snap properties ( for scroll / pause on paragraphes )
              const modalcontainer = document.querySelector('.modal-container');
              if (modalcontainer === null) return;
              const snapmodal = modalcontainer.querySelector('.modal');
              if (snapmodal === null) return (['snap-y', 'snap-mandatory']).forEach(cl => (snapmodal.classList.add(cl)));
              const siblings = modalcontainer.querySelectorAll('details');

              siblings.forEach(sibling => {
                (['snap-always', 'snap-top']).forEach(cl => {
                  sibling.classList.add(cl);
                })
              })

              break;
            case 'js-autocomplete':
              const jsTomSelect = new JsTomSelect();

              jsTomSelect.apply(item);
              break;
            case 'js-privilege':
              // add member line clone of last data-block="member"

              const projectPrivileges = new ProjectPrivileges();
              const handleprivileges = async () => {
                return await projectPrivileges.submitPrivileges();
              }
              //remove deleted , clean && validate datas , format names before sending the form
              const form = item.closest('form');
              const formSubmit = new FormSubmit(form);
              formSubmit.addHandler(handleprivileges);

              break;
            case 'js-tabs':
              let btns = item.querySelectorAll('.tab-control');
              if (btns.length === 0) {
                btns = item.querySelectorAll('legend');
              }
              let l = 0;
              btns.forEach((btn, index) => {
                const target = (btn.dataset.target) ? item.querySelector('#' + btn.dataset.target) : btn.closest('.tab');
                if (!target) return;
                const show_content = (tab, show) => {
                  const tabcontents = tab.querySelectorAll('.tab-content');
                  tabcontents.forEach(tabcontent => {
                    if (show === true) tabcontent.classList.remove('hide');
                    else tabcontent.classList.add('hide');
                  });
                };
                btn.style.left = l + 'px';
                if (index === 0) {
                  target.classList.add('active');
                  show_content(target, true);
                } else show_content(target, false);
                l += parseInt(btn.offsetWidth) + 20;
                btn.addEventListener('click', (e) => {
                  if (e.currentTarget.disabled === true) {
                    e.preventDefault();
                    return;
                  }
                  const oldactive = target.parentElement.querySelector('.tab.active');

                  if (oldactive !== null) {
                    oldactive.classList.remove('active');
                    show_content(oldactive, false);
                  }
                  target.classList.add('active');
                  show_content(target, true);
                });

              })
              const dismiss = item.querySelector('[data-dismiss="tabs"]');
              if (dismiss) dismiss.addEventListener('click', (e) => {
                let icon;
                if (item.classList.contains('js-tabs')) {
                  item.classList.remove('js-tabs');
                  btns.forEach(btn => btn.disabled = true);
                  icon = item.querySelector('.icon-arrow-pointing-out');
                  icon.classList.remove('icon-arrow-pointing-out');
                  icon.classList.add('icon-arrow-pointing-in');
                } else {
                  item.classList.add('js-tabs');
                  btns.forEach(btn => btn.disabled = false);
                  icon = item.querySelector('.icon-arrow-pointing-in');
                  icon.classList.remove('icon-arrow-pointing-in');
                  icon.classList.add('icon-arrow-pointing-out');
                }
              });

              break;
            case 'js-alerts':
              if (!item.dataset.message) return;
              const alert = new AlertBox(item).build(DOMPurify.sanitize(item.dataset.message), ((item.dataset.type) ? DOMPurify.sanitize(item.dataset.type) : 'warning'), item, {
                dismissible: (item.dataset.dismissible) ? item.dataset.dismissible : true,
                insertafter: true,
                codemessage: item.dataset.message,
                callback: () => {
                  item.remove();
                }
              });
              break;
              break;
            case 'js-notifications':
              const checkNotifs = (tim) => {
                fetch('/gui/jobssummary', fetchSettings()).then(response => response.text()).then(html => {
                  item.innerHTML = DOMPurify.sanitize(html);
                  /*if (tim < 600000) tim = 60000;
                  setTimeout(() => {
                    checkNotifs(tim);
                  }, tim);*/
                });
              }
              checkNotifs(60000);
              break;
            case 'js-search-autocomplete':
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
                  if (mutations.length) this.apply(item);
                });
              observer.observe(item, {
                childList: true,
                subtree: true
              });
              this.apply(item);*/
              break;
          }
        }
      })
    });
  }
}