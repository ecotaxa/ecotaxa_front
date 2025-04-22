import DOMPurify from 'dompurify';
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
} from '../modules/modules-config.js';
import {
  ModuleEventEmitter
} from '../modules/module-event-emitter.js';
import {
  entryTypes,
} from '../modules/entry.js';
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
      dirlist: "gui/files"
    },
    browse: ['directory', 'file'],
    textimport: 'to import'
  };
  let selected=null;
  container = (container instanceof HTMLElement) ? container : document.querySelector(container);
  if (!container) return;
  options = { ...defaultOptions,
    ...options
  };
  let url = {};
  url.dirlist = (container.dataset.dirlist) ? container.dataset.dirlist : options.url.dirlist;
  url.import = (container.dataset.import) ? container.dataset.import : options.url.import;
  options.selectors.importzoneid = (container.dataset.importzoneid) ? container.dataset.importzoneid : options.selectors.importzoneid;
  options.browse = (container.dataset.browse) ? container.dataset.browse.split(',') : options.browse;
  options.textimport = (container.dataset.textimport) ? container.dataset.textimport : options.textimport;
  const submitbtn = container.querySelector('[type="submit"]');
  let typeimport;
  let myFiles;
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
      let filters = typeimport.split('-');
      filters = filters.map(filter => {
        return new Set([...(filter_files[filter] ? filter_files[filter] : [])]);
      });
      myFiles.container.querySelectorAll('[data-ftype]').forEach(entry => {
        if (filters.has(entry.dataset.ftype)) entry.classList.remove('disabled');
        else entry.classList.add('disabled');
      });
    }
    const displayselection = document.getElementById(options.selectors.sourcezone);
    if (!displayselection) return;
    if (!myFiles) {
      const {
        JsMyFiles
      } = await import('../modules/js-my-files.js');
      myFiles = new JsMyFiles(displayselection, {
        import: url.toimport,
        url: url.dirlist,
        browse: options.browse,
        upload: {
          label: (displayselection.dataset.uploadlabel) ? (displayselection.dataset.uploadlabel) : 'upload',
          callback: () => {
            showSubmit(false);
          }
        }
      });
       myFiles.eventnames.clearother='clearother';
        ModuleEventEmitter.on(myFiles.eventnames.clearother, (e) => {deSelect();},myFiles.uuid);
      ModuleEventEmitter.on(eventnames.select, (e) => {
        myFiles.detachDropzone();
      }, myFiles.uuid);
      addImportControls(myFiles.jsDirList, myFiles.uuid);
      const detachcallback=function() {deSelect();showSubmit(false);}
      myFiles.jsDirList.detachcallback=detachcallback;
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

  function addImportControls(entrylist, uploaduuid, typentries = null,exclude=[]) {

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
      const control = {
      import: {
        action: 'import',
        class:["control-select"],
        exclude:exclude,
        typentries: (typentries) ? typentries : [entryTypes.branch],
        text: (options.toselect)?(options.toselect):'select to import',
        callback: add_remove_import
      }
    };
    entrylist.entrycontrols.options.controls = {
      ...entrylist.entrycontrols.options.controls,
      ...control
    };
    const import_action = function(entry) {
      if (entrylist.activentry) entrylist.activentry.setSelected(false);
      addImportEntry(entry);
      ModuleEventEmitter.emit(eventnames.select, {
        value: false
      }, uploaduuid);
    }
    entrylist.entrycontrols.addControl(control.import, 0, import_action);
    entrylist.entrycontrols.activateControl(control.import);
  }

  function showSubmit(show = true) {
    const submit = container.querySelector('[type="submit"]');
      if (show) {
      submit.classList.remove('hide');
      submit.disabled = false;
    } else submit.disabled = true;
  }

  function processImport() {
    if (filetoload.value === "") {
      alert('nothing to upload');
      return false;
    }
    return true;
  }
  init();
}