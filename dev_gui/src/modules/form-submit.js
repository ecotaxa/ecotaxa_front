import validator from 'validator';
import DOMPurify from 'dompurify';
const formcss = {
  invalid: 'input-invalid',
  inputvalidate: 'input-valid',
}
import {
  domselectors,
  css
} from '../modules/modules-config.js';
import {
  fetchSettings,
  decode_HTMLEntities
} from '../modules/utils.js';
domselectors["captcha"] = '.js-captcha';

export class FormSubmit {
  handlers = [];
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

    this.form.querySelectorAll('input[data-match]').forEach(input => {
      //
      const match = input.dataset.match;
      if (!match) return;
      const target = document.getElementById(match);
      if (!target) return;
      const invalid = (input.dataset.matchinvalid) ? input.dataset.matchinvalid : "no match";
      const check_match = (item, itemtarget) => {
        const label = (input.previousElementSibling && input.previousElementSibling.tagName.toLowerCase() == 'label') ? input.previousElementSibling : null;
        const labeltarget = (target.previousElementSibling && target.previousElementSibling.tagName.toLowerCase() == 'label') ? target.previousElementSibling : null;
        const {
          patternMismatch = false
        } = item.validity;
        const customvalidity = (patternMismatch) ? this.get_message(item, 'invalid') : ``;
        if (item.checkValidity() === true) {
          item.dataset.invalid = '';
          item.setCustomValidity('');
          if (item == input && label !== null) label.classList.remove(formcss.invalid);
          else if (labeltarget !== null) labeltarget.classList.remove(formcss.invalid);
          item.classList.remove(formcss.inputvalidate);
          if (item.value !== itemtarget.value) {
            input.setCustomValidity(invalid);
            if (label) {
              label.dataset.invalid = (label.dataset.invalid) ? label.dataset.invalid : invalid;
              label.classList.add(formcss.invalid);
            }
            input.classList.add(formcss.inputvalidate);
          } else {
            input.setCustomValidity("");
            if (label) label.classList.remove(formcss.invalid);
            input.classList.remove(formcss.inputvalidate);
          }
        } else {
          item.setCustomValidity(customvalidity);
          item.dataset.invalid = customvalidity;
          if (label) label.classList.add(formcss.invalid);
          item.classList.add(formcss.inputvalidate);
        }
        item.focus();
      };
      [input, target].forEach(item => {
        item.addEventListener('keyup', (e) => {
          const itemtarget = (item === input) ? target : input;
          check_match(item, itemtarget);
        });
      });

    });
  }
  get_message(field, type = 'invalid') {
    if (field.checkValidity() == false) {
      const {
        valueMissing = true
      } = field.validity;
      if (valueMissing) return `* ` + ((field.dataset.required) ? field.dataset.required : ((this.form.dataset.required) ? this.form.dataset.required : 'required'));
      else return (field.dataset[type]) ? field.dataset[type] : 'input invalid';
    } else return '';
  }

  validateField(field, init = false) {



    if (['textarea', 'input'].indexOf(field.tagName.toLowerCase()) >= 0) {

    }

    if (['select', 'input[type="checkbox"]'].indexOf(field.tagName.toLowerCase()) >= 0) {
      field.querySelectorAll('option:checked').forEach(option => {
        option.value = decode_HTMLEntities(DOMPurify.sanitize(option.value));
      });

    } else field.value = decode_HTMLEntities(DOMPurify.sanitize(field.value));

    const rep = field.checkValidity();
    const label = this.getFieldLabel(field);
    if (label) {
      if (rep) {
        label.classList.remove(formcss.invalid);
      } else if (!rep) {
        label.dataset.invalid = this.get_message(field);
        label.classList.add(formcss.invalid);
        window.scrollTo({
          top: parseInt(label.offsetTop),
          left: parseInt(label.offsetLeft),
          behavior: 'smooth'
        });
      }
    }
    return rep;
  }
  getFieldLabel(field) {
    return (field.closest('.form-box')) ? ((field.closest('.form-box').querySelector('.label')) ? field.closest('.form-box').querySelector('.label') : field.closest('.form-box').querySelector('label')) : null;
  }
  validateFields(init = false) {
    //todo: complete validation foreach field type
    let resp = true;
    // .required input for tom-select component

    [...this.form.elements].forEach(field => {
      if (field.name) {
        if (init === true) {
          if (!field.dataset.listen) {
            if (field.hasAttribute('required') && field.required) {
              const label = this.getFieldLabel(field);
              if (label) label.classList.add('required');
            }

            ['change', 'blur'].forEach(evt => {
              field.addEventListener(evt, (e) => {
                this.validateField(e.currentTarget, init);
              });
            });
            field.dataset.listen = true;
          }
        } else resp = (resp && this.validateField(field, init));

      }
    });
    // add/remove error class on tabs tab-control elements

    this.tabs.forEach(tab => {
      if (tab.querySelector(':invalid') || tab.querySelector(domselectors.component.alert.danger)) tab.classList.add(css.error);
      else tab.classList.remove(css.error);
    });
    return resp;
  }

  addHandler(handler) {
    this.handlers.push(handler);
  }
  fieldEnable(enable = true) {
    this.form.querySelectorAll('input[data-sub="enable"]').forEach(input => {
      if (enable === true) {
        input.disabled = false;
      } else input.disabled = true;
    });
  }

  async submitHandler() {
    if (!this.validateFields()) return false;

    if (this.handlers.length === 0) return true;
    let resp = true;
    // series
    /*  for (const handler of this.handlers) {
          const rep = await handler()
          resp = (resp && rep)
      }*/
    // concurrent
    await Promise.all(this.handlers.map(async handler => {
      const rep = await handler();
      resp = (resp && rep);
    }));
    if (resp === true) this.handlers = [];
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
    if (this.validateFields(false)) {
      const isbot = (this.form.querySelector(domselectors.captcha)) ? (this.form.dataset.isbot ? (this.form.dataset.isbot === true) : true) : false;
      if (isbot === true) return false;
      const yessubmit = await this.submitHandler();
      if (yessubmit) {
        if (this.options.fetch) this.formFetch(this.options.fetch);
        else this.form.submit();
        this.form.disabled = true;
        return true;
      } else return false;
    } else return false;
  }

  displayResponse(response, error = false) {
    const el = document.createElement('div');
    el.insertAdjacentHTML('afterbegin', response);
    if (error !== false) el.classList.add('is-error');
    this.form.parentElement.insertBefore(el, this.form);
    this.form.remove();
  }
}