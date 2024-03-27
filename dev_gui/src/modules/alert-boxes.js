import DOMPurify from 'dompurify';
import {
  generate_uuid,
  fetchSettings
} from '../modules/utils.js';
import {
  alertconfig,
  css
} from '../modules/modules-config.js';

let instance = null;
// alertbox one instance by page - display alertbox with uniqueid
export class AlertBox {
  separator = ' | ';
  allowedtypes = [];
  url = {
    translation: '/gui/i18n',
    template: '/gui/alertbox'
  }
  i18nmessages;
  alertconfig = alertconfig;
  constructor(element = document) {
    // will be used to load only part of translated messages
    this.allowedtypes = Object.values(this.alertconfig.types);
    return new Promise((resolve, reject) => {
      this.getI18nmessages();
      this.applyTo(element);
      if (!instance) instance = this;
      resolve(instance);
      reject(null);
    });
  }
  async getI18nmessages() {
    const response = await fetch(this.url.translation, fetchSettings);
    this.i18nmessages = await response.json();
  }
  applyTo(element) {
    let items = [...element.querySelectorAll(alertconfig.selector), ...element.querySelectorAll(alertconfig.domselectors.action)];
    const build_alert = (item) => {
      const type = (item.dataset.action === alertconfig.confirm_selector.substr(1)) ? alertconfig.types.confirm : ((item.dataset.type) ? item.dataset.type : alertconfig.types.warning);
      const options = { ...{
          dismissible: (item.dataset.dismissible) ? item.dataset.dismissible : true,
          insertafter: (item.dataset.action) ? false : true,
          inverse: (item.classList.contains(alertconfig.css.inverse)) ? true : ((item.dataset.action) ? false : true),
          codeid: true,
          message: (item.dataset.message),

        },
        ...item.dataset
      }
      return this.activateAlert(type, item, options);
    }

    items.forEach(item => {
      const options = item.dataset;

      if (options.event) {
        options.href = options.href ? options.href : item.href;
        item.addEventListener(options.event, (e) => {
          e.preventDefault();
          return build_alert(item);
        });
      } else build_alert(item);
    });
  }

  createAlert(type, message, parent = null, options = {}) {
    options = { ...{
        title: ``,
        dismissible: true,
        insertafter: false,
        inverse: true,
        codeid: true,
        small: true,
        inset: false,
        callback: null,
        callback_cancel: null,
      },
      ...options
    }
    parent = (parent instanceof HTMLElement) ? parent : this.getBoxById(parent);
    parent = (parent) ? parent : document.querySelector('main');
    const i18nmessages = this.i18nmessages;
    const codemessage = message;
    let box = this.getBoxById(codemessage);
    if (box == null) {
      message = (i18nmessages[message]) ? i18nmessages[message] : message;
      if (type === 'confirm') {
        message = ` <div class=" block overscroll-none text-sm font-semi-bold"><i class="icon icon-alert"></i><span>${message}</span></div><div class="btn-group flex justify-end"><button class="button text-base is-ok"  value=true>${(options.buttons && options.buttons.ok && options.buttons.ok.text)?options.buttons.ok.text:i18nmessages.ok}</button><button class="button is-cancel text-base"  value=false>${(options.buttons && options.buttons.cancel && options.buttons.cancel.text)?options.buttons.cancel.text:i18nmessages.cancel}</button></div>`;
      } else message = `<div class="inline-block mx-3">${message}</div>`;
      const title = `<strong class="text-sm font-bold">${((i18nmessages[type]) ? i18nmessages[type]+` `:``) + options.title}</strong>`;
      const id = generate_uuid();
      const button = (options.dismissible) ? `<div class="close" data-dismiss="${id}" aria-label="${i18nmessages.close}"><i class="icon-sm icon-cancel cursor-pointer"></i></div>` : ``;
      message = `<div id=${id} data-message="${codemessage}" class="alert ${type} ${(options.small)?`text-xs`:``} ${ (options.inverse===true)?`inverse`:``} ${(options.inset)?`md:w-3/4 lg:w-1/2 mx-2`:``} ${(options.small)?`mt-1 text-sm`:``}" role="alert"><i class="icon"></i>${title}${message}${button}</div>`
      parent.insertAdjacentHTML(((options.insertafter) ? 'afterend' : 'beforebegin'), message);
      const box = document.getElementById(id);
      if (box) return this.activateAlert(type, box, options);
    } else {
      // alert exists animate it
      this.refreshAlert(box);
    }

  }

