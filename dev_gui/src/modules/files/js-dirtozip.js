'use strict';
import {
  fetchSettings,
  format_bytes,
  dirseparator,
  generate_uuid
} from '../../modules/utils.js';

import {
  AsyncGzip,
  Zip,
  AsyncZipDeflate,
  ZipPassThrough,
  ZipDeflate,
} from 'fflate';
import {
  ModuleEventEmitter
} from '../../modules/module-event-emitter.js';
import { detect } from 'detect-browser';

const already_compressed = new Set([
  'zip', 'gz', 'png', 'jpg', 'jpeg', 'pdf', 'doc', 'docx', 'ppt', 'pptx',
  'xls', 'xlsx', 'heic', 'heif', '7z', 'bz2', 'rar', 'gif', 'webp', 'webm',
  'mp4', 'mov', 'mp3', 'aifc'
]);
const accept = '.tsv,.png,.jpg, .jpeg,.zip,.gz,.7z,.bz2';
const MAXSIZE = 1073741824; //4294967296; //// 3221225472; // 2147483648;
export function JsDirToZip(options = {}) {
  const eventnames = {
    ready: 'ready',
    follow: 'follow',
    complete: 'complete',
    endreaddir: 'endreaddir',
    gzip: 'gzip',
    endzip: 'endzip',
    sendfile: 'sendfile',
    bigfile: 'bigfile',
    terminate: 'terminate',
    pending: 'pending',
    errorfile: 'errorfile',
    counter: 'counter',
    reject: 'reject',
    message: 'message',
    error: 'error',
    init: 'init'
  };
  let jsScanDir, properties;
  let trydelete=0;
  const defaultOptions = {
    uploadurl: '/gui/files/upload',
    largefile: MAXSIZE,
    accept: accept.split(',')
  }
  // uses https://developer.mozilla.org/en-US/docs/Web/API/File_System_API/Origin_private_file_system
  //# alternative (not supported in Safari) for .createWritable
  options = { ...defaultOptions,
    ...options
  };
  // other module receiving events
  const _listener = (options.listener) ? options.listener : uuid;
  Object.freeze(options);
  const uuid = generate_uuid();
  initStorage();
  init();

function browserRequired() {
const browser = detect();
     const accepted={android:{chrome:109,opera:74,firefox:111,samsungbrowser:21,webview:109}, ios:false,other:{chrome:86,edge:86,opera:72,firefox:111}};
        let os =browser.os.toLowerCase();
        os=(os in ['android','ios'])?os:'other';
     const name=browser.name.toLowerCase();
     const version = parseInt(browser.version.split('.')[0]);
 if ((accepted[os] && accepted[os][name] && accepted[os][name]<= version)===false)  {
     ModuleEventEmitter.emit(eventnames.message, {
          id: "browser",
          name: "browser",
          message: "your browser does not have a required functionnality. Please upgrade or use a valid browser and version :"+  JSON.stringify(accepted).replaceAll('"',''),
        }, _listener);
     }
     }
  function init() {
    properties = initProps();
    ModuleEventEmitter.on(eventnames.init, async (e) => {
      //  if (!e.bigfile && !e.part) {
      console.log('event init', e)
      if (isActive() === false) {
        await reset();
        ModuleEventEmitter.emit(eventnames.complete, {
          name: eventnames.ready
        }, _listener);
        properties.endreaddir = false;
      } else console.log('partly finshed ', e);
    }, uuid);
    ModuleEventEmitter.on(eventnames.endzip, async(e) => {
      if (!e.bigfile && properties.zip) properties.zip.end();
      else if (e.bigfile && properties.gzipped) console.log('--gzipped end', properties.gzipped);
      console.log('endzip%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%',);
      const evtsend=async function() {
      const zipclosed = await listStorage(null,properties.zipname);
      if (zipclosed === true) { 
      const message = buildMessage(e, {
        name: eventnames.sendfile,
      });
      ModuleEventEmitter.emit(eventnames.complete, message, _listener);}
      else setTimeout(async function() {await evtsend();},2000);}
      evtsend();
    }, uuid);
    ModuleEventEmitter.on(eventnames.sendfile, async (e) => {
      const file = (e.bigfile) ? await properties.gzipped.getFile(): await getFile();
      if (e.bigfile) {
        const path = (e.path ? e.path : '').replace(e.bigfile, '');
        sendChunk(path);
      } else sendZipFile(file, (e.path ? e.path : ''), null);
    }, uuid);
    ModuleEventEmitter.on(eventnames.endreaddir, (e) => {
      properties.endreaddir = true;
      checkProcessed(e);
    }, uuid);
    ModuleEventEmitter.on(eventnames.counter, async (e) => {
      properties.endcounter = false;
      properties.counter[e.name] += 1;
      ModuleEventEmitter.emit(eventnames.counter, e, _listener);
      if (e.name === 'zip' && properties.counter.scan === properties.counter.zip) {
        properties.endcounter = true;
        checkProcessed(e);
      }
      if (e.name === 'zip' && properties.callback) await properties.callback();
    }, uuid);
  }

  function initProps() {
    return {
      zip: null,
      zipname: null,
      filestream: null,
      streamhandle: null,
      gzipped: null,
      sizetozip: 0,
      part: 0,
      follow: null,
      endcounter: false,
      endreaddir: false,
      callback: null,
      pos: 0,
      counter: {
        scan: 0,
        zip: 0,
        reject: 0
      },
      handlers: []
    }
  }
  async function reset() {
    properties = initProps();
    await initStorage();
  }

  function isActive() {
    return (properties.zip !== null || properties.follow !== null || properties.gzipped !== null || properties.endreaddir !== true);
  }
  async function initZip() {
    properties.pos = 0;
    properties.sizetozip = 0;
    console.log('==================newzip');
    properties.zip = new Zip((error, chunk, final) => {
      if (error) {
        console.log('error', error);
        return false;
      } else {
        properties.streamhandle.write(chunk, {
          at: self.pos
        });
        properties.pos += chunk.length;
        if (final) {
          properties.streamhandle.close();
          console.log('final-----------------------------*******************************-', properties.pos);
        }

      }
    });
    // hack for memory usage
    zipOnData();

    if (properties.follow) await properties.follow();
  }

  function checkProcessed(e) {
    if (properties.endreaddir === true && properties.endcounter === true) {
      const message = buildMessage(e, {
       name: eventnames.endzip
      });
      ModuleEventEmitter.emit(eventnames.complete, message, _listener);
    }
  }

  function zipOnData(zip = null) {
    zip = (zip === null) ? properties.zip : zip;
    const ondata = zip.ondata;
    zip.ondata = (error, data, final) => {
      ondata(error, data, final);
      if (final) {
        zip.d = null;
        zip.u.at(-1).d = null; // Object created in `zip.add()`
      }
    }
  }

  function buildMessage(e, message = {}) {
    if (e.hasOwnProperty("part")) {
      message.part = e.part;
    } else properties.part = 0;
    if (e.hasOwnProperty("bigfile")) message.bigfile = e.bigfile;
    if (e.hasOwnProperty("path")) message.path = e.path;
    return message;
  }

  async function quotaEstimate() {
    if (navigator && navigator.storage && navigator.storage.estimate) {
      navigator.storage.estimate().then((quota) => {
        const percentageUsed = ((quota.usage / quota.quota) * 100).toFixed(2);
        const remaining = format_bytes(quota.quota - quota.usage);
        ModuleEventEmitter.emit(eventnames.message, {
          id: "quota",
          name: "console",
          message: "you've used " + percentageUsed + "% of the available browser storage necessary to locally compress files (" + remaining + ").",
        }, _listener);
      });
    }
  }

  async function initStorage() {
    if (navigator && navigator.storage && navigator.storage.estimate) {
      await cleanStorage();
      quotaEstimate();
    } else ModuleEventEmitter.emit(eventnames.message, {
      name: "error",
      message: "no navigator storage"
    }, uuid);
  }

  async function createLocalStream(name, accept = {
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
    const streamhandle = await filestream.createWritable({mode:"exclusive"});
    return {
      filestream,
      streamhandle
    };
  }
  async function scanCommon(zipname, options = {}) {
    properties.endreaddir = false;
    if (properties.zip === null) {
      zipname = zipname.split(dirseparator)[0];
      zipname = (zipname.trim() === ``) ? 'temp' : zipname;
      const type = (options && options.type) ? options.type : '.zip';
      properties.zipname = ((options.zipname) ? options.zipname : zipname) + type; //
      const zipinstorage = await searchStorage(properties.zipname);
      if (zipinstorage) properties.zipname = '1_' + properties.zipname;
      const {
        filestream,
        streamhandle
      } = await createLocalStream(properties.zipname);
      properties.filestream = filestream;
      properties.streamhandle = streamhandle;
      let size = 0;
      properties.part = 0;
      await initZip();
      if (!jsScanDir) {
        const {
          JsScanDir
        } = await import('../files/js-scandir.js');
        const process_file = async (entry, callback) => {
          if (acceptFile(entry)) {
            properties.callback = callback;
            await processFile(entry);
          } else rejectFile(entry, callback);
        }
        jsScanDir = JsScanDir(process_file);
      }
    }
  }

  async function scanBrowse(pick, options = {}) {
    const entries = (pick instanceof FileList) ? Array.from(pick) : (pick.kind === "directory") ? await Array.fromAsync(pick.values()): (Array.isArray(pick)) ? pick : [pick];
    const name = entries[0].name;
    let relpath = (pick instanceof FileList) ? entries[0].webkitRelativePath : null;
    relpath = (relpath) ? relpath.split(dirseparator) : [``];
    if (relpath.length) relpath.pop();
    relpath = relpath.join(dirseparator)
    const path = (pick instanceof FileList) ? relpath : (pick.kind === "directory") ? pick.name : ``;
    await scanCommon(path, options);
    await jsScanDir.processEntries(entries, path, () => {
      dirComplete();
    });
  }

  async function scanHandle(dropped, options = {}) {
    await scanCommon(dropped.name, options);
    if (dropped.isDirectory === true) {
      await jsScanDir.readDirectory(dropped, () => {
        dirComplete();
      });
    } else if (dropped.isFile === true) {
      await jsScanDir.processFile(dropped, () => {
        dirComplete();
      });
    }
  }

  function dirComplete() {
    ModuleEventEmitter.emit(eventnames.endreaddir, {
      name: eventnames.endreaddir
    }, uuid);
  }

  function addHandler(handler) {
    properties.handlers.push(handler);
  }

  async function execHandler() {
    // serie
    if (properties.handlers.length > 0) {
      const handler = properties.handlers.shift();
      await handler();
    }
    return;
  }
  async function gzipBigFile(file, filepath) {
    if (properties.gzipped !== null) {
      await addHandler(async () => {
        await gzipBigFile(file, filepath);
      });
      return;
    }
    let dt = Date.now();
    filepath = (filepath.indexOf(dirseparator) === 0) ? filepath.substr(1) : filepath;
    /*filepath = filepath.split(dirseparator);
    filepath.pop();
    filepath = filepath.join(dirseparator);*/
    const ext = file.name.slice(file.name.lastIndexOf('.') + 1);
    if (already_compressed.has(ext)) {
      properties.gzipped = file;
      ModuleEventEmitter.emit(eventnames.counter, {
        name: 'zip',
        path: filepath,
        size: file.size
      }, uuid);
      ModuleEventEmitter.emit(eventnames.complete, {
        name: eventnames.bigfile,
        bigfile: file.name,
        path: filepath,
      }, _listener);
    } else {
      let zipname = file.name + '.gz';
      ModuleEventEmitter.emit(eventnames.complete, {
        name: eventnames.gzip,
        bigfile: file.name,
        path: filepath,
        size: file.size
      }, _listener);
      const {
        filestream,
        streamhandle
      } = await createLocalStream(zipname, {
        'application/gzip': ['.gz'],
      });
      let pos = 0;

      const gzipped = new AsyncGzip({
        level: 6,
        filename: filepath
      });
      gzipped.ondata = (err, data, final) => {
        if (err) {
          console.log('gzip err', err);
          onError(eventnames.errorfile, {
            bigfile: file.name,
            path: filepath,
            size: file.size
          });
        } else {
          streamhandle.write(data, {
            at: pos
          });
          pos += data.length;

          if (final) {
            console.log('final BIGFILE%%%%%%%%%%%%%%%%%%%%' + eventnames.bigfile, filepath)

            console.log('timetogzzip', (Date.now() - dt) / 1000);

            streamhandle.close();
            properties.gzipped = filestream;
            ModuleEventEmitter.emit(eventnames.counter, {
              name: 'zip',
              path: filepath,
              size: file.size
            }, uuid);
            ModuleEventEmitter.emit(eventnames.complete, {
              name: eventnames.bigfile,
              bigfile: file.name,
              path: filepath
            }, _listener);
          }
        }
      };
      const count = false;
      await readFile(file, filepath, gzipped, count);
    }


  }
  async function partZip() {
    properties.part += 1;
    ModuleEventEmitter.emit(eventnames.complete, {
     name: eventnames.endzip,
      part: properties.part
    }, _listener);
  }
  async function readFile(file, filepath, zippedstream, count = true) {
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
        if (count === true) ModuleEventEmitter.emit(eventnames.counter, {
          name: 'zip',
          path: filepath,
          size: (zippedstream.size) ? zippedstream.size : file.size
        }, uuid);
        break;
      }
      zippedstream.push(value);
    }
  }

  async function zipStream(file, filepath) {
    const ext = filepath.slice(filepath.lastIndexOf('.') + 1);
    const iscompressed = already_compressed.has(ext);
    const zippedstream = (iscompressed) ? new ZipPassThrough(filepath) : file.size > options.largefile ?
      new AsyncZipDeflate(filepath, {
        level: 6,
      }) : new ZipDeflate(filepath, {
        level: 6
      });
    properties.zip.add(zippedstream);
    await readFile(file, filepath, zippedstream);
  }

  async function addFileToZipStream(file, filepath, count = true) {
    if (count === true) ModuleEventEmitter.emit(eventnames.counter, {
      name: 'scan',
      path: filepath,
      size: file.size
    }, uuid);
    properties.follow = null;
    // check file size > max post size
    if (file.size >= MAXSIZE) {
      gzipBigFile(file, filepath);
    } else {
      // check zip file size > total zip size
      properties.sizetozip += file.size;
      if (properties.sizetozip >= MAXSIZE) {
        properties.follow = async () => {
          await zipStream(file, filepath);
        }
        partZip();
      } else {
        await zipStream(file, filepath);
      }
    }
  }

  function acceptFile(entry) {
    const filepath = entry.name;
    const ext = filepath.slice(filepath.lastIndexOf('.') + 1);
    return accept.includes(ext);
  }

  function rejectFile(file, callback = null) {
    const path = (file.fullPath) ? file.fullPath : file.webkitRelativePath;
    properties.counter.reject += 1;
    ModuleEventEmitter.emit(eventnames.reject, {
      name: eventnames.reject,
      path: path,
    }, _listener);
    if (callback !== null) callback();
  }
  async function processFile(entry) {
    const path = (entry.fullPath) ? entry.fullPath : entry.webkitRelativePath;
    entry.file(async file => {
      await addFileToZipStream(file, path);
    });
  }

  function onError(action, message = null) {
    message = (message) ? message : {};
    switch (action) {
      case eventnames.init:
        message.name = eventnames.init;
        break;
      case eventnames.errorfile:
        console.log('errorfile', message);
      default:
        message.name = eventnames.follow;
        break;
    }
    ModuleEventEmitter.emit(eventnames.error, message, _listener);
  }
  async function searchStorage(search) {
    const entry = await navigator.storage.getDirectory();
    for await (const [key, value] of entry.entries()) {
      if (search === key) {
        return true;
        break;
      }
    }
    return false;
  }
  async function cleanStorage(entry = null) {
    entry = (entry) ? entry : await navigator.storage.getDirectory();
     for await (const [key, value] of entry.entries()) {
      try {
        await entry.removeEntry(key);
        console.log(' Success remove storage ', key);
      } catch (error) {
        console.log(' error remove storage ' + key, error);
        }
      }
    }
