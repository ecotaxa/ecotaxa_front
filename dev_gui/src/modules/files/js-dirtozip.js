'use strict';
import {
  add_custom_events,
  fetchSettings
} from '../../modules/utils.js';
import {
  Gzip,
  Zip,
  AsyncZipDeflate,
  ZipPassThrough,
  ZipDeflate,
} from 'fflate';
const already_compressed = new Set([
  'zip', 'gz', 'png', 'jpg', 'jpeg', 'pdf', 'doc', 'docx', 'ppt', 'pptx',
  'xls', 'xlsx', 'heic', 'heif', '7z', 'bz2', 'rar', 'gif', 'webp', 'webm',
  'mp4', 'mov', 'mp3', 'aifc'
]);
const accept = '.tsv,.png,.jpg, .jpeg,.zip,.gz,.7z,.bz2';
let instance = null;
const MAXSIZE = 1073741824; ////maxfilesize: 1073741824,
export class JsDirToZip {
  _events = {};
  eventnames = {
    ready: 'ready',
    endzip: 'endzip',
    complete: 'complete',
    gzip: 'gzipfile',
    sendfile: 'sendfile',
    bigfile: 'bigfile',
    terminate: 'terminate',
    pending: 'pending',
    getfile: 'getzipfile',
    counter: 'counter',
    message: 'message',
    error: 'error'
  }
  zip = null;
  zipname = null;
  filestream = null;
  streamhandle = null;
  gzipped = null;
  sizetozip = 0;
  part = 0;
  continue = null;
  constructor(options = {}) {
    if (instance) return instance;
    const defaultOptions = {
      uploadurl: '/gui/files/upload',
      largefile: 4194304,
      accept: accept.split(',')
    }
    this.options = { ...defaultOptions,
      ...options
    };
    console.log('thisopts', this.options)

    this.init();

    instance = this;
    return instance;
  }
  init() {
    add_custom_events(this);
    this.initStorage();
    this.on(this.eventnames.ready, () => {
      //this.initZip();
      console.log('ready')
    });
  }
  reset() {
    this.zip = null;
    this.zipname = null;
    this.filestream = null;
    this.streamhandle = null;
    this.gzipped = null;
    this.sizetozip = 0;
    this.part = 0;
    this.continue = null;
    this.initStorage();
  }
  initZip() {
    const self = this;
    this.pos = 0;
    this.sizetozip = 0;
    this.zip = new Zip(
      (error, chunk, final) => {
        if (error) {
          console.log('error', error);
          return false;
        } else {
          self.streamhandle.write(chunk, {
            at: self.pos
          });
          self.pos += chunk.length;
          if (final) {
            self.streamhandle.close();
            console.log('final-----------------------------*******************************-', this.part);

          }

        }
      });
    if (this.continue) this.continue();
    else {
      // events
      this.on(this.eventnames.endzip, (e) => {

        if (!e.bigfile && this.zip) {
          console.log('zipend', this.zip)
          this.zip.end();
        } else console.log('-------------------------gzipped end ')
        const message = {
          name: this.eventnames.sendfile
        };
        if (e.part) {
          message["part"] = e.part;
        } else this.part = 0;
        if (e.bigfile) message["bigfile"] = e.bigfile;
        console.log('endzip%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%', e)
        this.emit(this.eventnames.complete, message);
      });

      this.on(this.eventnames.sendfile, async (e) => {
        const file = await this.getFile();
        console.log('sendfile', file)
        /*  if (e.bigfile) this.sendChunk((e.path ? e.path : ''));
          else */
        this.sendZipFile(file, (e.path ? e.path : ''), (e.bigfile ? e.bigfile : false));
      });
      this.on(this.eventnames.bigfile, (e) => {
        this.sendChunk((e.path ? e.path : ''));
      });
    }
  }
  async initStorage() {
    if (navigator && navigator.storage && navigator.storage.estimate) {
      await this.cleanStorage();
      this.emit(this.eventnames.ready);
      navigator.storage.estimate().then((quota) => {
        const percentageUsed = (quota.usage / quota.quota) * 100;
        const remaining = quota.quota - quota.usage;
        this.emit(this.eventnames.message, {
          name: "console",
          message: "You can write up to " + remaining + " more bytes."
        });
        this.emit(this.eventnames.message, {
          name: "console",
          message: "you've used " + percentageUsed + "% of the available storage."
        });
      });
    } else this.emit(this.eventnames.message, {
      name: "error",
      message: "no navigator storage"
    });
  }
  async createLocalStream(name, accept = {
    'application/zip': ['.zip'],
  }) {
    const root = await navigator.storage.getDirectory();
    const opts = {
      types: [{
        description: 'Temp file',
        accept: accept,
      }, ],
      create: true
    };
    const filestream = await root.getFileHandle(name, opts);
    const streamhandle = await filestream.createWritable();
    return {
      filestream,
      streamhandle
    };
  }

