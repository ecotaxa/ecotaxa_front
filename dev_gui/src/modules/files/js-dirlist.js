import {
  dom_purify,
  fetchSettings,
  create_box,
  dirseparator,
  urlseparator,
  add_custom_events,
  stop_on_error
}
from '../../modules/utils.js';
import {
  css,
} from '../../modules/modules-config.js';
const filter_files = {
  images: "png,jpeg,jpg,gif",
  tsv: "txt,tsv,zip, gzip,gz"
}

const eventEntry = new CustomEvent('eventEntry', {
  detail: () => {
    console.log('customevent', this.entry)
  },
})
const defaultOptions = {
  api_parameters: {
    entry: 'entry',
    dest: 'dest'
  },
  url: '/gui/files',
  controls: {
    scan: {
      display: {
        counter: 'counter',
        size: 'size',
      }
    },
    zip: {
      btn: {
        zip: 'makezip',
        zipped: 'makezipped'
      },
      display: {
        size: 'sizezipped',
        counter: 'counterzipped',
      }
    },

  },
  upload: {
    label: 'upload'
  },
  btnprefix: 'btn',
  btnfilelist: null,
  entry: {
    selector: '[data-name]',

    tags: {
      tag: 'ul',
      subtag: 'li',
      label: 'span'
    },
    selectors: {
      entries: '.entries'
    },
    draggable: true,
    prefix: `entry`,
    type: {
      root: "R",
      trash: "T",
      directory: "D",
      file: "F",
      trashed: "X",
    },
    specialdirs: ["R", "T"],
    trash_dir_name: 'trash.',
    css: {
      on: 'on',
      entryF: 'entryF',
      entryD: 'entryD',
      entryR: 'entryR',
      entryT: 'entryT',
      editable: 'editable',
      dragging: 'dragging',
      dragover: 'dragover',
      dragitem: 'dragitem'
    },
    icons: {
      image: 'img',
      document: 'doc'
    },
  },
  entrycontrols: {
    selectors: {
      typentries: '[data-typentries]',
      hascontrols: '.has-controls',
    },
    controls: {
      list: {
        action: 'list',
        typentries: ['D', 'R', 'T']
      },
      create: {
        action: 'create',
        text: 'new folder',
        icon: 'icon-folder-plus-sm',
        typentries: ['D', 'R']
      },
      remove: {
        action: 'remove',
        text: 'delete',
        icon: 'icon-trash-sm',
        typentries: ['D', 'F', 'X']
      },
      move: {
        action: 'move',
        typentries: ['D', 'F']
      },
      rename: {
        action: 'rename',
        trigger: 'dblclick',
        typentries: ['D', 'F']
      }
    },
    css: {
      entrycontrols: 'entrycontrols',
      entries: '.entries',
    }
  },
  selectors: {
    doupload: '.target-upload',
    droptarget: '.droptarget',
    dirlist: '.dirlist',
    uploadfile: 'uploadfile',
    displayresult: 'results',
    trigger: '.trigger',
  },
}
class Entry {
  _events;
  eventnames;
  name;
  type;
  label;
  entries = [];
  options = {
    selector: '[data-name]',
    tags: {
      tag: 'ul',
      subtag: 'li',
      label: 'span'
    },
    selectors: {
      entries: '.entries'
    },
    css: {
      on: 'on',
    },
    draggable: true,
    prefix: `entry`,
  };

