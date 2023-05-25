import validator from 'validator';
import DOMPurify from 'dompurify';
let instance = null;
const formcss = {
  invalid: 'invalid',
  inputvalidate: 'input-validate'
}
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
      if (!this.form) return;
      this.validateFields(true);
      this.init();
      instance = this;
    }
    return instance;
  }
  init() {

    // init the form ( options like beforeunload etc...)
    this.form.addEventListener('submit', async (e) => {
      const res = await this.submitForm();
      e.preventDefault();
    });
    if (this.form.dataset.captcha) {
      const captcha_handler = async function() {
        const token = grecaptcha.getResponse();
        console.log('token ', token)
        document.getElementById('g-recaptcha-response').value = token;
        return true;
      }
      this.handlers.push(captcha_handler);

    }
    this.specialFields();
  }
  specialFields() {
    // check if there is a password confirm input
    this.form.querySelectorAll('input[data-match]').forEach(input => {
      //
      const match = input.dataset.match;
      if (!match) return;
      const target = document.getElementById(match);
      if (!target) return;
      const invalid = (input.dataset.matchinvalid) ? input.dataset.matchinvalid : "no match";
      const label = input.closest('label');
      const check_match = (item, itemtarget) => {
        if (item.value !== itemtarget.value) {
          item.setCustomValidity(invalid);
          itemtarget.setCustomValidity(invalid);
          if (input != item) {
            if (label) label.classList.add(formcss.invalid);
            input.classList.add(formcss.inputvalidate);
          }
        } else {
          item.setCustomValidity("");
          itemtarget.setCustomValidity("");
          item.dataset.invalid = '';
          itemtarget.dataset.invalid = '';
          if (input != item) {
            if (label) label.classList.remove(formcss.invalid);
            input.classList.remove(formcss.inputvalidate);

          }
        }
        item.reportValidity();
        itemtarget.reportValidity();
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

  validateField(field) {

    const get_message = (field, type) => {
      let message = 'invalid';
      if (field.required) message = (field.dataset.required) ? field.dataset.required : ((this.form.dataset.required) ? this.form.dataset.required : 'invalid');
      if (message === 'invalid') message = (field.dataset.invalid) ? field.dataset.invalid : ((this.form.dataset.invalid) ? this.form.dataset.invalid : 'invalid input');
      return message;
    }
    if (['textarea', 'input'].indexOf(field.tagName.toLowerCase()) >= 0) {
      field.value = DOMPurify.sanitize(field.value);
    }

    const rep = field.checkValidity();
    if (field.classList.contains('select-one')) {
      console.log('select rep', rep);
    }
    const label = field.closest('.form-box') ? field.closest('.form-box').querySelector('label') : null;

    if (rep && label) label.classList.remove(formcss.invalid);

    else if (!rep) {
      if (label) {
        label.dataset.invalid = get_message(field);
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

  validateFields(init = false) {
    //todo: complete validation foreach field type
    let resp = true;
    // .required input for tom-select component
    this.form.querySelectorAll('input,textarea, select').forEach(field => {

      if (init === true) {

        if (!field.dataset.listen) {
          if (field.hasAttribute('required') && field.required) {
            const label = field.closest('.form-box') ? field.closest('.form-box').querySelector('label') : field.parentElement.querySelector('label');
            if (label) label.classList.add('required');
          }

          ['change', 'blur'].forEach(evt => {
            field.addEventListener(evt, (e) => {
              this.validateField(e.currentTarget);
            });
          });
          field.dataset.listen = true;
        }
      } else resp = (resp && this.validateField(field));
    });
    return resp;
  }

  addHandler(handler) {
    this.handlers.push(handler);
  }
  fieldEnable() {
    this.form.querySelectorAll('input[data-sub="enable"]').forEach(input => {
      input.removeAttribute('disabled');
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
    console.log('resp', resp)
    return resp;
  }
  async submitForm() {
    if (this.validateFields(false)) {
      const yessubmit = await this.submitHandler();
      if (yessubmit) {
        this.fieldEnable();
        this.form.submit();
      } else return false;
    } else return false;
  }
}