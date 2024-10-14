import {
  dom_purify,
  fetchSettings,
  create_box,
  dirseparator,
  urlseparator,
  stop_on_error,
  generate_uuid
}
from '../../modules/utils.js';
import {
  css,
} from '../../modules/modules-config.js';
import {
  AlertBox
} from '../../modules/alert-box.js';
import {
  ModuleEventEmitter,
} from '../../modules/module-event-emitter.js';
import {
  entryTypes,
  entryOptions,
  Entry,
  EntryControls
} from '../../modules/entry.js';
const filter_files = {
  images: "png,jpeg,jpg,gif",
  tsv: "txt,tsv,zip, gzip,gz"
}
// local css
css.intrash = 'intrash';
// original types
const json_types = {
  directory: 'D',
  file: 'F'
}
const trash_dir_name = 'trash.';
export const dirlistOptions = {
  api_parameters: {
    entry: 'entry',
    dest: 'dest',
    rootname: 'My Files',
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
    draggables: [entryTypes.branch, entryTypes.node],
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
        typentries: [entryTypes.branch, entryTypes.root, entryTypes.discard]
      },
      create: {
        action: 'create',
        text: 'new folder',
        icon: 'icon-folder-plus',
        typentries: [entryTypes.branch, entryTypes.root]
      },
      remove: {
        action: 'remove',
        text: 'delete',
        icon: 'icon-trash',
        typentries: [entryTypes.branch, entryTypes.node, entryTypes.discarded]
      },
      move: {
        action: 'move',
        typentries: [entryTypes.branch, entryTypes.node]
      },
      rename: {
        action: 'rename',
        trigger: 'dblclick',
        typentries: [entryTypes.branch, entryTypes.node]
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
    displayimport: 'displayimport',
    trigger: '.trigger',
  },
}