  constructor(entry, options = {}) {
    this.name = entry.name;
    this.type = entry.type;
    this.root = options.root;
    this.parent = (options.parent) ? options.parent : null;
    this.options = Object.assign(this.options, defaultOptions);
    this.options = Object.assign(this.options, options);
    this.label = (options.label) ? options.label : null;
    this.init(entry);
    return this;
  }
  init(entry) {
    //
    add_custom_events(this);
    const dataset = {
      name: this.name,
      type: this.type
    }
    if (this.label !== null) dataset.label = this.label;
    const el = create_box(this.options.tags.subtag, {
      draggable: this.options.draggable,
      dataset: dataset,
    });
    const cl = (this.options.class) ? this.options.class : [];
    cl.unshift(`${this.options.prefix}${this.type}`);
    this.label = create_box(this.options.tags.label, {
      class: cl,
      text: (entry.label) ? entry.label : entry.name
    }, el);
    this.container = el;
    this.initEvents();
  }
  initEvents() {
    Object.entries(this.options.actions).forEach(([key, action]) => {
      this.on(action, (e) => {
        this[key](e);
      });
    });
  }
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
    if (entry.parent) {
      const n = entry.parent.entries.indexOf(entry);
      delete entry.parent.entries[n];
    }
    entry.parent = this;
    this.entries.push(entry);
    const parent = this.getEntriesElement(true);
    parent.append(entry.container);
    return entry;
  }
  createEntry(entry) {
    const new_entry = new Entry(entry);
    this.appendEntry(new_entry);
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
  isOn() {
    return this.active;

  }

  toggleOn() {
    this.active = !(this.active);
    this.container.classList.toggle(this.options.css.on);
  }
  setOff() {
    this.active = false;
    this.container.classList.remove(this.options.css.on);
  }
  emitEvent(action = null, ev = null) {
    const self = this;
    const detail = {
      entry: self,
    }
    if (action) detail.action = action;
    if (ev) detail.event = ev;
    eventEntry.initCustomEvent('eventEntry', true, true, detail);
    window.dispatchEvent(eventEntry);
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
  handleDrop(e) {
    e.stopPropagation();
  }
  addListeners() {
    let func = (e) => {
      e.stopImmediatePropagation();
      this.dirControls(() => {
        this.emitEvent(this.eventnames.attach);
      });
    };
    let listeners = []
    if ([this.options.type.root, this.options.type.trash].indexOf(this.type) < 0) {
      listeners = this.moveHandlers();
      if (this.type === this.options.type.file) {
        func = (e) => {
          e.stopImmediatePropagation();
          this.toggleOn();
          this.emitEvent();
        }
      } else if (this.isInTrash()) {
        this.type = this.options.type.trashed;
      } else listeners = listeners.concat(this.dropHandlers());
      this.listenRename();
    } else listeners = listeners.concat(this.dropHandlers());
    listeners.unshift({
      name: 'click',
      target: 'label',
      func: func
    });
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
    if (this.container.classList.contains(this.options.css.dragging)) this.container.classList.remove(this.options.css.dragging);
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

  unMove() {
    if (this.from) {
      this.move(this.from);
      this.from.container.append(this);
      this.from = null;
    }
  }
}

class EntryAction extends Entry {
  eventnames = {
    attach: 'attach',
    detach: 'detach',
    istrashdir: 'istrashdir',
    trashed: 'trashed',
  }
  isTrashDir(name = null) {
    return ((name === null) ? this.name : name).indexOf(this.options.trash_dir_name) === 0;
  }
  isInTrash(path = null) {
    path = (path === null) ? this.getCurrentDirPath() : path;
    if (path === null) stop_on_error('path_not_found');
    path = path.split(dirseparator);
    return (path.length > 1 && path[0].indexOf(this.options.trash_dir_name)) === 0;
  }

  setWait() {
    this.loaded = this.container.dataset.loaded = false;
    this.container.classList.add('wait');
  }
  setLoaded() {
    this.container.classList.remove('wait');
    this.loaded = this.container.dataset.loaded = true;
  }

  dirControls(callback = null) {
    const el = this.container;
    if (el.dataset.action === "create") return;
    this.toggleOn();
    if (this.isOn()) this.dirActivate(callback).then(() => {
      this.emitEvent();
    });

  }

  async dirActivate(callback = null) {
    if (!this.loaded) this.list().then(() => {
      if (callback) callback(this);
    });
    else if (callback) callback(this);
  }

  getCurrentDirPath() {
    const current_path = (entry, dirs = []) => {
      if (entry.name) {
        dirs.push(entry.name);
        entry = entry.getParent();
        if (entry !== null) return current_path(entry, dirs);
      }
      return dirs;
    }
    let dirs = current_path(this);
    if (dirs.length > 1) dirs = dirs.reverse();
    return dirs.join(dirseparator);
  }

  async fetchAction(action, callback = null, callback_error = null) {
    const api_parameters = this.options.api_parameters;
    const label = this.getLabelElement();
    let entrypath = this.getCurrentDirPath();
    if (entrypath === '') return;
    const data = new FormData();
    data.append(api_parameters.entry, entrypath);
    switch (action) {
      case this.options.actions.create:
        if (label === null) return;
        entrypath = entrypath.split(dirseparator);
        entrypath[entrypath.length - 1] = label.textContent;
        if (entrypath !== "") data.set(api_parameters.entry, entrypath.join(dirseparator));
        break;
      case this.options.actions.move:
        // get new path - append item to drop directory
        if (callback !== null) {
          let destpath = callback();
          callback = null;
          if (destpath === entrypath) {
            console.log('dest = entry', destpath);
            return;
          }
          data.append(api_parameters.dest, destpath);
        } else return;
        break;
      case this.options.actions.rename:
        const destpath = entrypath.split(dirseparator);
        destpath[destpath.length - 1] = label.textContent;
        if (destpath.join(dirseparator) === entrypath) return;
        data.append(api_parameters.dest, destpath.join(dirseparator));
        break;
    }
    const response = await fetch(this.options.url + urlseparator + action, fetchSettings({
      method: "POST",
      body: data
    }));
    const json = await response.json();
    if (json.status === 200) {
      if (callback) callback(json.message);
      return true;
    } else {
      if (callback_error) callback_error(json);
      else stop_on_error(json);
    }
  }
  listenRename(evt = 'dblclick') {

    const entry = this;
    const label = entry.getLabelElement();
    label.addEventListener(evt, (e) => {
      if (this.type === this.options.type.trash) {
        e.preventDefault();
        return;
      }
      const send_rename = async (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          label.contentEditable = false;
          entry.container.draggable = (this.options.specialdirs.indexOf(entry.type) < 0);
          const callback = (txt) => {
            label.classList.remove(entry.options.css.editable);
            if (txt === "") window.alertbox.addItemMessage(label, {
              type: 'error',
              content: window.alertbox.i18nmessages.exists,
              duration: 2000
            });
            else txt = txt.split(dirseparator).pop();
            label.removeEventListener('keydown', send_rename);
            label.textContent = txt;
            if (entry.type === entry.options.type.directory) entry.dirControls();
            delete entry.container.dataset.action;
          }
          const action = (entry.container.dataset.action) ? entry.container.dataset.action : entry.options.actions.rename;
          await entry.fetchAction(action, callback);
        }
      }
      label.contentEditable = true;
      entry.container.draggable = false;
      label.classList.add(entry.options.css.editable);
      label.addEventListener('keydown', send_rename);
    });
  }

  createEntry(entry) {
    const ext = entry.name.split('.').pop();
    const options = this.options;
    options.draggable = (options.specialdirs.indexOf(entry.type) < 0);
    options.class = [];
    if (this.isTrashDir(entry.name)) entry.type = this.options.type.trash;
    const cl = (entry.type === options.type.file) ? (filter_files.images.split(',').indexOf(ext) >= 0) ? options.icons.image : options.icons.document : null;
    if (cl !== null) options.class.push(cl);
    const new_entry = new EntryAction(entry, options);
    this.appendEntry(new_entry);
    new_entry.addListeners();
    if (entry.type === this.options.type.trash) new_entry.emitEvent(this.eventnames.istrashdir);
    return new_entry;
  }
  findEntry(name, type) {
    const entries = this.getEntries();
    for (const entry of entries) {
      if (entry.name === name && entry.type === type) return entry;
    }
    return null;
  }
  async list() {
    if (this.type === this.options.type.file) return;
    const tag = this.options.tags.tag;
    const subtag = this.options.tags.subtag;
    const subdir = (this.name) ? this.getCurrentDirPath() : null;
    this.setWait();
    this.removeEntries();
    const fetchoptions = {
      headers: new Headers({
        'content-type': 'application/json'
      })
    }
    const response = await fetch(this.options.url + urlseparator + this.options.actions.list + ((subdir) ? dirseparator + subdir : ''), fetchSettings(fetchoptions));
    const json = await response.json();
    if (response.ok) {
      if (json.entries && json.entries.length) {
        let files = [],
          directories = [],
          entries = json.entries;
        while (entries.length > 0) {
          const entry = entries.shift();
          if (entry.type === this.options.type.file) files.push(entry);
          else directories.push(entry);
        };
        files.sort((a, b) => (a.name < b.name));
        directories.sort((a, b) => (a.name < b.name));
        this.createListEntries([directories, files]);
      }
      this.setLoaded();
    } else {
      window.alertbox.addItemMessage({
        parent: this.container,
        type: "error",
        content: json.error + ' ' + json.text
      })
    }

  }
  remove() {
    if (this.isTrashDir()) return;

    this.fetchAction(this.options.actions.remove).then(ret => {
      this.setParent(null);
      this.removeListeners(this.dropHandlers());
      this.setOff();
      this.container.animate({
        transform: "translateX(-100%) scale(0)"
      }, {
        duration: 1000
      });
      setTimeout(() => {
        if (this.isInTrash(this.from)) this.destroy();
        else this.emitEvent(this.eventnames.trashed);
      }, 1000);

    });
  }
  create() {
    const new_entry = this.createEntry({
      type: 'D',
      name: 'NewFolder'
    });
    // move new entry to top of the list
    const entries = this.getEntriesElement();
    entries.prepend(new_entry.container);
    new_entry.container.dataset.action = this.options.actions.create;
    new_entry.label.dispatchEvent(new Event('dblclick'));
  }
  rename() {
    if (this.isTrashDir()) return;
    this.fetchAction(this.options.actions.rename).then(() => {
      console.log('renamed', this)
    });
  }

  move(dest, callback = null) {
    if (this.isTrashDir()) return;
    if ([this.options.type.trash, this.options.type.trashed].indexOf(dest.type) >= 0) return this.remove();
    this.fetchAction(this.options.actions.move, () => {
      return dest.getCurrentDirPath() + dirseparator + this.name;
    }).then(() => {
      this.setParent(dest);
      if (callback !== null) callback();
    }).catch(err => {
      console.log('errmove', err)
    });
  }
  setParent(dest) {
    this.from = this.getCurrentDirPath();
    if (dest !== null) {
      dest.entries.push(this);
      this.parent = dest;
      const entries = dest.getEntriesElement(true);
      entries.append(this.container);
    }
    const i = this.parent.entries.indexOf(this);
    if (i >= 0) delete this.parent.entries[i];
    else console.log('entry not found in parent entries', this.parent);

  }
}

class JsEntryControls {
  _events = {};
  eventnames = {
    control: 'control',
    error: 'error',
  }
  options = defaultOptions.entrycontrols;
  box;
  container;
  entry = null;
  constructor(container = document, options = {}) {
    if (!container.jsentrycontrols) {
      this.options = Object.assign(this.options, options);
      this.container = container;
      this.entry = null;
      this.init();
      container.jsentrycontrols = this;
    }
    return container.jsentrycontrols;
  }
  init() {
    add_custom_events(this);
    this.box = this.createControls();
    this.initEvents();

  }
  createControls() {
    const box = create_box('div', {
      class: [this.options.css.entrycontrols, css.hide]
    });
    Object.values(this.options.controls).filter(control => (control.icon || control.text)).forEach(control => {
      const ctrl = create_box('span', {}, box);
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
        if (this.entry === null) return;
        const detail = {
          callback: () => {
            console.log('done', control.action);
          }
        }
        this.entry.emit(control.action, detail);
      }
      ctrl.addEventListener(evt, func);
      //
      control.ctrl = ctrl;
    });
    return box;
  }
  initEvents() {}
  detachControls() {
    if (this.entry === null) return;
    this.entry.container.classList.remove(this.options.selectors.hascontrols.substr(1));
    this.box.classList.add(css.hide);
    this.box.disabled = true;
    this.container.append(this.box);
    this.entry = null;
  }

  attachControls(entry) {
    this.detachControls();
    this.entry = entry;
    this.entry.container.prepend(this.box);
    this.entry.container.classList.add(this.options.selectors.hascontrols.substr(1));
    this.activateControls();
    this.box.classList.remove(css.hide);
    delete this.box.disabled;
  }

  activateControls() {
    if (this.entry === null) return;
    // add btns
    const isintrash = this.entry.isInTrash();
    Object.values(this.options.controls).filter(control => (control.icon || control.text)).forEach(control => {
      const ctrl = control.ctrl;
      const typentries = (ctrl.dataset.typentries) ? ctrl.dataset.typentries.split(',') : [];
      const type = (isintrash) ? this.entry.options.type.trashed : this.entry.container.dataset.type;
      if (typentries.indexOf(type) >= 0) {
        ctrl.classList.remove(css.hide);
      } else ctrl.classList.add(css.hide);
    });
    //
  }
}

