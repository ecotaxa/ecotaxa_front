import DOMPurify from 'dompurify';

import {
  FormSubmit
} from '../modules/form-submit.js';
import {
  fetchSettings,
} from '../modules/utils.js';
import {
  css,
  filter_files
} from '../modules/modules-config.js';

export class JsImport {
  typeimport;
  myFiles;
  constructor(container, options = {}) {
    container = (container instanceof HTMLElement) ? container : document.querySelector(container);
    if (!container) return;
    this.container = container;
    const defaultOptions = {
      selector: {
        displayresult: 'results',
        typeimport: "typeimport",
        importzone: "file_to_load",
        showfiles: ".showfiles",
        displayselection: "dirlist"
      }
    };

    this.options = Object.assign(defaultOptions, options);

    this.init();
  }

  init() {
    // init steps to display import sequence
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
  async showSelection(refresh = false) {
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
    const displayselection = document.getElementById(this.options.selector.displayselection);
    const displayresult = document.getElementById(this.options.selector.displayresult);
    if (!displayselection || !displayresult) return;
    if (!this.myFiles) {
      const {
        JsMyFiles
      } =
      await import('../modules/js-my-files.js');
      this.myFiles = new JsMyFiles(displayselection, {
        enableupload: true,
        enablestore: true,
        btnfilelist: this.options.showfiles,
        upload: {
          label: (displayselection.dataset.uploadlabel) ? (displayselection.dataset.uploadlabel) : 'upload',
          callback: () => {
            this.addImportPath('/tmp/ecotaxa_user.760/ecotaxa_import');
            this.showSubmit();
          }
        }
      });
    }

    if (refresh === true) apply_filters();

  }
  addImportPath(value) {
    document.getElementById(this.options.selector.importzone).value = value;
    const displayresult = document.getElementById(this.options.selector.displayresult);
    if (displayresult) displayresult.innerHTML = `<li>${value.split('/').pop()}</li>`;
    const options = this.container.querySelector('#' + this.options.selector.importoptions);
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