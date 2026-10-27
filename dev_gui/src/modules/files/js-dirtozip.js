'use strict';
import {
  fetchSettings,
  format_bytes,
  dirseparator,
  generate_uuid
} from '../../modules/utils.js';

import {
  ZipWriter,
  BlobReader,
} from '@zip.js/zip.js';
import {
  ModuleEventEmitter
} from '../../modules/module-event-emitter.js';
import { detect } from 'detect-browser';
import {AlertBox} from '../../modules/alert-box.js';
import * as tus from 'tus-js-client';
const already_compressed = new Set([
  'zip', 'gz', 'png', 'jpg', 'jpeg', 'pdf', 'doc', 'docx', 'ppt', 'pptx',
  'xls', 'xlsx', 'heic', 'heif', '7z', 'bz2', 'rar', 'gif', 'webp', 'webm',
  'mp4', 'mov', 'mp3', 'aifc'
]);
const can_be_compressed = new Set(['tsv','txt','log','csv']);
const accept = '.tsv,.png,.jpg, .jpeg,.zip,.gz,.7z,.bz2';

export function JsDirToZip(options = {}) {
  const MAXSIZE = (document.querySelector('[data-max_upload_size]'))?parseInt(document.querySelector('[data-max_upload_size]').dataset['max_upload_size']):1073741824;//681574400;//681574400; // 650M //1073741824; //4294967296; //// 3221225472; // 2147483648;
  const UPLOADINPARTS = (document.querySelector('[data-uploadinparts]'))?true:false;
  // translated messages from the template, {file} and {max} are replaced
  const TOOLARGE = {
    file: (document.querySelector('[data-toolargefile]')) ? document.querySelector('[data-toolargefile]').dataset['toolargefile'] : 'The file {file} is too large to upload (over {max}).',
    archive: (document.querySelector('[data-toolargearchive]')) ? document.querySelector('[data-toolargearchive]').dataset['toolargearchive'] : 'The archive is too large to upload (over {max}). Remove some files, or add them in several separate uploads.'
  };
  const eventnames = {
    ready: 'ready',
    follow: 'follow',
    complete: 'complete',
    endreaddir: 'endreaddir',
    endzip: 'endzip',
    sendfile: 'sendfile',
    bigfile: 'bigfile',
    terminate: 'terminate',
    pending: 'pending',
    progress: 'progress',
    errorfile: 'errorfile',
    uploaderror: 'uploaderror',
    counter: 'counter',
    reject: 'reject',
    message: 'message',
    error: 'error',
    init: 'init',
    setuploadpath:'setuploadpath'
  };
  let jsScanDir, properties,uploadpath;
  let trydelete=0;
  // scan batches (drop / browse) are run one after another so they never
  // interleave while feeding the same archive
  let scanChain = Promise.resolve();
  function serializeScan(task) {
    const run = scanChain.then(task, task);
    scanChain = run.catch(() => {});
    return run;
  }
  // resolves the batch currently being ingested (its files are processed
  // asynchronously through the counter events, so the batch is only "done"
  // once its completion callback - or endProcess - fires)
  let batchDeferred = null;
  function newBatch() {
    let resolve;
    const promise = new Promise((r) => { resolve = r; });
    batchDeferred = {
      promise,
      resolve: () => { batchDeferred = null; resolve(); }
    };
    return batchDeferred;
  }
  function endBatch() {
    if (batchDeferred) batchDeferred.resolve();
  }
  const defaultOptions = {
    uploadurl: '/gui/files/upload',
    tusuploadurl: window.location.origin + '/api/user_files/upload',
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
     if (Object.keys(accepted).indexOf(os)<0 || Object.keys(accepted[os]).indexOf(name)<0 || parseInt(accepted[os][name])>parseInt(version))  {
     ModuleEventEmitter.emit(eventnames.message, {
          id: "browser",
          name: "browser",
          message: "your browser does not have a required functionnality. Please upgrade or use a valid browser and version :"+  JSON.stringify(accepted).replaceAll('"',''),
        }, _listener);
     }
     }
  function init() {
    properties = initProps();
     ModuleEventEmitter.on(eventnames.setuploadpath, async(e) => {
    uploadpath=e.path;},uuid);
    ModuleEventEmitter.on(eventnames.init, async (e) => {
      if (!isActive()) {
        await reset();
        ModuleEventEmitter.emit(eventnames.complete, {
          name: eventnames.ready
        }, _listener);
          ModuleEventEmitter.emit(eventnames.message, {
          name: AlertBox.alertconfig.types.success,
          message: "Upload of "+ e.path +" is done",
        }, _listener);
        properties.endreaddir = false;
      } else console.log('partly finished '+properties.hashandlers+ 'follow='+properties.follow, e);
    }, uuid);
    ModuleEventEmitter.on(eventnames.endzip, async(e) => {
      // end() only once per archive
      if (!e.bigfile && properties.zip && !properties.zip.ending) {
        properties.zip.ending = true;
        properties.closed = true;
        await properties.zip.close();
      }
      const evtsend=async function() {
      const zipclosed = await listStorage(null,properties.zipname);
      if (zipclosed === true) {
      const message = buildMessage(e, {
        name: eventnames.sendfile,      });

      ModuleEventEmitter.emit(eventnames.complete, message, _listener);}
      else setTimeout(async function() {await evtsend();},2000);}
      evtsend();
    }, uuid);
    ModuleEventEmitter.on(eventnames.sendfile, async (e) => {
      if (properties.hashandlers) {
        const message = buildMessage(e, {
            name: eventnames.follow,
        });
        ModuleEventEmitter.emit(eventnames.follow, message, _listener);
        await execHandler();
      } else { const message = buildMessage(e, {
        name: eventnames.pending,
      });

        ModuleEventEmitter.emit(eventnames.complete, message, _listener);
      }

      const file = await getFile();
      sendZipFile(file, (e.path ? e.path : uploadpath), null);
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
    ModuleEventEmitter.on(eventnames.error,  (e) => {});
  }

  function initProps() {
    return {
      zip: null,
      zipname: null,
      filestream: null,
      streamhandle: null,
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
        reject: 0,
        error:0,
      },
      handlers: [],
      hashandlers:false,
      // number of scan batches (drop / browse) currently being ingested
      scanning: 0,
      // true once the archive has been closed for upload: no more additions
      closed: false,
     }
  }
  async function reset() {
    properties = initProps();
    await initStorage();
  }

  function isActive() {
    return (properties.zip !== null || properties.follow !== null || properties.hashandlers || properties.endreaddir !== true);
  }

  async function initZip() {
    properties.pos = 0;
    properties.sizetozip = 0;
    properties.zip = new ZipWriter(properties.streamhandle, { zip64: true });
    if (properties.follow) await properties.follow();
  }

  function emitEndZip(e) {
    const message = buildMessage(e, {
      name: eventnames.endzip
    });
    ModuleEventEmitter.emit(eventnames.complete, message, _listener);
    // archive fully built and waiting for the user: the next drop / browse
    // batch can now be ingested
    endBatch();
  }
  function checkProcessed(e) {
    // a drop / browse is still feeding the current archive: don't close it yet
    if (properties.scanning > 0) return;
    if (properties.endreaddir === true) {
      if (properties.endcounter === true) {
        emitEndZip(e);
      } else if (properties.counter.error > 0) {
        endProcess();
      } else if (properties.counter.scan === properties.counter.zip) {
        // reading finished with nothing left to zip (e.g. every dropped file
        // was rejected) - release the batch so more can be added
        emitEndZip(e);
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
    if (properties.closed) {
      ModuleEventEmitter.emit(eventnames.message, {
        name: AlertBox.alertconfig.types.info,
        message: 'The upload has already started. Wait until it finishes before adding more files.',
      }, _listener);
      return false;
    }
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
    return true;
  }

  function scanBrowse(pick, options = {}) {
    return serializeScan(() => scanBrowseImpl(pick, options));
  }
  async function scanBrowseImpl(pick, options = {}) {
    const entries = (pick instanceof FileList) ? Array.from(pick) : (pick.kind === "directory") ? await Array.fromAsync(pick.values()): (Array.isArray(pick)) ? pick : [pick];
    const name = entries[0].name;
    let relpath = (pick instanceof FileList) ? entries[0].webkitRelativePath : null;
    relpath = (relpath) ? relpath.split(dirseparator) : [``];
    if (relpath.length) relpath.pop();
    relpath = relpath.join(dirseparator);
    const path = (pick instanceof FileList) ? relpath : (pick.kind === "directory") ? pick.name : ``;
    if ((await scanCommon(path, options)) === false) return;
    properties.scanning += 1;
    const batch = newBatch();
    await jsScanDir.processEntries(entries, path, () => {
      properties.scanning = Math.max(0, properties.scanning - 1);
      dirComplete();
    });
    await batch.promise;
  }

  function scanHandle(dropped, options = {}) {
    return serializeScan(() => scanHandleImpl(dropped, options));
  }
  async function scanHandleImpl(dropped, options = {}) {
    // `dropped` may be a single entry or several entries dropped at once; they
    // all go into one zip, so scanCommon runs once and dirComplete() is emitted
    // only after the last entry has been read.
    const entries = Array.isArray(dropped) ? dropped.slice() : [dropped];
    if (!entries.length) return;
    if ((await scanCommon(entries[0].name, options)) === false) return;
    properties.scanning += 1;
    const batch = newBatch();
    const next = async () => {
      if (!entries.length) {
        properties.scanning = Math.max(0, properties.scanning - 1);
        dirComplete();
        return;
      }
      const entry = entries.shift();
      if (entry.isDirectory === true) {
        await jsScanDir.readDirectory(entry, next);
      } else if (entry.isFile === true) {
        await jsScanDir.processFile(entry, next);
      } else {
        await next();
      }
    };
    await next();
    await batch.promise;
  }

  function dirComplete() {
    ModuleEventEmitter.emit(eventnames.endreaddir, {
      name: eventnames.endreaddir
    }, uuid);
  }

  async function execHandler() {
    // serie
    if (properties.hashandlers) {
      const handler = properties.handlers.shift();
      await handler();
     properties.hashandlers = (properties.handlers.length>0)
    }
    return;
  }
  async function partZip() {
    properties.part += 1;
    ModuleEventEmitter.emit(eventnames.complete, {
      name: eventnames.endzip,
      part: properties.part
    }, _listener);
  }

  async function zipStream(file, filepath) {
    const relativePath = (filepath.indexOf(dirseparator) === 0) ? filepath.slice(1) : filepath;
    const ext = relativePath.slice(relativePath.lastIndexOf('.') + 1).toLowerCase();
    const iscompressed = already_compressed.has(ext);
    const level = iscompressed ? 0 : 6;
    try {
      // stored entries (level 0) only need a crc32: a web worker would just add copy overhead per file
      await properties.zip.add(relativePath, new BlobReader(file), {
        level,
        zip64: true,
        bufferedWrite: false,
        useWebWorkers: !iscompressed
      });
      ModuleEventEmitter.emit(eventnames.counter, {
        name: 'zip',
        path: filepath,
        size: file.size
      }, uuid);
    } catch (err) {
      properties.counter.error += 1;
      onError(eventnames.errorfile, {
        name: eventnames.error,
        path: filepath,
        message: 'Error zipping file ' + file.name + ': ' + ((err && err.message) ? err.message : err)
      }, _listener);
      endProcess(true);
    }
  }
  function compressed_estimate(file) {
    const ext = file.name.slice(file.name.lastIndexOf('.') + 1);
    if (can_be_compressed.has(ext)) return Math.floor(file.size/2);
    return file.size;
  }
  async function addFileToZipStream(file, filepath, count = true) {
    if (count === true) ModuleEventEmitter.emit(eventnames.counter, {
      name: 'scan',
      path: filepath,
      size: file.size
    }, uuid);
    properties.follow = null;

    // check file size > max post size
    const compressed_size = compressed_estimate(file);
    if (compressed_size >= MAXSIZE ) {
      // a single file over the server limit can't be sent
      const message = TOOLARGE.file.replace('{file}', filepath).replace('{max}', format_bytes(MAXSIZE));
      properties.counter.error += 1;
      onError(eventnames.errorfile, {
        name: eventnames.error,
        path: filepath,
        message: message,
      }, _listener);
      return endProcess(true);
    } else {
      // check zip file size > total zip size
      properties.sizetozip += compressed_size;
      if (properties.sizetozip > MAXSIZE) {
      if(UPLOADINPARTS) {
      properties.follow = async () => {
          await zipStream(file, filepath);
        }
        partZip();
        } else {
          // the archive being built is over the server limit: alert and stop
          const message = TOOLARGE.archive.replace('{max}', format_bytes(MAXSIZE));
          properties.counter.error += 1;
          onError(eventnames.errorfile, {
            name: eventnames.error,
            path: filepath,
            message: message,
          }, _listener);
          return endProcess(true);
        }
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
    const entrypath = (entry.fullPath) ? entry.fullPath : entry.webkitRelativePath;
    entry.file(async file => {
      await addFileToZipStream(file, entrypath);
    }, (err) => {
      // the file could not be read: report it and release the current batch so
      // the archive does not stay stuck half-built
      properties.counter.error += 1;
      onError(eventnames.errorfile, {
        name: eventnames.error,
        path: entrypath,
        message: 'Could not read file ' + entrypath,
      }, _listener);
      endProcess(true);
    });
  }

  function onError(action, message = null) {
    message = (message) ? message : {};
    switch (action) {
      case eventnames.init:
      case eventnames.errorfile:
        message.name=action;
        break;
      default:
        //message.name = eventnames.error;
        break;
    }
    ModuleEventEmitter.emit(eventnames.message, message, _listener);
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
    if (properties.follow) {
      properties.streamhandle = await properties.filestream.createWritable({mode:"exclusive"});
      message.name = eventnames.follow;
      ModuleEventEmitter.emit(eventnames.follow, message, _listener);
      await initZip();
      return;
    } else properties.zip = null;
    if (!properties.hashandlers) {message.name = eventnames.terminate;ModuleEventEmitter.emit(eventnames.complete, message, _listener);}
  }

  async function getFile(filestream = null) {
    filestream = (filestream === null) ? properties.filestream : filestream;
    const file = await filestream.getFile();
    return file;
  }
  async function sendZipFile(file, path, callbackchunk = null, bigfile = false) {
    if (properties.counter.error > 0) return endProcess();
    const message = {
      name: eventnames.pending,
      bigfile: bigfile,
      path: path
    }
    path = path + ((path.slice(-1) === dirseparator) ? `` : dirseparator) + file.name;
    message.path = path;
    const upload = new tus.Upload(file, {
      endpoint: options.tusuploadurl,
      retryDelays: [0, 3000, 5000, 10000, 20000],
      chunkSize: 128*1024*1024, // TODO: Some config
      storeFingerprintForResumableUploads: false,
      removeFingerprintOnSuccess: true,
      metadata: {
        filename: file.name,
        filetype: file.type,
        path: path
      },
      onError: async (error) => {
        properties.follow = null;
        if (bigfile || properties.hashandlers) {
          // unchanged: multi-part / big-file uploads can't be resumed here
          await endFetch(message);
          properties.counter.error += 1;
          onError(eventnames.errorfile, message);
          endProcess();
          return;
        }
        // single archive: keep the zip in OPFS so the user can re-send it.
        // Do NOT endFetch / terminate / reset, and do NOT bump counter.error
        // (sendZipFile()'s `if (properties.counter.error > 0) return endProcess()`
        //  guard must stay clear so a retry can go through).
        properties.zip = null; // mirror endFetch's cleanup; archive file stays
        ModuleEventEmitter.emit(eventnames.message, {
          name: AlertBox.alertconfig.types.error,
          message: 'Upload failed (' +
            ((error && error.message) ? error.message : 'network or server error') +
            '). Click "Retry upload" to try again.',
          path: message.path,
        }, _listener);
        ModuleEventEmitter.emit(eventnames.complete, {
          name: eventnames.uploaderror,
          path: uploadpath, // dir only; sendfile handler appends file.name
          part: 0,
          bigfile: false,
        }, _listener);
      },
      onProgress: (bytesUploaded, bytesTotal) => {
        const percentage = (bytesUploaded / bytesTotal * 100).toFixed();
        ModuleEventEmitter.emit(eventnames.progress, {
          name: eventnames.progress,
          percentage: percentage,
          path: path
        }, _listener);
      },
      onSuccess: async () => {
        if (callbackchunk) {
          await callbackchunk();
        } else {
          if (!bigfile || !properties.hashandlers) await endFetch(message);
          if (bigfile) {
            message.name = eventnames.follow;
            ModuleEventEmitter.emit(eventnames.follow, message, _listener);
          }
        }
      }
    });

    // Check if there are any previous uploads to continue.
    upload.findPreviousUploads().then(function (previousUploads) {
      // Found previous uploads so we select the first one.
      if (previousUploads.length) {
        upload.resumeFromPreviousUpload(previousUploads[0]);
      }
      // Start the upload
      upload.start();
    });
  }
  
  async function sendZipFile_old(file, path, callbackchunk = null, bigfile = false) {
  if(properties.counter.error>0) return endProcess();
    const message = {
      name: eventnames.pending,
      bigfile:bigfile,
      path: path
    }
    const formdata = new FormData();
    path = path + ((path.slice(-1) === dirseparator) ? `` : dirseparator) + file.name;
    formdata.append('path', path);
    formdata.append('file', file, file.name);
    if (properties.part) formdata.append('part', properties.part);
    else if (callbackchunk !== null) formdata.append('ischunk', true);
    message.path = path;
    const response = await fetch(options.uploadurl, {
      //  mode: 'cors',
      method: "POST",
      credentials: "include",
      body: formdata,
    });
    const body=await response.text();
      if (response.ok) {
      if (callbackchunk) {
        await callbackchunk();
      } else { if(!bigfile || !properties.hashandlers)  await endFetch(message);
       if (bigfile) {message.name=eventnames.follow;
      ModuleEventEmitter.emit(eventnames.follow, message, _listener);
      } }
      } else {
        properties.follow=null;
        await endFetch(message);
         properties.counter.error+=1;
        onError(eventnames.errorfile, message); if(bigfile || properties.hashandlers) endProcess();    }
  }
  function endProcess(silent = false) {
    properties.follow=null;
    properties.scanning = 0;
    endBatch();
    if (!silent) onError(eventnames.errorfile,{
            name: AlertBox.alertconfig.types.error,
            message: "Upload not done. one or more files exceeds max upload size",
            path:uploadpath,
            });
    reset().then(() => {
        ModuleEventEmitter.emit(eventnames.complete, {
          name: eventnames.ready
        }, _listener);
        properties.endreaddir = false;  });
    return false;
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