class JsDirList {
  _events = {};
  eventnames = {
    attach: 'attach',
    detach: 'detach',
    action: 'action',
    complete: 'complete',
    error: 'error',
  }
  options = defaultOptions;

  constructor(parent, options = {}) {
    if (!parent.jsdirlist) {
      parent = (parent instanceof HTMLElement) ? parent : document.querySelector(parent);
      if (!parent) return;
      this.options = Object.assign(this.options, options);
      this.options.entry.url = this.options.url;
      this.container = create_box(this.options.entry.tags.tag, {
        class: this.options.selectors.dirlist.substr(1)
      }, parent);
      this.init();
      this.container.append(this.root.container);
      parent.jsdirlist = this;
    }
    return parent.jsdirlist;
  }

  init() {
    add_custom_events(this);
    const type = this.options.entry.type.root;
    const obj = {};
    this.entrycontrols = (this.options.controls) ? new JsEntryControls(this.container, this.options.entrycontrols) : null;
    Object.entries(this.options.entrycontrols.controls).forEach(([key, control]) => {
      obj[key] = control.action;
    });
    this.options.entry.actions = obj;
    this.initEvents();
    const options = this.options.entry;
    options.draggable = false;
    this.root = new EntryAction({
      type: type,
      name: '',
      label: '..',
      root: this
    }, options);

    this.root.addListeners();

  }
  initEvents() {
    // events controls on entries
    const self = this;
    // alerts on error
    this.on(this.eventnames.error, (e) => {
      console.log('dirlist receive error message', e)
      if (window.alertbox) {
        window.alertbox.renderAlert({
          type: window.alertbox.alertconfig.types.error,
          content: e,
          inverse: true,
          dismissible: true
        });
      }
    });
    window.addEventListener('eventEntry', (e) => {
      const eventnames = e.detail.entry.eventnames;
      switch (e.detail.action) {
        case eventnames.istrashdir:
          if (this.trashdir) this.trashdir.container.remove();
          this.trashdir = e.detail.entry;
          this.root.container.parentElement.insertBefore(e.detail.entry.container, this.root.container);
          break;
        case eventnames.trashed:
          let parent = e.detail.entry.parent;
          if (e.detail.entry.isInTrash(e.detail.entry.from)) {
            parent = this.root;
          } else {
            this.moveEntry(e.detail.entry, this.trashdir);
            e.detail.entry.container.classList.add('bg-danger-100');
          }
          this.attachControls(parent);
          break;
        case eventnames.attach:
          // no upload on trash dir
          const type = (e.detail.entry.isInTrash()) ? e.detail.entry.options.type.trashed : e.detail.entry.container.dataset.type;
          if (type === e.detail.entry.options.type.trash) return;
          if (e.detail.action === eventnames.attach && type === e.detail.entry.options.type.trashed) return;
          this.attachControls(e.detail.entry);
          break;
        case "dragstart":
          this.dragentry = this.activentry = e.detail.entry;
          e.detail.entry.container.classList.add(e.detail.entry.options.css.dragging);
          this.detachControls();
          break;
        case "dragover":
          if (!this.dragentry) return;
          if (this.overitem !== e.detail.entry.container) {
            if (this.overitem) this.overitem.classList.remove(e.detail.entry.options.css.dragover);
            e.detail.entry.container.classList.add(e.detail.entry.options.css.dragover);
            this.overitem = e.detail.entry.container;
          }
          break;
        case "dragend":
          this.dragentry = null;
          if (this.overitem) this.overitem.classList.remove(e.detail.entry.options.css.dragover);
          this.overitem = null;
          break;
        case "drop":
          if (!this.dragentry) {
            this.emit(this.eventnames.action, e);
            return true;
          } else {
            console.log(' dragentry drop', e.detail.entry.name);
          }
          //e.stopPropagation();
          const el = this.dragentry.container;
          const dest_entry = e.detail.entry;
          dest_entry.resetDragOver();
          if (this.dragentry !== null) {
            if (this.dragentry.options.actions.move) {
              try {
                this.dragentry.move(dest_entry);
                if ([this.dragentry.options.type.trashed].indexOf(dest_entry.type) >= 0) this.attachControls(dest_entry);
              } catch (error) {
                console.log('errordrop ', error)
                this.dragentry.unMove();
              }
            } else console.log('noactionon drop');

          } else console.log(' parent===null or dragitem===null or dragitem===parent', this.dragentry)

          break;
        default:
          if (e.detail.entry.active) {
            this.attachControls(e.detail.entry);
          } else this.attachControls(this.root);
          break;
      }
    });
  }
  moveEntry(entry, dest) {
    entry.from = entry.getCurrentDirPath();
    const trdirs = entry.from.split(dirseparator);
    trdirs.pop();
    trdirs.forEach((trdir, index) => {
      const type = (dest.type === dest.options.type.trash) ? dest.options.type.trashed : dest.type;
      let subdest = dest.findEntry(trdir, type);
      if (subdest === null) {
        subdest = dest.createEntry({
          type: entry.options.type.directory,
          name: trdir
        });
      }
      dest = subdest;
    });
    if (dest.findEntry(entry.name, entry.type) === null) dest.appendEntry(entry);
  }
  attachControls(entry) {
    if (this.entrycontrols) this.entrycontrols.attachControls(entry);
    this.activentry = entry;
    this.emit(this.eventnames.attach, {
      entry: this.activentry
    });
  }

  detachControls() {
    const dest = (this.activentry) ? ((this.activentry.parent) ? this.activentry.parent : this.root) : this.root;
    if (this.entrycontrols) this.entrycontrols.attachControls(dest);
    this.activentry = dest;
    this.emit(this.eventnames.attach, {
      entry: dest
    });
  }
}
export {
  JsDirList,
  eventEntry
};