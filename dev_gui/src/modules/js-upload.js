import DOMPurify from 'dompurify';
import {
  Zip,
  AsyncZipDeflate,
  ZipPassThrough,
  ZipDeflate,
} from 'fflate';
import {
  FormSubmit
} from '../modules/form-submit.js';

import {
  download_blob,
  fetchSettings,
} from '../modules/utils.js';
import {
  css
} from '../modules/modules-config.js';
const already_compressed = new Set([
  'zip', 'gz', 'png', 'jpg', 'jpeg', 'pdf', 'doc', 'docx', 'ppt', 'pptx',
  'xls', 'xlsx', 'heic', 'heif', '7z', 'bz2', 'rar', 'gif', 'webp', 'webm',
  'mp4', 'mov', 'mp3', 'aifc'
]);
const accept = '.tsv,.png,.jpg, .jpeg,.zip,.gz,.7z,.bz2';
const largefile = 50000;
const chunksize = 2000000;
let instance = null;
const defdir = "ecotaxa_import";

export class JsUpload {
  zipstream;
  zipsize = 0;
  pathname;
  zipname;
  numfiles = 0;
  sizefiles = 0;
  zipparts = [];
  counter = 0;
  counterdisplay = null;
  ziptrigger = null;
  displaylist = null;
  timer = 0;
  targetdir = '';
  sent = false;
  dropzone;
  root = '.';
  constructor(container, callback = null, options = {}) {
    if (instance) return instance;
    container = (container instanceof HTMLElement) ? container : document.querySelector(container);
    if (!container) return;
    this.container = container;
    this.callback = callback;
    const defaultOptions = {
      level: 0,
      //  url: "http://localhost:5001/gui/files/upload",
      url: "https://localhost:8000/my_files/",
      filefield: 'file',
      selector: {
        makezip: '.makezip',
        droptarget: '.droptarget',
        trigger: '.trigger',
        uploadfile: 'uploadfile',
        formu: 'formupload',
        stepper: 'stepper',
        stepitem: 'stepper-item',
        filetoload: 'file_to_load',
        progress: "progress-upload"
      },
      display: {
        dropzone: 'dropzone',
        counter: 'counter',
        size: 'sizetozip',
        counterzipped: 'counterzipped',
        sizezipped: 'sizezipped',
        dirlist: 'dirlist',
        boxtitle: 'boxtitle',
        timer: 'timer'
      },
      css: {
        enabled: 'enabled'
      }
    };

    this.options = Object.assign(defaultOptions, options);

    this.init(container);
    instance = this;
    return instance;
  }

