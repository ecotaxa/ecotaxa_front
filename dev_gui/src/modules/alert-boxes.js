import DOMPurify from 'dompurify';
import {
  fetchSettings
} from '../modules/utils.js';
import {
  alertconfig
} from '../modules/modules-config.js';

let instance = null;
// alertbox one instance by page - display alertbox with uniqueid
export class AlertBox {
  constructor(element = document) {
    if (!instance) {
      this.init(element);
      instance = this;
    }
    return instance;
  }
  init(element) {
    let items = [...element.querySelectorAll(alertconfig.selector), ...element.querySelectorAll(alertconfig.domselectors.action)];
    const build_alert = (item) => {
      const options = { ...{
          dismissible: (item.dataset.dismissible) ? item.dataset.dismissible : true,
          insertafter: (item.dataset.action) ? false : true,
          inverse: (item.classList.contains(alertconfig.css.inverse)) ? true : ((item.dataset.action) ? false : true),
          codeid: true,
          message: (item.dataset.message),
          type: (item.dataset.action === alertconfig.confirm_selector.substr(1)) ? alertconfig.types.confirm : ((item.dataset.type) ? item.dataset.type : alertconfig.types.warning),
        },
        ...item.dataset
      }
      if (item.classList.contains(alertconfig.domselectors.alert) || item.dataset.action === alertconfig.confirm_selector.substr(1)) return this.build(options);
      else return this.createFrom(item, options);
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
  createFrom(box, options) {

    if (options.duration) {
      setTimeout(() => {
        this.dismissAlert(box.id);
      }, options.duration);
    } else if (options.dismissible) this.dismissListener(box.id);
    const type = (options.confirm) ? alertconfig.types.confirm : ((options.type) ? options.type : alertconfig.types.warning);
    if (type === alertconfig.types.confirm) {
      let callback;
      if (options.href) callback = () => {

        fetch(options.href + '&' + new URLSearchParams({
          partial: true
        }), fetchSettings()).then(response => response.text()).then(response => {
          let responsebox = box.querySelector(alertconfig.domselectors.message);
          if (!responsebox) {
            responsebox = document.createElement('div');
            box.append(responsebox);
          };
          responsebox.innerHTML = DOMPurify.sanitize(response);

          box.querySelector(alertconfig.domselectors.buttons).remove();
          box.dataset.refresh = true;
        });
      };
      else callback = () => {
        return true
      };
      return this.waitForAnswer(box.id, callback);
    }
    return true;
  }
  build(options = {
    type: alertconfig.types.warning
  }) {

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
      template_url: '/gui/alertbox',
      buttons: {
        ok: '.is-ok',
        cancel: '.is-cancel'
      }
    };
    let parent = (options.parent && options.parent instanceof HTMLElement) ? options.parent : document.querySelector(options.parent);
    parent = (parent) ? parent : document.body;
    options = Object.assign(defaultOptions, options);
    this.buttons = options.buttons;
    Object.freeze(options);
    const params = new URLSearchParams();
    params.append('type', options.type);
    params.append('title', DOMPurify.sanitize(((options.title === undefined || options.title === '') ? '' : ': ' + options.title)));
    params.append('message', DOMPurify.sanitize(options.message));
    params.append('num', parent.querySelectorAll(alertconfig.selector).length);
    params.append('inverse', options.inverse);
    params.append('dismissible', options.dismissible);
    params.append('is_safe', true);
    if (options.codeid) params.append('codeid', options.codeid);
    fetch(window.location.origin + options.template_url, fetchSettings({
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
      return this.createFrom(box, options);

    }).catch(err => {
      console.log('err', err);
    });

  }
  getBoxById(id) {
    return (id !== '' && document.getElementById(id)) ? document.getElementById(id) : document.querySelector('[data-message="' + id + '"]');
  }
  refreshAlert(id) {
    const box = this.getBoxById(id);
    if (!box || !box.classList.contains(alertconfig.selector.substr(1))) return;
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

  dismissAlert(id) {
    const box = this.getBoxById(id);
    if (!box || !box.classList.contains(alertconfig.selector.substr(1))) return;
    const refresh = (box.dataset.refresh) ? box.dataset.refresh : null;
    box.animate([{
      transform: 'translateX(-50%) translateY(-100%)',
    }], {
      duration: 300,
      easing: 'ease-out',
      iterations: 1,
    });
    setTimeout(() => {
      if (refresh) window.location.reload();
      else box.remove();
    }, 300);
  }

  dismissListener(id) {
    const box = this.getBoxById(id);
    if (!box || !box.classList.contains(alertconfig.selector.substr(1))) return;
    const close = box.querySelector('[data-dismiss="' + alertconfig.selector.substr(1) + '"]');
    if (!close) return;
    close.addEventListener('click', (e) => {
      this.dismissAlert(id);

    });
  }

  waitForAnswer(id, callback) {
    const box = this.getBoxById(id);
    if (!box || !box.classList.contains(alertconfig.css.alert)) return;
    window.scrollTo({
      top: box.offsetTop,
      behavior: 'smooth'
    });
    const cancel = box.querySelector(this.buttons.cancel);
    const ok = box.querySelector(this.buttons.ok);
    return new Promise((resolve, reject) => {
      cancel.addEventListener('click', (e) => {
        resolve(false);
        this.dismissAlert(id);
      }, {
        once: true
      });
      ok.addEventListener('click', (e) => {
        resolve(true);
        if (callback !== null) callback();
        else return true;

      }, {
        once: true
      });
    })
  }

}