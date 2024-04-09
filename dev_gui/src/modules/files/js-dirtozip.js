'use strict';
import {
  add_custom_events,
  fetchSettings,
  format_bytes
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
    endreaddir: 'endreaddir',
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
  counter = {
    scan: 0,
    zip: 0
  }
  // uses https://developer.mozilla.org/en-US/docs/Web/API/File_System_API/Origin_private_file_system
  //# alternative (not supported in Safari) for .createWritable
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
      console.log('ready')
    });
  }
  reset() {
    console.log('reset');
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
  async initZip() {
    console.log('initzip')
    const self = this;
    this.pos = 0;
    this.sizetozip = 0;

    this.zip = new Zip((error, chunk, final) => {
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
          console.log('final-----------------------------*******************************-', self.pos);

        }

      }
    });
    /*  const fflToRS = fflateStream =>
        new ReadableStream({
          start(controller) {
            // Push to the ReadableStream whenever the fflate
            // stream gets data
            fflateStream.ondata = (err, data, final) => {
              if (err) controller.error(err);
              else {
                controller.enqueue(data);
                // End the stream on the final chunk
                if (final) {
                  controller.close();
                  console.log('final-----------------------------******************************-');
                }
              }
            }
          },
          cancel() {
            // We can stop working if the stream is cancelled
            // This may happen if the user cancels the download
            fflateStream.terminate();
          }
        });
      const zipstream = fflToRS(this.zip);
      zipstream.pipeTo(self.streamhandle);*/
    if (this.continue) await this.continue();
    else {
      // events
      this.on(this.eventnames.endzip, (e) => {
        if (!e.bigfile && this.zip) {

          this.zip.end();
          console.log('zipend', this.zip)
          console.log('fstrem', this.filestream)
        } else if (e.bigfile && this.gzipped) console.log('-------------------------gzipped end ', this.gzipped)
        const message = {
          name: this.eventnames.sendfile
        };
        if (e.part) {
          message["part"] = e.part;
        } else this.part = 0;
        if (e.hasOwnProperty("bigfile")) message["bigfile"] = e.bigfile;
        if (e.hasOwnProperty("path")) message["path"] = e.path;
        console.log('endzip%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%', e)
        this.emit(this.eventnames.complete, message);
      });

      this.on(this.eventnames.sendfile, async (e) => {
        console.log('eventsendfile', e)
        let file = (e.bigfile) ? await this.getFile(this.gzipped): await this.getFile();
        console.log('sendfile', file)
        /* if (e.bigfile) this.sendChunk((e.path ? e.path : ''));
          else */
        this.sendZipFile(file, (e.path ? e.path : ''), null, (e.bigfile ? e.bigfile : false));
      });
      this.on(this.eventnames.bigfile, (e) => {
        console.log('onsendchunk', e)
        this.sendChunk((e.path ? e.path : ''));
      });
      this.on(this.eventnames.endreaddir, (e) => {
        this.endreaddir = true;
        if (e.hasOwnProperty('name') && e.name === this.eventnames.endzip) {
          this.emit(this.eventnames.complete, {
            name: this.eventnames.endzip
          });
        }
      });
      this.on(this.eventnames.counter, async (e) => {
        this.counter[e.name] += 1;
        if (this.endreaddir && e.name === 'zip' && this.counter.scan === this.counter.zip) {
          console.log('end', this.counter)
          this.emit(this.eventnames.complete, {
            name: this.eventnames.endzip
          });
        }
        if (e.name === 'zip' && this.callback) await this.callback();
      });
    }
  }

  async quotaEstimate() {

    if (navigator && navigator.storage && navigator.storage.estimate) {
      navigator.storage.estimate().then((quota) => {
        const percentageUsed = ((quota.usage / quota.quota) * 100).toFixed(2);
        const remaining = format_bytes(quota.quota - quota.usage);
        this.emit(this.eventnames.message, {
          id: "quota",
          name: "console",
          message: "you've used " + percentageUsed + "% of the available storage (" + remaining + ")."
        });
      });
    }
  }

  async initStorage() {
    if (navigator && navigator.storage && navigator.storage.estimate) {
      await this.cleanStorage();
      this.emit(this.eventnames.ready);
      this.quotaEstimate();
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
  async scanCommon(is_dir, zipname, options = {}) {
    this.endreaddir = false;
    this.counter.scan = this.counter.zip = 0;
    if (this.zip === null) {
      const type = (options && options.type) ? options.type : '.zip';
      this.zipname = ((options.zipname) ? options.zipname : zipname) + type; //
      const zipinstorage = await this.searchStorage(this.zipname);
      if (zipinstorage) this.zipname = '1_' + this.zipname;
      const {
        filestream,
        streamhandle
      } = await this.createLocalStream(this.zipname);

      this.filestream = filestream;
      this.streamhandle = streamhandle;
      let size = 0;
      this.part = 0;
      await this.initZip();
      if (!this.jsScanDir) {
        const {
          JsScanDir
        } = await import('../files/js-scandir.js');
        this.jsScanDir = new JsScanDir();
      }
      this.jsScanDir.processFile = async (entry, callback) => {
        this.callback = callback;
        await this.processFile(entry);

      };
    }
  }

  async scanFiles(files, options = {}) {
    if (files.length === 0) return;
    const zipname = files[0].webkitRelativePath.split("/")[0];
    console.log(zipname, files[0]);
    await this.scanCommon(false, zipname, options);
    for (let n = 0; n < files.length; n++) {
      if (n === files.length - 1) this.emit(this.eventnames.endreaddir, {});
      await this.addFileToZipStream(files[n], files[n].webkitRelativePath);
    }

  }

  async scanHandle(dir, options = {}) {
    await this.scanCommon(true, dir.name, options);
    await this.jsScanDir.readDirectory(dir, () => {
      this.emit(this.eventnames.endreaddir, {
        name: this.eventnames.endzip
      });
    });

  }
  async sendBigFile(file, filepath) {
    console.log('sendbigfilepath', filepath)
    this.dt = Date.now();
    filepath = (filepath.indexOf('/') === 0) ? filepath.substr(1) : filepath;
    /*let filepath = file.webkitRelativePath;
    filepath = (filepath === '') ? dirname + '/' + file.name : filepath;*/
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
        name: this.eventnames.gzip,
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
        filename: filepath
      });
      gzipped.ondata = (data, final) => {
        if (final) {
          console.log('final BIGFILE%%%%%%%%%%%%%%%%%%%%' + selfi.eventnames.bigfile, filepath)
          selfi.emit(selfi.eventnames.complete, {
            name: selfi.eventnames.bigfile,
            bigfile: filepath

          });

          streamhandle.close();
          console.log('timetozip', (Date.now() - this.dt) / 1000)
          selfi.gzipped = filestream;
          console.log('big file *******************' + filepath, selfi.gzipped);

        } else {
          streamhandle.write(data, {
            at: pos
          });
          pos += data.length;
        }
      };
      await this.readFile(file, filepath, gzipped);
    }


  }
  async partZip() {
    this.part += 1;
    this.emit(this.eventnames.complete, {
      name: this.eventnames.endzip,
      part: this.part
    });
  }
  async readFile(file, filepath, zippedstream) {
    const self = this;
    const reader = file.stream().getReader();
    let pause = false;
    /*  onBackpressure(zippedstream, this.streamhandle, should_apply_backpressure => {
        if (should_apply_backpressure) pause = true;
        else if (pause) pause = false;
      });*/
    while (true) {
      const {
        done,
        value
      } = await reader.read();
      if (done) {
        zippedstream.push(new Uint8Array(0), true);
        self.emit(self.eventnames.counter, {
          name: 'zip',
          filepath: filepath,
          size: (zippedstream.size) ? zippedstream.size : file.size
        });
        break;
      }
      zippedstream.push(value);
    }
  }
  async zipStream(file, filepath) {
    const self = this;
    const ext = filepath.slice(filepath.lastIndexOf('.') + 1);
    const iscompressed = already_compressed.has(ext);
    const zippedstream = (iscompressed) ? new ZipPassThrough(filepath) : file.size > this.options.largefile ?
      new AsyncZipDeflate(filepath, {
        level: 6,
      }) : new ZipDeflate(filepath, {
        level: 6
      });
    this.zip.add(zippedstream);
    await this.readFile(file, filepath, zippedstream);
  }

  async addFileToZipStream(file, filepath) {
    console.log('emitscan', this.counter)
    this.emit(this.eventnames.counter, {
      name: 'scan',
      filepath: filepath,
      size: file.size
    });
    this.continue = null;
    // check file size > max post size
    if (file.size >= MAXSIZE) {
      await this.sendBigFile(file, filepath);
    } else {
      // check zip file size > total zip size
      this.sizetozip += file.size;
      if (this.sizetozip >= MAXSIZE) {
        this.continue = async () => {
          await this.zipStream(file, filepath);
        }
        this.partZip();
      } else {
        await this.zipStream(file, filepath);
      }
    }
  }

  async processFile(entry) {
    const self = this;
    const filepath = entry.fullPath;
    const ext = filepath.slice(filepath.lastIndexOf('.') + 1);
    if (this.options.accept.includes(ext)) {
      console.log('reject', filepath);
      return;
    }
    if (entry.isDirectory) {
      console.log('zipdir', this.callback)
      if (this.callback !== null) await this.callback();
    } else {
      entry.file(async file => {
        await this.addFileToZipStream(file, filepath);
      });

    }
  }
  onError() {
    this.cleanStorage();
    this.emit(this.eventnames.error, {
      name: "reload"
    });
  }
  async searchStorage(search) {
    const entry = await navigator.storage.getDirectory();
    for await (const [key, value] of entry.entries()) {
      if (search === key) {
        console.log('key', key);
        return true;
        false
        break;
      }
    }
    return false;
  }
  async cleanStorage(entry = null) {
    return;
    entry = (entry) ? entry : await navigator.storage.getDirectory();
    for await (const [key, value] of entry.entries()) {
      try {
        await entry.removeEntry(key);
      } catch (error) {
        console.log(' remove storage ' + key, error);
      }
    }

  }

  async endFetch(message, clean = false) {
    message.name = this.eventnames.terminate;
    if (message.hasOwnProperty("bigfile") && message.bigfile !== "" &&
      message.bigfile !== false && message.bigfile !== null) {
      message["bigfile"] = this.gzipped.name;
      this.gzipped = null;
    } else {
      if (this.continue) {
        this.streamhandle = await this.filestream.createWritable();
        await this.initZip();
      } else this.reset();
    }
    this.emit(this.eventnames.complete, message);
    console.log('continue', this.continue)
  }

  async sendChunk(path, start = 0, chunknum = 0, chunksize = MAXSIZE) {
    console.log('send chunk ', this.gzipped)
    console.log('chunkpath', path)
    const file = (this.gzipped) ? await this.getFile(this.gzipped): await this.getFile();
    console.log('file', file)
    path = path.split('/');
    path.pop();
    path = path.join('/');
    const end = Math.min(start + chunksize, file.size);
    console.log('end---', end)
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
  async getFile(filestream = null) {
    filestream = (filestream === null) ? this.filestream : filestream;
    const file = await filestream.getFile();
    return file;
  }
  async sendZipFile(file, path, callbackchunk = null, isbigfile = false) {
    console.log('sendzipfile------------_______________________' + isbigfile, file)
    const message = (isbigfile) ? {
      bigfile: file.name
    } : {};
    this.emit(this.eventnames.pending, message);
    console.log('file', file)
    console.log('path', path)
    console.log('callbackchunk---sendzip', callbackchunk)
    const formdata = new FormData();
    formdata.append('path', path + file.name);
    formdata.append('file', file, file.name);
    if (this.part) formdata.append('part', this.part);
    else if (callbackchunk !== null) formdata.append('ischunk', true);
    fetch(this.options.uploadurl, {
      //  mode: 'cors',
      method: "POST",
      credentials: "include",
      body: formdata,
    }).then(async (response) => {
      console.log('response----------------------', response);
      console.log('callbackchunk-------------------------------', callbackchunk)
      if (callbackchunk !== null) {
        await callbackchunk();
      } else await this.endFetch(message);
    });
  }
}