  renderMessage(message) {
    // message = {type:required,string, content:required string, date: string,dismissible:bool,  duration:int, inverse:bool}
    let box = this.getBoxById(message.content);
    if (box) return this.refreshMessage(box);
    const i18nmessages = this.i18nmessages;
    box = document.createElement('div');
    box.id = generate_uuid();
    box.dataset.message = message.content;
    if (message.hasOwnProperty('duration') && message.duration) box.dataset.duration = message.duration;
    box.classList.add(message.type);
    if (message.hasOwnProperty('cookiename')) box.dataset.cook = message.type + message.cookiename;
    if (message.hasOwnProperty('date')) box.dataset.value = message.date;
    if (message.hasOwnProperty('inverse') && message.inverse) box.classList.add('inverse');
    const showall = `<div class="showall hide" data-title="${i18nmessages.viewfull}"><i class="icon iconview"></i></div>`;
    let html = `<div class="content"><div class="signal hidden sm:block"><i class="icon"></i></div><div class="message"><strong class="type">${(i18nmessages.alerttype && i18nmessages.alerttype[message.type])?i18nmessages.alerttype[message.type]:message.type}</strong>${(i18nmessages[message.content]) ? i18nmessages[message.content] : message.content}</div>`;
    if (message.dismissible) html += `<div class="close" data-dismiss="${box.id}"  aria-label="${i18nmessages.close}"><i class="icon-sm icon-cancel cursor-pointer"></i></div>`;
    box.insertAdjacentHTML('afterbegin', html + `${showall}</div>`);
    this.alertMessage(box, true);
  }

  activateAlert(type, box, options) {

    box = (box instanceof HTMLElement) ? box : this.getBoxById(box);
    if (box === null) return;

    if (options.duration) {
      setTimeout(() => {
        this.dismissAlert(box);
      }, options.duration);
    } else if (options.dismissible) this.dismissListener(box);
    if (type === alertconfig.types.confirm) {
      let callback = (options.callback) ? options.callback : null,
        callback_cancel = (options.callback_cancel) ? (options.callback_cancel) : null;
      if (options.href) callback = () => {
        fetch(options.href + '&' + new URLSearchParams({
          partial: true
        }), fetchSettings()).then(response => response.text()).then(response => {
          let responsebox = box.querySelector(alertconfig.domselectors.message);
          if (!responsebox) {
            responsebox = document.createElement('div');
            box.classList.add(alertconfig.domselectors.message.substr(1));
            box.append(responsebox);
          };
          responsebox.innerHTML = DOMPurify.sanitize(response);
          const btns = box.querySelector(alertconfig.domselectors.buttons.group);
          if (btns) {
            btns.innerHTML = `< button class = "button is-close text-base"  value = false >${this.i18nmessages.close} </button>`;
            btns.querySelector('.is-close').addEventListener('click', (e) => {
              this.dismissAlert(box);
            });
          }
          box.dataset.refresh = true;
        });
      };

      return this.waitForAnswer(box, callback, callback_cancel);
    }
    return true;
  }
  messagesContainer() {
    let item = document.getElementById(this.alertconfig.domselectors.alertmessages.substr(1));
    if (item === null) {
      item = document.createElement('div');
      item.classList.add(this.alertconfig.domselectors.alertmessages.substr(1));
      document.body.append(item);
      const container = document.createElement('div');
      container.classList.add(this.alertconfig.domselectors.messageslist.substr(1));
      item.append(container);
    }
    this.messages_container = (!this.messages_container) ? item.querySelector(this.alertconfig.domselectors.messageslist) : this.messages_container;
  }
  alertMessages() {
    if (!this.messages_container) this.messagesContainer();
    // adjust
    if (this.messages_container === null) return;
    Array.from(this.messages_container.children).forEach(box => {
      const alertmessage = this.alertMessage(box);
    });
  }

