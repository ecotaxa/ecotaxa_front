import DOMPurify from 'dompurify';
import {
  fetchSettings,
  create_box
} from '../modules/utils.js';
import {
  css,
} from '../modules/modules-config.js';
css.displayimport = 'displayimport';
export class JsImport {
  typeimport;
  myFiles;
  eventnames = {
    import: 'import'
  };
  url = {};
  constructor(container, options = {}) {
    container = (container instanceof HTMLElement) ? container : document.querySelector(container);
    if (!container) return;
    this.container = container;
    const defaultOptions = {
      selector: {
        typeimport: "typeimport",
        importzone: "file_to_load",
        showfiles: ".showfiles",
      },
      url: {
        import: "gui/import",
        dirlist: "gui/files"
      },
      importzone: "import-list",
      sourcezone: "dirlist"
    };

    this.options = Object.assign(defaultOptions, options);
    this.url.dirlist = (container.dataset.dirlist) ? container.dataset.dirlist : this.options.url.dirlist;
    this.url.import = (container.dataset.import) ? container.dataset.import : this.options.url.import;
    const importzoneid = (container.dataset.importzone) ? container.dataset.importzone : this.options.importzone;
    console.log('container ' + importzoneid, container)
    this.init(importzoneid);
  }

  init(importzoneid) {
    // init steps to display import sequence
    this.addImportZone(importzoneid);
    this.container.querySelectorAll('input[name="' + this.options.selector.typeimport + '"]').forEach(typeimport => {
      typeimport.addEventListener('change', (e) => {
        if (e.currentTarget.checked) {
          console.log(e.currentTarget)
          this.typeimport = e.currentTarget.value;
          this.showSelection(true);
        }
      })
    });
    this.showSelection();
  }
  addImportZone(importzoneid) {
    let importzone = document.getElementById(importzoneid);
    console.log('importzone ' + importzoneid, importzone)
    importzone.classList.add(css.displayimport);
    if (importzone === null) return;
    if (importzone.children.length === 0) {
      const input = create_box('input', {
        type: "hidden",
        id: "files_to_load",
        name: "files_to_load",
        class: "form-input",
        required: true
      })
      const response = create_box('div', {
        class: "response-summary"
      }, );
      create_box('div', {
        id: "total-objects",
        class: "info",
        data: {
          text: "Total objects"
        }
      }, response);
      create_box('div', {
        id: "total-tsv",
        class: "info",
        data: {
          text: "Total TSV"
        }
      }, response);
    }
    return importzone;
  }
  async showSelection(refresh = false) {
    console.log('showselection')
    const apply_filters = () => {
      let filters = this.typeimport.split('-');
      filters = filters.map(filter => {
        return new Set([...(filter_files[filter] ? filter_files[filter] : [])]);
      });
      this.myFiles.container.querySelectorAll('[data-ftype]').forEach(entry => {
        if (filters.has(entry.dataset.ftype)) entry.classList.remove('disabled');
        else entry.classList.add('disabled');
      });
    }
    const displayselection = document.getElementById(this.options.sourcezone);
    const displayresult = document.getElementById(this.options.importzone);
    if (!displayselection || !displayresult) return;
    console.log('displayselection', displayselection)
    if (!this.myFiles) {

      const {
        JsMyFiles
      } =
      await import('../modules/js-my-files.js');


      this.myFiles = new JsMyFiles(displayselection, {
        import: this.url.toimport,
        url: this.url.dirlist,
        upload: {
          label: (displayselection.dataset.uploadlabel) ? (displayselection.dataset.uploadlabel) : 'upload',
          callback: () => {
            this.showSubmit();
          }
        }
      });
      this.addImportControls();
    }

    if (refresh === true) apply_filters();

  }
  addImportPath(value) {
    document.getElementById(this.options.selector.importzone).value = value;
    const displayresult = document.getElementById(this.options.selector.displayresult);
    if (displayresult) displayresult.innerHTML = `<li>${value.split('/').pop()}</li>`;
    const options = this.container.querySelector('#' + this.options.selector.importoptions);
  }
  addImportControls() {
    const import_entry = (entry) => {

    }
    const control = {
      import: {
        action: 'import',
        icon: 'icon-arrow-down-on-square-stack',
        typentries: ['D', 'F'],
        text: 'import into project',
        callback: import_entry
      }
    };
    this.myFiles.jsDirList.options.entrycontrols.controls = { ...control,
      ...this.myFiles.jsDirList.options.entrycontrols.controls
    };
    this.myFiles.jsDirList.import = (entry) => {
      console.log('yes good , very googd', entry);

    }
  }
  showSubmit(show = true) {
    const submit = this.container.querySelector('[type="submit"]');
    console.log('sub', submit)
    if (show) {
      submit.classList.remove('hide');
      submit.disabled = false;
    } else submit.disabled = true;
  }
}