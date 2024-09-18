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
      importzone: "import-list",
      sourcezone: "dirlist"
    },
    url: {
      import: "gui/import",
      dirlist: "gui/files"
    },

  };
  options = { ...defaultOptions,
    ...options
  };
  container = (container instanceof HTMLElement) ? container : document.querySelector(container);
  if (!container) return;
  let url = {};
  url.dirlist = (container.dataset.dirlist) ? container.dataset.dirlist : options.url.dirlist;
  url.import = (container.dataset.import) ? container.dataset.import : options.url.import;
  const submitbtn = container.querySelector('[type="submit"]');
  let typeimport;
  let myFiles;
  let eventnames = {
    import: 'import'
  };
  let importliste = "";
  let filetoload;
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
    if (!importzone) {
      const importzoneid = (container.dataset.importzone) ? container.dataset.importzone : options.selectors.importzone;
      const zone = document.getElementById(importzoneid);
      if (zone === null) return;
      filetoload = create_box('input', {
        type: "hidden",
        id: options.selectors.inputname,
        name: options.selectors.inputname,
        class: "form-input",
        required: true
      }, zone);

      const response = create_box('div', {
        class: "response-summary"
      }, );
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
      importzone = create_box('ul', {
        class: css.displayimport,
      }, zone);
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
    myFiles.jsDirList.detachControls();
    importliste = entry;
    console.log('entryimp', entry)
    const toimport = entry.container.cloneNode(true);
    Array.from(importzone.children).forEach(child => {
      child.remove();
    });
    importzone.append(toimport);
    showSubmit();
  }

  function addImportControls() {
    function add_remove_import(e) {
      console.log('e removeimport callback', myFiles.jsDirList.dragentry)
      console.log('e removeimportevent', e)
    }
    const control = {
      import: {
        action: 'import',
        icon: 'icon-arrow-down-on-square-stack',
        typentries: [entryTypes.branch],
        text: 'import into project',
        callback: add_remove_import
      }
    };
    myFiles.jsDirList.entrycontrols.options.controls = { ...control,
      ...myFiles.jsDirList.entrycontrols.options.controls
    };
    console.log('entrycontrols', myFiles.jsDirList.entrycontrols.options.controls)

    function import_action(entry) {
      addImportEntry(entry);
    }
    console.log(' entrycontrols', myFiles.jsDirList.entrycontrols)
    myFiles.jsDirList.entrycontrols.addControl(control.import, 0, import_action);
    myFiles.jsDirList.entrycontrols.activateControls();
    importzone.addEventListener('drop', (e) => {
      e.stopPropagation();
      dragentry.container.classList.remove(dragentry.options.css.dragging);
      addImportEntry(dragentry);
      importzone.classList.remove(dragentry.options.css.dragover);
      add_remove_import(e);
      dragentry = myFiles.jsDirList.dragentry = null;
    });
    importzone.addEventListener('dragover', (e) => {
      e.preventDefault();
      if (!dragentry) {
        dragentry = myFiles.jsDirList.dragentry;
        dragentry.setOff();
        importzone.classList.add(dragentry.options.css.dragover);
      }
    });

  }

  function showSubmit(show = true) {
    const submit = container.querySelector('[type="submit"]');
    if (show) {
      submit.classList.remove('hide');
      submit.disabled = false;
    } else submit.disabled = true;
  }

  function processImport() {
    if (importliste === "") {
      alert('nothing to upload');
      return false;
    }
    filetoload.value = importliste.getCurrentDirPath();
    return true;
  }
  init();
}