  alertMessage(box, attach = false) {
    box.classList.add(this.alertconfig.domselectors.alertmessage.substr(1));
    const message = box.querySelector(this.alertconfig.domselectors.message);
    if (message === null) return;
    if (attach === true) {
      if (this.messages_container === null) this.messagesContainer();
      this.messages_container.prepend(box);
    }
    if (message.scrollHeight > message.offsetHeight) {
      const showall = box.querySelector(this.alertconfig.domselectors.showall);
      if (showall) {
        showall.classList.remove(css.hide);
        showall.addEventListener('click', (e) => {
          e.stopImmediatePropagation();
          box.classList.toggle(this.alertconfig.css.viewall);
        });
      }
    }
    box.animate([{
      transform: 'translateX(120%)',
      opacity: 0.85,
    }, {
      opacity: 1,
      transform: 'translateX(0%)'
    }], {
      duration: 600,
      easing: 'ease-out',
      iterations: 1,
    });
    if (box.dataset.duration) {
      setTimeout(() => {
        this.dismissAlert(box);
      }, parseInt(box.dataset.duration));
    } else this.dismissListener(box);
    return true;
  }

  build(type, options = {}) {
    type = (type) ? type : alertconfig.types.warning;
    const samealert = (options.codeid && options.message) ? document.querySelector(alertconfig.selector + '[data-message="' + (options.message) + '"]') : ((options.id) ? document.getElementById(id) : null);

    if (samealert) {
      this.refreshAlert(samealert.id);
      return;
    }
    let response;
    const defaultOptions = {
      title: '',
      duration: null,
      dismissible: false,
      extra: null,
      inverse: true,
      insertafter: false,
      callback: null,
      replaceparent: false,

    };
    let parent = (options.parent && options.parent instanceof HTMLElement) ? options.parent : document.querySelector(options.parent);
    parent = (parent) ? parent : document.body;
    options = { ...defaultOptions,
      ...options
    };
    Object.freeze(options);
    const params = new URLSearchParams();
    params.append('type', options.type);
    params.append('title', DOMPurify.sanitize(((options.title === undefined || options.title === '') ? '' : ': ' + options.title)));
    params.append('message', DOMPurify.sanitize(options.message));
    params.append('num', parent.querySelectorAll(this.alertconfig.selector).length);
    params.append('inverse', options.inverse);
    params.append('dismissible', options.dismissible);
    params.append('is_safe', true);
    if (options.codeid) params.append('codeid', options.codeid);
    fetch(this.url.template, fetchSettings({
      method: 'POST',
      body: params
    })).then(response =>
      response.text()).then(response => {
      // sanitize here - nothing stored
      let box;
      response = DOMPurify.sanitize(response);
      const parser = new DOMParser();
      response = parser.parseFromString(response, "text/html");
      response = response.querySelector(this.alertconfig.selector);
      if (options.insertafter === true) {
        box = parent.parentElement.insertBefore(response, parent.nextElementSibling);
      } else {
        box = response;
        parent.prepend(box);
      }
      return this.activateAlert(type, box, options);

    }).catch(err => {
      console.log('err', err);
    });

  }
  getBoxById(id, parent = document) {
    return (id !== '' && document.getElementById(id)) ? document.getElementById(id) : parent.querySelector('[data-message="' + id + '"]');
  }
  refreshAlert(box) {
    box = (box instanceof HTMLElement) ? box : this.getBoxById(box);
    if (!box || !box.classList.contains(this.alertconfig.selector.substr(1))) return;
    const style = window.getComputedStyle(box);
    box.animate([{
        transform: 'scale(1), scale(1.05)',
        background: style["color"],
        color: style["background-color"]
      },
      {
        transform: 'scale(1.05) scale(1)',
        background: style["background-color"],
        color: style["color"]
      }
    ], {
      duration: 400,
      easing: 'ease-out',
      iterations: 1,
    });
  }

