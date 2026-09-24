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
import {
  ModuleEventEmitter
} from '../modules/module-event-emitter.js';
import {
  entryTypes,
  entryOptions,
  eventEntry,
  Entry,
  EntryControls,
  MultiEntryControls
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
  // hover toolbar - empty by default, selection is done with the per-row
  // checkbox below
  entrycontrols: {
    controls: {},
  },
  // single-select checkbox on every row (MultiEntryControls), same look as the
  // import picker's multiselect (js-import.js), pinned at the row's left edge:
  // clicking the checkbox or dblclicking the icon/name toggles it, click on
  // the icon/name opens the entry, hovering the icon/name previews the tick.
  // Ticking an entry unticks the previous one.
  rowselect: {
    class: ['control-select', 'import-toggle'],
    typentries: [entryTypes.branch, entryTypes.node],
  },
  droptarget: 'droptarget',
  tree: 'taxotree',

}

function EntryAction(entry, options) {
  // deferListeners: getListeners() is overridden below, JsTree / createEntry()
  // call addListeners() once the override is in place
  const entryaction = new Entry(entry, { ...options, deferListeners: true });
  entryaction.status=entry.status;
  entryaction.eventnames = {
    attach: 'attach',
    detach: 'detach',
    select: 'select',
  };
  entryaction.newEntry = function(entry) {
    return EntryAction(entry, this.options);
  }
  // rollover shows the controls. With the select checkbox (rowselect): click
  // opens the entry and lists its children, dblclick toggles its checkbox
  // (JsTree attachSelect). Without it, same as My files (js-dirlist.js):
  // click activates the entry, dblclick opens it.
  entryaction.getListeners = function() {
    if (this.options.rowselect) {
      const open = (this.isBranch(true)) ? () => this.toggleOpen() : null;
      // clickselect (import page server tree): like the import "My files"
      // list - click toggles the checkbox, dblclick opens the entry
      if (this.options.clickselect) return this.interactionListeners(() => {
        if (this.selectToggle) this.selectToggle();
      }, open);
      return this.interactionListeners(open, () => {
        if (this.selectToggle) this.selectToggle();
      });
    }
    return this.interactionListeners(() => {
      this.emitEvent(this.eventnames.attach);
    });
  }
  entryaction.select = function() {
    this.emitEvent(this.eventnames.select);
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
  if (entry.status==='D') entryaction.container.classList.add(css.deprecated);
  return entryaction;
}
export function JsTree(parent, options = {}) {
  parent = (parent instanceof HTMLElement) ? parent : document.querySelector(parent);
  parent.innerHTML = '';
  options = { ...jstreeOptions,
    ...options
  };
  let detachcallback=null;
  const uuid = generate_uuid();
  if (!parent || parent.querySelector('.' + options.tree) !== null) return;
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
    class: options.tree
  }, parent);
  let root, activentry, dragentry, overitem = null;
  let hoverLeaveTimer = null;
  // single selection (rowselect checkbox) and who gets told about it
  let selected = null;
  let selectcallback = (options.actions && options.actions.select) ? (entry, on) => {
    if (on) options.actions.select(entry);
  } : null;
  const entrycontrols = EntryControls(container, options.entrycontrols) ;
  // options coming from a data-exclude attribute are a comma separated string
  const exclude = (Array.isArray(options.exclude)) ? options.exclude : ((options.exclude) ? options.exclude.split(',') : []);
  // data-selectunder: only descendants of the entry with this name get the select checkbox
  const selectunder = (options.selectunder) ? options.selectunder : null;
  const isUnder = (entry) => {
    for (let parent = entry.getParent(); parent; parent = parent.getParent()) {
      if (parent.name === selectunder) return true;
    }
    return false;
  };
  const rowcontrols = (options.rowselect) ? MultiEntryControls({
    accept: (entry) => entry.status !== 'D' && (!selectunder || isUnder(entry)),
    controls: {
      select: {
        action: (entry) => toggleSelect(entry),
        class: options.rowselect.class,
        exclude: exclude,
        typentries: options.rowselect.typentries,
      }
    }
  }) : null;
  init(parent);
  container.append(root.container);
  function init() {
    const type = entryTypes.root;
    const obj = {};
    Object.entries(options.entrycontrols.controls).forEach(([key, control]) => {
      obj[key] = control.action;
    });
    obj.select = 'select';
    options.entry.actions = obj;
    options.entry.listener = uuid;
    if (rowcontrols) {
      options.entry.rowselect = true;
      if (options.clickselect) options.entry.clickselect = true;
      // onEntryCreated fires from the Entry constructor, before createEntry()
      // appends it and before EntryAction sets its status - defer until the
      // entry is in place (same as js-import.js multiselect)
      options.entry.onEntryCreated = (entry) => {
        queueMicrotask(() => attachSelect(entry));
      };
    }
    initEvents();
    root = EntryAction({
      type: type,
      name: '',
      id: options.entry.root,
      label: options.api_parameters.rootname,
    }, options.entry);
    root.addListeners();
    root.setOpen(true);

  }

  function initEvents() {
    // events controls on entries
    ModuleEventEmitter.on(options.entry.event.name, (e) => {
      const evtnames = e.entry.eventnames;
      let dragentry, activentry;
      switch (e.action) {
        case evtnames.attach:
        if (detachcallback) detachcallback();
          selectEntry(e.entry);
          break;
        case "mouseenter":
          // controls only ever show on rollover - selection is shown via
          // .row-selected instead
          if (hoverLeaveTimer) {
            clearTimeout(hoverLeaveTimer);
            hoverLeaveTimer = null;
          }
          if (entrycontrols && e.entry.status !== 'D') entrycontrols.attachControls(e.entry);
          break;
        case "mouseleave":
          // debounced so moving from one row to the next doesn't flicker
          if (hoverLeaveTimer) clearTimeout(hoverLeaveTimer);
          hoverLeaveTimer = setTimeout(() => {
            hoverLeaveTimer = null;
            if (entrycontrols) entrycontrols.detachControls();
          }, 150);
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
            } else console.log('noaction on drop');

          } else console.log(' parent===null or dragitem===null or dragitem===parent', dragentry)

          break;
        case evtnames.select:
          {
            const droptarget = (options.droptarget) ? document.getElementById(options.droptarget) : null;
            if (!droptarget) console.log('no-target',options);
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
          }
          break;
        default:
           if (e.entry.active) attachControls(e.entry);
           else attachControls(root);
          break;
      }
    }, uuid);
  }

  // --- single select checkbox (rowselect) ---
  function attachSelect(entry) {
    if (entry.selectButton) return;
    const ctrls = rowcontrols.attachControls(entry);
    if (!ctrls || !ctrls.select) return;
    entry.selectButton = ctrls.select;
    // called by the icon/name dblclick (Entry.interactionListeners)
    entry.selectToggle = () => toggleSelect(entry);
    // a child re-created (list() reload) for the selected entry keeps its tick
    if (selected && selected !== entry && selected.id === entry.id && !selected.container.isConnected) {
      selected = entry;
      setSelectedState(entry, true);
    }
  }

  function setSelectedState(entry, on) {
    if (entry.selectButton) entry.selectButton.classList.toggle('is-selected', on);
    // dash on every ancestor, so a selection inside a collapsed branch stays visible
    for (let parent = entry.getParent(); parent; parent = parent.getParent()) {
      if (parent.container) parent.container.classList.toggle('has-selected-inside', on);
    }
  }

  function toggleSelect(entry) {
    if (entry.status === 'D') return;
    const willSelect = (selected !== entry);
    if (selected) setSelectedState(selected, false);
    selected = (willSelect) ? entry : null;
    if (selected) setSelectedState(selected, true);
    activentry = entry;
    if (selectcallback) selectcallback(entry, willSelect);
    else if (willSelect) entry.select();
    else clearDroptarget(entry);
  }

  // untick (default behaviour, no select callback): drop the value that
  // entry.select() put into the droptarget
  function clearDroptarget(entry) {
    const droptarget = (options.droptarget) ? document.getElementById(options.droptarget) : null;
    if (!droptarget) return;
    if (droptarget.tomselect) droptarget.tomselect.removeItem(entry.id);
    else if (['input', 'textarea'].indexOf(droptarget.tagName.toLowerCase()) >= 0) {
      if (String(droptarget.value) === String(entry.id)) droptarget.value = '';
    } else if (droptarget.textContent === String(entry.id)) droptarget.textContent = '';
  }

  // untick without notifying (e.g. the caller reset its own form)
  function clearSelection() {
    if (selected) setSelectedState(selected, false);
    selected = null;
  }

  function getSelected() {
    return selected;
  }

  // callback(entry, on) replaces the default droptarget filling
  function setSelectCallback(callback) {
    selectcallback = callback;
  }

  function search(name) {

  }

  function getActiventry() {
    return activentry;
  }

  function setActiventry(entry = null) {
    activentry = entry;
  }
  // marks the truly selected row (persists while hover previews elsewhere)
  function markSelectedRow(entry) {
    if (activentry && activentry !== entry) activentry.container.classList.remove('row-selected');
    entry.container.classList.add('row-selected');
  }

  // selects an entry (background only) without showing its controls toolbar -
  // that only ever appears on an actual rollover
  function selectEntry(entry) {
    if (entry.status == 'D') return;
    markSelectedRow(entry);
    activentry = entry;
    ModuleEventEmitter.emit(eventnames.attach, {
      entry: activentry
    }, options.listener);
  }

  function attachControls(entry) {
  if(entry.status=='D') return;
    if (entrycontrols) entrycontrols.attachControls(entry);
    markSelectedRow(entry);
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
  function setDetachcallback(callback) {
  detachcallback=callback;}
   return {
    uuid,
    setDetachcallback,
    setSelectCallback,
    clearSelection,
    getSelected,
    getActiventry,
    setActiventry,
    entrycontrols,
    attachControls,
    detachControls,
  }
}