import {
  browser_accept,
  dom_purify,
  fetchSettings,
  add_custom_events,
  create_box,
  format_bytes,
  generate_uuid,
  dirseparator
} from '../modules/utils.js';
import {
  css,
} from '../modules/modules-config.js';
import {
  JsDirList,
  defaultOptions
} from '../modules/files/js-dirlist.js';
const objaccept = {
  "image/*": [".png", ".jpeg", ".jpg"],
  "text/tab-separated-values": [".tsv"],
  "application/zip": [".zip"],
  "application/gzip": [".gz"],
  "application/x-bzip": [".bz"],
  "application/x-bzip2": [".bz2"]
}
const accept = Object.values(objaccept).reduce((a, b) => a.concat(b));
css.mright = 'mr-4';
const filter_files = {
  images: "png,jpeg,jpg,gif",
  tsv: "txt,tsv,zip, gzip,gz"
}
export class JsMyFiles {
  done = true;
  jsDirToZip = null;
  jsDirList = null;
  trash_dir_name = 'trash.';
  counters = {};
  _events = {};
  eventnames = {
    complete: 'complete',
    error: 'error',
  };
  rejected = [];

  constructor(container, options = {}) {
    if (!container.jsmyfiles) {
      container = (container instanceof HTMLElement) ? container : document.querySelector(container);
      if (!container) return;
      dom_purify(container, 'dataset');
      this.container = container;
      const defaultOptions = {
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
          reject: {
            display: {
              counter: 'counterrejected'
            }
          }
        },
        upload: {
          label: 'upload'
        },
        btnprefix: 'btn',
        btnfilelist: null,
        selectors: {
          droptarget: '.droptarget',
          trigger: '.trigger',
          uploadfile: 'uploadfile',
        },
        display: {
          progression: 'display-progression',
          dropzone: 'dropzone',
          boxtitle: 'boxtitle',
          counters: 'counters',
          sizes: 'sizes',
          timers: 'timers'
        },

        css: {
          dragover: 'dragover'
        }
      };
      this.options = Object.assign(defaultOptions, options);
      this.options.browse = (container.dataset.browse) ? container.dataset.browse.split(',') : ['directory', 'file'];
      this.haspicker = (window.showDirectoryPicker);
      this.options.browse = (container.dataset.browse) ? container.dataset.browse.split(',') : ['directory', 'file'];
      this.init();
      container.jsmyfiles = this;
    }
    return container.jsmyfiles;
  }
  init() {
    // create dirlist box
    add_custom_events(this);
    this.addDisplayProgression();

    this.addDirList();
    this.addDropzone();
    this.initControls();
    this.initEvents().then(() => {
      this.resetCounters();
    });
  }
  initTimer() {
    this.timer = new Date();
  }
  async initEvents() {
    add_custom_events(this);
    //To be refactored - for steppers )
    this.on(this.eventnames.processed, async (e) => {
      if (this.nextaction) await this.nextaction();
    });
    // alerts on error
    this.on(this.eventnames.error, (e) => {
      console.log('scandir receive error message', e)
      if (window.alertbox) {
        window.alertbox.renderAlert({
          type: window.alertbox.alertconfig.types.error,
          content: e,
          inverse: true,
          dismissible: true
        });
      }
    });
    const self = this;
    if (this.options.controls.zip) {
      const {
        JsDirToZip
      } = await import('../modules/files/js-dirtozip.js');
      this.jsDirToZip = new JsDirToZip();
      Object.keys(this.jsDirToZip.eventnames).forEach((key) => {
        this.eventnames[key] = this.jsDirToZip.eventnames[key];
        this.jsDirToZip.on(key, (e) => {
          switch (key) {
            case this.eventnames.counter:
              self.fileCounter(e);
              break;
            case this.eventnames.reject:
              this.rejected.push(e.path);
              this.fileCounter({
                name: 'reject',
                path: e.path,
              });
              break;
            case this.eventnames.complete:
              if (!e || !e.name) {
                console.log('no emit complete name');
                return;
              }
              self.showControl(e.name, e);
              break;
            case this.eventnames.message:
              switch (e.name) {
                case 'console':
                  this.addConsoleMessage({
                    id: (e.id) ? e.id : null,
                    content: e.message,
                    parent: this.container
                  });
                  break;
                case window.alertbox.alertconfig.types.error:
                case window.alertbox.alertconfig.types.success:
                case window.alertbox.alertconfig.types.danger:
                case window.alertbox.alertconfig.types.info:
                  window.alertbox.renderAlert({
                    type: e.name,
                    content: e.message,
                    dismissible: true,
                    inverse: false
                  });
                  console.log('error', e);
                  break;
                default:
                  console.log('message', e);
                  break;
              }
              break;
            case this.eventnames.terminate:
              console.log('terminate', e)
              break;
            default:
              console.log('showcontrol ' + key, e)
              self.showControl(key, e);
              break;
          }
        });
      });
    }
    window.addEventListener('beforeunload', (e) => {
      if (!this.done) {
        e.preventDefault();
        e.returnValue = (this.options.preventclose) ? this.options.preventclose : `Some work is in progress in this window.\nAre you sure you want to leave?`;
      }
    });
  }
  emitToZip(btn) {
    const message = (btn.dataset.message) ? JSON.parse(btn.dataset.message) : null;
    if (!message) btn.classList.add(css.hide);
    if (message) {
      if (message.name) {
        const name = message.name;
        delete message.name;
        this.jsDirToZip.emit(name, message);
      }
    }
    if (name === this.eventnames.sendfile) btn.disabled = true;
  }

  quotaEstimate(obj) {
    return this.jsDirToZip.quotaEstimate();
  }
  scanBrowse(e, options) {
    return this.jsDirToZip.scanBrowse(e, options);

  }
  scanHandle(dir, options) {
    return this.jsDirToZip.scanHandle(dir, options);
  }
  async handleBrowse(e) {
    this.initTimer();
    this.toggleCounters(true);
    if (!this.haspicker) e = e.target.files;
    await this.scanBrowse(e, {
      accept: accept,
    });
  }

  addDropzone() { //
    this.uploadentry = null;
    this.dropzone = create_box('div', {
      id: this.options.display.dropzone
    });
    const input = (this.haspicker) ? null : create_box('input', {
      type: "file",
      name: this.options.selectors.uploadfile,
      id: this.options.selectors.uploadfile,
      multiple: true,
      allowdirs: true,
      accept: accept,
      class: 'hidden'
    }, this.dropzone);
    if (input) input.addEventListener("change", (e) => {
      this.handleBrowse(e)
    });
    const btns = create_box('div', {},
      this.dropzone);

    this.options.browse.forEach(opt => {
      const text = (this.container.dataset[`textbrowse${opt}`]) ? this.container.dataset[`textbrowse${opt}`] : `browse${opt}`;
      const btn = create_box('span', {
        class: this.options.selectors.trigger.slice(1),
        dataset: {
          type: opt
        },
        text: text
      }, btns);
      btn.addEventListener('click', async (e) => {
        if (this.haspicker) {
          this.openDirDialog(opt, (e) => {
            this.handleBrowse(e)
          });
        } else {
          if (opt === "directory") {
            input.directory = true;
            input.webkitdirectory = true;
          } else { //file
            input.directory = false;
            input.webkitdirectory = false;
          }
          input.dispatchEvent(new MouseEvent("click"));

        }

      });
    });
    const spandrop = create_box('span', {
      text: this.container.dataset.textdrop
    }, btns);

  }

  toggleDropTarget(on = true) {
    const self = this;
    const droptarget = (this.activentry) ? this.activentry.container : null;
    if (droptarget === null) return;
    const cssdragover = (this.jsDirList) ? this.jsDirList.options.entry.css.dragover : this.options.css.dragover;
    const target_dragover = (e) => {
      if (!this.dragover && this.activentry && this.activentry.container === e.currentTarget) {
        droptarget.classList.add(cssdragover);
      }
      self.handleDragOver(e);
    }
    const target_drop = async (e) => {
      droptarget.classList.remove(cssdragover);
      self.handleDrop(e);
    }

    // set events and css for new dropzone
    if (on === false) {
      droptarget.removeEventListener('dragover', target_dragover);
      droptarget.removeEventListener('drop', target_drop);
      droptarget.classList.remove(this.options.selectors.droptarget.substr(1));
    } else {
      droptarget.addEventListener('dragover', target_dragover);
      droptarget.addEventListener('drop', target_drop);
      droptarget.classList.add(this.options.selectors.droptarget.substr(1));
    }
  }

  async addDirList() {
    this.jsDirList = new JsDirList(this.container);
    this.activentry = this.jsDirList.root;
    this.rootitem = this.targetitem = this.activentry.container;
    this.jsDirList.on(this.jsDirList.eventnames.attach, (e) => {
      if (!e.entry) return;
      this.detachDropzone();
      this.activentry = e.entry;
      this.targetitem = this.activentry.container;
      if ([this.activentry.options.type.directory, this.activentry.options.type.root].indexOf(this.activentry.type) >= 0) this.addUploadDialog();
    });
    this.jsDirList.on(this.jsDirList.eventnames.detach, (e) => {
      this.detachDropzone();
      this.activentry = null;
      this.targetitem = null;
    });
    this.jsDirList.on(this.jsDirList.eventnames.action, (e) => {
      if (e.detail.action === "drop") this.handleDrop(e.detail.event);
      else console.log('action not managed ' + e.detail.action, e.detail)
    });
    this.activentry.label.dispatchEvent(new Event('click'));
  }

  addDisplayProgression() {
    // add counters
    if (this.displayprogression) return;
    let el = document.getElementById(this.options.display.progression);
    if (!el) {
      el = create_box('div', {
        id: this.options.display.progression
      }, this.container);
      el.innerHTML = `<div class="flex sm:flex-row"><div class="${this.options.display.counters}"></div><div class="${this.options.display.sizes}"></div><div class="${css.progress}"></div><div class="${this.options.display.timers}"></div></div>`;
      this.displayprogression = el;
    }
  }
  enableDropzone(enable = true, destroy = false) {
    if (destroy || enable === false) this.dropzone.classList.add(css.hide);
    if (enable) {
      this.dropzone.dataset.enabled = true;
      this.dropzone.classList.remove(css.hide);
    } else delete this.dropzone.dataset.enabled;
  }
  //
  attachDropzone() {
    if (this.dropzone.dataset.enabled) {
      this.targetitem.insertBefore(this.dropzone, this.activentry.label.nextElementSibling);
      this.toggleDropTarget(true);
    }
  }
  detachDropzone() {
    this.enableDropzone(false);
    this.toggleDropTarget(false);
  }

  openDirDialog(type, callback) {
    // if chrome 86 , edge 86, opera 72
    const showpick = (type === "directory") ? window.showDirectoryPicker : window.showOpenFilePicker;
    const pickopts = (type === "directory") ? {
      mode: "read",
      multiple: true
    } : {
      types: [{
        description: "Images,.tsv, zip, gzip, tar files",
        accept: objaccept,
      }, ],
      excludeAcceptAllOption: true,
      multiple: true,
    };
    showpick(pickopts).then(pick => {
      callback(pick);
    });
  }

  //  drag&drop
  async handleDrop(e) {
    if (this.uploadentry !== null) return;
    this.uploadentry = this.activentry;
    let dataTransfer;
    if (e.dataTransfer) {
      e.preventDefault();
      dataTransfer = e.dataTransfer;
    } else dataTransfer = e;
    this.done = false;
    this.initTimer();
    const items = [...((dataTransfer.items) ? dataTransfer.items : dataTransfer.files)];
    if (items.length) {
      this.enableDropzone(false);
      await items.forEach(async item => {
        if (item.kind === "file") {
          item = await item.webkitGetAsEntry();
          this.toggleCounters(true);
          await this.scanHandle(item);
        }
      })
    }
  }
  handleDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
  }
  showComplete() {
    this.timer = (new Date() - this.timer) / 1000;
    console.log('item-------------------------------------' + parseInt(this.timer / 60) + ' --- ' + (this.timer - (parseInt(this.timer / 60) * 60)));
    this.enableDropzone();
  }

  stopOnError(err) {
    console.log('err', err);
  }

  addConsoleMessage(message) {
    //message {message:, parent:}
    message.parent = (message.parent) ? message.parent : this.container;
    window.alertbox.addConsoleMessage(message);
  }

  addUploadDialog() {
    console.log(' uploadentry ', this.uploadentry)
    if (this.uploadentry !== null) return;
    if (this.options.controls.scan) {
      this.enableDropzone(true);
      this.attachDropzone();
    }
  }

  async addFilesStore(name, callback) {
    name = (name) ? name : this.options.dbname;
    if (!this.jsFilesStore) {
      const {
        JsFilesStore
      } = await import('../modules/files/js-filesystem.js');
      this.jsFilesStore = new JsFilesStore(null, callback);
      this.displayFiles();
    }
    if (callback) await callback();
  }
  displayFiles() {
    this.jsFilesStore.getItems('local');
  }

  fileCounter(e) {
    const counters = this.counters[e.name];
    counters.counter += 1
    if (e.size !== null) counters.size += parseInt(e.size);
    counters.display.counter.textContent = counters.counter;
    if (counters.display.size) counters.display.size.textContent = format_bytes(counters.size);
    this.quotaEstimate();
  }

  resetCounter(item) {
    const counters = this.counters[item];
    ['counter', 'size'].forEach(el => {
      if (counters.display[el]) {
        this.counters[item][el] = 0;
        counters.display[el].textContent = 0;
      }
    });
    this.toggleCounters(false);
  }
  resetCounters() {
    Object.keys(this.options.controls).forEach(key => {
      this.resetCounter(key);
    })
  }
  toggleCounters(show = true) {
    const el = document.getElementById(this.options.display.progression);
    if (!el) return;
    if (show) el.classList.remove(css.hide);
    else el.classList.add(css.hide);
  }

  initFileCounter(item, opts, i) {
    const sep = (i) ? ` / ` : ``;
    let counter = 0;
    let counterdisplay = null;
    let size = 0;
    let sizedisplay = null;
    // create dom display elements


    let boxcounters = document.getElementById(this.options.display.progression);
    const itemopts = {
      display: {},

    };
    Object.entries(opts).forEach(([k, val]) => {
      const cl = k + 's';
      const txt = {
        counter: ' read',
        size: ' read',
        counterzipped: ' compressed',
        sizezipped: ' compressed',
        counterrejected: ' rejected',
      }
      let elinsert = boxcounters.querySelector('.' + cl);
      if (!elinsert) elinsert = create_box('div', {
        class: cl
      }, boxcounters, ``);
      let el = elinsert.querySelector('.' + val);
      if (!el) {
        el = create_box('span', {
          class: val,
        }, elinsert, ` / `);
        if (txt.hasOwnProperty(val)) {
          // add a link to display the rejected files list
          if (val === 'counterrejected') {
            const link = create_box('a', {
              text: txt[val],
              class: 'text-error',
              title: `Click to display the list of rejected files`
            }, elinsert);
            link.addEventListener('click', (e) => {
              e.preventDefault();
              this.displayReject(link);
            });
          } else elinsert.append(document.createTextNode(txt[val]));
        }
      } else this.resetCounter(item);
      itemopts.display[k] = el;
      itemopts[k] = 0;
    });

    this.counters = { ...this.counters,
      ...{
        [item]: itemopts
      }
    };
  }
  displayReject(el) {
    const message = {
      type: window.alertbox.alertconfig.types.warning,
      parent: el,
      content: `Files ${this.rejected.join('<br>')} type rejected`,
    };
    if (el.dataset.hasmessage) {
      window.alertbox.removeItemMessage(message);
      delete el.dataset.hasmessage;
    } else {
      el.dataset.hasmessage = true;
      window.alertbox.addItemMessage(message);
    }
  }
  showControl(action, opts) {
    const target = ((opts.hasOwnProperty('bigfile') && opts.bigfile) ? 'zipped' : 'zip');
    let message, text = null;
    // 'zip' ---only btn for zip actions for the moment
    const btn = this[this.options.btnprefix + 'zip' + target];
    if (!btn) return;
    btn.removeAttribute("disabled");
    const part = (opts && opts.part) ? opts.part : false;
    const bigfile = (opts && opts.bigfile) ? opts.bigfile : false;
    const filepath = (opts && opts.path) ? opts.path : this.uploadentry.getCurrentDirPath();
    switch (action) {
      case this.eventnames.ready:
        this.resetCounters();
        this.uploadentry.list();
        if (btn.dataset.message) delete btn.dataset.message;
        btn.classList.add(css.hide);
        break;
      case this.eventnames.follow:
        if (btn.dataset.message) delete btn.dataset.message;
        btn.classList.add(css.hide);
        break;
      case this.eventnames.endzip:
        if (!part) this.showComplete();
        btn.textContent = `Close zip file` + ((part) ? ` ` + part : ``);
        btn.title = (part) ? `Your file is too big - you have to send this part before continuing to process the directory` : `Click to end zip file`;
        message = {
          name: this.eventnames.endzip,
          part: part,
          filepath: filepath,
          bigfile: (target !== 'zip') ? bigfile : false,
        };
        btn.dataset.message = JSON.stringify(message);
        break;
      case this.eventnames.complete:
        console.log('complete', opts)
        if (bigfile && bigfile !== '') {
          btn.textContent = `Upload big File separately`;
          message = {
            name: this.eventnames.bigfile,
            path: filepath,
            part: part,
            bigfile: bigfile
          };
          btn.dataset.message = JSON.stringify(message);
          console.log('bigfile', message)
        }
        break;
      case this.eventnames.sendfile:
        console.log('opts sendfile', opts)
        message = {
          name: this.eventnames.sendfile,
          path: filepath,
          part: part,
          bigfile: bigfile
        };
        btn.textContent = `Upload zip file`;
        if (message.bigfile && message.bigfile !== '') btn.textContent += ` ` + opts;
        btn.dataset.message = JSON.stringify(message);
        break;
      case this.eventnames.pending:
        btn.textContent = ` Pending ` + ((target !== 'zip') ? ' big file' : '');
        btn.dataset.message = '';
        btn.setAttribute("disabled", true);
        break;
      case this.eventnames.gzip:
        text = `compressing separately big file :${(opts && opts.bigfile)?filepath:``} ${(opts && opts.size)?opts.size:``}`;
        btn.textContent = text;
        btn.setAttribute("disabled", true);
        btn.dataset.message = JSON.stringify({
          name: this.eventnames.endzip,
          path: filepath,
          part: part,
          bigfile: bigfile
        });
        break;
      case this.eventnames.terminate:
        console.log('terminate ' + ((target !== 'zip') ? 'bigfile' : ''));
        btn.dataset.message = JSON.stringify({
          name: 'ready',
          bigfile: (target !== 'zip')
        });
        btn.click();
        this.uploadentry = null;
        break;
    }
    if (btn.dataset.message) btn.classList.remove(css.hide);
  }

  getBtn(item, target) {
    const btnkey = this.options.btnprefix + item + target;
    if (this[btnkey]) return this[btnkey];
    const display = this.options.controls[item].btn[target];
    const btn = document.getElementById(display);
    const parent = this.displayprogression;
    if (!btn) {
      parent.insertAdjacentHTML('beforeend', `<button id="${display}" class="button ${display} ${css.mright} ${css.hide}"></button>`);
      this[btnkey] = document.getElementById(display);
      this[btnkey].addEventListener('click', async (e) => {
        e.stopImmediatePropagation();
        this.emitToZip(e.currentTarget);
      });
    } else parent.append(btn);
    return this[btnkey];
  }

  initControls() {
    Object.entries(this.options.controls).forEach(([key, control], i) => {
      this.initFileCounter(key, control.display, i);
      if (control.btn) this.activateControls(key, control.btn);
    });
  }
  activateControls(key, btns) {
    Object.keys(btns).forEach((btn) => {
      this[this.options.btnprefix + key + btn] = this.getBtn(key, btn);
    })

  }

}