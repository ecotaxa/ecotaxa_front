import treecss from "../css/js-tree.css";
import {
  dom_purify,
  fetchSettings,
  create_box,
  dirseparator,
  urlseparator,
  generate_uuid
}
from '../modules/utils.js';
import {
  css,
} from '../modules/modules-config.js';
css.forminput = 'form-input';
import {
  ModuleEventEmitter
} from '../modules/module-event-emitter.js';
import {
  entryTypes,
  entryOptions,
  eventEntry,
  Entry,
  EntryControls
}
from '../modules/entry.js';
const jstreeOptions = {
  api_parameters: {
    entry: 'entry',
    rootname: ''
  },
  url: '/gui/search/taxotreejson',
  trigger: null,
  entry: {
    root: '#',
    draggable: false,
    tags: {
      tag: 'ul',
      subtag: 'li',
      label: 'span'
    },
    event: {
      name: 'eventEntry'
    }
  },
  entrycontrols: {
    controls: {
      select: {
        action: 'select',
        text: 'select entry',
        icon: 'icon-check',
        typentries: [entryTypes.branch, entryTypes.node],
      },
    },
  },
  selectors: {
    droptarget: 'droptarget',
    tree: 'taxotree',
  },
}

export function JsTree(parent, options = {}) {
  parent = (parent instanceof HTMLElement) ? parent : document.querySelector(parent);
  options = { ...jstreeOptions,
    ...options
  };
  const uuid = generate_uuid();
  if (!parent || parent.querySelector('.' + options.selectors.tree) !== null) return;
  options.entry = { ...entryOptions,
    ...options.entry
  };
  options.entry.url = options.url;
  options.entry.root = (options.root) ? options.root : '#';
  const eventnames = {
    attach: 'attach',
    detach: 'detach',
    action: 'action',
    complete: 'complete',
    error: 'error',
  }
  let selectors = null;
  if (options.selectors) {
    selectors = JSON.parse(options.selectors);
    delete options.selectors;
  }
  if (selectors) options.selectors = selectors;
  options.entry.draggable = false;
  const container = create_box(options.entry.tags.tag, {
    class: options.selectors.tree
  }, parent);
  options.listener = uuid;
  let root, activentry, dragentry, overitem, entrycontrols = null;
  init(parent);
  container.append(root.container);


  function EntryAction(entry, options) {
    const entryaction = new Entry(entry, options);
    entryaction.eventnames = {
      attach: 'attach',
      detach: 'detach',
      select: 'select',
    };
    entryaction.newEntry = function(entry) {
      return EntryAction(entry, this.options);
    }
    entryaction.select = function(entry) {
      console.log('entry selected', entry);
    }
    entryaction.getUrl = function() {
      return this.options.url + '?' + new URLSearchParams({
        id: this.id
      });
    }
    entryaction.setAttributes = function(entry) {
      entry.type = (entry.type) ? entry.type : ((entry.children === true) ? entryTypes.branch : entryTypes.node);
      entry.data = {
        parent: entry.parent
      };
      entry.parent = this;
      return entry;
    }

    return entryaction;
  }

  function init() {
    const type = entryTypes.root;
    const obj = {};
    entrycontrols = (entrycontrols === null) ? EntryControls(container, options.entrycontrols) : null;
    Object.entries(options.entrycontrols.controls).forEach(([key, control]) => {
      obj[key] = control.action;
    });
    options.entry.actions = obj;
    console.log('actions', obj)
    initEvents();

    root = EntryAction({
      type: type,
      name: '',
      id: options.entry.root,
      label: (options.title) ? options.title : 'Tree',
    }, options.entry);
    root.addListeners();
    root.label.click();
  }

  function initEvents() {
    // events controls on entries
    ModuleEventEmitter.on(options.entry.event.name, (e) => {
      const evtnames = e.entry.eventnames;
      let dragentry, activentry;
      switch (e.action) {
        case evtnames.attach:
          attachControls(e.entry);
          break;
        case "dragstart":
          dragentry = activentry = e.entry;
          e.entry.container.classList.add(e.entry.options.css.dragging);
          detachControls();
          break;
        case "dragover":
          if (!dragentry) return;
          if (overitem !== e.entry.container) {
            if (overitem) overitem.classList.remove(e.entry.options.css.dragover);
            e.entry.container.classList.add(e.entry.options.css.dragover);
            overitem = e.entry.container;
          }
          break;
        case "dragend":
          dragentry = null;
          if (overitem) overitem.classList.remove(e.entry.options.css.dragover);
          overitem = null;
          break;
        case "drop":
          if (!dragentry) {
            ModuleEventEmitter.emit(eventnames.action, e, uuid);
            return true;
          }
          const el = dragentry.container;
          const dest_entry = e.entry;
          dest_entry.resetDragOver();
          if (dragentry !== null) {
            if (dragentry.options.actions.move) {
              try {
                dragentry.move(dest_entry);
                if ([dragentry.options.type.trashed].indexOf(dest_entry.type) >= 0) attachControls(dest_entry);
              } catch (error) {
                console.log('errordrop ', error)
                dragentry.unMove();
              }
            } else console.log('noactionon drop');

          } else console.log(' parent===null or dragitem===null or dragitem===parent', dragentry)

          break;
        case evtnames.select:
          const droptarget = (options.selectors.droptarget) ? document.getElementById(options.selectors.droptarget) : null;
          if (!droptarget) console.log('no-target');
          else {
            if (droptarget.tomselect) {
              const ts = droptarget.tomselect;
              let obj = ts.getOption(e.entry.id);
              if (!obj) {
                obj = {};
                obj[ts.settings.valueField] = e.entry.id;
                obj[ts.settings.searchField] = e.entry.name;
                ts.addOption(obj);
              }
              ts.addItem(e.entry.id);
            } else {
              switch (droptarget.tagName.toLowerCase()) {
                case 'input':
                case 'textarea':
                  droptarget.value = e.entry.id;

                  break;
                default:
                  droptarget.textContent = e.entry.id;
                  break;
              }
            }
            if (options.trigger) options.trigger.click();

          }
          break;
        default:
          if (e.entry.active) {
            attachControls(e.entry);
          } else attachControls(root);
          break;
      }
    }, uuid);
  }

  function search(name) {

  }

  function attachControls(entry) {
    if (entrycontrols) entrycontrols.attachControls(entry);

    activentry = entry;
    ModuleEventEmitter.emit(eventnames.attach, {
      entry: activentry
    }, options.listener);
  }

  function detachControls() {
    const dest = (activentry) ? ((activentry.parent) ? activentry.parent : root) : root;
    if (entrycontrols) entrycontrols.attachControls(dest);
    ModuleEventEmitter.emit(eventnames.detach, {
      entry: activentry
    }, options.listener);
    activentry = dest;
  }
}