  async scanHandle(dir, options = {}) {
    console.log('this.zip', this.zip)
    if (this.zip === null) {
      const type = (options && options.type) ? options.type : '.zip';
      this.zipname = ((options.zipname) ? options.zipname : dir.name) + type;
      //

      const {
        filestream,
        streamhandle
      } = await this.createLocalStream(this.zipname);
      console.log('streamhandle', streamhandle)
      this.filestream = filestream;
      this.streamhandle = streamhandle;
      let size = 0;
      this.part = 0;
      this.initZip();
      console
      const zip = this.zip;
      if (!this.jsScanDir) {
        const {
          JsScanDir
        } = await import('../files/js-scandir.js');
        this.jsScanDir = new JsScanDir();
      }
      this.jsScanDir.processFile = (entry, callback) => {
        this.processFile(entry, callback);
      };
      await this.jsScanDir.readDirectory(dir, () => {
        this.emit(this.eventnames.complete, {
          name: this.eventnames.endzip
        });

      });
    }
  }
  async sendBigFile(file, callback) {
    const filepath = file.webkitRelativePath;
    console.log('bigfilepath', filepath)
    const ext = file.name.slice(file.name.lastIndexOf('.') + 1);
    if (already_compressed.has(ext)) {
      this.gzipped = file;
      this.emit(this.eventnames.counter, {
        name: 'zip',
        filepath: filepath,
        size: file.size
      });
      this.emit(this.eventnames.complete, {
        name: this.eventnames.bigfile,
        bigfile: filepath
      });
    } else {
      this.emit(this.eventnames.gzip, {
        bigfile: filepath,
        size: file.size
      });
      let zipname = file.name.split(ext);
      zipname.pop();
      zipname = zipname.join(ext) + 'gz';
      console.log('bigfile ext=' + ext, zipname)
      const {
        filestream,
        streamhandle
      } = await this.createLocalStream(zipname, {
        'application/gzip': ['.gz'],
      });
      let pos = 0;
      const selfi = this;
      const gzipped = new Gzip({
        level: 9,
        filename: file.name
      });
      gzipped.ondata = (data, final) => {
        if (final) {
          console.log('final' + selfi.eventnames.bigfile, filepath)
          selfi.emit(selfi.eventnames.counter, {
            name: 'zip',
            filepath: filepath,
            size: file.size
          });
          selfi.gzipped = filestream;
          console.log('big file *******************', this.gzipped);
          selfi.emit(selfi.eventnames.complete, {
            name: selfi.eventnames.bigfile,
            bigfile: filepath
          });

          console.log('callbackbig', callback)
          //  gzipped.terminate();
          //  streamhandle.close();


        } else {
          streamhandle.write(data, {
            at: pos
          });
          pos += data.length;
        }
      };
      await this.readFile(file, filepath, gzipped, callback);
    }


  }
  async partZip() {
    this.part += 1;
    this.emit(this.eventnames.complete, {
      name: this.eventnames.endzip,
      part: this.part
    });
  }
  async readFile(file, filepath, zippedstream, callback = null) {
    const reader = file.stream().getReader();
    while (true) {
      const {
        done,
        value
      } = await reader.read();
      if (done) {
        zippedstream.push(new Uint8Array(0), true);
        this.emit(this.eventnames.counter, {
          name: 'zip',
          filepath: filepath,
          size: (zippedstream.size) ? zippedstream.size : file.size
        });
        if (zippedstream.terminate) zippedstream.terminate();
        if (callback) callback();
        return done;
      }
      zippedstream.push(value);
    }
  }
  async zipStream(file, filepath, callback) {
    const ext = filepath.slice(filepath.lastIndexOf('.') + 1);
    const iscompressed = already_compressed.has(ext);
    const zippedstream = (iscompressed) ? new ZipPassThrough(filepath) : file.size > this.options.largefile ?
      new AsyncZipDeflate(filepath, {
        level: 9
      }) : new ZipDeflate(filepath, {
        level: 6
      });
    this.zip.add(zippedstream);
    await this.readFile(file, filepath, zippedstream, callback);
  }
  async processFile(entry, callback = null) {
    const self = this;
    const filepath = entry.fullPath;
    const ext = filepath.slice(filepath.lastIndexOf('.') + 1);
    if (this.options.accept.includes(ext)) {
      console.log('reject', filepath);
      return;
    }
    if (entry.isDirectory) {
      //  console.log('zipdir', callback)
      if (callback) callback();
    } else {
      entry.file(async file => {
        this.emit(this.eventnames.counter, {
          name: 'scan',
          filepath: filepath,
          size: file.size
        });
        this.continue = null;
        // check file size > max post size
        if (file.size >= MAXSIZE) {
          this.sendBigFile(file, callback);
        } else {
          // check zip file size > total zip size
          this.sizetozip += file.size;
          if (this.sizetozip >= MAXSIZE) {
            this.continue = async () => {
              await this.zipStream(file, filepath, callback);
            }
            this.partZip();
          } else {
            await this.zipStream(file, filepath, callback);
          }
        }
      });

    }
  }
  onError() {
    this.cleanStorage();
    this.emit(this.eventnames.error, {
      name: "reload"
    });
  }
  async cleanStorage(entry = null) {
    entry = (entry) ? entry : await navigator.storage.getDirectory();
    for await (const [key, value] of entry.entries()) {
      console.log({
        key,
        value
      });
      await entry.removeEntry(key);
    }

  }

