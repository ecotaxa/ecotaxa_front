import {
  ActivRequest
} from "../modules/activ-request.js";
import {
  fetchSettings,
  create_box,
  dirseparator,
  error_content
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
  // Shared by apply_filters() (checkbox enable/disable) and processImport()
  // (submit-time validation) so both agree on what counts as an image /
  // an ecotaxa metadata file for the currently selected import type.
  const imageExts = new Set(filter_files.images.split(',').map(ext => ext.trim()));
  const allAcceptedExts = new Set([...filter_files.images.split(','), ...filter_files.tsv.split(',')].map(ext => ext.trim()));
  const isImageExt = (ext) => imageExts.has(ext);
  const isEcotaxaMetaExt = (ext, name) => (ext === 'tsv' || ext === 'txt') && /^ecotaxa/i.test(name || '');
  const isAllowedExt = (ext, name) => {
    if (typeimport === 'images') return isImageExt(ext);
    if (typeimport === 'tsv') return isEcotaxaMetaExt(ext, name);
    return allAcceptedExts.has(ext); // images-tsv (general): any accepted type
  };
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
    filesmutated: 'filesmutated',
  };
  let importliste = "";
  let filetoload = document.getElementById(options.selectors.inputname);
  let importzone = null;
  let dragentry = null;

  function init() {
    // init steps to display import sequence
    addImportZone();
    container.querySelectorAll('input[name="' + options.selectors.typeimport + '"]').forEach(radio => {
      radio.addEventListener('change', (e) => {
        if (e.currentTarget.checked) {
          typeimport = e.currentTarget.value;
          showSelection(true);
          syncSelectionWithType();
        }
      });
    });
    initTypeImportTabs();
    container.formsubmit.addHandler('submit', async () => {
      return processImport();
    });
    showSelection();
  }

  // The type of import (images / tsv / images-tsv) is actually driven by the
  // js-tabs legends in jobs/import.html (legend.tab-control[data-typeimport]),
  // not by the typeimport radios above (kept for other/older forms). Wire
  // those tabs the same way: switching one updates typeimport, re-applies the
  // file-type filter, and re-syncs the selection against the newly selected
  // type (see syncSelectionWithType).
  function initTypeImportTabs() {
    const tabControls = container.querySelectorAll('.tab-control[data-typeimport]');
    if (tabControls.length === 0) return;
    tabControls.forEach(tab => {
      tab.addEventListener('click', () => {
        if (!tab.dataset.typeimport || tab.dataset.typeimport === typeimport) return;
        typeimport = tab.dataset.typeimport;
        showSelection(true);
        syncSelectionWithType();
      });
    });
    const activeTab = container.querySelector('.tab.active .tab-control[data-typeimport]');
    typeimport = (activeTab || tabControls[0]).dataset.typeimport;
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
      jsDirList.container.querySelectorAll('[data-ftype]').forEach(entry => {
        const allowed = isAllowedExt(entry.dataset.ftype, entry.dataset.name);
        entry.classList.toggle('disabled', !allowed);
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
        // read-only picker: no per-entry toolbar, so drop the "activate tools" hint
        notips: true,
        // single click expands/collapses a row, double click toggles its checkbox
        clickExpand: true,
        // wrap icon+name in their own indented div so the checkbox prepended
        // into the row stays unindented, lining up in a single left column
        wrapContent: true,
        entry: {
          tags: { tag: 'div', subtag: 'div', label: 'span' },
        },
      });
      // Import browses "My files" read-only: no create/remove/move/rename
      // toolbar. JsDirList guards every toolbar call with `if (this.entrycontrols)`
      // so nulling it here disables the toolbar without touching EntryControls.
      jsDirList.entrycontrols = null;
      addImportControls(jsDirList, jsDirList.uuid, null, [], true);
      // deploy the "My files" root so its folders show right away
      jsDirList.root.setOpen(true);
      // Note: NOT wired as jsDirList.detachcallback - this tree is a persistent
      // multiselect picker, so browsing/expanding folders must not clear ticks
      // (unlike the single-select accordion pickers below, which do want that).
      const detachcallback=function() {deSelect();showSubmit(false);}
      // Keep the import tree in sync with changes made to the server files
      // elsewhere - typically the "My files" manager opened in a modal
      // (create / delete / rename / move a directory, or an upload). Those paths
      // emit 'filesmutated' on the shared bus (js-dirlist.js fetchAction and
      // js-my-files.js upload "ready"). Registered once, inside this guard.
      ModuleEventEmitter.on(eventnames.filesmutated, async () => {
        if (!jsDirList || !jsDirList.root) return;
        await jsDirList.root.list();
        jsDirList.root.setOpen(true);
        if (typeimport) apply_filters();
      });
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
  updatePartialMarks();
  }

  function attachImportToggle(entry) {
    const btn = create_box('span', {
      class: ['control-select', 'import-toggle']
    });
    entry.container.prepend(btn);
    entry.importButton = btn;
    // A double-click still fires two ordinary 'click' events on the same
    // target before 'dblclick' does (standard browser behaviour), so a
    // double-click here used to toggle the entry on then off again -
    // queue the toggle behind a short delay and cancel it if a dblclick
    // follows within it, same pattern as js-dirlist.js's getListeners().
    let clickTimer = null;
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      e.preventDefault();
      if (clickTimer) clearTimeout(clickTimer);
      clickTimer = setTimeout(() => {
        clickTimer = null;
        toggleMultiSelect(entry);
      }, 250);
    });
    // stop it bubbling to the row (which would otherwise trigger its own
    // expand/collapse) and cancel the queued toggle so a double-click nets
    // no change instead of toggling twice.
    btn.addEventListener('dblclick', (e) => {
      e.stopPropagation();
      e.preventDefault();
      if (clickTimer) {
        clearTimeout(clickTimer);
        clickTimer = null;
      }
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

  // Walk every ancestor folder up to and including the root.
  function eachAncestor(entry, fn) {
    let parent = entry.getParent();
    while (parent) {
      if (parent.importButton) fn(parent);
      parent = parent.getParent();
    }
  }

  // Tint the name of every unchecked folder that still has a checked entry
  // somewhere inside it, so a selection buried in a collapsed folder stays
  // visible. Recomputed from multiSelected on every selection change.
  function updatePartialMarks() {
    if (!jsDirList || !jsDirList.container) return;
    jsDirList.container
      .querySelectorAll('[data-name].has-selected-inside')
      .forEach((el) => el.classList.remove('has-selected-inside'));
    multiSelected.forEach((entry) => {
      eachAncestor(entry, (ancestor) => {
        const key = ancestor.getCurrentPath().join(dirseparator);
        if (!multiSelected.has(key) && ancestor.container)
          ancestor.container.classList.add('has-selected-inside');
      });
    });
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

  // After a tick, climb from the entry's parent upward: if every loaded,
  // importable child of a folder is now checked, tick the folder itself too
  // (it no longer needs the "has-selected-inside" dash - it's fully checked),
  // and keep climbing since that may complete the next level up as well.
  function promoteFullAncestors(entry) {
    let parent = entry.getParent();
    while (parent && parent.importButton) {
      const key = parent.getCurrentPath().join(dirseparator);
      if (multiSelected.has(key)) {
        parent = parent.getParent();
        continue;
      }
      const children = (Array.isArray(parent.entries) ? parent.entries : []).filter((c) => c && c.importButton);
      if (children.length === 0) break;
      const allChecked = children.every((c) => multiSelected.has(c.getCurrentPath().join(dirseparator)));
      if (!allChecked) break;
      setSelectedState(parent, true);
      parent = parent.getParent();
    }
  }

  // Called right after typeimport changes. Walks every loaded file entry and:
  // - drops any ticked file that no longer matches the new type, tagging it
  //   with entry.wasSelected so we remember the user wanted it,
  // - restores any unticked file whose entry.wasSelected is set and which
  //   matches the new type again (e.g. switching back to a previous tab).
  // A manual untick (toggleMultiSelect) clears the tag, so we never resurrect
  // something the user deliberately unchecked.
  function syncSelectionWithType() {
    if (!jsDirList || !jsDirList.root) return;
    let changed = false;
    const visit = (entry) => {
      if (entry.type !== entryTypes.node) return;
      const key = entry.getCurrentPath().join(dirseparator);
      const allowed = isAllowedExt(entry.ftype, entry.name);
      const isSelected = multiSelected.has(key);
      if (isSelected && !allowed) {
        entry.wasSelected = true;
        setSelectedState(entry, false);
        // Unticking bubbles up: an ancestor folder can no longer claim that
        // all of its contents are selected (mirrors toggleMultiSelect).
        eachAncestor(entry, (ancestor) => setSelectedState(ancestor, false));
        changed = true;
      } else if (!isSelected && allowed && entry.wasSelected) {
        setSelectedState(entry, true);
        promoteFullAncestors(entry);
        changed = true;
      }
    };
    eachDescendant(jsDirList.root, visit);
    if (!changed) return;
    showSubmit(multiSelected.size > 0);
    updatePartialMarks();
  }

  function toggleMultiSelect(entry) {
    const key = entry.getCurrentPath().join(dirseparator);
    const willSelect = !multiSelected.has(key);
    // Block hand-picking a single file that doesn't match the current
    // import type (mirrors the dimmed/disabled look apply_filters gives it).
    // Bulk-selecting a folder is untouched - it still ticks everything
    // inside it, matching today's "select this whole directory" behavior.
    if (willSelect && entry.type === entryTypes.node && !isAllowedExt(entry.ftype, entry.name)) return;

    setSelectedState(entry, willSelect);

    const isBranch = [entryTypes.branch, entryTypes.root].indexOf(entry.type) >= 0;
    if (isBranch) {
      // Ticking/unticking a folder cascades to every loaded child.
      eachDescendant(entry, (child) => {
        setSelectedState(child, willSelect);
        // A manual untick is deliberate - forget any type-switch memory too,
        // so a later tab change doesn't resurrect it (see syncSelectionWithType).
        if (!willSelect && child.type === entryTypes.node) child.wasSelected = false;
      });
    }
    if (!willSelect) {
      if (entry.type === entryTypes.node) entry.wasSelected = false;
      // Unticking anything bubbles up: an ancestor folder can no longer
      // claim that all of its contents are selected. Ticked siblings stay.
      eachAncestor(entry, (ancestor) => setSelectedState(ancestor, false));
    } else {
      promoteFullAncestors(entry);
    }
    showSubmit(multiSelected.size > 0);
    updatePartialMarks();
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
      // toggle button (attachImportToggle). The dirlist toolbar is disabled
      // by the caller (jsDirList.entrycontrols = null).
      const allowed = (typentries) ? typentries : [entryTypes.branch, entryTypes.node];
      entrylist.root.options.onEntryCreated = (entry) => {
        if (allowed.indexOf(entry.type) < 0) return;
        if (exclude.indexOf(entry.name) >= 0) return;
        // Never offer the trash directory, nor anything inside it, for import.
        // (branches inside trash are already retyped to 'discarded' above, but
        //  files keep their 'node' type, so guard explicitly.)
        if ((entry.isTrashDir && entry.isTrashDir()) ||
          (entry.isInTrash && entry.isInTrash())) return;
        attachImportToggle(entry);
        // A child loaded (lazily) under an already-ticked folder inherits the tick.
        if (hasSelectedAncestor(entry)) setSelectedState(entry, true);
      };
      // The root ("My files") directory is built before onEntryCreated is set,
      // so give it the same toggle explicitly: ticking it cascades to every
      // loaded child, exactly like any other directory.
      if (entrylist.root && !entrylist.root.importButton &&
        exclude.indexOf(entrylist.root.name) < 0) {
        attachImportToggle(entrylist.root);
      }
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
      const entries = Array.from(multiSelected.values());
      const hasDirectory = entries.some(entry => [entryTypes.branch, entryTypes.root].indexOf(entry.type) >= 0);
      if (!hasDirectory) {
        const files = entries.filter(entry => entry.type === entryTypes.node);
        const hasImage = files.some(entry => isImageExt(entry.ftype));
        const hasEcotaxaMeta = files.some(entry => isEcotaxaMetaExt(entry.ftype, entry.name));
        const valid = typeimport === 'images' ? hasImage
          : typeimport === 'tsv' ? hasEcotaxaMeta
          : hasImage && hasEcotaxaMeta; // images-tsv (general)
        if (!valid) {
          AlertBox.addAlert({
            type: AlertBox.alertconfig.types.danger,
            content: typeimport === 'images'
              ? 'Select at least one image to import.'
              : typeimport === 'tsv'
              ? 'Select at least one metadata file (ecotaxa*.tsv or .txt) to import.'
              : 'Select at least one image and one metadata file (ecotaxa*.tsv or .txt) to import.',
            dismissible: true,
          });
          return false;
        }
      }
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
          content: error_content(err),
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