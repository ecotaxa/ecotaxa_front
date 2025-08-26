import {
  dom_purify,
  fetchSettings,
  create_box,
  format_bytes,
  generate_uuid,
  dirseparator,
  html_spinner
} from '../modules/utils.js';
import {
  css,
} from '../modules/modules-config.js';
import {
  AlertBox
} from '../modules/alert-box.js';
import {
  JsDirList,
  dirlistOptions
} from '../modules/files/js-dirlist.js';
import {
  ModuleEventEmitter
} from '../modules/module-event-emitter.js';
const objaccept = {
  "image/*": [".png", ".jpeg", ".jpg"],
  "text/tab-separated-values": [".tsv"],
  "application/zip": [".zip"],
  "application/gzip": [".gz"],
  "application/x-bzip": [".bz"],
  "application/x-bzip2": [".bz2"]
}
const accept = Object.values(objaccept).reduce((a, b) => a.concat(b));
css.button = 'button p-1 mx-auto sm:mr-4 mb-4';
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
  errorfile = [];
  listener;
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
          },
          errorfile: {
            display: {
              counter: 'countererrorfile'
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
      this.uuid = generate_uuid();
      this.init();
      container.jsmyfiles = this;
    }
    return container.jsmyfiles;
  }
  init() {
    // create dirlist box
    this.addDisplayProgression();
    this.addDropzone();
    this.addDirList();
    this.initControls();
    this.initEvents().then(() => {
      this.resetCounters();
    });
  }
  initTimer() {
    this.timer = new Date();
  }
  async initEvents() {
    //To be refactored - for steppers )
    ModuleEventEmitter.on(this.eventnames.processed, async (e) => {
      if (this.nextaction) await this.nextaction();
    }, this.uuid);
    const self = this;
    if (this.options.controls.zip) {
      const {
        JsDirToZip
      } = await import('../modules/files/js-dirtozip.js');
      this.jsDirToZip = JsDirToZip({
        listener: this.uuid
      });

      Object.keys(this.jsDirToZip.eventnames).forEach((key) => {
        this.eventnames[key] = this.jsDirToZip.eventnames[key];
        ModuleEventEmitter.on(key, (e) => {
          switch (key) {
            case this.eventnames.counter:
              this.fileCounter(e);
              break;
            case this.eventnames.reject:
              this.rejected.push(e.path);
              this.fileCounter({
                name: 'reject',
                path: e.path,
              });
              break;
            case this.eventnames.follow:
            case this.eventnames.complete:
              if (!e || !e.hasOwnProperty("name") || e.name === "") {
                console.log('no emit complete name' + key, e);
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
                  case 'browser':
                   AlertBox.addAlert({
                    type: AlertBox.alertconfig.types.danger,
                    content: e.message,
                    dismissible: false,
                    inverse: false
                  });
                  break;
                case this.eventnames.errorfile:
                    self.showControl(e.name, e);
                    e.name=AlertBox.alertconfig.types.error;
                    e.message+=(e.path)?' '+e.path:'';
                case AlertBox.alertconfig.types.error:
                case AlertBox.alertconfig.types.success:
                case AlertBox.alertconfig.types.danger:
                case AlertBox.alertconfig.types.info:
                  AlertBox.addAlert({
                    type: e.name,
                    content: e.message,
                    dismissible: true,
                    inverse: false
                  });
                  break;
                default:
                  console.log('message', e);
                  break;
              }
              break;
          }
        }, this.uuid);
      });
            this.jsDirToZip.browserRequired() ;
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
        console.log('name'+name,message)
        ModuleEventEmitter.emit(name, message, this.jsDirToZip.uuid);
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
    if (!this.setUploadEntry()) return;
    this.initTimer();
    this.toggleCounters(true);
    if (!this.haspicker) e = e.target.files;
    await this.scanBrowse(e, {
      accept: accept,
    });
  }

  addDropzone() { //
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
        // if other functionalities add controls ( like import) clear
        if(this.eventnames.clearother) ModuleEventEmitter.emit(this.eventnames.clearother,{},this.uuid);
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

    function highlight(e) {
        droptarget.classList.add(cssdragover)
    }
    function unhighlight(e) {
        droptarget.classList.remove(cssdragover);
    }
    const cssdragover = (this.jsDirList) ? (this.jsDirList.options.entry) ? this.jsDirList.options.entry.css.dragover : this.options.css.dragover : this.options.css.dragover;
    const target_dragover = (e) => {e.preventDefault();
      if (!this.dragover && this.activentry && this.activentry.container === e.currentTarget) {
        droptarget.classList.add(cssdragover);
      }
    e.dataTransfer.dropEffect = "move";
    }
    const target_drop = async (e) => { await self.handleDrop(e);}
    // set events and css for new dropzone
    if (on === false) {
     ['dragenter', 'dragover'].forEach(eventname => {
        droptarget.removeEventListener(eventname, highlight, false);
    });
    ['dragleave', 'drop'].forEach(eventname => {
        droptarget.removeEventListener(eventname, unhighlight, false);
    });
      droptarget.removeEventListener('drop', target_drop);
      droptarget.classList.remove(this.options.selectors.droptarget.substr(1));
    } else {
    ['dragenter', 'dragover'].forEach(eventname => {
        droptarget.addEventListener(eventname, highlight, false);
    });
    ['dragleave', 'drop'].forEach(eventname => {
    droptarget.addEventListener(eventname, unhighlight, false);
    });
      droptarget.addEventListener('drop', target_drop);
      droptarget.classList.add(this.options.selectors.droptarget.substr(1));
    }
  }

  async addDirList() {
    this.jsDirList = new JsDirList(this.container);
    this.activentry = this.jsDirList.root;
    this.rootitem = this.targetitem = this.activentry.container;
    ModuleEventEmitter.on(this.jsDirList.eventnames.attach, (e) => {
      if (!e.entry) return;
      if (e.entry !== this.activentry && this.activentry.isBranch(true)) this.detachDropzone();
      this.activentry = e.entry;
      this.targetitem = this.activentry.container;
      if (this.activentry.isBranch(true)) this.addUploadDialog();
    }, this.jsDirList.uuid);
    ModuleEventEmitter.on(this.jsDirList.eventnames.detach, (e) => {
      this.detachDropzone();
      this.activentry = null;
      this.uploadentry = null;
      this.targetitem = null;
    }, this.jsDirList.uuid);
    ModuleEventEmitter.on(this.jsDirList.eventnames.action, (e) => {
      switch (e.action) {
        case "drop":
          this.handleDrop(e.event);
          break;

        default:
          console.log('action not managed ' + e.action, e);
          break;
      }
    }, this.jsDirList.uuid);
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
      el.insertAdjacentHTML('afterbegin', `<div class="${this.options.display.progression}"><div class="${this.options.display.counters}"></div><div class="${this.options.display.sizes}"></div><div class="${css.progress}"></div><div class="${this.options.display.timers}"></div></div>`);
      this.displayprogression = el;
    }
  }
  enableDropzone(enable = true, destroy = false) {
    if (destroy || enable === false) this.dropzone.classList.add(css.hide);
    if (enable) {
      this.dropzone.dataset.active = true;
      this.dropzone.classList.remove(css.hide);
    } else delete this.dropzone.dataset.active;
  }
  //
  attachDropzone() {
    if (this.dropzone.dataset.active) {
      this.targetitem.insertBefore(this.dropzone, this.activentry.label.nextElementSibling);
      this.toggleDropTarget(true);
    }
    ['dragover', 'dragenter'].forEach(eventname => {
     window.addEventListener(eventname, function(e) {e.preventDefault();}, false);
    });
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

  setUploadEntry() {
    if (this.uploadentry && this.uploadentry !== this.activentry) {
      AlertBox.addAlert({
        type: "error",
        content: 'Only one upload destination authorized. Close and upload the current zipfile.',
        dismissible: true,
        inverse: true
      });
      return false;
    }
    this.uploadentry = this.activentry;
    return true;
  }
  // drag&drop


  async handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    if (!this.setUploadEntry()) return;
    let dataTransfer;
    if (e.dataTransfer) {
      dataTransfer = e.dataTransfer;
    } else dataTransfer = e;
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
   showComplete() {
    this.timer = (new Date() - this.timer) / 1000;
    this.enableDropzone(true);
  }

  stopOnError(err) {
    console.log('err', err);
  }

  addConsoleMessage(message) {
    //message {message:, parent:}
    message.parent = (message.parent) ? message.parent : this.container;
    AlertBox.addConsole(message);
  }

  addUploadDialog() {
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
    counters.counter += 1;
    if (e.size !== null) counters.size += parseInt(e.size);
    counters.display.counter.textContent = counters.counter;
    if (counters.display.size) counters.display.size.textContent = format_bytes(counters.size);
    this.quotaEstimate();
  }

  resetCounter(item) {
    const counters = this.counters[item];
    ['counter', 'size'].forEach(el => {
      if (counters.display[el]) {
        counters[el] = 0;
        counters.display[el].textContent = 0;
      }
    });
  }
  resetCounters() {
    Object.keys(this.options.controls).forEach(key => {
      this.resetCounter(key);
    });
    this.toggleCounters(false);
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
        countererrorfile: ' error',
      }
      const displaylist = ['counterrejected', 'countererrorfile'];
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
          if (displaylist.indexOf(val) >= 0) {
            const link = create_box('a', {
              text: txt[val],
              class: 'text-error',
              title: `Click to display the list of ${txt[val]} files`
            }, elinsert);
            link.addEventListener('click', (e) => {
              e.preventDefault();
              this.displayExcept(link, val);
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
  displayExcept(el, type) {
    type = type.replace('counter', '');
    const textval = {
      rejected: ` type rejected`,
      errorfile: ` in error`
    };
    if (Object.keys(textval).indexOf(type) < 0) return;
    const message = {
      type: AlertBox.alertconfig.types.warning,
      parent: el,
      content: `Files ${this.rejected.join('<br>')} ${textval[type]}`,
    };
    if (el.dataset.hasmessage) {
      AlertBox.removeMessage(message);
      delete el.dataset.hasmessage;
    } else {
      el.dataset.hasmessage = true;
      AlertBox.addMessage(message);
    }
  }

  showControl(action, opts) {
    const part = (opts && opts.part) ? opts.part : false;
    const bigfile = (opts && opts.bigfile) ? opts.bigfile : false;
    const filepath = (opts && opts.path) ? opts.path : this.uploadentry.getCurrentDirPath();
    const target = ((opts.hasOwnProperty('bigfile') && bigfile !== false) ? 'zipped' : 'zip');
    let message, text = null;
    // 'zip' ---only btn for zip actions for the moment
    const btn = this[this.options.btnprefix + 'zip' + target];
    if (!btn) return;
    btn.disabled = false;
    let click_btn=false;
    switch (action) {
      case this.eventnames.ready:
        this.resetCounters();
        if (this.uploadentry)  this.uploadentry.list().then(()=>{ this.uploadentry.setOpen(true);this.uploadentry = null;});
        message = null;
        break;
      case this.eventnames.follow:
        if (bigfile) {
          console.log(' follow', opts);
          message = {};
          btn.textContent = `Wait for next operation`;
          btn.disabled = true;
        } else message = null;

        break;
      case this.eventnames.bigfile:
        if (bigfile && bigfile !== '') {
          btn.textContent = `Upload big File separately`;
          message = {
            name: this.eventnames.endzip,
            path: filepath,
            part: part,
            bigfile: bigfile
          };
        }
        break;
        case this.eventnames.endzip:
        if (!part) this.showComplete();
        // combine endzip and upload for prod
        btn.textContent = `Upload zip file` + ((part) ? ` ` + part : ``);
        btn.title = (part) ? `Your file is too big - you have to send this part before continuing to process the directory` : `Click to send zip file`;
       /* btn.textContent = `Close zip file` + ((part) ? ` ` + part : ``);
        btn.title = (part) ? `Your file is too big - you have to send this part before continuing to process the directory` : `Click to end zip file`;*/
        message = {
          name: this.eventnames.endzip,
          part: part,
          filepath: filepath,
          path: filepath,
          bigfile: bigfile,
        };
        break;
    case this.eventnames.sendfile:
        this.done=false;
        btn.dataset.message = JSON.stringify({
          name: this.eventnames.sendfile,
          path: filepath,
          part: part,
          bigfile: bigfile
        });
        // send file , 2 steps are for tests - timeout for zip.end() in dirtozip
        setTimeout( () => {this.emitToZip(btn);},1000);
        return;
        //btn.textContent = `Upload zip file`;
        //if (message.bigfile && message.bigfile !== '') btn.textContent += ` ` + opts;
        break;
      case this.eventnames.pending:
        btn.textContent = ` Uploading ` + ((target !== 'zip') ? ' big file' : '');
        btn.disabled = true;
        message = {};
        break;
      case this.eventnames.gzip:
        text = `compressing big file :${(opts && opts.bigfile)?filepath :``} ${(opts && opts.size)?format_bytes(opts.size):``}`;
        btn.textContent = text;
        btn.disabled = true;
        message = {};
        break;
      case this.eventnames.terminate:
        btn.dataset.message = JSON.stringify({
          name: this.eventnames.init,
          bigfile: bigfile,
          part: part,
          path: filepath
        });
        this.done=true;
        btn.classList.add(css.hide);
        btn.click();
        return;
        break;
      case this.eventnames.errorfile:
      case this.eventnames.error:
        btn.textContent = (opts.text) ? opts.text : `Error `+JSON.stringify(message);
        btn.classList.add(css.console);
        btn.disabled=true;
        message=null;
        break;
      default:
        console.log('default control' + action, opts);
        return;
        break;
    }
    if (message === null) {
      delete btn.dataset.message;
      btn.classList.add(css.hide);
    } else {
      btn.dataset.message = JSON.stringify(message);
      btn.classList.remove(css.hide);
      if (btn.disabled) {
        btn.classList.add(css.console);
       if(!btn.classList.contains(css.console)) btn.insertAdjacentHTML('afterbegin', html_spinner('text-stone-200 ml-1 mr-2 align-text-bottom inline-block'));
      } else btn.classList.remove(css.console);
    };

  }

  getBtn(item, target) {
    const btnkey = this.options.btnprefix + item + target;
    if (this[btnkey]) return this[btnkey];
    const display = this.options.controls[item].btn[target];
    const btn = document.getElementById(display);
    const parent = this.displayprogression;
    if (!btn) {
      this[btnkey] = create_box('button', {
        id: display,
        class: [display, css.hide].concat(css.button.split(' '))
      }, parent);
      this[btnkey].addEventListener('click', async (e) => {
        e.stopImmediatePropagation();
        e.preventDefault();
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