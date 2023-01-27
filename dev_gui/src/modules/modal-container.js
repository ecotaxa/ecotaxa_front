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

      if (trigger.dataset.what === "help") {
        this.modal = document.querySelector('#modal-help', '.modal-help');

      } else if (trigger.dataset.target && trigger.dataset.target !== 'unique') this.modal = document.querySelector('#' + trigger.dataset.target);
      else this.modal = trigger.closest('.modal-container');
      this.modalcontent = this.modal.querySelector('.modal-content');

      this.addListeners();
    }
    return this;
  }
  addListeners() {

    const summary = this.modal.querySelector('summary');
    if (summary) summary.addEventListener('toggle', (e) => {
      const body = document.querySelector('body');
      summary.setAttribute('aria-hidden', (!this.modal.open));
      body.classList.toggle('hidevscroll');
      this.toggleAction(summary);

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
    this.toggleAction(trigger);
    this.openContent(trigger);
  }

  openContent(trigger) {
    if (!trigger.dataset.for) return;

    const siblings = this.getContentSiblings();
    siblings.forEach(sibling => {
      if (sibling !== trigger) sibling.removeAttribute('open');
    });

    this.modal.querySelector('#' + trigger.dataset.for).open = true;
  }


  toggleAction(trigger) {
    const summary = this.modal.querySelector('summary');
    let action = trigger.dataset.action;
    if (!action) return;
    if (trigger.dataset.what) {
      document.querySelectorAll('[data-what="' + trigger.dataset.what + '"]').forEach(sibling => {
        if (sibling !== trigger) sibling.dataset.action = action.replace('close-', '');
      });
    }
    if (trigger.dataset.for) trigger.dataset.action = (action.indexOf('close-') === 0) ? action.replace('close-', '') : 'close-' + action;
    summary.dataset.action = (action.indexOf('close-') === 0) ? action.replace('close-', '') : 'close-' + action;
  }

  dismissModal(erase = false, content = null) {
    if (this.modalcontent) {

      const event = new Event('dismissmodal');
      console.log('js', this.modalcontent.querySelectorAll('.js'))
      this.modalcontent.querySelectorAll('.js').forEach(element => element.dispatchEvent(event));
      if (erase) this.modalcontent.innerHTML = ``;
    }
    if (this.trigger.dataset.for) {
      this.modal.open = false;
      this.toggleAction(this.trigger);
    }

  }

}