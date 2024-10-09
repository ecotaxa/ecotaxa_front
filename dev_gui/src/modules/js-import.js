import DOMPurify from 'dompurify';
import {
  fetchSettings,
  create_box
} from '../modules/utils.js';
import {
  css,
} from '../modules/modules-config.js';
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
    import: 'import'
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
          console.log(e.currentTarget)
          typeimport = e.currentTarget.value;
          showSelection(true);
        }
      })
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
      addImportControls();
    }
    if (refresh === true) apply_filters();

  }

  function addImportPath(value) {
    document.getElementById(options.selector.importzone).value = value;
    const displayresult = document.getElementById(options.selector.displayresult);
    if (displayresult) displayresult.innerHTML = `<li>${value.split('/').pop()}</li>`;
    const options = container.querySelector('#' + options.selector.importoptions);
  }

  function addImportEntry(entry) {
    // remove dir or file controls
    //  myFiles.jsDirList.detachControls();
    filetoload.value = entry.getCurrentDirPath();
    showSubmit();
  }

  function addImportControls() {
    let selected = null;

    function add_remove_import(e) {
      if (selected) {
        delete selected.label.dataset.selected;
        selected.setSelected(false);

      }
      if (selected === myFiles.jsDirList.activentry) {
        selected = null;
        return;
      }
      const cl = myFiles.jsDirList.activentry.options.css.selected;
      myFiles.jsDirList.activentry.setSelected(true);
      myFiles.jsDirList.activentry.label.dataset.selected = options.textimport;
      myFiles.jsDirList.entrycontrols.showControls(false);
      myFiles.enableDropzone(false);
      selected = myFiles.jsDirList.activentry;
    }

    const control = {
      import: {
        action: 'import',
        icon: 'icon-check',
        typentries: [entryTypes.branch],
        text: 'import into project',
        callback: add_remove_import
      }
    };
    myFiles.jsDirList.entrycontrols.options.controls = {
      ...myFiles.jsDirList.entrycontrols.options.controls,
      ...control
    };
    const import_action = function(entry) {
      addImportEntry(entry);
    }
    myFiles.jsDirList.entrycontrols.addControl(control.import, 0, import_action);
    myFiles.jsDirList.entrycontrols.activateControls();

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