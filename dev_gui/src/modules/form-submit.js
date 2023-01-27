import validator from 'validator';
import DOMPurify from 'dompurify';
let instance = null;
export class FormSubmit {
  handlers = [];
  form = null;
  listener = null;
  constructor(form, options = {}) {
    if (!instance) {
      if (!form) return;
      const defaultOptions = {};
      this.options = Object.assign(defaultOptions, options);
      this.form = form instanceof HTMLElement ? form : document.querySelector(form);
      this.validateFields(true);
      instance = this;
    }
    return instance;
  }

  validateField(field) {

    const getMessage = (field) => {
      let message = 'invalid';
      if (field.required) message = (field.dataset.required) ? field.dataset.required : ((this.form.dataset.required) ? this.form.dataset.required : 'invalid');
      if (message === 'invalid') message = (field.dataset.invalid) ? field.dataset.invalid : ((this.form.dataset.invalid) ? this.form.dataset.invalid : 'invalid input');
      return message;
    }
    const rep = field.checkValidity();
    const label = field.closest('.form-box') ? field.closest('.form-box').querySelector('label') : null;

    if (rep && label) label.classList.remove('invalid');
    else if (!rep) {
      if (label) {
        label.dataset.invalid = getMessage(field);
        label.classList.add('invalid');
      }

    }
    if (field.classList.contains('tomselected') && field.nextElementSibling) {
      field.nextElementSibling.classList.add('input-validate');
    } else field.classList.add('input-validate');

    return rep;
  }

  validateFields(init = false) {

    // todo: complete validation foreach field type
    let resp = true;

    this.form.querySelectorAll('input,textarea, select').forEach(field => {
      if (init === true) {
        if (!field.dataset.listen) {
          ['change', 'blur'].forEach(evt => {
            field.addEventListener(evt, (e) => {
              this.validateField(e.currentTarget);
            });
          });
          field.dataset.listen = true;
        }
      } else {
        const rep = this.validateField(field);
        resp = (resp && rep);
      }


    });
    return resp;
  }
  addHandler(handler) {
    this.handlers.push(handler);
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
}