async function listStorage(entry = null,name=null) {
    entry = (entry) ? entry : await navigator.storage.getDirectory();
    let rep=true;
     for await (const [key, value] of entry.entries()) {
        if (name!==null) {
            const parts = key.split('.');
            if (parts.pop()==='crswap' && parts.join('.') ===name) {
            rep=false;
            break;
            }
        }
        }
      return rep;
    }
  async function endFetch(message, clean = false) {
    message.name = eventnames.terminate;
    if (properties.follow) {
      properties.streamhandle = await properties.filestream.createWritable({mode:"exclusive"});
      message.name = eventnames.follow;
      ModuleEventEmitter.emit(eventnames.follow, message, _listener)
      await initZip();
      return;
    } else if (message.hasOwnProperty("bigfile") && message.bigfile !== false) {
      properties.gzipped = null;

      if (properties.handlers.length > 0) {
        message.name = eventnames.follow;
        ModuleEventEmitter.emit(eventnames.follow, message, _listener);
        console.log(' handlers to do', message);
        if (properties.handlers.length > 0) await execHandler();
        return;
      }
    } else properties.zip = null;
    ModuleEventEmitter.emit(eventnames.complete, message, _listener);
  }

  async function sendChunk(path, start = 0, chunknum = 0, chunksize = MAXSIZE) {
    console.log('send chunk ', properties.gzipped)
    const file = await properties.gzipped.getFile();
    const end = Math.min(start + chunksize, file.size);
    if (end === file.size) {
     await sendZipFile(file, path, null, true);
    } else {
      const partfile = file.slice(start, end);
      partfile.name = chunknum + '_' + file.name;
      await sendZipfile(partfile, path, async () => {
        start += end;
        chunknum++;

        if (start <= file.size) await sendChunk(path, start, chunknum, chunksize);
      }, true)
    }
    return chunknum;
  }
  async function getFile(filestream = null) {
    filestream = (filestream === null) ? properties.filestream : filestream;
    const file = await filestream.getFile();
    return file;
  }
  async function sendZipFile(file, path, callbackchunk = null, bigfile = false) {
    const message = {
      name: eventnames.pending,
      path: path
    }
    if (bigfile) message.bigfile = file.name;
    ModuleEventEmitter.emit(eventnames.complete, message, _listener);
    const formdata = new FormData();
    path = path + ((path.slice(-1) === dirseparator) ? `` : dirseparator) + file.name;
    formdata.append('path', path);
    formdata.append('file', file, file.name);
    if (properties.part) formdata.append('part', properties.part);
    else if (callbackchunk !== null) formdata.append('ischunk', true);
    fetch(options.uploadurl, {
      //  mode: 'cors',
      method: "POST",
      credentials: "include",
      body: formdata,
    }).then(async (response) => {
      console.log('response----------------------', response);
      console.log('callbackchunk-------------------------------', callbackchunk)
      message.path = path;
      if (response.status !== 200) {
        onError(eventnames.error, message);
        return;
      }
      if (callbackchunk !== null) { console.log('callbackchunk not null')
        await callbackchunk();
      } else await endFetch(message);
    });
  }
  return {
    uuid,
    eventnames,
    scanBrowse,
    scanHandle,
    quotaEstimate,
    browserRequired
  }
}