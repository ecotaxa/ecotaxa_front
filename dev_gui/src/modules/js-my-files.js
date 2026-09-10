
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
  objaccept,
} from '../modules/modules-config.js';
import {
  AlertBox
} from '../modules/alert-box.js';
import {
  JsDirList,
} from '../modules/files/js-dirlist.js';
import {
  ModuleEventEmitter
} from '../modules/module-event-emitter.js';
const accept = Object.values(objaccept).reduce((a, b) => a.concat(b));
css.button = 'button is-action self-start my-1';
css.inline = 'inline-block';
// collapsible progression boxes, in display order
const BOX_ORDER = ['zipped', 'rejected', 'errorfile'];
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
  zipped = [];
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
          label: 'upload',
          droptarget:true,
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
              this.updateExceptCounters();
              break;
            case this.eventnames.progress:
              self.showControl(key, e);
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
                  if (this.activentry) this.detachDropzone();
                   AlertBox.addAlert({
                    type: AlertBox.alertconfig.types.danger,
                    content: e.message,
                    dismissible: false,
                    inverse: false
                  });
                  break;
                case this.eventnames.errorfile:
                    if (e.path) this.errorfile.push(e.path);
                    this.updateExceptCounters();
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
                  AlertBox.addAlert({
                    type: AlertBox.alertconfig.types.info,
                    content: e.message,
                    dismissible: true,
                    inverse: true
                  });
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
  uploadBusy() {
    // an upload is actually being sent: no more files can join the archive
    if (this.done === false) {
      AlertBox.addAlert({
        type: AlertBox.alertconfig.types.info,
        content: 'Upload in progress — wait until it finishes before adding more files.',
        dismissible: true,
        inverse: false
      });
      return true;
    }
    return false;
  }
  async handleBrowse(e) {
    if (this.uploadBusy()) return;
    if (!this.setUploadEntry()) return;
    this.initTimer();
    this.toggleCounters(true);
    this.updateExceptCounters();
    if (!this.haspicker) e = e.target.files;
    const picks = (e instanceof FileList) ? [...e] : (Array.isArray(e) ? e : [e]);
    const seen = new Set();
    const named = [];
    picks.forEach((it) => {
      const rel = it.webkitRelativePath || '';
      const name = rel ? rel.split(dirseparator)[0] : it.name;
      if (!name || seen.has(name)) return;
      seen.add(name);
      named.push({
        name: name,
        isDir: (it.kind === 'directory') || rel.includes(dirseparator)
      });
    });
    this.addDroppedNames(named);
    await this.scanBrowse(e, {
      accept: accept,
    });
  }

  addDropzone() {
    this.dropzone = document.getElementById(this.options.display.dropzone);
    if (this.dropzone===null) this.dropzone = create_box('div', {
      id: this.options.display.dropzone
    },this.container);
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
    this.options.browse.forEach(opt => {
      const text = (this.container.dataset[`textbrowse${opt}`]) ? this.container.dataset[`textbrowse${opt}`] : `browse${opt}`;
      const btn = create_box('div', {
        class: [this.options.selectors.trigger.slice(1), css.inline],
        dataset: {
          type: opt
        },
        text: text
      }, this.dropzone);
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

    // progression / counters / upload button live right below the dropzone,
    // outside of it
    this.addDisplayProgression(this.dropzone.parentElement || this.container);
    this.dropzone.insertAdjacentElement('afterend', this.displayprogression);

    // the native directory picker only takes one folder at a time - a persistent
    // console-style note right under the dropzone points the user at drag & drop
    // for several
    const dirhint = create_box('div', {
      class: [css.console, 'flex', 'items-start', 'gap-1.5'],
      dataset: {
        role: 'dir-hint'
      }
    });
    create_box('i', {
      class: ['icon', 'icon-info', 'shrink-0']
    }, dirhint);
    create_box('span', {
      text: this.container.dataset.textbrowsedirectoryhint ||
        'To add several directories at once, drag & drop them onto the zone.'
    }, dirhint);
    this.dropzone.insertAdjacentElement('afterend', dirhint);

    this.droptarget=(this.options.upload.droptarget)?this.dropzone:null;
  }

  // entries still being zipped: light, shown inside the dropzone
  droppedNamesBox() {
    if (!this.droppedbox || !this.droppedbox.isConnected) {
      this.droppedbox = this.dropzone.querySelector('.dropzone-files')
        || create_box('div', {
          class: 'dropzone-files'
        }, this.dropzone);
    }
    return this.droppedbox;
  }
  addDroppedNames(items) {
    if (!items || !items.length) return;
    const box = this.droppedNamesBox();
    items.forEach(({
      name,
      isDir
    }) => {
      if (!name) return;
      const chip = create_box('span', {
        class: ['dropzone-file', 'zipping'],
        dataset: {
          type: isDir ? 'dir' : 'file'
        },
        title: name
      }, box);
      create_box('span', {
        class: 'dropzone-file-name',
        text: name
      }, chip);
    });
  }
  // the archive is done: record the entries that were being zipped and drop
  // their live chips from the dropzone (they are shown on demand from the
  // "compressed" counter instead)
  markDroppedZipped() {
    if (!this.droppedbox) return;
    const done = this.droppedbox.querySelectorAll('.dropzone-file.zipping');
    if (!done.length) return;
    done.forEach((el) => {
      this.zipped.push({
        name: el.getAttribute('title') || el.textContent.trim(),
        isDir: el.dataset.type === 'dir'
      });
      el.remove();
    });
    if (!this.droppedbox.querySelector('.dropzone-file')) {
      this.droppedbox.remove();
      this.droppedbox = null;
    }
    this.updateExceptCounters();
  }
  clearDroppedNames() {
    if (this.droppedbox) {
      this.droppedbox.remove();
      this.droppedbox = null;
    }
    this.zipped = [];
  }

  toggleDropTarget(on = true,) {
    const droptarget = (this.droptarget)?this.droptarget:((this.activentry) ? this.activentry.container : null);
    if (droptarget === null) return;
    const cssdragover = (this.jsDirList) ? (this.jsDirList.options.entry) ? this.jsDirList.options.entry.css.dragover : this.options.css.dragover : this.options.css.dragover;
    // build the handlers once so add/removeEventListener actually pair up -
    // toggleDropTarget is called again on every folder change and fresh
    // closures would just stack another drop listener each time
    if (!this._dropHandlers || this._dropHandlers.el !== droptarget) {
      const self = this;
      this._dropHandlers = {
        el: droptarget,
        highlight: () => droptarget.classList.add(cssdragover),
        unhighlight: () => droptarget.classList.remove(cssdragover),
        drop: async (e) => { await self.handleDrop(e); }
      };
    }
    const h = this._dropHandlers;
    const dropclass = this.options.selectors.droptarget.slice(1);
    // always detach first: listeners must never stack
    ['dragenter', 'dragover'].forEach(ev => droptarget.removeEventListener(ev, h.highlight, false));
    ['dragleave', 'drop'].forEach(ev => droptarget.removeEventListener(ev, h.unhighlight, false));
    droptarget.removeEventListener('drop', h.drop);
    if (on === false) {
      droptarget.classList.remove(dropclass);
      return;
    }
    ['dragenter', 'dragover'].forEach(ev => droptarget.addEventListener(ev, h.highlight, false));
    ['dragleave', 'drop'].forEach(ev => droptarget.addEventListener(ev, h.unhighlight, false));
    droptarget.addEventListener('drop', h.drop);
    droptarget.classList.add(dropclass);
  }

  async addDirList() {
    if (this.container!==null) this.jsDirList = new JsDirList(this.container);
    this.activentry = this.jsDirList.root;
    this.rootitem = this.targetitem = this.activentry.container;
    ModuleEventEmitter.on(this.jsDirList.eventnames.attach, (e) => {
      if (!e.entry) return;
      if (e.entry !== this.activentry && this.activentry.isBranch(true)) this.detachDropzone();
      this.activentry = e.entry;
      this.targetitem = this.activentry.container;
      if (this.activentry.isBranch(true)) this.enableUploadDialog();
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

  addDisplayProgression(parent=null) {
    // holds the collapsible progression boxes and the upload button
    if (this.displayprogression) return;
    let el = document.getElementById(this.options.display.progression);
    if (el===null) {
      parent=(parent===null)?this.container:parent;
      el = create_box('div', {
        id: this.options.display.progression
      }, parent);
    } else el.classList.remove(css.hide);
    this.displayprogression = el;
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
      this.toggleDropTarget(true);
    }
    // add the window-level preventDefault once (needed so drop events fire)
    if (!this._windowDragGuard) {
      this._windowDragGuard = (e) => e.preventDefault();
      ['dragover', 'dragenter'].forEach(eventname => {
        window.addEventListener(eventname, this._windowDragGuard, false);
      });
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
     ModuleEventEmitter.emit(this.jsDirToZip.eventnames.setuploadpath, {name:this.jsDirToZip.eventnames.setuploadpath, path:this.uploadentry.getCurrentDirPath()}, this.jsDirToZip.uuid);
    return true;
  }
  // drag&drop


  async handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    if (this.uploadBusy()) return;
    if (!this.setUploadEntry()) return;
    let dataTransfer;
    if (e.dataTransfer) {
      dataTransfer = e.dataTransfer;
    } else dataTransfer = e;
    this.initTimer();
    const items = [...((dataTransfer.items) ? dataTransfer.items : dataTransfer.files)];
    // webkitGetAsEntry() must be called synchronously here: the DataTransferItem
    // objects are cleared as soon as the drop handler returns, so resolve every
    // dropped entry now and hand them to a single scan pass.
    const entries = items
      .filter(item => item.kind === "file")
      .map(item => item.webkitGetAsEntry())
      .filter(Boolean);
    if (entries.length) {
      this.addDroppedNames(entries.map((en) => ({
        name: en.name,
        isDir: en.isDirectory === true
      })));
      this.toggleCounters(true);
      this.updateExceptCounters();
      await this.scanHandle(entries);
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

  enableUploadDialog() {
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
    if (!counters) return;
    counters.counter += 1;
    if (e.size != null) counters.size += (parseInt(e.size) || 0);
    // the read / compressed detail lives in the "processed" box (title + footer)
    this.syncListBox('zipped');
    this.quotaEstimate();
  }

  resetCounter(item) {
    const counters = this.counters[item];
    if (!counters) return;
    counters.counter = 0;
    counters.size = 0;
  }
  resetCounters() {
    Object.keys(this.options.controls).forEach(key => {
      this.resetCounter(key);
    });
    this.rejected = [];
    this.errorfile = [];
    const parent = this.displayprogression || this.container;
    if (parent) parent.querySelectorAll('.except-list').forEach((p) => p.remove());
    this.clearDroppedNames();
    this.updateExceptCounters();
    this.toggleCounters(false);
  }
  toggleCounters(show = true) {
    const el = document.getElementById(this.options.display.progression);
    if (!el) return;
    if (show) el.classList.remove(css.hide);
    else el.classList.add(css.hide);
  }

  // scan / zip / reject / errorfile keep running totals only
  initFileCounter(item) {
    this.counters = { ...this.counters,
      [item]: {
        counter: 0,
        size: 0,
        display: {}
      }
    };
  }

  // one collapsible box per concern; its always-visible title is the toggle
  initProgressionBoxes() {
    const box = this.displayprogression;
    if (!box || box.dataset.boxdelegated) return;
    box.dataset.boxdelegated = '1';
    box.addEventListener('click', (e) => {
      const title = e.target.closest('.except-list-title');
      if (!title || !box.contains(title)) return;
      const panel = title.closest('.except-list');
      if (panel) panel.classList.toggle('is-open');
    });
  }

  listBoxConf(type) {
    return {
      zipped: {
        suffix: 'processed',
        list: this.zipped,
        icons: true,
        foot: true,
        always: true
      },
      rejected: {
        suffix: 'rejected',
        list: this.rejected,
        icons: false,
        foot: false
      },
      errorfile: {
        suffix: 'in error',
        list: this.errorfile,
        icons: false,
        foot: false
      },
    }[type];
  }

  // rebuild every collapsible box from the current lists
  updateExceptCounters() {
    BOX_ORDER.forEach((type) => this.syncListBox(type));
  }

  // create / update / drop one box, keeping its open state
  syncListBox(type) {
    const parent = this.displayprogression;
    if (!parent) return;
    const conf = this.listBoxConf(type);
    if (!conf) return;
    const list = conf.list || [];
    let panel = parent.querySelector(`.except-list[data-except="${type}"]`);
    if (!conf.always && !list.length) {
      if (panel) panel.remove();
      return;
    }
    if (!panel) {
      panel = create_box('div', {
        // the processed box carries the live read / compressed counters in its
        // footer, so open it by default - the user can still collapse it
        class: conf.foot ? ['except-list', 'is-open'] : 'except-list',
        dataset: {
          except: type
        }
      });
      this.placeListBox(panel, type);
      create_box('p', {
        class: 'except-list-title'
      }, panel);
      const body = create_box('div', {
        class: 'except-list-body'
      }, panel);
      create_box('ul', {
        class: 'except-list-items'
      }, body);
      if (conf.foot) create_box('div', {
        class: 'except-list-foot'
      }, body);
    }
    panel.querySelector('.except-list-title').textContent =
      `${list.length} ${(list.length === 1) ? 'entry' : 'entries'} ${conf.suffix}`;
    const ul = panel.querySelector('.except-list-items');
    ul.textContent = '';
    if (!list.length) {
      create_box('li', {
        class: 'except-list-empty',
        text: '—'
      }, ul);
    } else {
      list.forEach((entry) => {
        if (conf.icons) {
          const li = create_box('li', {
            class: 'dropzone-file',
            dataset: {
              type: entry.isDir ? 'dir' : 'file'
            },
            title: entry.name
          }, ul);
          create_box('span', {
            class: 'dropzone-file-name',
            text: entry.name
          }, li);
        } else {
          create_box('li', {
            text: entry,
            title: entry
          }, ul);
        }
      });
    }
    if (conf.foot) this.updateProcessedFoot();
  }

  // keep the boxes in a stable order after the progression card
  placeListBox(panel, type) {
    const parent = this.displayprogression;
    const order = BOX_ORDER;
    const idx = order.indexOf(type);
    for (let i = idx + 1; i < order.length; i++) {
      const later = parent.querySelector(`.except-list[data-except="${order[i]}"]`);
      if (later) return void later.before(panel);
    }
    for (let i = idx - 1; i >= 0; i--) {
      const earlier = parent.querySelector(`.except-list[data-except="${order[i]}"]`);
      if (earlier) return void earlier.after(panel);
    }
    const card = parent.querySelector('.display-progression');
    if (card) card.after(panel);
    else parent.prepend(panel);
  }

  // "x read / x compressed" (count + size) footer of the processed box
  updateProcessedFoot() {
    const box = this.displayprogression;
    const foot = box && box.querySelector('.except-list[data-except="zipped"] .except-list-foot');
    if (!foot) return;
    const scan = this.counters.scan || {};
    const zip = this.counters.zip || {};
    foot.textContent = '';
    create_box('span', {
      text: `${scan.counter || 0} read / ${zip.counter || 0} compressed`
    }, foot);
    create_box('span', {
      text: `${format_bytes(scan.size || 0)} read / ${format_bytes(zip.size || 0)} compressed`
    }, foot);
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
          message = {};
          btn.disabled = true;
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
        if (!part) {
          this.showComplete();
          this.markDroppedZipped();
        }
        btn.textContent = this.container.dataset.ended || `Upload`;
        message = {
          name: this.eventnames.endzip,
          part: part,
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
        setTimeout( () => {this.emitToZip(btn);},1000);
        if(btn.previousElementSibling && btn.previousElementSibling.tagName.toLowerCase()!=="svg")  btn.insertAdjacentHTML('beforebegin', html_spinner('text-stone-200 ml-1 mr-2 align-text-bottom inline-block'));
        return;
        break;
      case this.eventnames.progress:
        if (parseFloat(opts.percentage) >= 100) {
          btn.textContent = ` Decompressing...`;
        } else {
          btn.textContent = ` Uploading ` + ((target !== 'zip') ? ' big file' : '') + ` ${opts.percentage}%`;
        }
        btn.disabled = true;
        message = {};
        break;
      case this.eventnames.pending:
        btn.textContent = ` Decompressing...`;
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
        if (btn.previousElementSibling && btn.previousElementSibling.tagName.toLowerCase()==="svg")  btn.previousElementSibling.remove();
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
      case this.eventnames.uploaderror:
        // upload failed but the compressed archive is still in browser storage:
        // keep the button live so the user can re-send it without rebuilding
        if (btn.previousElementSibling &&
          btn.previousElementSibling.tagName.toLowerCase() === "svg")
          btn.previousElementSibling.remove(); // drop the progress spinner
        btn.textContent = this.container.dataset.retry || `Retry upload`;
        btn.classList.remove(css.console);
        btn.disabled = false;
        message = {
          name: this.eventnames.sendfile,
          path: filepath,
          part: part,
          bigfile: bigfile,
        };
        break;
      case this.eventnames.errorfile:
      case this.eventnames.error:
        btn.textContent = opts.text || opts.message || `Error`;
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
       if(!btn.classList.contains(css.console) && btn.previousElementSibling && btn.previousElementSibling.tagName.toLowerCase()!=="svg") btn.insertAdjacentHTML('beforebegin', html_spinner('text-stone-200 ml-1 mr-2 align-text-bottom inline-block'));
      } else btn.classList.remove(css.console);
    }
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
    Object.entries(this.options.controls).forEach(([key, control]) => {
      this.initFileCounter(key);
      if (control.btn) this.activateControls(key, control.btn);
    });
    this.initProgressionBoxes();
  }
  activateControls(key, btns) {
    Object.keys(btns).forEach((btn) => {
      this[this.options.btnprefix + key + btn] = this.getBtn(key, btn);
    })

  }

}