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
      if (!instance) instance = this;
      resolve(instance);
      reject(null);
    });
  }
  async getI18nmessages() {
    const response = await fetch(this.url.translation, fetchSettings);
    this.i18nmessages = await response.json();
  }

  activateAll(element = document) {
    // init admin messages and flashed messages  - top right of the page
    this.alertMessages();
    // init page content alert messages - secondary alerts or information
    let items = [...element.querySelectorAll(alertconfig.selector)];
    const activate_alert = (item) => {
      const type = (item.dataset.type) ? item.dataset.type : alertconfig.types.warning;
      const options = { ...{
          dismissible: (item.dataset.dismissible) ? item.dataset.dismissible : true,
          inverse: (item.classList.contains(alertconfig.css.inverse)) ? true : ((item.dataset.action) ? false : true),
          content: (item.dataset.message) ? item.dataset.message : item.textContent,
          title: (item.dataset.title) ? item.dataset.title : type
        },
        ...item.dataset
      }
      this.activateAlert(type, item, options);

    }
    items.forEach(item => {
      const options = item.dataset;
      if (options.event) {
        options.href = options.href ? options.href : item.href;
        item.addEventListener(options.event, (e) => {
          e.preventDefault();
          return activate_alert(item);
        });
      } else activate_alert(item);
    });

  }

  renderAlert(message, options = null) {
    // message = {type:required,string, content:required string, date: string,dismissible:bool,  duration:int, inverse:bool}
    let box = this.getBoxById(message.content);
    if (box) return this.refreshAlert(box);
    const i18nmessages = this.i18nmessages;
    box = document.createElement('div');
    box.id = generate_uuid();
    box.dataset.type = message.type;
    box.dataset.message = message.content;
    if (message.hasOwnProperty('duration') && message.duration) box.dataset.duration = message.duration;
    box.classList.add(message.type);
    if (message.hasOwnProperty('cookiename')) box.dataset.cook = message.type + message.cookiename;
    if (message.hasOwnProperty('date')) box.dataset.value = message.date;
    if (message.hasOwnProperty('inverse') && message.inverse === true) box.classList.add('inverse');
    let buttons = ``;
    let showall = `<div class="showall hide" data-title="${i18nmessages.viewfull}"><i class="icon iconview"></i></div>`;
    if (message.type === alertconfig.types.confirm) {
      buttons = (options.buttons) ? options.buttons : null;
      buttons = `${showall}<div class="btn-group flex justify-end max-w-full"><button class="button text-base ${alertconfig.domselectors.buttons.ok.substr(1)}"  value=true>${(options.buttons && options.buttons.ok && options.buttons.ok.text)?options.buttons.ok.text:i18nmessages.ok}</button><button class="button ${alertconfig.domselectors.buttons.cancel.substr(1)} text-base"  value=false>${(options.buttons && options.buttons.cancel && options.buttons.cancel.text)?options.buttons.cancel.text:i18nmessages.cancel}</button></div>`;
      showall = ``;
    }
    let html = `<div class="content"><div class="signal hidden sm:block"><i class="icon"></i></div><div class="message"><strong class="type">${(i18nmessages.alerttype && i18nmessages.alerttype[message.type])?i18nmessages.alerttype[message.type]:message.type}</strong>${(i18nmessages[message.content]) ? i18nmessages[message.content] : message.content} ${buttons}</div>`;
    if (message.dismissible) html += `<div class="close" data-dismiss="${box.id}"  aria-label="${i18nmessages.close}"><i class="icon-sm icon-cancel cursor-pointer"></i></div>`;

    box.insertAdjacentHTML('afterbegin', html + `${showall} </div>`);
    const ret = this.alertMessage(box, true);
    if (ret === true && message.type === alertconfig.types.confirm) return this.waitForAnswer(box, options.callback, options.callback_cancel);
  }
  createConfirm(content, options = {}) {
    let box = this.getBoxById(content);
    if (box == null) {
      const message = {
        type: alertconfig.types.confirm,
        content: content,
      };
      options = { ...{
          title: ``,
          callback: null,
          callback_cancel: null,
        },
        ...options
      }

      message.dismissible = true;
      message.title = options.title;
      return this.renderAlert(message, options);
    } else {
      // alert exists animate it
      this.refreshAlert(box);
    }

  }


  activateConfirm(box, options) {
    box = (box instanceof HTMLElement) ? box : this.getBoxById(box);
    if (box === null) return;
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

  activateAlert(type, box, options) {
    box = (box instanceof HTMLElement) ? box : this.getBoxById(box);
    if (box === null) return;
    if (options.duration) {
      setTimeout(() => {
        this.dismissAlert(box);
      }, options.duration);
    } else if (options.dismissible) this.dismissListener(box);
    if (type === alertconfig.types.confirm) {
      return this.activateConfirm(box, options);
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
    const animate = (box.dataset.type && box.dataset.type === alertconfig.types.confirm) ? [{
      opacity: 0.85,
    }, {
      opacity: 1,
    }] : [{
      transform: 'translateX(120%)',
      opacity: 0.85,
    }, {
      opacity: 1,
      transform: 'translateX(0%)'
    }];
    box.animate(animate, {
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

  getBoxById(id, parent = document) {
    return (id !== '' && document.getElementById(id)) ? document.getElementById(id) : parent.querySelector('[data-message="' + id + '"]');
  }
  refreshAlert(box) {
    box = (box instanceof HTMLElement) ? box : this.getBoxById(box);
    const style = window.getComputedStyle(box);
    box.animate([{
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
    const animate = (box.dataset.type && box.dataset.type === alertconfig.types.confirm) ? [{
      opacity: 1,
    }, {
      opacity: 0.85,
    }] : [{
      transform: 'translateX(0%)',
      opacity: 1,
    }, {
      opacity: 0.85,
      transform: 'translateX(120%)'
    }];
    box.animate(animate, {
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
  // messages attached to document or form elements
  realTarget(el) {
    // to work with tom-select or other components
    if (el.tomselect) return el.tomselect.wrapper;
    return el;
  }
  hasItemMessages(el, type = null) {
    el = this.realTarget(el);
    if (el === null) return false;
    if (type) return (el.dataset[type] !== undefined);
    for (const type of this.allowedtypes) {
      if (el.dataset[type]) return true;
    }
    return false;
  }
  addItemMessage(message) {
    // message {type:, parent:  ,content:, duration:}
    if (this.allowedtypes.indexOf(message.type) < 0) return;
    if (message.parent === null) return;
    const el = this.realTarget(message.parent);
    el.classList.add('relative');
    const messages = (el.dataset[message.type]) ? el.dataset[message.type].split(', ') : [];
    message.content = (this.i18nmessages[message.content]) ? this.i18nmessages[message.content] : message.content;
    if (messages.indexOf(message.content) < 0) {
      messages.push(message.content);
      el.dataset[message.type] = messages.join(this.separator);
      el.classList.add(this.alertconfig.css.has[message.type]);
    } else this.refreshAlert(el);
    if (message.duration && message.duration !== null) {
      setTimeout(() => {
        this.removeItemMessage(message);
      }, message.duration);
    }
  }

  removeItemMessage(message) {
    // message {type:, parent:  ,content:null}
    if (this.allowedtypes.indexOf(message.type) < 0) return;
    el = this.realTarget(message.parent);
    if (el === null || !el.dataset[message.type]) return;
    if (message.content !== null) {
      message.content = (this.i18nmessages[message.content]) ? this.i18nmessages[message.content] : message.content;
      const messages = el.dataset[message.type].split(this.separator);
      const i = messages.indexOf(message.content);
      if (i >= 0) delete messages[i];
      if (messages.length === 0) delete el.dataset[message.type];
      else el.dataset[message.type] = messages.join(this.separator);
    } else delete el.dataset[message.type];
    if (!el.dataset[message.type]) el.classList.remove(this.alertconfig.css.has[message.type]);
  }
  classError() {
    return false;
  }
}