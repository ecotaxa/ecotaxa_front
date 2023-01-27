import DOMPurify from 'dompurify';
import {
  fetchSettings
} from '../modules/utils.js';
import {
  alertconfig
} from '../modules/modules-config.js';


let instance = null;
export class AlertBox {
  boxes = [];
  module;
  constructor(module) {
    this.module = module;

  }
  build(text, type = 'warning', parent = null, options = {}) {
    // avoid displaying the same message
    const samealert = document.querySelector(alertconfig.selector + '.' + type + '[data-message="' + text + '"]');
    if (samealert) {
      console.log('samealert', samealert)
      samealert.classList.add('animate');
      return;
    }
    let response;
    const defaultOptions = {
      title: '',
      duration: null,
      buttons: null,
      dismissible: false,
      extra: null,
      inverse: true,
      insertafter: false,
      callback: null,
      replaceparent: false,
      template_url: '/gui/alertbox',
      buttons: {
        ok: '.is-ok',
        cancel: '.is-cancel'
      }
    };
    parent = (parent && parent instanceof HTMLElement) ? parent : document.querySelector(parent);
    parent = (parent) ? parent : document.body;
    options = Object.assign(defaultOptions, options);
    Object.freeze(options);
    const params = new URLSearchParams();
    params.append('type', type);
    params.append('title', ((options.title === undefined || options.title === '') ? '' : ': ' + options.title));
    params.append('message', text);
    params.append('num', parent.querySelectorAll(alertconfig.selector).length);
    params.append('inverse', options.inverse);
    params.append('dismissible', options.dismissible);
    params.append('dismissby', options.dismissby);
    if (options.codemessage) params.append('codemessage', options.codemessage);

    fetch(options.template_url, fetchSettings({
      method: 'POST',
      body: params
    })).then(response =>
      response.text()).then(response => {
      // sanitize here - nothing stored
      let box;
      response = DOMPurify.sanitize(response);
      const parser = new DOMParser();
      response = parser.parseFromString(response, "text/html");
      response = response.querySelector(alertconfig.selector);
      if (options.insertafter === true) {
        box = parent.parentElement.insertBefore(response, parent.nextElementSibling);
      } else {
        box = response;
        parent.prepend(box);
      }
      if (options.dismissible) this.dismissListener();

      if (options.duration) {
        setTimeout(() => {
          this.dismissAlert();
        }, options.duration);
      }
      this.boxes[this.module].push(box);
      if (type === 'confirm') return this.waitForAnswer();
      else return true;

    }).catch(err => {
      console.log('err', err);
    });

  }
  refreshAlert() {
    if (this.box) this.box.animate([{
        transform: 'scale(1), scale(1.5)'
      },
      {
        transform: 'scale(1.5) scale(1)'
      }
    ], {
      duration: 500,
      iterations: 1,
    });
  }
  dismissAlert() {
    if (this.box) this.box.remove();
  }

  dismissListener() {
    const dismiss = this.box.querySelector(alertconfig.dismiss_selector);
    if (!dismiss) return;
    dismiss.addEventListener('click', (e) => {
      this.dismissAlert();
    });
  }

  waitForAnswer() {
    const cancel = this.box.querySelector(this.buttons.cancel);
    const ok = this.box.querySelector(this.buttons.ok);
    return new Promise((resolve, reject) => {
      cancel.addEventListener('click', (e) => {
        resolve(false);
        this.dismissAlert();
      }, {
        once: true
      });
      ok.addEventListener('click', (e) => {

        resolve(true);
        if (this.options.callback !== null) this.options.callback();
        this.dismissAlert();
      }, {
        once: true
      });
    })
  }

}