  init(container) {
    // create a filepicker depends on browser
    this.dropzone = document.createElement('div');
    this.dropzone.id = this.options.display.dropzone;
    this.dropzone.innerHTML = `<input type="file" class="hidden"  name="${this.options.selector.uploadfile}" id="${this.options.selector.uploadfile}">
            <div class="${this.options.selector.droptarget.slice(1)}">
            <div id="${this.options.display.boxtitle}"><span class="${this.options.selector.trigger.slice(1)}">${this.container.dataset.textbrowse}</span>  ${this.container.dataset.textdrop}</div>
          </div><div><span id="${this.options.display.counter}"></span>/<span id="${this.options.display.counterzipped}"></span></div>
          <div><span id="${this.options.display.size}"></span>/<span id="${this.options.display.sizezipped}"></span></div><div id="${this.options.display.timer}"></div>
          <div id="${this.options.selector.makezip.slice(1)}" class="button ${this.options.selector.makezip.slice(1)} ${css.hide} "><div id="${this.options.selector.progress}"></div>${container.dataset.ended}</div>`;
    container.append(this.dropzone);
    this.counterdisplay = document.getElementById(this.options.display.counter);
    this.counterzippeddisplay = document.getElementById(this.options.display.counterzipped);
    this.sizedisplay = document.getElementById(this.options.display.size);
    this.sizezippeddisplay = document.getElementById(this.options.display.sizezipped);
    this.ziptrigger = container.querySelector(this.options.selector.makezip);
    this.displaylist = document.getElementById(this.options.display.dirlist);
    const droptarget = this.container.querySelector(this.options.selector.droptarget);
    droptarget.addEventListener('dragover', (e) => {
      this.handleDragOver(e);
    });
    droptarget.addEventListener('drop', async (e) => {
      this.handleDrop(e);

    });
    container.querySelector(this.options.selector.trigger).addEventListener('click', (e) => {
      let datatransfer = e;
      this.openDirDialog(accept, (e) => {
        console.log('edrop', datatransfer)
      });
    });
  }
  attachDropzone(target) {
    console.log('attch', target);
    this.targetdir = (target.parentElement.dataset.name) ? target.parentElement.dataset.name : '';
    console.log('targetdir', this.targetdir)
    this.dropzone.classList.add(this.options.css.enabled);
    console.log('att', this.dropzone);
    target.append(this.dropzone);
  }
  detachDropzone() {
    this.targetdir = null;
    this.container.classList.remove(this.options.css.enabled);

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

  async handleDrop(e) {
    let dataTransfer;
    if (e.dataTransfer) {
      e.preventDefault();
      dataTransfer = e.dataTransfer;
    } else dataTransfer = e;
    this.timer = new Date();
    console.log('dataTransfer ', dataTransfer.items)

    const items = [...((dataTransfer.items) ? dataTransfer.items : dataTransfer.files)];
    if (items.length) {
      this.enableDropzone(false);
      this.zipname = '_upload.zip';
      this.zip = new Zip();

      this.zipReadableStream = await this.fflToStream();
      const on_error = (err) => {
        console.log('err_read_dir', err);
      }
      const on_complete = async () => {
        this.timer = (new Date() - this.timer) / 1000;
        console.log('item-------------------------------------' + parseInt(this.timer / 60) + ' --- ' + (
          this.timer - (parseInt(this.timer / 60) * 60)), this.zip);
        this.enableDropzone();
        this.zip.end();
        this.ziptrigger.classList.remove(css.hide);
        this.ziptrigger.addEventListener('click', async (e) => {
          this.ziptrigger.disabled = true;
          console.log('upload click')
          this.enableDropzone(false, true);

          return await this.sendZip();
        });
      }
      //this.pathname.pop();
      for (let i = 0; i < items.length; i++) {
        let item = items[i].webkitGetAsEntry();
        if (item.isDirectory === true) {
          this.zipname = item.name + this.zipname;
          await this.readDirectory(item, this.root, on_complete);
        } else if (item.isFile === true) {
          // put directly in input file

        }

      }
    }
  }
  stopOnError(err) {
    console.log('err', err);
  }

  enableDropzone(enable = true, destroy = false) {
    if (destroy) this.dropzone.classList.add(css.hide);
    if (enable) this.dropzone.classList.add(this.options.css.enabled);
    else this.dropzone.classList.remove(this.options.css.enabled);

  }
  async supportsRequestStreams() {
    let duplexAccessed = false;
    const hasContentType = new Request(this.options.url, {
      body: new ReadableStream(),
      method: 'POST',
      get duplex() {
        duplexAccessed = true;
        return 'half';
      },
    }).headers.has('Content-Type');

    return duplexAccessed && !hasContentType;
  }

  fileType(data) {
    const mime_type = (signature) => {
      switch (signature) {
        case '89504E47':
          return 'image/png';
        case '47494638':
          return 'image/gif';
        case '25504446':
          return 'application/pdf';
        case 'FFD8FFDB':
        case 'FFD8FFE0':
        case 'FFD8FFE1':
          return 'image/jpeg';
        case '504B0304':
          return 'application/zip';
        case 'EFBBBF22':
          return 'text/tsv'; //'text/tab-separated-values';
        default:
          console.log('unknownsign', signature)
          return 'unknown';
      }
    }
    const uint = new Uint8Array(data);
    let bytes = []
    for (let i = 0; i < 4; i++) {
      bytes.push(uint[i].toString(16))
    }
    data = bytes.join('').toUpperCase();
    return {
      input: uint,
      mimetype: mime_type(data)
    };
  }

  async fflToStream() {
    const fflateStream = this.zip;
    const transform = new TransformStream();
    const writer = transform.writable.getWriter();
    return new TransformStream({
      start(controller) {
        fflateStream.ondata = (error, data, final) => {
          if (error) {
            console.log('error', error);
            return false;
          } else {
            controller.enqueue(data);
            if (final) {
              console.log('final', final);
              //  controller.terminate();
            }

          }
        }
      },
      flush(controller) {
        console.log('terminate ffstrem')
        controller.terminate();
      }
    })

  }
  //


  async readDirectory(dir, parent, oncomplete, onerror = null) {
    console.log('read', dir.name)
    const self = this;
    let errored = false;
    let direntries = [],
      handlers = [],
      files = [];

    const on_error = onerror ? onerror : (err) => {
      console.log('on_error', err)
      if (!errored) {
        errored = true;

      }
    };

    const readfile = async function(file, zippedstream) {
      const reader = file.stream().getReader();
      while (true) {
        const {
          done,
          value
        } = await reader.read();
        if (done) {
          await zippedstream.push(new Uint8Array(0), true);
          return done;
        }
        await zippedstream.push(value);
      }

    };

    //
    const process_file = async function() {
      const entry = files.shift();
      const filepath = entry.fullPath.slice(1);
      //  console.log('fileadd=' + self.numfiles, entry.name)
      const ext = filepath.slice(filepath.lastIndexOf('.') + 1);
      const zip_file = async (filetozip) => {
        const iscompressed = already_compressed.has(ext);
        const zippedstream = iscompressed ?
          new ZipPassThrough(filepath) :
          filetozip.size > largefile ?
          new AsyncZipDeflate(filepath, {
            level: 9
          }) : new ZipDeflate(filepath, {
            level: 6
          });
        //  console.log('zipstr', zippedstream)
        zippedstream.ondata = async function(err, dat, final) {
          if (err) console.log('err add chunk to zipfile' + dat, err);
          else if (final) {

            if (files.length) {
              console.log('files', files.length);
              await process_file();
            } else {
              console.log('lastfile', dir.name);
              await on_complete();
            }
          }
        };
        await self.zip.add(zippedstream);
        return await readfile(filetozip, zippedstream);
      };
      self.numfiles++;
      if (self.numfiles === 1) {
        fetch(self.options.url.replace('my_files', 'stream_my_files'), {
          mode: 'cors',
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/zip",
          },
          body: self.zipReadableStream.readable,
          duplex: 'half',
        }).then((response) => {
          console.log('response', response);
        });
      }
      await entry.file(zip_file);

    };
    //

    const process_entries = function() {
      const entry = direntries.shift();
      if (entry.isFile) {
        //console.log('fileleft ***---' + dir.name, entry.name);
        self.counter++;
        self.counterdisplay.textContent = self.counter;
        //const f = entry.getAsFile();
        files.push(entry);
        //  await process_file(entry, entry.fullPath.slice(1));
        self.counter--;
        self.counterdisplay.textContent = self.counter;
      } else if (entry.isDirectory) {
        console.log('entry is dir', entry)
        handlers.push(entry);
      }
      if (direntries.length) process_entries();

    }
    const on_complete = async function() {
      for (const handler of handlers) {
        console.log(handler);
        await self.readDirectory(handler, dir, async function() {
          console.log('idir', handler.name);
          if (files.length) await process_file();
        });
      }

    }
    const reader = dir.createReader();
    const on_read = async function(ents) {
      if (ents.length && !errored) {
        direntries = [...direntries, ...ents];
        await reader.readEntries(on_read, on_error);
      } else if (!errored) {
        process_entries();
        console.log('theend------------------- ' + dir.name, direntries.length)
        await on_complete();


      } else {
        console.log('treat error readdir');
      }
    }

    await reader.readEntries(on_read, on_error);

    console.log('enddir' + dir.name, direntries.length)

  }