function EntryAction(args, options) {
  const entryaction = new Entry(args, options);
  entryaction.eventnames = {
    attach: 'attach',
    detach: 'detach',
    isdiscard: 'isdiscard',
    discarded: 'discarded',
    editable: 'editable'
  };
  entryaction.newEntry = function(entry) {

    return EntryAction(entry, this.options);
  }
  entryaction.isTrashDir = function(name = null) {
    return ((name === null) ? this.name : name).indexOf(trash_dir_name) === 0;
  }
  entryaction.isInTrash = function(path = null) {
    path = (path === null) ? this.getCurrentDirPath() : path;
    if (path === null) stop_on_error('path_not_found');
    path = path.split(dirseparator);
    return (path.length > 1 && path[0].indexOf(trash_dir_name)) === 0;
  }
  entryaction.branchListener = function(callback = null) {
    const el = this.container;
    if (el.dataset.action === "create") return;
    this.toggleActive();
    if (this.isActive()) this.branchActivate(callback).then(() => {
      this.emitEvent();
    });
  }

  entryaction.getCurrentDirPath = function() {
    return this.getCurrentPath().join(dirseparator);
  }

  entryaction.fetchAction = async function(action, callback = null, callback_error = null) {
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
          if (destpath === entrypath) return;
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
      body: data,
    }));
    const json = await response.json();
    if (response.status === 200) {
      if (callback) callback(json.message);
      return true;
    } else {
      if (callback_error) {
        callback_error(json);
      } else {
        if (typeof json.body === 'string') json.body = JSON.parse(json.body);
        const detail = (json.body.detail) ? json.body.detail : json.body;
        AlertBox.addAlert({
          type: "error",
          content: response.status + ' ' + json.text + ' ' + detail,
          dismiss: true
        })
      }
      return false;
    }
  }
  entryaction.listenRename = function(evt = 'dblclick') {
    const entry = this;
    const label = entry.getLabelElement();
    label.addEventListener(evt, (e) => {
      label.dataset.oldname = label.textContent;
      if (this.type === entryTypes.discard) {
        e.preventDefault();
        return;
      }
      entry.setEditable();
    });
    // remove editable when click on entry
    entry.container.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopImmediatePropagation();
      entry.setEditable(false);
      if (entry.container.dataset.action === entry.options.actions.create) entry.container.remove();
    });
  }
  entryaction.setEditable = function(on = true) {
    const entry = this;
    const label = entry.getLabelElement();
    const send_rename = async (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        if (label.dataset.oldname && label.dataset.oldname !== label.textContent) {
          const callback = (txt) => {
            if (txt === "") AlertBox.addMessage(label, {
              type: 'error',
              content: AlertBox.i18nmessages.exists,
              duration: 2000
            });
            else txt = txt.split(dirseparator).pop();
            label.textContent = txt;
            if (entry.type === entryTypes.branch) entry.branchListener();
            delete entry.container.dataset.action;
          }
          const action = (entry.container.dataset.action) ? entry.container.dataset.action : entry.options.actions.rename;
          await entry.fetchAction(action, callback);
        }
        entry.setEditable(false);
      }
    }
    if (on === true) {
      label.contentEditable = true;
      entry.container.draggable = false;
      label.classList.add(entry.options.css.editable);
      label.addEventListener('keydown', send_rename);
    } else {
      label.contentEditable = false;
      label.classList.remove(entry.options.css.editable);
      label.removeEventListener('keydown', send_rename);
      entry.container.draggable = entry.isDraggable();
    }
  }
  entryaction.getListeners = function() {
    let listeners = [];
    let func = (e) => {
      e.stopImmediatePropagation();
      this.branchListener(() => {
        this.emitEvent(this.eventnames.attach);
      });
    };

    if ([entryTypes.root, entryTypes.discard].indexOf(this.type) < 0) {
      listeners = this.moveHandlers();
      if (this.type === entryTypes.node) {
        func = (e) => {
          e.stopImmediatePropagation();
          this.toggleActive();
          this.emitEvent();
        }
      } else if (this.isInTrash()) {
        this.type = entryTypes.discarded;
      } else listeners = listeners.concat(this.dropHandlers());
      this.listenRename();
    } else listeners = listeners.concat(this.dropHandlers());
    listeners.unshift({
      name: 'click',
      target: 'label',
      func: func
    });
    return listeners;
  }
  entryaction.setAttributes = function(entry) {
    // convert attributes
    entry.type = (entry.type === json_types.directory) ? entryTypes.branch : entryTypes.node;
    if (this.isTrashDir(entry.name)) entry.type = entryTypes.discard;
    entry.parent = this;
    return entry;
  }
  entryaction.extraStyles = function(entry) {
    const ext = entry.name.split('.').pop();
    const cl = (entry.type === entryTypes.node) ? (filter_files.images.split(',').indexOf(ext) >= 0) ? this.options.icons.image : this.options.icons.document : null;
  }
  entryaction.setDiscard = function() {
    if (this.type === entryTypes.discard) this.emitEvent(this.eventnames.isdiscard);
  }

  entryaction.getUrl = function() {
    const subdir = (this.name) ? this.getCurrentDirPath() : null;
    return this.options.url + urlseparator + this.options.actions.list + ((subdir) ? dirseparator + subdir : '');
  }
  entryaction.jsonEntries = async function(response) {
    const json = await response.json();
    return (json.entries) ? json.entries : undefined;
  }

  entryaction.remove = function() {
    if (this.isTrashDir()) return;
    this.fetchAction(this.options.actions.remove).then(ret => {
      if (ret === true) {
        this.setParent(null);
        this.removeListeners(this.dropHandlers());
        this.setOff();
        this.container.animate({
          transform: "translateX(-100%) scale(0)"
        }, {
          duration: 1000
        });
        setTimeout(() => {
          if (this.from && this.from.isInTrash()) this.destroy();
          else this.emitEvent(this.eventnames.discarded);
        }, 1000);
      }
    }).catch(error => {
      AlertBox.addMessage({
        parent: this.container,
        type: "error",
        content: error.error + ' ' + error.text
      })
    });
  }
  entryaction.create = function() {
    const new_entry = this.createEntry({
      type: json_types.directory,
      name: 'NewFolder'
    });
    // move new entry to top of the list
    const entries = this.getEntriesElement();
    entries.prepend(new_entry.container);
    new_entry.container.dataset.action = this.options.actions.create;
    new_entry.label.dispatchEvent(new Event('dblclick'));
  }
  entryaction.rename = function() {
    if (this.isTrashDir()) return;
    this.fetchAction(this.options.actions.rename).then(() => {
      console.log('renamed', this)
    });
  }

  entryaction.move = function(dest, callback = null) {
    if (this.isTrashDir()) return;
    if (this.isDiscarded()) return this.remove();
    this.fetchAction(this.options.actions.move, () => {
      return dest.getCurrentDirPath() + dirseparator + this.name;
    }).then(() => {
      this.setParent(dest);
      if (callback !== null) callback();
    }).catch(err => {
      console.log('errmove', err)
    });
  }
  entryaction.setParent = function(dest) {
    this.from = this.parent;
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
  return entryaction;
}

