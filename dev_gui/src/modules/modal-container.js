import {
  domselectors,
  css,
  models
} from '../modules/modules-config.js';

export class ModalContainer {
  listener = null;
  trigger = null;
  modal = null;
  modalcontent = null;
  constructor(trigger) {
    const defaultOptions = {};
    // todo search for options in the item data attrs
    if (!this.modal && (!this.trigger || this.trigger !== trigger)) {
      this.trigger = trigger;

      if (trigger.dataset.what === models.help) {
        this.modal = (document.getElementById(domselectors.component.modal.help.substr(1))) ? document.getElementById(domselectors.component.modal.help.substr(1)) : document.querySelector(domselectors.component.modal.help);
      } else if (trigger.dataset.target && trigger.dataset.target !== 'unique') this.modal = document.getElementById(trigger.dataset.target);
      else this.modal = trigger.closest(domselectors.component.modal.modalcontainer);
      this.modalcontent = this.modal.querySelector(domselectors.component.modal.modalcontent);

      this.addListeners();
    }
    return this;
  }
  addListeners() {
    this.modal.addEventListener('toggle', (e) => {
      const open = e.currentTarget.open;
      if (open) document.body.classList.add(css.hidevscroll);
      else document.body.classList.remove(css.hidevscroll);
      const summary = this.modal.querySelector('summary');
      if (summary) {
        summary.setAttribute('aria-hidden', !open);
        this.toggleAction(summary);
      }

    });

  }

  setContent(html) {
    // data have been sanitzed before in other scripts and from the server
    html = html instanceof HTMLElement ? html.outerHTML : html;
    this.modalcontent.innerHTML = html;
    return this.modalcontent;
  }
  getContentSiblings() {
    return this.modal.querySelectorAll('details');
  }
  getBySelector(selector) {
    return this.modal.querySelector(selector);
  }
  modalOpen(trigger) {
    if (!this.modal.open) this.modal.open = true;
    this.openContent(trigger);


  }

  openContent(trigger) {

    if (!trigger.dataset.for) return;
    if (trigger.dataset.close) return this.dismissModal();
    const siblings = this.getContentSiblings();
    siblings.forEach(sibling => {
      if (sibling !== trigger) sibling.removeAttribute('open');
    });
    const paragraph = this.modal.querySelector('#' + trigger.dataset.for);
    if (paragraph) paragraph.open = true;
    else console.log('help ' + trigger.dataset.for+'display error', this.modal);
    this.toggleAction(trigger);
  }


  toggleAction(trigger) {
    const summary = this.modal.querySelector('summary');
    let action = trigger.dataset.action;
    if (!action) return;
    if (trigger.dataset.what) {
      document.querySelectorAll('[data-close]').forEach(sibling => {
        if (sibling !== trigger) delete sibling.dataset.close;
      });
    }
    if (trigger.dataset.for) {
      if (trigger.dataset.close) delete trigger.dataset.close;
      else trigger.dataset.close = true;
    }
  }

  dismissModal(erase = false, content = null) {
    if (this.modalcontent) {
      const event = new Event('dismissmodal');
      this.modalcontent.querySelectorAll('.js').forEach(element => element.dispatchEvent(event));
      if (erase) this.modalcontent.innerHTML = ``;

    }
    if (this.trigger.dataset.for) {
      this.modal.open = false;
      this.toggleAction(this.trigger);
    }

  }

}