  compressionLevel(name) {
    if (!name) {

      return -1;
    }
    let ext = name.split('.');
    ext = (ext.length > 1) ? ext[ext.length - 1] : ext[0];
    return (already_compressed.find(ex => (ex === ext))) ? 2 : this.options.level;
  }

  async sendZip() {
    //  const filestream = new WritableStream();
    //  const writer = filestream.getWriter();
    //

    //


    /*  fetch(this.options.url.replace('my_files', 'stream_my_files'), {
        mode: 'cors',
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "text/plain",
        },
        body: this.zipReadableStream,
        duplex: 'half',
      });*/
    /**********************************/
    /*webtransport
      const transport = new WebTransport(this.options.url);

      // Optionally, set up functions to respond to
      // the connection closing:
      transport.closed.then(() => {
        console.log(`The HTTP/3 connection to ${url} closed gracefully.`);
      }).catch((error) => {
        console.error(`The HTTP/3 connection to ${url} closed due to ${error}.`);
      });

      // Once .ready fulfills, the connection can be used.
      await transport.ready;
      const streamsend = await transport.createUnidirectionalStream();
      const writer = streamsend.writable.getWriter();
      const streamtest = new ReadableStream({
        async start(controller) {
          await wait(1000);
          controller.enqueue('This ');
          await wait(1000);
          controller.enqueue('is ');
          await wait(1000);
          controller.enqueue('a ');
          await wait(1000);
          controller.enqueue('slow ');
          await wait(1000);
          controller.enqueue('request.');
          controller.close();
        },
      }).pipeTo(writer);

    */




  }


}