  async endFetch() {
    const message = {
      name: this.eventnames.terminate,

    }


    if (this.gzipped) {

      message["bigfile"] = this.gzipped.name;
      this.gzipped = null;
    } else if (this.continue) {
      this.streamhandle = await this.filestream.createWritable();
      this.initZip();
    } else await this.cleanStorage();
    this.emit(this.eventnames.complete, message);
  }
  async sendChunk(path, start = 0, chunknum = 0, chunksize = MAXSIZE) {
    const file = (this.gzipped.kind) ? await this.gzipped.getFile(): file;
    path = path.split('/');
    path.pop();
    path = path.join('/');
    const end = Math.min(start + chunksize, file.size);
    if (end === file.size) {

      this.sendZipFile(file, path, null, true);
    } else {
      const partfile = file.slice(start, end);
      partfile.name = chunknum + '_' + file.name;
      this.sendZipfile(partfile, path, () => {
        start += end;
        chunknum++;

        if (start <= file.size) this.sendChunk(path, start, chunknum, chunksize);
      }, true)
    }
    return chunknum;
  }
  async getFile() {
    const file = await this.filestream.getFile();
    return file;
  }
  async sendZipFile(file, path, callbackchunk = false, isbigfile = false) {
    const message = (isbigfile) ? {
      bigfile: file.name
    } : null;
    this.emit(this.eventnames.pending, message);
    console.log('file', file)
    const formdata = new FormData();
    formdata.append('tag', 'ecotaxa_import');
    formdata.append('path', path + file.name);
    formdata.append('file', file, file.name);
    if (this.part) formdata.append('part', this.part);
    else if (callbackchunk) formdata.append('ischunk', true);
    fetch(this.options.uploadurl, {
      //  mode: 'cors',
      method: "POST",
      credentials: "include",
      body: formdata,
    }).then(async (response) => {
      console.log('response----------------------', response);
      if (callbackchunk) {
        callbackchunk();
      } else this.endFetch();
    });
  }
}