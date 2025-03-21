import DOMPurify from 'dompurify';
import {
  computePosition,
} from '@floating-ui/dom';
import {
  css
} from '../modules/modules-config.js';
import {
  create_box,
  generate_uuid,
} from '../modules/utils.js';
export const tooltips_eventnames = {
  tooltips: 'tooltips'
};
export class Tooltips {
  /*  activate function */
  _events;

  constructor() {
    this.eventnames = tooltips_eventnames;
    this.initEvents();
    return this;
  }
  initEvents() {


    this.on(this.eventnames.tooltips, (e) => {
      return;
      if (!e.target) return;
      console.log('etarget', e.target.querySelectorAll('[data-title]'));
      e.target.querySelectorAll('[data-title]').forEach(async (item) => {
        let tip;
        if (!item.dataset.tipid) {
          item.dataset.tipid = generate_uuid();
          tip = create_box('div', {
            id: item.dataset.tipid,
            text: item.dataset.title,
            class: css.tip
          });
          item.parentElement.insertBefore(tip, item);
        } else tip = document.getElementById(item.dataset.tipid);
        item.addEventListener('mouseover', () => {
          computePosition(item, tip, {
            placement: 'bottom-start',
            strategy: 'fixed',
          });
          tip.classList.remove(css.hide);
        });
        item.addEventListener('mouseout', () => {
          tip.classList.add(css.hide);
        });
      });
    });
    // dispatch event
  }
}