import {
  create_box,
  dirseparator,
  urlseparator,
  fetchSettings,
  generate_uuid
}
from '../modules/utils.js';
import {
  css
} from '../modules/modules-config.js';
import {
  AlertBox
} from '../modules/alert-box.js';
import {
  ModuleEventEmitter
} from '../modules/module-event-emitter.js';
export const entryTypes = Object.freeze({
  node: "N",
  branch: "B",
  root: "R",
  discard: "D",
  discarded: "X"
});
export const entryOptions = {
  selector: '[data-name]',
  tags: {
    tag: 'ul',
    subtag: 'li',
    label: 'span'
  },
  selectors: {
    entries: '.entries'
  },
  draggables: [],
  prefix: `entry`,
  css: {
    on: 'on',
    entryN: 'entryN',
    entryB: 'entryB',
    entryR: 'entryR',
    entryD: 'entryD',
    editable: 'editable',
    dragging: 'dragging',
    dragover: 'dragover',
    dragitem: 'dragitem',
    selected: 'selected',
  },
  event: {
    name: 'eventEntry'
  }
};

export class Entry {
  eventnames = {
    attach: 'attach',
    control: 'control'
  };
  name;
  type;
  label;
  entries = [];
  event = {
    listener: window,
    name: entryOptions.event.name,
    init: {
      bubbles: false,
      cancelable: true
    },
  };


  constructor(entry, options = {}) {
    this.name = entry.name;
    this.type = entry.type;
    this.id = entry.id;
    this.parent = entry.parent;
    this.options = { ...entryOptions,
      ...options
    };
    this.uuid = generate_uuid();

    this.eventnames = { ...this.eventnames,
      ...this.options.eventnames
    };
    this.label = (options.label) ? options.label : null;
    this.event = {
      name: entryOptions.event.name,
      listener: (options.listener) ? options.listener : this.uuid
    };
    this.init(entry);
    return this;
  }
  init(entry) {
    const dataset = {
      name: this.name,
      type: this.type
    }
    if (this.label !== null) dataset.label = this.label;
    const el = create_box(this.options.tags.subtag, {
      draggable: this.isDraggable(),
      dataset: dataset,
    });
    const cl = `${this.options.prefix}${this.type}`;
    this.label = create_box(this.options.tags.label, {
      class: cl,
      text: (entry.label) ? entry.label : entry.name
    }, el);
    this.container = el;
    this.initEvents();
  }
  initEvents() {}
  getParent() {
    return this.parent;
  }
  getLabelElement() {
    return this.label;
  }
  getParentElement() {
    return this.container.parentElement.closest(this.options.selector);
  }

  getEntries() {
    return this.entries;
  }
  getEntriesElement(create = false) {
    let entries = this.container.querySelector(this.options.selectors.entries);
    if (create && entries === null) {
      return create_box(this.options.tags.tag, {
        class: this.options.selectors.entries.substr(1)
      }, this.container);
    }
    return entries;
  }

  appendEntry(entry) {
    if (entry.parent && entry.parent.entries) {
      const n = entry.parent.entries.indexOf(entry);
      delete entry.parent.entries[n];
    }
    entry.parent = this;
    this.entries.push(entry);
    const parent = this.getEntriesElement(true);
    parent.append(entry.container);
    return entry;
  }
  /* when extended */
  newEntry(entry) {
    return new Entry(entry, this.options);
  }
  /** extra attr , styles , types  */
  setAttributes(entry) {
    return entry;
  }
  extraStyles(entry) {}
  setDiscard() {}
  /*end extra attr , styles , types  */
  createEntry(entry) {
    this.options.css.icons = [];
    entry = this.setAttributes(entry);
    this.extraStyles(entry);
    const new_entry = this.newEntry(entry, this.options);
    this.appendEntry(new_entry);
    new_entry.addListeners();
    new_entry.setDiscard();
    return new_entry;
  }
  findEntry(name) {
    const entries = this.getEntries();
    for (const entry of entries) {
      if (entry.name === name) return entry;
    }
    return null;
  }
  //
  createListEntries(listentries) {
    const direntry = this.getEntriesElement(true);
    listentries.forEach(entries => {
      entries.forEach((entry) => {
        const new_entry = this.createEntry(entry);
      });
    });
  }
  removeEntries() {
    this.entries = [];
    const el = this.getEntriesElement();
    if (el) el.remove();
  }
  isActive() {
    return this.active;
  }