export class JsDirList {
  eventnames = {
    attach: 'attach',
    detach: 'detach',
    action: 'action',
    complete: 'complete',
    error: 'error',
  }
  options;
  uuid;
  constructor(parent, options = {}) {
    if (!parent.jsdirlist) {
      parent = (parent instanceof HTMLElement) ? parent : document.querySelector(parent);
      if (!parent) return;
      this.options = { ...dirlistOptions,
        ...options
      };

      this.options.entry = { ...entryOptions,
        ...this.options.entry,
      };
      this.options.entry.url = this.options.url;
      this.container = create_box(
        this.options.entry.tags.tag, {
          class: this.options.selectors.dirlist.substr(1)
        }, parent);
      // unique id to communicate ModuleEventEmitter
      this.uuid = generate_uuid();
      this.init();
      this.container.append(this.root.container);

      parent.jsdirlist = this;
    }
    return parent.jsdirlist;
  }
  init() {
    const type = entryTypes.root;
    const obj = {};
    this.entrycontrols = (this.entrycontrols === undefined) ? EntryControls(this.container, this.options.entrycontrols) : null;
    Object.entries(this.options.entrycontrols.controls).forEach(([key, control]) => {
      obj[key] = control.action;
    });
    this.options.entry.actions = obj;

    const options = { ...this.options.entry,
      ...{
        api_parameters: this.options.api_parameters
      }
    };
    options.listener = this.uuid;
    this.root = EntryAction({
      type: type,
      name: '',
      label: this.options.api_parameters.rootname,
      class: this.options.api_parameters.rootclass

    }, options);
    this.initEvents();
    this.root.addListeners();
  }

  initEvents(options) {
    // events controls on entries
    const self = this;
    ModuleEventEmitter.on(this.options.entry.event.name, (e) => {
      const evtnames = e.entry.eventnames;
      switch (e.action) {
        case evtnames.isdiscard:
          if (this.trashdir) this.trashdir.container.remove();
          this.trashdir = e.entry;
          this.root.container.parentElement.insertBefore(e.entry.container, this.root.container);
          this.root.container.append(e.entry.container);
          break;
        case evtnames.discarded:
          let parent = e.entry.parent;
          if (e.entry.isInTrash()) {
            e.entry.container.remove();
            parent = this.root;
          } else {
            e.entry.moveTo(this.trashdir);
            e.entry.container.classList.add(css.intrash);
          }
          this.attachControls(parent);
          break;
        case evtnames.attach:
          // no upload on trash dir
          const type = (e.entry.isInTrash()) ? entryTypes.discarded : e.entry.container.dataset.type;
          if (type === entryTypes.discard) return;
          if (e.action === evtnames.attach && type === entryTypes.discarded) return;
          this.attachControls(e.entry);
          break;
        case "dragstart":
          this.dragentry = this.activentry = e.entry;
          e.entry.container.classList.add(e.entry.options.css.dragging);
          this.detachControls();
          break;
        case "dragover":
          if (!this.dragentry) return;
          if (this.overitem !== e.entry.container) {
            if (this.overitem) this.overitem.classList.remove(e.entry.options.css.dragover);
            e.entry.container.classList.add(e.entry.options.css.dragover);
            this.overitem = e.entry.container;
          }
          break;
        case "dragend":
          this.dragentry = null;
          if (this.overitem) this.overitem.classList.remove(e.entry.options.css.dragover);
          this.overitem = null;
          break;
        case "drop":
          if (!this.dragentry) {
            ModuleEventEmitter.emit(this.eventnames.action, e, this.uuid);
          }
          const dest_entry = e.entry;
          dest_entry.resetDragOver();
          if (this.dragentry) {
            if (this.dragentry.options.actions.move) {
              try {
                this.dragentry.move(dest_entry);
                if ([entryTypes.discarded].indexOf(dest_entry.type) >= 0) this.attachControls(dest_entry);
              } catch (error) {
                console.log('errordrop ', error)
                this.dragentry.unMove();
              }
            } else console.log('noactionon drop');
          }
          break;
        case evtnames.editable:
          if (this.editable) this.editable.setEditable(false);
          break;

        default:
          if (e.entry.active) {
            this.attachControls(e.entry);
          } else this.attachControls(this.root);
          break;
      }
    }, this.uuid);
  }

  attachControls(entry) {
    if (this.entrycontrols) this.entrycontrols.attachControls(entry);
    this.activentry = entry;
    ModuleEventEmitter.emit(this.eventnames.attach, {
      entry: this.activentry
    }, this.uuid);
  }

  detachControls() {
    const dest = (this.activentry) ? ((this.activentry.parent) ? this.activentry.parent : this.root) : this.root;
    if (this.entrycontrols) this.entrycontrols.attachControls(dest);
    this.activentry = dest;
    ModuleEventEmitter.emit(this.eventnames.attach, {
      entry: dest
    }, this.uuid);
  }
}