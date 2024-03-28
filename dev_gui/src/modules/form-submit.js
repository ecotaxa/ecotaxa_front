import validator from 'validator';
import DOMPurify from 'dompurify';
import {
  domselectors,
  css
} from '../modules/modules-config.js';
import {
  fetchSettings,
  decode_HTMLEntities,
  html_spinner,
} from '../modules/utils.js';

domselectors.captcha = '.js-captcha';
css.invalid = 'invalid';
css.inputvalid = 'valid';
css.required = 'required';
css.tshidden = 'ts-hidden-accessible';
export class FormSubmit {
  handlers = {
    validate: [],
    submit: []
  };
  form = null;
  listener = null;
  constructor(form, options = {}) {
    if (!form) return;
    if (!form.formsubmit) {
      this.form = form instanceof HTMLElement ? form : document.querySelector(form);
      const defaultOptions = {
        fetch: null,
      };
      options = Object.assign(options, this.form.dataset);
      this.options = Object.assign(defaultOptions, options);
      if (!this.form) return;
      this.tabs = this.form.querySelectorAll(domselectors.component.tabs.tab);
      this.validateFields(true);
      this.init();

      form.formsubmit = this;
    }
    return form.formsubmit;
  }
  init() {

    // init the form ( options like beforeunload etc...)
    this.form.addEventListener('keydown', (e) => {
      // prevent enter submit
      if (e.key === 'Enter' && e.target instanceof HTMLInputElement) e.preventDefault();
    });
    window.addEventListener("pageshow", (e) => {
      const historytraversal = event.persisted ||
        (typeof window.performance != "undefined" &&
          window.performance.navigation.type === 2);
      if (historytraversal) {
        this.enableForm();
      }
    });
    this.form.addEventListener('validate', (e) => {
      this.validateFields();
    });
    this.form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const res = await this.submitForm();
      return res;
    });
    this.specialFields();
  }
  specialFields() {
    // check if there is a password confirm input
    // add show text for password fields

    this.form.querySelectorAll('input[data-match]').forEach(input => { //
      const match = input.dataset.match;
      if (!match) return;
      const target = document.getElementById(match);
      if (!target) return;
      const invalid = (input.dataset.matchinvalid) ? input.dataset.matchinvalid : "no match";
      const check_match = (item, itemtarget) => {
        const label = item.closest(domselectors.component.form.formbox).querySelector('label[for="' + item.id + '"]');
        const labeltarget = itemtarget.closest(domselectors.component.form.formbox).querySelector('label[for="' + itemtarget.id + '"]');
        const {
          patternMismatch = false
        } = item.validity;
        const customvalidity = (patternMismatch) ? this.get_message(item, 'invalid') : ``;
        if (item.checkValidity() === true) {
          item.setCustomValidity('');
          if (item == input && label !== null) label.classList.remove(css.invalid);
          else if (labeltarget !== null) labeltarget.classList.remove(css.invalid);
          item.classList.remove(css.invalid);
          if (item.value !== itemtarget.value) {
            itemtarget.setCustomValidity(invalid);
            if (labeltarget) {
              labeltarget.dataset.invalid = invalid;
              labeltarget.classList.add(css.invalid);
            }
            itemtarget.classList.add(css.invalid);
          } else {
            itemtarget.setCustomValidity("");
            if (labeltarget) labeltarget.classList.remove(css.invalid);
            itemtarget.classList.remove(css.invalid);
          }
        } else {
          item.setCustomValidity(customvalidity);
          label.dataset.invalid = customvalidity;
          if (label) label.classList.add(css.invalid);
          item.classList.add(css.invalid);
        }
        item.focus();
      };
      [input, target].forEach(item => {
        item.addEventListener('keyup', (e) => {
          const itemtarget = (item === input) ? target : input;
          const itemsrc = (item === input) ? input : target;
          check_match(itemsrc, itemtarget);
        });
      });

    });
  }
  get_message(field, type = 'invalid') {
    const {
      valueMissing = true
    } = field.validity;
    if (valueMissing) return `* ` + ((field.dataset.required) ? field.dataset.required : ((this.form.dataset.required) ? this.form.dataset.required : (field.validationMessage) ? (field.validationMessage) : 'required'));
    else return (field.dataset[type]) ? field.dataset[type] : (field.validationMessage) ? (field.validationMessage) : 'input invalid';
  }
  setLabelState(field, valid) {
    const label = this.getFieldLabel(field);
    if (label == null) return;
    if (valid === true) {
      label.classList.remove(css.invalid);
    } else {
      label.dataset.invalid = this.get_message(field);
      label.classList.add(css.invalid);
      const rect = label.getBoundingClientRect();
      const x = rect.left;
      const y = rect.top;
      window.scrollTo({
        top: y,
        left: x,
        behavior: 'smooth'
      });
    }
  }
  validateField(field, init = false) {
    if (['select'].indexOf(field.tagName.toLowerCase()) >= 0) {
      field.querySelectorAll('option:checked').forEach(option => {
        option.value = decode_HTMLEntities(DOMPurify.sanitize(option.value));
      });
    } else field.value = decode_HTMLEntities(DOMPurify.sanitize(field.value));
    if (field.tomselect) field.classList.remove(css.tshidden);
    let rep = field.checkValidity();
    console.log(field.name, rep)
    if (field.tomselect) field.classList.add(css.tshidden);
    if (rep && field.dataset.unique !== undefined) {
      rep = this.validateFieldUnique(field);
    }
    const evt = document.createEvent("Event");
    evt.initEvent(((rep) ? 'valid' : 'invalid'), true, true);
    field.dispatchEvent(evt);
    return rep;
  }

  getFieldLabel(field) {
    let label = field.closest('[for="' + field.name + '"]') ? field.closest('[for="' + field.name + '"]') : (field.closest('[data-for="' + field.name + '"]')) ? field.closest('[data-for="' + field.name + '"]') : null;
    if (label === null) {
      label = (field.closest(domselectors.component.form.formbox)) ? ((field.closest(domselectors.component.form.formbox).querySelector('.label')) ? field.closest(domselectors.component.form.formbox).querySelector('.label') : field.closest(domselectors.component.form.formbox).querySelector('label')) : null;
    }
    if (label === null) {
      label = (field.parentElement && field.parentElement.dataset.elem) ? ((field.closest('fieldset')) ? field.closest('fieldset').querySelector('.' + field.parentElement.dataset.elem) : null) : null;
    }

    return label;
  }
  validateFieldUnique(field) {
    const label = this.getFieldLabel(field);
    if (String(field.dataset.unique).toLowerCase() === String(field.value).toLowerCase()) {
      //field.dataset.invalid = window.alertbox.i18nmessages.noduplicate;
      // just send a warning for the moment
      if (label) {
        label.dataset.confirm = window.alertbox.i18nmessages.noduplicate;
        label.classList.add(window.alertbox.alertconfig.css.confirm);
      }
      const callback_cancel = function() {
        field.dataset.unique = false;
        if (label) {
          label.classList.remove(window.alertbox.alertconfig.css.confirm);
          delete label.dataset.confirm;
        }
      }
      const confirm = window.alertbox.createAlert(window.alertbox.alertconfig.types.confirm, ((label) ? label.textContent + ` : ` : ``) + window.alertbox.i18nmessages.noduplicate, null, {
        callback_cancel: callback_cancel,
        buttons: {
          ok: {
            text: window.alertbox.i18nmessages.modify
          },
          cancel: {
            text: window.alertbox.i18nmessages.saveanyway
          }
        }
      });
      return confirm;
    } else if (label.dataset.confirm) {
      label.classList.remove(window.alertbox.alertconfig.css.confirm);
      delete label.dataset.confirm;
    }
    return true;
  }
  async validateFields(init = false) {
    //todo: complete validation foreach field type
    let resp = true,
      r = true;
    [...this.form.elements].forEach(field => {
      if (init === true) {
        if (!field.dataset.listen) {
          if (field.required) {
            const label = this.getFieldLabel(field);
            if (label) label.classList.add(css.required);
          }
          field.addEventListener('change', (e) => {
            this.validateField(e.target);
          });
          field.dataset.listen = true;
          field.addEventListener('invalid', (e) => {
            this.setLabelState(field, false);
          });
          field.addEventListener('valid', (e) => {
            this.setLabelState(field, true);
          });
        }
      } else if (field.name && field.type && (['submit', 'hidden'].indexOf(field.type) < 0 && (['radio', 'checkbox'].indexOf(field.type) < 0 || field.required))) {
        r = this.validateField(field, false);
        resp = (resp && r);
      }

    });
    // add/remove error class on tabs tab-control elements
    this.tabs.forEach(tab => {
      if (tab.querySelector(':invalid') || tab.querySelector(domselectors.component.alert.danger)) tab.classList.add(css.error);
      else tab.classList.remove(css.error);
    });
    r = await this.execHandler('validate');
    return (r && resp);
  }

  addHandler(type, handler) {
    this.handlers[type].push(handler);
  }
  fieldEnable(enable = true) {
    this.form.querySelectorAll('input[data-sub="enable"]').forEach(input => {
      if (enable === true) {
        input.disabled = false;
      } else input.disabled = true;
    });
  }

  async execHandler(type) {
    if (this.handlers[type].length === 0) return true;
    let resp = true;
    // series
    /*  for (const handler of this.handlers) {
          const rep = await handler()
          resp = (resp && rep)
      }*/
    // concurrent
    await Promise.all(this.handlers[type].map(async handler => {
      const rep = await handler();
      resp = (resp && rep);
    }));
    //  if (resp === true) this.handlers[type] = [];
    return resp;
  }
  // no redirection when using data-fetch
  formFetch(format = null) {
    const formdata = new FormData(this.form);
    formdata["fetch"] = true;
    fetch(this.form.action, fetchSettings({
        method: 'POST',
        body: formdata,
      }))
      .then(response => {
        switch (format) {
          case "text":
          case "html":
            return response.text();
            break;
          default:
            return response.json();
        }
      })
      .then(response => {
        this.displayResponse(response);
      })
      .catch(err => {
        this.displayResponse(err, true)
      }).finally(response => {
        this.form.disabled = true;
      });
    return false;
  }

  async submitForm() {
    this.fieldEnable();
    // important async
    const valid = await this.validateFields(false);

    if (valid) {
      const isbot = (this.form.querySelector(domselectors.captcha)) ? (this.form.dataset.isbot ? (this.form.dataset.isbot === true) : true) : false;
      if (isbot === true) return false;
      const yessubmit = await this.execHandler('submit');
      if (yessubmit) {
        if (this.options.fetch) this.formFetch(this.options.fetch);
        else this.form.submit();
        this.disableForm();
        return true;
      }
    }
    return false;
  }
  enableForm() {
    this.form.disabled = false;
    const btn = (this.form.querySelector('[type="submit"] svg'));
    if (btn) btn.remove();
  }
  disableForm() {
    this.form.disabled = true;
    const btn = this.form.querySelector('[type="submit"]');
    if (btn) btn.insertAdjacentHTML('afterbegin', html_spinner('text-stone-50 ml-1 mr-2 align-text-bottom inline-block'));

  }
  displayResponse(response, error = false) {
    const el = document.createElement('div');
    el.insertAdjacentHTML('afterbegin', response);
    if (error !== false) el.classList.add('is-error');
    this.form.parentElement.insertBefore(el, this.form);
    this.form.remove();
  }
}