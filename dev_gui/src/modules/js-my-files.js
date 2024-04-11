import {
  dom_purify,
  fetchSettings,
  add_custom_events,
  create_box,
  format_bytes
} from '../modules/utils.js';
import {
  css,
  filter_files
} from '../modules/modules-config.js';
import {
  generate_uuid,
} from '../modules/utils.js';
const accept = '.tsv,.png,.jpg, .jpeg,.zip,.gz,.7z,.bz2';
const localcss = {
  mright: 'mr-4',
}
const dirseparator = "/";
export class JsMyFiles {
  done = true;
  jsDirToZip = null;
  counters = {};
  _events = {};
  eventnames = {
    complete: 'complete',
    error: 'error',
  }
  constructor(container, options = {}) {
    if (!container.jsmyfiles) {
      container = (container instanceof HTMLElement) ? container : document.querySelector(container);
      if (!container) return;
      dom_purify(container, 'dataset');
      this.container = container;
      console.log("/gui/files/list")
      const defaultOptions = {

        url: "/gui/files/list",
        compress: {
          label: 'compress'
        },
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

        },
        upload: {
          label: 'upload'
        },
        btnprefix: 'btn',
        btnfilelist: null,
        selector: {
          doupload: '.target-upload',
          droptarget: '.droptarget',
          trigger: '.trigger',
          entries: '.entries',
          dirlist: '.dirlist',
          uploadfile: 'uploadfile',
          displayresult: 'results',
        },
        entrycontrols: {
          selector: '.entrycontrols',
          url: 'gui/me/my_files/',
          controls: [{
              action: 'newfolder',
              text: 'new folder',
              icon: 'icon-folder-plus-sm',
              typentry: 'entryD'
            }, {
              action: 'rename',
              text: 'rename',
              icon: 'icon-pencil-sm'
            },
            {
              action: 'delete',
              text: 'delete',
              icon: 'icon-trash-sm'
            },
          ]
        },
        display: {
          progression: 'display-progression',
          dropzone: 'dropzone',
          boxtitle: 'boxtitle',
          counters: 'counters',
          sizes: 'sizes',
          timers: 'timers'
        },

      };
      this.options = Object.assign(defaultOptions, options);
      this.init();
      container.jsmyfiles = this;
    }
    return container.jsmyfiles;
  }
  init() {
    // create dirlist box
    this.addDropzone();
    this.addDisplayProgression();
    this.addDirList();
    this.initEvents();
  }
  initTimer() {
    this.timer = new Date();
  }
  initEvents() {
    add_custom_events(this);

    //To be refactored - for steppers )
    this.on(this.eventnames.processed, async (e) => {
      if (this.nextaction) await this.nextaction();
    })
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
    })
    window.addEventListener('beforeunload', (e) => {
      if (!this.done) {
        e.preventDefault();
        e.returnValue = (this.options.preventclose) ? this.options.preventclose : `Some work is in progress in this window.\nAre you sure you want to leave?`;
      }


    });
  }
  addDropzone() { //
    this.dropzone = document.createElement('div');
    this.dropzone.id = this.options.display.dropzone;
    this.dropzone.innerHTML = `<input type="file" class="hidden"  name="${this.options.selector.uploadfile}" id="${this.options.selector.uploadfile}">
            <div class="${this.options.selector.droptarget.substr(1)}">
            <div class="${this.options.display.boxtitle}"><span class="${this.options.selector.trigger.slice(1)}">${this.container.dataset.textbrowse}</span>  ${this.container.dataset.textdrop}</div>
          </div>`;
    this.container.append(this.dropzone);
    this.setDropTarget(this.dropzone.querySelector(this.options.selector.droptarget));
    this.container.querySelector(this.options.selector.trigger).addEventListener('click', async (e) => {
      this.handleBrowse();
    });
  }
  setDropTarget(droptarget) {
    const dropclass = this.options.selector.droptarget.substr(1);
    const target_dragover = (e) => {
      this.handleDragOver(e);
    }
    const target_drop = async (e) => {
      this.handleDrop(e);
    }
    // set events and css for new dropzone
    if (!this.droptarget || this.droptarget != droptarget) {
      if (this.droptarget) {
        this.droptarget.removeEventListener('dragover', target_dragover);
        this.droptarget.removeEventListener('drop', target_drop);
        this.droptarget.classList.remove(dropclass);
      }
      this.droptarget = droptarget;
      this.droptarget.addEventListener('dragover', target_dragover);
      this.droptarget.addEventListener('drop', target_drop);
      this.droptarget.classList.add(dropclass);
    }
  }
  async addDirList(source = null) {
    let el = this.container.querySelector(this.options.selector.dirlist);
    console.log('el dirlist', el)
    if (!el) {
      el = document.createElement('div');
      el.classList.add(this.options.selector.dirlist.substr(1));
      this.container.append(el);
      this.displaylist = el;
    }
    this.serverList();
  }
  addDisplayProgression() {
    // add counters
    if (this.displayprogression) return;
    let el = document.getElementById(this.options.display.progression);
    if (!el) {
      console.log('counterscreate')
      el = document.createElement('div');
      el.id = this.options.display.progression;
      el.innerHTML = `<div class="flex sm:flex-row"><div class="${this.options.display.counters}"></div><div class="${this.options.display.sizes}"></div><div class="${css.progress}"></div><div class="${this.options.display.timers}"></div></div>`;
      this.container.prepend(el);
      this.displayprogression = el;
    }
  }
  serverList(parent = null, subdir = null, tag = null) {
    parent = parent ? parent : this.container.querySelector(this.options.selector.dirlist);
    if (!parent) return;
    // remove, move
    const entry_controls = () => {
      let box = this.container.querySelector(this.options.entrycontrols.selector);
      if (box === null) {
        box = document.createElement('div');
        box.classList.add(this.options.entrycontrols.selector.substr(1));
        this.options.entrycontrols.controls.forEach(control => {
          const el = document.createElement('span');
          if (control.typentry) el.dataset.typentry = control.typentry;
          if (control.icon) {
            el.insertAdjacentHTML('afterbegin', `<i class="icon ${control.icon}"></i>`);
            el.dataset.title = control.text;
          } else el.textContent = control.text;
          box.append(el);
          el.addEventListener('click', async (e) => {
            if (el.parentElement.classList.contains('entryD') || el.parentElement.classList.contains('entryD')) {
              const name = (el.parentElement.dataset.name) ? new URLSearchParams({
                entry: el.parentElement.dataset.name
              }) : null;
              if (name === null) return false;
              const response = await fetch(this.options.entrycontrols.url + control.action + name, fetchSettings());
              const json = await response.json();
              if (json.success) {
                switch (json.action) {
                  case 'rename':
                    el.parentElement.textContent = json.name;
                    break;
                  case 'delete':
                    el.parentElement.remove();
                    break;
                }
                return true;
              } else {
                console.log('err', json)

              }
            }
            return false;
          });
        });
        box.classList.add(css.hide);
        this.container.append(box);
      }
      return box;
    }
    const entrycontrols = entry_controls();
    const attach_controls = (el, typentry = null) => {
      if (!el.dataset.name) return false;
      console.log('entrycontrols parent', entrycontrols.parentElement)
      entrycontrols.parentElement.classList.remove('has-controls');
      el.insertBefore(entrycontrols, el.firstElementChild);
      entrycontrols.querySelectorAll('[data-typentry]').forEach(ctrl => {
        if (!ctrl.dataset.typentry || typentry === ctrl.dataset.typentry) ctrl.classList.remove(css.hide);
        else ctrl.classList.add(css.hide);
      });
      el.classList.add('has-controls');
      entrycontrols.classList.remove(css.hide);

    }
    parent.classList.add('wait');
    const el = parent.querySelector(this.options.selector.entries);
    if (el) el.remove();
    tag = (tag) ? ((tag === 'select') ? 'optiongroup' : tag) : 'ul';
    const subtag = (tag === 'ul') ? 'li' : 'option';
    fetch(this.options.url + ((subdir) ? subdir : ''), fetchSettings()).then(response => response.json()).then(async json => {
      if (json.entries && json.entries.length) {
        if (parent.dataset.label) parent.insertAdjacentHTML('afterbegin', `<label>${parent.dataset.label}</label>`);
        let html = [`<${tag} class="${this.options.selector.entries.slice(1)}">`],
          files = [],
          directories = [],
          entries = json.entries;
        while (entries.length > 0) {
          const entry = entries.shift();
          if (entry.type === 'F') files.push(entry);
          else directories.push(entry);
        };
        files.sort((a, b) => (a.name < b.name));
        directories.sort((a, b) => (a.name < b.name));
        [directories, files].forEach(entries => {
          entries.forEach((entry) => {
            const ext = entry.name.split('.').pop();
            const entrydetail = `<span class="entry${entry.type}"><i class="icon p-[0.125rem] icon-${((entry.type === "D") ? 'folder-sm' : ((filter_files.images.split(',').indexOf(ext)>=0)?'image-sm':'document-sm'))} align-text-bottom mb-0.5 mr-0.5"></i>${entry.name}</span>`;
            html.push(`<${subtag} ${(entry.type==='D')?`draggable="true"`:``} data-name="${entry.name}" ${(tag==='select')?` class="entry${entry.type}"`:``}>${entrydetail}`);
            html.push(`</${subtag}>`);
          });
        });
        html.push(`</${tag}>`);
        parent.insertAdjacentHTML('beforeend', html.join(``));
        parent.querySelectorAll('.entryF').forEach(file => {
          file.addEventListener('click', (e) => {
            e.stopImmediatePropagation();
            attach_controls(file.parentElement);
            this.detachDropzone();
          });
        });
        parent.querySelectorAll('.entryD').forEach(dir => {
          dir.addEventListener('click', (e) => {
            e.stopImmediatePropagation();
            const dirlist = dir.parentElement;
            dirlist.classList.toggle('on');
            const ico = e.currentTarget.querySelector('i.icon');
            if (ico) {
              ico.classList.toggle('icon-folder-sm');
              ico.classList.toggle('icon-folder-open-sm');
            }
            if (dirlist.classList.contains('on')) {
              console.log('is on', dirlist)
              if (!dirlist.dataset.load) {
                this.serverList(dirlist, ((subdir) ? subdir + '/' : '/') + dirlist.dataset.name, tag);

              }
            }
          });

        });

      }
      await this.addUploadDialog((subdir === null) ? this.container : parent);
      parent.classList.remove('wait');
      parent.dataset.loaded = true;
      parent.classList.add('on');
      if (subdir) {
        console.log('subdir attach', parent);
        attach_controls(parent, 'entryD');
        this.setDropTarget(parent);
      }
    });

  }

  attachDropzone(target) {
    if (this.dropzone.dataset.enabled) {
      this.targetdir = target;
      target.append(this.dropzone);
    }
  }
  detachDropzone() {
    if (this.dropzone.dataset.enabled) {
      this.targetdir = null;
      this.container.append(this.dropzone);
    }
  }

  openDirDialog(accept, callback) {
    const input = document.createElement("input");
    input.type = "file";
    input.directory = true;
    input.multiple = true;
    input.webkitdirectory = true;
    input.allowdirs = true;
    input.accept = accept;
    input.addEventListener("change", callback);
    input.dispatchEvent(new MouseEvent("click"));
  }
  handleDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
  }
  // browse
  async handleBrowse() {
    this.initTimer();
    this.openDirDialog(accept, async (e) => {
      const files = e.target.files;
      this.toggleCounters(true);
      await this.jsDirToZip.scanFiles(files);
    });
  }
  // or drag&drop
  async handleDrop(e) {
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
          await this.readEntry(item);
        }
      })
    }
  }
  showComplete() {
    this.timer = (new Date() - this.timer) / 1000;
    console.log('item-------------------------------------' + parseInt(this.timer / 60) + ' --- ' + (
      this.timer - (parseInt(this.timer / 60) * 60)));
    this.enableDropzone();
  }

  stopOnError(err) {
    console.log('err', err);
  }

  enableDropzone(enable = true, destroy = false) {
    if (destroy) this.dropzone.classList.add(css.hide);
    if (enable) this.dropzone.dataset.enabled = true;
    else delete this.dropzone.dataset.enabled;

  }

  addConsoleMessage(message) {
    //message {message:, parent:}
    const tag = 'p';
    let el = message.parent.querySelector('.' + css.console);
    if (el === null) {
      el = document.createElement('div');
      el.classList.add(css.console);
      message.parent.prepend(el);
    }
    if (message.id) {
      const msg = el.querySelector(`${tag}[data-id="${message.id}"]`);
      if (msg) msg.innerHTML = message.content;
      else el.insertAdjacentHTML('beforeend', `<${tag} data-id="${message.id}">${message.content}</${tag}>`);
    } else el.insertAdjacentHTML('beforeend', `<${tag}>${message.content}</${tag}>`);

  }

  async addUploadDialog(item) {
    item = (item) ? item : this.container;
    if (this.options.controls.scan) {
      this.enableDropzone(true);
      this.attachDropzone(item);
      if (this.options.controls.zip) {
        const {
          JsDirToZip
        } = await import('../modules/files/js-dirtozip.js');
        this.jsDirToZip = new JsDirToZip();
        this.jsDirToZip.on(this.jsDirToZip.eventnames.ready, (e) => {
          console.log('ready')
          this.initControls();
        });
        this.jsDirToZip.on(this.jsDirToZip.eventnames.message, async (e) => {
          switch (e.name) {
            case 'console':
              this.addConsoleMessage({
                id: (e.id) ? e.id : null,
                content: e.message,
                parent: (e.parent) ? item : this.container
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
        })


        const self = this;
        this.jsDirToZip.on(this.jsDirToZip.eventnames.ready, (e) => {
          self.showControl(this.jsDirToZip.eventnames.ready);
        });
        this.jsDirToZip.on(this.jsDirToZip.eventnames.counter, (e) => {
          self.fileCounter(e.name, e.filepath, e.size);
        });
        this.jsDirToZip.on(this.jsDirToZip.eventnames.complete, (e) => {
          if (!e || !e.name) {
            console.log('no emit complete name');
            return;
          }
          self.showControl(e.name, ((e.hasOwnProperty('bigfile') && e.bigfile) ? 'zipped' : 'zip'), (e.hasOwnProperty('part')) ? e.part : ((e.hasOwnProperty('bigfile')) ? e.bigfile : null));
        });
        this.jsDirToZip.on(this.jsDirToZip.eventnames.pending, (e) => {
          self.showControl(this.jsDirToZip.eventnames.pending, ((e && e.hasOwnProperty('bigfile') && e.bigfile) ? 'zipped' : 'zip'));
        });
        this.jsDirToZip.on(this.jsDirToZip.eventnames.gzip, (e) => {
          console.log('gzipped', e)
          self.showControl(this.jsDirToZip.eventnames.gzip, 'zipped', e);
        });
        this.jsDirToZip.on(this.jsDirToZip.eventnames.terminate, (e) => {
          console.log('terminate', e)
          self.showControl(this.jsDirToZip.eventnames.terminate, ((e && e.hasOwnProperty('bigfile') && e.bigfile) ? 'zipped' : 'zip'));
        });
      }

    }

  }
  async readEntry(entry) {
    await this.jsDirToZip.scanHandle(entry);
  }
  getCurrentDirPath() {
    if (this.targetdir === null) return '';
    const current_path = (el, dirs = []) => {

      if (el != null) {
        dirs.push(el.dataset.name);
        el = el.closest('.entryD');
        if (el !== null) {
          el = el.parentElement;
          if (el !== null && el.dataset.name) current_path(el, dirs);
        }
      }
      return dirs;
    }
    const dirs = current_path(this.targetdir);
    return dirs.join(dirseparator);
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

  fileCounter(item, filepath, size = null) {
    const counters = this.counters[item];
    counters.counter++;
    if (size !== null) counters.size += parseInt(size);
    counters.display.counter.textContent = counters.counter;
    if (counters.display.size) counters.display.size.textContent = format_bytes(counters.size);
    this.jsDirToZip.quotaEstimate();
  }

  resetCounter(item) {
    const counters = this.counters[item];
    ['counter', 'size'].forEach(el => {
      counters.display[el].textContent = 0;
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
        sizezipped: ' compressed'
      }
      let elinsert = boxcounters.querySelector('.' + cl);
      if (!elinsert) elinsert = create_box('div', {
        class: cl
      }, boxcounters, ``);
      let el = elinsert.querySelector('.' + val);
      if (!el) {
        el = create_box('span', {
          class: val,
        }, elinsert);
        if (txt.hasOwnProperty(val)) elinsert.append(document.createTextNode(txt[val]));
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

  showControl(action, target = 'zip', opts = null) {
    let message, text = null;
    // 'zip' ---only btn for zip actions for the moment
    const btn = this[this.options.btnprefix + 'zip' + target];
    if (!btn) return;
    btn.removeAttribute("disabled");
    switch (action) {
      case this.jsDirToZip.eventnames.ready:
        if (btn.dataset.message) delete btn.dataset.message;
        btn.classList.add(css.hide);
        this.initControls();
        break;
      case this.jsDirToZip.eventnames.endzip:
        const part = opts;
        if (!part) this.showComplete();
        btn.textContent = `Close zip file` + ((part) ? part : ``);
        btn.title = (part) ? `Your file is too big - you have to send this part before continuing to process the directory` : `Click to end zip file`;
        message = {
          name: this.jsDirToZip.eventnames.endzip,
          part: part,
          bigfile: (target !== 'zip'),
        };
        if (part) message["part"] = part;
        btn.dataset.message = JSON.stringify(message);
        break;
      case this.jsDirToZip.eventnames.bigfile:
        btn.textContent = `Upload big File separately`;
        message = {
          name: this.jsDirToZip.eventnames.bigfile,
          path: this.getCurrentDirPath(),
          bigfile: true
        };

        const filepath = opts;
        if (filepath) message["path"] = filepath;
        btn.dataset.message = JSON.stringify(message);
        console.log('bigfile', message)
        break;
      case this.jsDirToZip.eventnames.sendfile:
        message = {
          name: this.jsDirToZip.eventnames.sendfile,
          path: this.getCurrentDirPath(),
          bigfile: opts,
        };
        btn.textContent = `Upload zip file`;
        if (message.bigfile !== null) btn.textContent += ` ` + opts;
        btn.dataset.message = JSON.stringify(message);
        console.log('messageup', message)
        break;
      case this.jsDirToZip.eventnames.pending:
        btn.textContent = ` Pending ` + ((target !== 'zip') ? ' big file' : '');
        btn.dataset.message = '';
        btn.setAttribute("disabled", true);
        break;
      case this.jsDirToZip.eventnames.gzip:
        text = `compressing separately big file :${(opts && opts.bigfile)?opts.bigfile:``} ${(opts && opts.size)?opts.size:``}`;
        btn.textContent = text;
        btn.setAttribute("disabled", true);
        console.log('optsbigfl', opts)
        btn.dataset.message = JSON.stringify({
          name: this.jsDirToZip.eventnames.endzip,
          path: (opts.hasOwnProperty("bigfile")) ? opts.bigfile : e.path,
          bigfile: (opts.hasOwnProperty("bigfile") && opts.bigfile !== ""),
        });
        break;
      case this.jsDirToZip.eventnames.terminate:
        console.log('terminate ' + ((target !== 'zip') ? 'bigfile' : ''));
        this.serverList(this.targetdir);
        //default:
        btn.dataset.message = JSON.stringify({
          name: 'ready',
          bigfile: (target !== 'zip')
        });
        btn.textContent = `End!! ${ ((target !== 'zip') ? 'bigfile' : '')}`;

        break;
    }
    if (btn.dataset.message) btn.classList.remove(css.hide);
  }
  emitToZip(btn) {
    const message = (btn.dataset.message) ? JSON.parse(btn.dataset.message) : null;
    if (!message) btn.classList.add(css.hide);
    if (message) {
      if (message.name) {
        const name = message.name;
        delete message.name;
        console.log('emit ----' + name, message)
        this.jsDirToZip.emit(name, message);
      }
    }
    if (name === this.jsDirToZip.eventnames.sendfile) btn.disabled = true;
  }
  getBtn(item, target) {
    const btnkey = this.options.btnprefix + item + target;
    if (this[btnkey]) return this[btnkey];
    const display = this.options.controls[item].btn[target];
    const btn = document.getElementById(display);
    const parent = (this.targetdir) ? this.targetdir : this.displayprogression;
    if (!btn) {
      parent.insertAdjacentHTML('beforeend', `<button id="${display}" class="button ${display} ${localcss.mright} ${css.hide}"></button>`);
      this[btnkey] = document.getElementById(display);
      this[btnkey].addEventListener('click', async (e) => {
        e.stopImmediatePropagation();
        this.emitToZip(e.currentTarget);
      });
    } else parent.append(btn);
    return this[btnkey];
  }

  initControls(item = null) {
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