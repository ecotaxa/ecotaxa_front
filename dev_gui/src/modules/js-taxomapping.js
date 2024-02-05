//from css tricks
// used in tables about project stats details
// used in tables imports when cells contains lots of data
// apply mostly to details tags
import DOMPurify from 'dompurify';
const css = {
  line: 'taxoline',
  mapline: 'mapping-line',
  cancel: 'cancel-line',
};
export class TaxoMapping {
  // animation and specific display on accordions list / details tag open
  numlines = 0;

  constructor(line) {
    if (!line instanceof HTMLElement) return;
    if (!line.taxomapping) {
      const keepname = (line.dataset.name) ? line.dataset.name : null;
      if (keepname === null) return null;
      this.keepname = keepname;
      this.init(line);
      line.taxomapping = this;

    }
    return line.taxomapping;
  }


  init(line) {
    if (line.dataset.addline) {
      let controls = {};
      ['select', 'replace'].forEach(selector => {
        controls[selector] = line.querySelector('[name="item-' + selector + '"]');
      });
      this.linecontrols = controls;
      controls = null;
      let btn = line.querySelector('.' + line.dataset.addline);
      btn = (btn === null) ? this.createBtn(line) : btn;
      btn.addEventListener('click', (e) => {
        this.addLine(line);
      });
      this.btn = btn;
    }
    this.beforeSubmit(line);
  }
  createBtn(line) {
    const btn = document.createElement('div');
    btn.classList.add(line.dataset.addline);
    btn.insertAdjacentHTML('afterbegin', `<i class="icon icon-plus-sm block mx-auto"></i>`);
    btn.textContent = (line.dataset.addtext) ? DOMPurify(line.dataset.addtext).sanitize() : 'Add';
    line.append(btn);
    return btn;
  }
  addLine(line) {

    // verify values not "" for select and replace inputs
    let cando = true;
    Object.values(this.linecontrols).forEach(input => {
      const inputvalue = (input.tomselect) ? input.tomselect.items : new String(input.value);

      cando = cando && (inputvalue.length > 0);
    });
    if (cando === false) {
      this.btn.dataset.title = (line.dataset.notselected) ? line.dataset.notselected : 'select values to replace';
      return;
    } else if (this.btn.dataset.title) delete this.btn.dataset.title;
    const newline = document.createElement('div');
    newline.classList.add(css.line);
    newline.classList.add('pb-2');
    this.numlines++;

    Object.values(this.linecontrols).forEach(input => {
      const keep = document.createElement('div');
      keep.classList.add(css.mapline);
      keep.classList.add('mr-2');
      if (input.tomselect) {
        const tsinput = line.querySelector('.ts-control > div');
        keep.dataset.value = input.value;
        keep.textContent = tsinput.textContent;
        keep.dataset.replace = this.numlines;
        input.tomselect.clear(true);
      } else {
        keep.dataset.value = input.options[input.selectedIndex].value;
        keep.textContent = input.options[input.selectedIndex].text;
        newline.dataset.index = input.selectedIndex;
        keep.dataset.select = this.numlines;
        input.options[input.selectedIndex].disabled = true;
        input.selectedIndex = -1;
      }
      input.parentElement.insertBefore(keep, input);
      newline.append(keep);
    });
    this.btnCancel(newline, (line.dataset.cancel) ? line.dataset.cancel : 'cancel');
    line.parentElement.insertBefore(newline, line);
  }

  btnCancel(item, text) {
    const cancel = document.createElement('div');
    cancel.id = 'cancel_' + this.numlines;
    cancel.classList.add(css.cancel);
    ['action', 'name'].forEach(data => {
      delete cancel.dataset[data];
    });
    item.append(cancel);
    cancel.insertAdjacentHTML('afterbegin', `<i class="icon icon-cancel absolute centered"></i>`);
    cancel.addEventListener('click', (e) => {
      this.linecontrols.select.options[item.dataset.index].disabled = false;
      item.remove();
    });
  }

  beforeSubmit(item) {
    const form = item.closest('form');
    if (form === null) return;
    const format_mapping_field = () => {
      let keephidden = form.querySelector('input[name="' + this.keepname + '"]');
      if (keephidden !== null) keephidden.remove();
      keephidden = document.createElement('input');
      keephidden.type = 'hidden';
      keephidden.name = this.keepname;
      let mapping = {};
      form.querySelectorAll('[data-select]').forEach(el => {
        const replace = el.parentElement.querySelector('[data-replace="' + el.dataset.select + '"]');
        if (replace !== null) mapping[el.dataset.value] = replace.dataset.value;
      });
      form.append(keephidden);
      keephidden.value = JSON.stringify(mapping);
      return true;
    };

    if (form.formsubmit) {
      form.formsubmit.addHandler(format_mapping_field);

    } else form.addEventListener('submit', (e) => {
      format_mapping_field();

    });
  }
}