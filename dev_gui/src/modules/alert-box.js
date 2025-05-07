import DOMPurify from 'dompurify';
import {
  generate_uuid,
  fetchSettings,
  create_box
} from '../modules/utils.js';
import {
  css
} from '../modules/modules-config.js';
// alertbox one instance by page - display alertbox with uniqueid
async function createAlertBox() {
  // to remove
  const alertconfig = {
    danger: 'danger',
    info: 'info',
    warning: 'warning',
    css: {
      alert: 'alert',
      confirm: 'confirm',
      inverse: 'inverse',
      viewall: 'viewall',
      h_auto: 'h-auto',
      has: {
        warning: 'has-warning',
        error: 'has-error',
        success: 'has-success',
        info: 'has-info',
        message: 'has-message',
        danger: 'has-danger',
      },
      icon: {
        anchor: 'icon-bell-alert'
      }
    },
    types: {
      confirm: 'confirm',
      info: 'info',
      warning: 'warning',
      danger: 'danger',
      error: 'error',
      maintenance: 'maintenance'
    },
    dismiss_selector: '[data-dismiss]',
    selector: '.alert',
    domselectors: {
      alert: '.js-alert',
      alertmessages: '.site-alertmessages',
      messageslist: '.alertmessages-list',
      alertmessage: '.alertmessage',
      summary: '[data-summary]',
      action: '[data-action="confirm"]',
      message: '.message',
      showall: '.showall',
      buttons: {
        group: '.btn-group',
        ok: '.is-ok',
        cancel: '.is-cancel'
      }
    },
    confirm_selector: '.alert.confirm'

  }
  const separator = ' | ';
  let messages_container;
  let url = {
    translation: '/gui/i18n',
    template: '/gui/alertbox'
  }
  const messagemodel = {
    parent: null,
    type: alertconfig.types.info,
    content: '',
  }
  const allowedtypes = Object.values(alertconfig.types);
  const i18nmessages = await getI18nmessages();
  async function getI18nmessages() {
    const response = await fetch(url.translation, fetchSettings);
    return await response.json();
  }

  function applyTo(element = document) {
    // init admin messages and flashed messages  - top right of the page
    alertMessages();
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
      return activateAlert(type, item, options);
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

  function addAlert(message, options = null) {
    // message = {type:required,string, content:required string, date: string,dismissible:bool,  duration:int, inverse:bool}
    let box = getBoxById(message.content);
    if (box) return refreshAlert(box);
    const dataset = {
      type: message.type,
      message: message.content
    };
    const classlist = [message.type];
    if (message.hasOwnProperty('duration') && message.duration) dataset.duration = message.duration;
    if (message.hasOwnProperty('cookiename')) dataset.cook = message.type + message.cookiename;
    if (message.hasOwnProperty('date')) dataset.value = message.date;
    if (message.hasOwnProperty('inverse') && message.inverse === true) classlist.push('inverse');
    box = create_box('div', {
      id: generate_uuid(),
      dataset: dataset,
      class: classlist
    })
    let buttons = ``;
    let showall = `<div class="showall hide" data-title="${i18nmessages.viewfull}"><i class="icon iconview"></i></div>`;
    if (message.type === alertconfig.types.confirm) {
      buttons = (options.buttons) ? options.buttons : null;
      buttons = `${showall}<div class="btn-group flex justify-end max-w-full"><button class="button text-base ${alertconfig.domselectors.buttons.ok.substr(1)}"  value=true>${(options.buttons && options.buttons.ok && options.buttons.ok.text)?options.buttons.ok.text:i18nmessages.ok}</button><button class="button ${alertconfig.domselectors.buttons.cancel.substr(1)} text-base"  value=false>${(options.buttons && options.buttons.cancel && options.buttons.cancel.text)?options.buttons.cancel.text:i18nmessages.cancel}</button></div>`;
      showall = ``;
    }
    let html = `<div class="content"><div class="signal hidden sm:block"><i class="icon"></i></div><div class="message"><strong class="type">${(i18nmessages.alerttype && i18nmessages.alerttype[message.type])?i18nmessages.alerttype[message.type]:message.type}</strong>${unescape((i18nmessages[message.content]) ? i18nmessages[message.content] : message.content)} ${buttons}</div>`;
    if (message.dismissible) html += `<div class="close" data-dismiss="${box.id}"  aria-label="${i18nmessages.close}"><i class="icon-sm icon-x-mark cursor-pointer"></i></div>`;

    box.insertAdjacentHTML('afterbegin', html + `${showall} </div>`);
    const ret = alertMessage(box, true);
    if (ret === true && message.type === alertconfig.types.confirm) {
      activateConfirm(box, options);
     return waitForAnswer(box, options.callback, options.callback_cancel);
    }
  }

  function addConfirm(content, options = {}) {
    let box = getBoxById(content);
    if (box == null) {
      const message = {
        type: alertconfig.types.confirm,
        content: content,
      };
      options = { ...{
          title: ``,
          callback: null,
          callback_cancel: null,
          partial: true,

        },
        ...options
      }

      message.dismissible = true;
      message.title = options.title;
      return addAlert(message, options);

    } else {
      // alert exists animate it
      refreshAlert(box);
    }

  }


  function activateConfirm(box, options) {
    box = (box instanceof HTMLElement) ? box : getBoxById(box);
    if (box === null) return;
    let callback = (options.callback) ? options.callback : null,
      callback_cancel = (options.callback_cancel) ? (options.callback_cancel) : null;
    if (options.href) callback = () => {
      fetch(options.href + '&' + new URLSearchParams({
        partial: true
      }), fetchSettings()).then(response => {

        let responsebox = box.querySelector(alertconfig.domselectors.message);
        if (!responsebox) {
          responsebox = create_box('div', {
            class: alertconfig.domselectors.message.substr(1)
          }, responsebox);

        };
        responsebox.innerHTML = DOMPurify.sanitize(response.text());
        const btns = box.querySelector(alertconfig.domselectors.buttons.group);
        if (btns) {
          btns.innerHTML = `< button class = "button is-close text-base"  value = false >${i18nmessages.close} </button>`;
          btns.querySelector('.is-close').addEventListener('click', (e) => {
            dismissAlert(box);
          });
        }
        box.dataset.refresh = true;
      });
    };
    //waitForAnswer(box, callback, callback_cancel);
  }

  function activateAlert(type, box, options) {
    box = (box instanceof HTMLElement) ? box : getBoxById(box);
    if (box === null) return;
    if (options.duration) {
      setTimeout(() => {
        dismissAlert(box);
      }, options.duration);
    } else if (options.dismissible) dismissListener(box);
    if (type === alertconfig.types.confirm) {
     activateConfirm(box, options);
      return waitForAnswer(box, options.callback, options.callback_cancel);
    }
    return true;
  }

  function messagesContainer() {
    let item = document.getElementById(alertconfig.domselectors.alertmessages.substr(1));
    if (item === null) {
      item = create_box('div', {
        class: alertconfig.domselectors.alertmessages.substr(1)
      }, document.body);
      const container = create_box('div', {
        class: alertconfig.domselectors.messageslist.substr(1)
      }, item);
    }
    messages_container = (!messages_container) ? item.querySelector(alertconfig.domselectors.messageslist) : messages_container;
  }

  function alertMessages() {
    if (!messages_container) messagesContainer();
    // adjust
    if (messages_container === null) return;
    Array.from(messages_container.children).forEach(box => {
      const alertmessage = alertMessage(box);
    });
  }

  function alertMessage(box, attach = false) {
    box.classList.add(alertconfig.domselectors.alertmessage.substr(1));
    const message = box.querySelector(alertconfig.domselectors.message);
    if (message === null) return;
    if (attach === true) {
      if (messages_container === null) messagesContainer();
      messages_container.prepend(box);
    }
    if (message.scrollHeight > message.offsetHeight) {
      const showall = box.querySelector(alertconfig.domselectors.showall);
      if (showall) {
        showall.classList.remove(css.hide);
        showall.addEventListener('click', (e) => {
          e.stopImmediatePropagation();
          box.classList.toggle(alertconfig.css.viewall);
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
        dismissAlert(box);
      }, parseInt(box.dataset.duration));
    } else dismissListener(box);
    return true;
  }

  function getBoxById(id, parent = document) {
    id=escape(unescape(id));
    return (id !== '' && document.getElementById(id)) ? document.getElementById(id) : parent.querySelector('[data-message="' + id + '"]');
  }

  function refreshAlert(box) {
    box = (box instanceof HTMLElement) ? box : getBoxById(box);
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

  function dismissAlert(box) {
    box = (box instanceof HTMLElement) ? box : getBoxById(box);
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

  function dismissListener(box) {
    box = (box instanceof HTMLElement) ? box : getBoxById(box);
    if (!box) return;
    const close = box.querySelector('[data-dismiss="' + box.id + '"]');
    if (!close) return;
    close.addEventListener('click', (e) => {
      // mandatory prevent event from propagation
      e.stopImmediatePropagation();
      dismissAlert(box);
      return false;
    });
  }

  function waitForAnswer(box, callback, callback_cancel = null) {
    if (!box) return;
    window.scrollTo({
      top: box.offsetTop,
      behavior: 'smooth'
    });
    const cancel = box.querySelector(alertconfig.domselectors.buttons.cancel);
    const ok = box.querySelector(alertconfig.domselectors.buttons.ok);
    return new Promise((resolve, reject) => {
      cancel.addEventListener('click', (e) => {
        resolve(false);
        e.stopImmediatePropagation();
        if (callback_cancel !== null) callback_cancel();
        dismissAlert(box);
      }, {
        once: true
      });
      ok.addEventListener('click', async (e) => {
        resolve(true);
        e.stopImmediatePropagation();
        if (callback !== null) callback();
        dismissAlert(box);
      }, {
        once: true
      });
    })
  }
  // messages attached to document or form elements
  function realTarget(el) {
    // to work with tom-select or other components
    if (el.tomselect) return el.tomselect.wrapper;
    return el;
  }

  function hasMessage(el, type = null) {
    el = realTarget(el);
    if (el === null) return false;
    if (type) return (el.dataset[type] !== undefined);
    for (const type of allowedtypes) {
      if (el.dataset[type]) return true;
    }
    return false;
  }

  function addMessage(message) {
    // message {type:, parent:  ,content:, duration:}
    if (allowedtypes.indexOf(message.type) < 0) return;
    if (message.parent === null) return;
    const el = realTarget(message.parent);
    el.classList.add(css.relative);
    const messages = (el.dataset[message.type]) ? el.dataset[message.type].split(', ') : [];
    message.content = (i18nmessages[message.content]) ? i18nmessages[message.content] : message.content;
    if (messages.indexOf(message.content) < 0) {
      messages.push(message.content);
      el.dataset[message.type] = messages.join(separator);
      el.classList.add(alertconfig.css.has[message.type]);
    } else refreshAlert(el);
    if (message.duration && message.duration !== null) {
      setTimeout(() => {
        removeMessage(message);
      }, message.duration);
    }
  }

  function removeMessage(message) {
    // message {type:, parent:  ,content:null}
    if (allowedtypes.indexOf(message.type) < 0) return;
    const el = realTarget(message.parent);
    if (el === null || !el.dataset[message.type]) return;
    if (message.content !== null) {
      message.content = (i18nmessages[message.content]) ? i18nmessages[message.content] : message.content;
      const messages = el.dataset[message.type].split(separator);
      const i = messages.indexOf(message.content);
      if (i >= 0) delete messages[i];
      if (messages.length === 0) delete el.dataset[message.type];
      else el.dataset[message.type] = messages.join(separator);
    } else delete el.dataset[message.type];
    if (!el.dataset[message.type]) el.classList.remove(alertconfig.css.has[message.type]);
  }

  function addConsole(message) {
    if (message.parent === null) return;
    const tag = 'p';
    let el = message.parent.querySelector('.' + css.console);
    if (el === null) {
      el = create_box('div', {
        class: [css.console]
      });
      message.parent.prepend(el);
    }
    if (message.id) {
      const msg = el.querySelector(`${tag}[data-id="${message.id}"]`);
      if (msg) msg.innerHTML = unescape(message.content);
      else el.insertAdjacentHTML('beforeend', `<${tag} data-id="${message.id}">${unescape(message.content)}</${tag}>`);
    } else el.insertAdjacentHTML('beforeend', `<${tag}>${unescape(message.content)}</${tag}>`);
  }

  function error() {
    return false;
  }
  return {
    alertconfig,
    applyTo,
    addMessage,
    removeMessage,
    hasMessage,
    addConfirm,
    addConsole,
    addAlert,
    dismissAlert,
    i18nmessages,
    error
  }

}
const AlertBox = await createAlertBox();
export {
  AlertBox
}