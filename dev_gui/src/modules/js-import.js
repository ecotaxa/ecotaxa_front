import {
  ActivRequest
} from "../modules/activ-request.js";
import {
  fetchSettings,
  create_box,
  dirseparator
} from '../modules/utils.js';
import {
  css,
  filter_files,
} from '../modules/modules-config.js';
import {
  ModuleEventEmitter
} from '../modules/module-event-emitter.js';
import {
  entryTypes,
} from '../modules/entry.js';
import {
  AlertBox
} from '../modules/alert-box.js';
css.displayimport = 'displayimport';
export function JsImport(container, options = {}) {
  const defaultOptions = {
    selectors: {
      typeimport: "typeimport",
      inputname: "file_to_load",
      showfiles: ".showfiles",
      importzoneid: "import-list",
      sourcezone: "dirlist",
    },
    url: {
      import: "gui/import",
      dirlist: "gui/files",
      stageimport: "gui/files/import/stage"
    },
    browse: ['directory', 'file'],
    textimport: 'import'
  };
  let selected = null;
  // Multiple files/directories selected in the "My files" tree, keyed by their path.
  let multiSelected = new Map();
  container = (container instanceof HTMLElement) ? container : document.querySelector(container);
  if (!container) return;
  options = { ...defaultOptions,
    ...options
  };
  let url = {};
  url.dirlist = (container.dataset.dirlist) ? container.dataset.dirlist : options.url.dirlist;
  url.import = (container.dataset.import) ? container.dataset.import : options.url.import;
  url.stageimport = (container.dataset.stageimport) ? container.dataset.stageimport : options.url.stageimport;
  options.selectors.importzoneid = (container.dataset.importzoneid) ? container.dataset.importzoneid : options.selectors.importzoneid;
  options.browse = (container.dataset.browse) ? container.dataset.browse.split(',') : options.browse;
  options.textimport = (container.dataset.textimport) ? container.dataset.textimport : options.textimport;
  const submitbtn = container.querySelector('[type="submit"]');
  let typeimport;
  let jsDirList;
  let eventnames = {
    import: 'import',
    select: 'select',
  };
  let importliste = "";
  let filetoload = document.getElementById(options.selectors.inputname);
  let importzone = null;
  let dragentry = null;

  function init() {
    // init steps to display import sequence
    addImportZone();
    container.querySelectorAll('input[name="' + options.selectors.typeimport + '"]').forEach(typeimport => {
      typeimport.addEventListener('change', (e) => {
        if (e.currentTarget.checked) {
          typeimport = e.currentTarget.value;
          showSelection(true);
        }
      });
    });
    container.formsubmit.addHandler('submit', async () => {
      return processImport();
    });
    showSelection();
  }

  function addImportZone() {
    if (!filetoload) {
      const importzoneid = (container.dataset.importzone) ? container.dataset.importzone : options.selectors.importzone;
      let zone = document.getElementById(importzoneid);
      if (zone === null) {
        zone = create_box('div', {
          id: importzoneid
        }, container);
      };
      filetoload = create_box('input', {
        type: "hidden",
        id: options.selectors.inputname,
        name: options.selectors.inputname,
        class: "form-input",
        required: true
      }, zone);
      const response = create_box('div', {
        class: "response-summary"
      }, zone);
      create_box('div', {
        id: "total-objects",
        class: css.info,
        data: {
          text: "Total objects"
        }
      }, response);
      create_box('div', {
        id: "total-tsv",
        class: css.info,
        data: {
          text: "Total TSV"
        }
      }, response);
    }
  }
  async function showSelection(refresh = false) {
    const apply_filters = () => {
      const filters = typeimport.split('-');
      const allowed = new Set(filters.flatMap(filter => filter_files[filter] ? filter_files[filter].split(',').map(ext => ext.trim()) : []));
      jsDirList.container.querySelectorAll('[data-ftype]').forEach(entry => {
        if (allowed.has(entry.dataset.ftype)) entry.classList.remove('disabled');
        else entry.classList.add('disabled');
      });
    }
    const displayselection = document.getElementById(options.selectors.sourcezone);
    if (!displayselection) return;
    if (!jsDirList) {
      const {
        JsDirList
      } = await import('../modules/files/js-dirlist.js');
      jsDirList = new JsDirList(displayselection, {
        url: url.dirlist,
      });
      addImportControls(jsDirList, jsDirList.uuid, null, [], true);
      const detachcallback=function() {deSelect();showSubmit(false);}
      jsDirList.detachcallback=detachcallback;
      container.querySelectorAll('[data-import]').forEach(async (item) => {
        item.dataset.request = item.dataset.import;
        await ActivRequest.makeRequest(item);
        item.addEventListener('click',(e) => {
        showSubmit((selected!==null));
        });
        const other= item.previousElementSibling || item.nextElementSibling;
        if (other && other.dataset.summary) other.addEventListener('click',(e) => {
        showSubmit(false);
        });
        if (item.jstree) {
            item.jstree.entrycontrols.options.controls = {};
            item.jstree.setDetachcallback(detachcallback);
            const exclude = (item.dataset.exclude)?item.dataset.exclude.split(','):[];
         addImportControls(item.jstree, item.jstree.uuid, [entryTypes.branch, entryTypes.node],exclude);
         }
      })
        // detach entry controls if accordion or tabs when not active
        const accordion=container.querySelector('.js-accordion')?container.querySelector('.js-accordion'):container.querySelector('.js-tabs');
        if (accordion && accordion.dataset.detail) {
        const summaries=accordion.querySelectorAll(accordion.dataset.detail);
        summaries.forEach(summary=> {
         summary.emitevent= () => { deSelect();}
        });
        }
       //
    }
    if (refresh === true) apply_filters();
  }
  function deSelect() {
  if(selected!==null) {selected.setSelected(false);selected.active=true;selected.emitEvent();selected=null;}
  if(multiSelected.size>0) {
    multiSelected.forEach(entry => {
      if (entry.importButton) entry.importButton.classList.remove('is-selected');
    });
    multiSelected.clear();
    showSubmit(false);
  }
  }

  function attachImportToggle(entry) {
    const btn = create_box('span', {
      class: ['control-select', 'import-toggle']
    }, entry.container);
    create_box('i', {
      class: ['icon', 'icon-check']
    }, btn);
    entry.importButton = btn;
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      e.preventDefault();
      toggleMultiSelect(entry);
    });
  }

  // Set/clear the selection of a single entry (map membership + button style).
  function setSelectedState(entry, selected) {
    const key = entry.getCurrentPath().join(dirseparator);
    if (selected) multiSelected.set(key, entry);
    else multiSelected.delete(key);
    if (entry.importButton) entry.importButton.classList.toggle('is-selected', selected);
  }

  // Walk every already-loaded descendant entry (files never have .entries).
  function eachDescendant(entry, fn) {
    if (!Array.isArray(entry.entries) || entry.entries.length === 0) return;
    entry.entries.forEach(child => {
      if (!child) return;
      if (child.importButton) fn(child);
      eachDescendant(child, fn);
    });
  }

  // Walk every ancestor folder up to (but excluding) the untoggleable root.
  function eachAncestor(entry, fn) {
    let parent = entry.getParent();
    while (parent) {
      if (parent.importButton) fn(parent);
      parent = parent.getParent();
    }
  }

  // True when an ancestor folder is currently selected.
  function hasSelectedAncestor(entry) {
    let parent = entry.getParent();
    while (parent) {
      if (multiSelected.has(parent.getCurrentPath().join(dirseparator))) return true;
      parent = parent.getParent();
    }
    return false;
  }

  function toggleMultiSelect(entry) {
    const key = entry.getCurrentPath().join(dirseparator);
    const willSelect = !multiSelected.has(key);

    setSelectedState(entry, willSelect);

    const isBranch = [entryTypes.branch, entryTypes.root].indexOf(entry.type) >= 0;
    if (isBranch) {
      // Ticking/unticking a folder cascades to every loaded child.
      eachDescendant(entry, (child) => setSelectedState(child, willSelect));
    }
    if (!willSelect) {
      // Unticking anything bubbles up: an ancestor folder can no longer
      // claim that all of its contents are selected. Ticked siblings stay.
      eachAncestor(entry, (ancestor) => setSelectedState(ancestor, false));
    }
    showSubmit(multiSelected.size > 0);
  }
  function addImportPath(value) {
    document.getElementById(options.selector.importzone).value = value;
    const displayresult = document.getElementById(options.selector.displayresult);
    if (displayresult) displayresult.innerHTML = `<li>${value.split('/').pop()}</li>`;
    const options = container.querySelector('#' + options.selector.importoptions);
  }

  function addImportEntry(entry) {
    filetoload.value = entry.getCurrentPath().join(dirseparator);
    showSubmit();
  }

  function addImportControls(entrylist, uploaduuid, typentries = null,exclude=[],multiselect=false) {

    if (multiselect) {
      // Each file/directory line gets its own persistent checkbox-like
      // toggle button, independent from the shared entrycontrols toolbar
      // (create/remove/move/rename) that only ever displays for one entry
      // at a time.
      const allowed = (typentries) ? typentries : [entryTypes.branch, entryTypes.node];
      entrylist.root.options.onEntryCreated = (entry) => {
        if (allowed.indexOf(entry.type) < 0) return;
        if (exclude.indexOf(entry.name) >= 0) return;
        attachImportToggle(entry);
        // A child loaded (lazily) under an already-ticked folder inherits the tick.
        if (hasSelectedAncestor(entry)) setSelectedState(entry, true);
      };
      return;
    }

    function add_remove_import(e) {
        if (selected) {
        delete selected.label.dataset.selected;
        selected.setSelected(false);
        }
      const activentry = entrylist.getActiventry();
      if (selected === activentry  ) {
        selected = null;
        return;
      }
      const cl = activentry.options.css.selected;
      activentry.setSelected(true);
      activentry.label.dataset.selected = options.textimport;
      entrylist.entrycontrols.showControls(false);
      selected = activentry;
    }
      entrylist.entrycontrols.removeControls();
      const control = {
      import: {
        action: 'import',
        class:["control-select"],
        exclude:exclude,
        typentries: (typentries) ? typentries : [entryTypes.branch,entryTypes.node],
        text: (options.toselect)?(options.toselect):'import',
        callback: add_remove_import
      }
    };
     control.import.action = function(entry) {
      if (entrylist.activentry) entrylist.activentry.setSelected(false);
      addImportEntry(entry);
      ModuleEventEmitter.emit(eventnames.select, {
        value: false
      }, uploaduuid);
    }
   entrylist.entrycontrols.options.controls = { ...entrylist.entrycontrols.options.controls,
      ...control,

    };

    entrylist.entrycontrols.createControls();
    entrylist.entrycontrols.activateControls();
    }

  function showSubmit(show = true) {
    const submit = container.querySelector('[type="submit"]');
      if (show) {
      submit.classList.remove('hide');
      submit.disabled = false;
    } else submit.disabled = true;
  }

  async function processImport() {
    if (multiSelected.size > 0) {
      const formdata = new FormData();
      const projid = document.getElementById('projid');
      formdata.append('projid', (projid) ? projid.value : '');
      multiSelected.forEach((entry, key) => {
        // Use the map key: a subtree wiped by removeEntries() can leave an
        // entry whose parent chain (and thus getCurrentPath()) is stale.
        formdata.append('entries', key);
      });
      const json = await fetch(url.stageimport, fetchSettings({
        method: 'POST',
        body: formdata,
      })).then(response => response.json()).catch(err => {
        AlertBox.addAlert({
          type: AlertBox.alertconfig.types.danger,
          content: err.status ? `${err.status} ${err.statusText}` : err,
          dismissible: false,
        });
        return null;
      });
      if (!json || json.status !== 200 || !json.message || !json.message.source_path) {
        AlertBox.addAlert({
          type: AlertBox.alertconfig.types.danger,
          content: 'Unable to prepare the selected files/directories for import.',
          dismissible: true,
        });
        return false;
      }
      filetoload.value = json.message.source_path;
      return true;
    }
    if (filetoload.value === "") {
      alert('nothing to upload');
      return false;
    }
    return true;
  }
  init();
}