  toggleActive() {
    this.active = !(this.active);
    this.container.classList.toggle(this.options.css.on);
  }
  setSelected(selected = true) {
    const cl = this.options.css.selected;
    if (selected === true) this.container.classList.add(cl);
    else this.container.classList.remove(cl);
    this.setOn(selected);
  }
  setOn(on = true) {
    this.active = on;
    if (on === true) this.container.classList.add(this.options.css.on);
    else this.container.classList.remove(this.options.css.on);
  }
  setOff() {
    this.setSelected(false);
  }
  getListeners() {
    let listeners = [];
    const self = this;
    let func = (e) => {
      e.stopImmediatePropagation();
      this.branchListener(() => {
        this.emitEvent(this.eventnames.attach);
      });
    };
    if ([entryTypes.root, entryTypes.discard].indexOf(this.type) < 0) {
      if (this.type === entryTypes.node) {
        func = (e) => {
          e.stopImmediatePropagation();
          this.toggleActive();
          this.emitEvent();
        }
      }
    }
    listeners.unshift({
      name: 'click',
      target: 'label',
      func: func
    });
    return listeners;
  }

  isBranch(checkroot = true) {
    const branchtypes = [entryTypes.branch];
    if (checkroot && branchtypes.indexOf(entryTypes.root) < 0) branchtypes.push(entryTypes.root);
    return (branchtypes.indexOf(this.type) >= 0)
  }
  isDiscarded() {
    return ([entryTypes.discard, entryTypes.discarded].indexOf(this.type) >= 0)
  }
  emitEvent(action = null, ev = null) {
    const self = this;
    const detail = {
      entry: self,
    }
    if (action) detail.action = action;
    if (ev) detail.event = ev;
    else ev = this.eventnames.control;
    ModuleEventEmitter.emit(this.event.name, detail, this.event.listener);
  }
  moveHandlers() {
    return [{
      name: 'dragstart',
      func: (e) => {
        this.handleDragStart(e);
      }
    }, {
      name: 'dragend',
      func: (e) => {
        this.handleDragEnd(e);
      }
    }];
  }
  dropHandlers() {
    return [{
      name: 'dragover',
      func: (e) => {
        this.handleDragOver(e);
      }
    }, {
      name: 'drop',
      func: (e) => {
        this.handleDrop(e);
      }
    }];
  }
  branchListener(callback = null) {
    this.toggleActive();
    if (this.isActive()) this.branchActivate(callback).then(() => {
      this.emitEvent();
    });
  }
  addListeners() {
    const listeners = this.getListeners();
    for (const listener of listeners) {
      const el = (listener.target === 'label') ? this.getLabelElement() : this.container;
      el.addEventListener(listener.name, listener.func);
    }
  }
  removeListeners(listeners) {
    for (const listener in listeners) {
      const el = (listener.target === 'label') ? this.getLabelElement() : this.container;
      el.removeEventListener(listener.label, listener.func);
    }
  }
  destroy() {
    this.container.remove();
  }

  handleDragStart(e) {
    e.stopImmediatePropagation();
    this.container.classList.add(this.options.css.dragging);
    e.dataTransfer.effectAllowed = 'move';
    this.emitEvent('dragstart', e);
  }
  handleDragOver(e) {
    e.stopPropagation();
    e.preventDefault();
    this.emitEvent('dragover', e);
    return;
  }
  handleDragEnd(e) {
    e.stopPropagation();
    e.preventDefault();
    this.container.classList.remove(this.options.css.dragging);
    this.emitEvent('dragend', e);
  }
  resetDragOver() {
    document.querySelectorAll('.' + this.options.css.dragover).forEach(el => {
      el.classList.remove(this.options.css.dragover);
    });
  }
  handleDrop(e) {
    /***/
    e.stopImmediatePropagation();
    this.emitEvent('drop', e);
  }
  setWait() {

    this.loaded = this.container.dataset.loaded = false;
    this.container.classList.add(css.wait);
  }
  setLoaded() {
    this.container.classList.remove(css.wait);
    this.loaded = this.container.dataset.loaded = true;
  }
  findEntry(name, type) {
    const entries = this.getEntries();
    for (const entry of entries) {
      if (entry.name === name && entry.type === type) return entry;
    }
    return null;
  }