  dismissAlert(box) {
    box = (box instanceof HTMLElement) ? box : this.getBoxById(box);
    if (!box) return;
    const refresh = (box.dataset.refresh) ? box.dataset.refresh : null;
    // check if there is a cookie management - for top alert messages
    if (box.dataset.cook && box.dataset.value != undefined) {
      const params = new FormData();
      params.append("name", box.dataset.cook);
      params.append("value", box.dataset.value);
      fetch('/gui/setmsgcookie', fetchSettings({
        method: "POST",
        body: params
      }));
    }
    box.animate([{
      transform: 'translateX(0%)',
      opacity: 1,
    }, {
      opacity: 0.85,
      transform: 'translateX(120%)'
    }], {
      duration: 600,
      easing: 'ease-out',
      iterations: 1,
    });
    setTimeout(() => {
      if (refresh !== null) window.location.reload();
      else {
        box.remove();
      }
    }, 300);
  }

  dismissListener(box) {
    box = (box instanceof HTMLElement) ? box : this.getBoxById(box);
    if (!box) return;
    const close = box.querySelector('[data-dismiss="' + box.id + '"]');
    if (!close) return;
    close.addEventListener('click', (e) => {
      // mandatory prevent event from propagation
      e.stopImmediatePropagation();
      this.dismissAlert(box);
      return false;
    });
  }

  waitForAnswer(box, callback, callback_cancel = null) {
    if (!box) return;
    window.scrollTo({
      top: box.offsetTop,
      behavior: 'smooth'
    });
    const cancel = box.querySelector(this.alertconfig.domselectors.buttons.cancel);
    const ok = box.querySelector(this.alertconfig.domselectors.buttons.ok);
    return new Promise((resolve, reject) => {
      cancel.addEventListener('click', (e) => {
        resolve(false);
        e.stopImmediatePropagation();
        if (callback_cancel !== null) callback_cancel();
        this.dismissAlert(box);

      }, {
        once: true
      });
      ok.addEventListener('click', (e) => {
        resolve(true);
        e.stopImmediatePropagation();
        if (callback !== null) callback();
        this.dismissAlert(box);

      }, {
        once: true
      });
    })
  }
  realTarget(el) {
    // to work with tom-select or other components
    if (el.tomselect) return el.tomselect.wrapper;
    return el;
  }
  hasMessages(el, type = null) {
    el = this.realTarget(el);
    if (el === null) return false;
    if (type) return (el.dataset[type] !== undefined);
    for (const type of this.allowedtypes) {
      if (el.dataset[type]) return true;
    }
    return false;
  }
  addMessage(type, el, message, tim = null) {
    if (this.allowedtypes.indexOf(type) < 0) return;
    if (el === null) return;
    el = this.realTarget(el);
    el.classList.add('relative');
    const messages = (el.dataset[type]) ? el.dataset[type].split(', ') : [];
    message = (this.i18nmessages[message]) ? this.i18nmessages[message] : message;
    if (messages.indexOf(message) < 0) {
      messages.push(message);
      el.dataset[type] = messages.join(this.separator);
      el.classList.add(this.alertconfig.css.has[type]);
    } else this.refreshMessage(el);
    if (tim !== null) {
      setTimeout(() => {
        this.removeMessage(type, el, message);
      }, tim);
    }
  }
  refreshMessage(el) {
    const style = window.getComputedStyle(el);
    el.animate([{
        background: style["color"],
        color: style["background-color"]
      },
      {
        background: style["background-color"],
        color: style["color"]
      }
    ], {
      duration: 400,
      easing: 'ease-out',
      iterations: 1,
    });
  }
  removeMessage(type, el, message = null) {
    if (this.allowedtypes.indexOf(type) < 0) return;
    el = this.realTarget(el);
    if (el === null || !el.dataset[type]) return;
    if (message !== null) {
      message = (this.i18nmessages[message]) ? this.i18nmessages[message] : message;
      const messages = el.dataset[type].split(this.separator);
      const i = messages.indexOf(message);
      if (i >= 0) delete messages[i];
      if (messages.length === 0) delete el.dataset[type];
      else el.dataset[type] = messages.join(this.separator);
    } else delete el.dataset[type];
    if (!el.dataset[type]) el.classList.remove(this.alertconfig.css.has[type]);
  }
  classError() {
    return false;
  }
}