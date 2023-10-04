// not in user
export class JsSearch {
  constructor(trigger) {
    trigger = trigger instanceof HTMLElement ? trigger : document.querySelector(trigger);
    const defaultOptions = {
      target: '_blank',
      parent: document.querySelector('[data-anchor="search"]')
    }
    this.options = Object.assign(defaultOptions, trigger.dataset);
    Object.freeze(this.options);

  }

}