  async branchActivate(callback = null) {
    if (!this.loaded) this.list().then(() => {
      if (callback) callback(this);
    });
    else if (callback) callback(this);
  }
  getCurrentPath() {
    const current_path = (entry, branchs = []) => {
      if (entry.name) {
        branchs.push(entry.name);
        entry = entry.getParent();
        if (entry !== null) return current_path(entry, branchs);
      }
      return branchs;
    }
    let branchs = current_path(this);
    if (branchs.length > 1) branchs = branchs.reverse();
    return branchs;
  }
  async jsonEntries(response) {
    const json = await response.json();
    return json;
  }
  isDraggable() {
    return (this.options.draggables && this.options.draggables.indexOf(this.type) >= 0);
  }
  async list() {
    if (this.type === entryTypes.node) return;

    const url = (this.getUrl) ? this.getUrl() : null;
    if (url === null) return;
    const tag = this.options.tags.tag;
    const subtag = this.options.tags.subtag;
    this.setWait();
    this.removeEntries();
    const fetchoptions = {
      headers: new Headers({
        'content-type': 'application/json'
      })
    };
    const response = await fetch(url, fetchSettings(fetchoptions));
    if (response.ok) {
      const entries = await this.jsonEntries(response);

      if (entries.length) {
        let nodes = [],
          branches = [];
        while (entries.length > 0) {
          const entry = entries.shift();
          if (entry.children === false) {
            nodes.push(entry);
          } else {
            branches.push(entry);
          }
        };
        nodes.sort((a, b) => (a.name < b.name));
        branches.sort((a, b) => (a.name < b.name));
        this.createListEntries([branches, nodes]);
      }
      this.setLoaded();
    } else {
      AlertBox.addMessage({
        parent: this.container,
        type: "error",
        content: response.error + ' ' + response.text
      })
    }

  }
  moveTo(dest) {
    const branches = dest.getCurrentPath();
    const type = (dest.type === entryTypes.discard) ? entryTypes.discarded : dest.type;
    branches.pop();
    branches.forEach((branch, index) => {
      let subdest = dest.findEntry(branch, type);
      if (subdest === null) {
        subdest = dest.createEntry({
          type: type,
          name: branch
        });
      }
      dest = subdest;
    });
    if (dest.findEntry(this.name, this.type) === null) {
      this.from = this.parent;
      dest.appendEntry(this);
    }
  }
  unMove() {
    if (this.from) {
      this.moveTo(this.from);
      this.from = null;
    }
  }
}
export function EntryControls(container = document, options = {}) {
  const eventnames = {
    control: 'control',
    error: 'error',
  }
  const controloptions = {
    selectors: {
      typentries: '[data-typentries]',
      hascontrols: '.has-controls',
    },
    controls: {
      list: {
        action: 'list',
        typentries: ['B', 'T']
      },
    },
    css: {
      entrycontrols: 'entrycontrols',
      entries: '.entries',
    }
  };
  let box, activentry = null;
  options = Object.assign(controloptions, options);
  init();

  function init() {
    createControls();
    initEvents();
  }

  function addControl(control, position = null, action = null) {
    const ctrl = create_box('span', (control.class)?{class:control.class}:{});
    const l = box.children.length;
    if (position === null || l < position + 1) box.append(ctrl);
    else if (position === 0 || l === 0) box.prepend(ctrl);
    else box.inserBefore(crtl, box.children[position]);
    if (control.typentries) ctrl.dataset.typentries = control.typentries;
    if (control.icon) {
      const icon = create_box('i', {
        class: ['icon', control.icon]
      }, ctrl);
      ctrl.dataset.title = control.text;
    } else ctrl.textContent = control.text;
    //add listener
    const evt = (control.trigger) ? control.trigger : 'click';
    const func = (e) => {
      if (activentry === null) return;
      const detail = {
        callback: () => {
          console.log('done', control.action);
        }
      }

      if (!activentry[control.action] && action !== null) {
        action(activentry);
      } else if (activentry[control.action]) activentry[control.action](detail);
      if (control.callback)  control.callback(e);
    };
    ctrl.addEventListener(evt, func);
    //
    control.ctrl = ctrl;
  }

  function createControls() {
    box = create_box('div', {
      class: [options.css.entrycontrols, css.hide]
    });
    Object.values(options.controls).filter(control => (control.icon || control.text)).forEach(control => {
      addControl(control);
    });
  }

  function initEvents() {}

  function detachControls() {
    if (activentry === null) return;
    activentry.container.classList.remove(options.selectors.hascontrols.substr(1));
    box.classList.add(css.hide);
    box.disabled = true;
    container.append(box);
    activentry = null;
  }

  function attachControls(entry) {

    detachControls();
    activentry = entry;
    activentry.container.prepend(box);
    activentry.container.classList.add(options.selectors.hascontrols.substr(1));
    activateControls();
    box.classList.remove(css.hide);
    delete box.disabled;
  }

  function showControls(show = true) {
    if (show === true) box.classList.remove(css.hide);
    else box.classList.add(css.hide);
    box.disabled = !show;
  }

  function activateControl(control, isdiscarded = false) {
    const ctrl = control.ctrl;
    if (control.exclude && activentry !==null && control.exclude.indexOf(activentry.name)>=0) {ctrl.classList.add(css.hide);return;}
    const typentries = (ctrl.dataset.typentries) ? ctrl.dataset.typentries.split(',') : [];
    const type = (isdiscarded) ? entryTypes.discarded : activentry.container.dataset.type;
    if (typentries.indexOf(type) >= 0) {
      ctrl.classList.remove(css.hide);
    } else ctrl.classList.add(css.hide);
  }

  function activateControls() {
    if (activentry === null) return;
    // add btns
    const isdiscarded = activentry.isDiscarded();
     Object.values(options.controls).filter(control => (control.icon || control.text)).forEach(control => {
     activateControl(control, isdiscarded);
    });
    //
  }
  return {
    options,
    addControl,
    attachControls,
    detachControls,
    showControls,
    activateControls,
    activateControl
  }
}