import validator from 'validator';
import DOMPurify from 'dompurify';
let instance = null;
const formcss = {
  invalid: 'invalid',
  inputvalidate: 'input-validate',
  togglepw: 'togglepw',
  pw: 'pw'
}
import {
  fetchSettings,
} from '../modules/utils.js';
export class FormSubmit {
  handlers = [];
  form = null;
  listener = null;
  constructor(form, options = {}) {
    if (!instance) {
      if (!form) return;
      this.form = form instanceof HTMLElement ? form : document.querySelector(form);
      const defaultOptions = {
        fetch: null,
      };
      options = Object.assign(options, this.form.dataset);
      this.options = Object.assign(defaultOptions, options);
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
      e.preventDefault();
      const res = await this.submitForm();

    });
    if (this.form.dataset.captcha) {
      const captchakey = this.form.dataset.captchakey;
      if (!captchakey) return;
      const captchacode = document.getElementById(captchakey);
      const captcharesponse = this.form.dataset.captcha;
      captchacode.addEventListener('load', (e) => {
        //
        const onloadCallback = function() {
          grecaptcha.render('g-recaptcha', {
            'sitekey': captchakey
          });


        }
        window.onloadCallback = onloadCallback;
        //
        /*
                grecaptcha.ready(function() {
                  grecaptcha.render(captcharesponse, {
                    "sitekey": captchakey
                  });
                  grecaptcha.execute(captchakey, {
                    action: 'createuser'
                  }).then(function(token) {
                    // Add your logic to submit to your backend server here.
                    console.log('token ', token)
                    document.getElementById(captcharesponse).value = token;
                  });
                });
              });*/


      });
      /*const captcha_handler = function() {
        return true;
      }
      this.handlers.push(captcha_handler);*/
    }
    this.specialFields();
  }
  specialFields() {
    // check if there is a password confirm input
    // add show text for password fields
    this.form.querySelectorAll('input[type="password"]').forEach(input => {
      const view = document.createElement('i');
      view.classList.add(formcss.togglepw);
      view.classList.add(formcss.pw);
      input.parentNode.insertBefore(view, input.nextSibling);
      view.addEventListener('click', () => {
        if (input.type === "password") input.type = "text";
        else input.type = "password";
        view.classList.toggle(formcss.pw);
      })
    })

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
        const customvalidity = (patternMismatch) ?
          this.get_message(item, 'invalid') : '';
        if (item.checkValidity() === true) {
          item.dataset.invalid = '';
          item.setCustomValidity("");
          if (item == input) label.classList.remove(formcss.invalid);
          else labeltarget.classList.remove(formcss.invalid);
          item.classList.remove(formcss.inputvalidate);
          if (item.value !== itemtarget.value) {
            input.setCustomValidity(invalid);
            input.dataset.invalid = invalid;
            if (label) label.classList.add(formcss.invalid);
            input.classList.add(formcss.inputvalidate);
          } else {
            input.setCustomValidity("");
            input.dataset.invalid = "";
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
      if (valueMissing) return (field.dataset.required) ? field.dataset.required : ((this.form.dataset.required) ? this.form.dataset.required : 'required');
      else return (field.dataset[type]) ? field.dataset[type] : 'input invalid';
    } else return '';
  }

  validateField(field, init = false) {



    if (['textarea', 'input'].indexOf(field.tagName.toLowerCase()) >= 0) {

    }
    if (['select', 'input[type="checkbox"]'].indexOf(field.tagName.toLowerCase()) >= 0) {
      field.querySelectorAll('option:checked').forEach(option => {
        option.value = DOMPurify.sanitize(option.value);
      });

    } else field.value = DOMPurify.sanitize(field.value);

    const rep = field.checkValidity();

    if (field.classList.contains('select-one')) {
      console.log('select rep', rep);
    }
    const label = field.closest('.form-box') ? field.closest('.form-box').querySelector('label') : null;

    if (rep && label) {
      label.classList.remove(formcss.invalid);
    } else if (!rep) {
      if (label) {
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

  validateFields(init = false) {
    //todo: complete validation foreach field type
    let resp = true;
    // .required input for tom-select component

    [...this.form.elements].forEach(field => {
      if (field.name) {

        if (init === true) {

          if (!field.dataset.listen) {
            if (field.hasAttribute('required') && field.required) {
              const label = field.closest('.form-box') ? field.closest('.form-box').querySelector('label') : field.parentElement.querySelector('label');
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
    return resp;
  }

  addHandler(handler) {
    this.handlers.push(handler);
  }
  fieldEnable(enable = true) {
    this.form.querySelectorAll('input[data-sub="enable"]').forEach(input => {
      if (enable === true) input.removeAttribute('disabled');
      else input.disabled = true;
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
      });
    return false;
  }

  async submitForm() {
    if (this.validateFields(false)) {
      const yessubmit = await this.submitHandler();
      if (yessubmit) {
        this.fieldEnable();
        if (this.options.fetch) this.formFetch(this.options.fetch);
        else this.form.submit();
        this.fieldEnable(false);
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