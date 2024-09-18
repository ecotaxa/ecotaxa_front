import {
  ModuleEventEmitter
} from '../../modules/module-event-emitter.js';
let instance = null;

export function JsScanDir(process_file = null) {
  const eventnames = {
    complete: 'scan.complete',
    processed: 'scan.processed',
    error: 'scan.error',
  }
  let nextaction;
  ModuleEventEmitter.on(eventnames.error, (e) => {
    console.log('scandir receive error message', e)
  });
  ModuleEventEmitter.on(eventnames.processed, async (e) => {
    console.log('e', e)
  });

  async function processFile(entry, callback = null) {
    if (process_file) process_file(entry, callback);
    else if (callback) await callback();
  }

  function stopOnError(err) {
    console.log('err', err);
  }

  function fileType(data) {
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


  async function readDirectory(dir, oncomplete) {
    let errored = false;
    let direntries = [];
    const on_error = onerror ? onerror : (err) => {
      console.log('on_error', err)
      if (!errored) {
        errored = true;
      }
    };
    const reader = dir.createReader();
    const on_read = async function(ents) {
      if (ents.length && !errored) {
        direntries = [...direntries, ...ents];
        await reader.readEntries(on_read, on_error);
      } else if (!errored) {
        const complete = async function() {
          if (oncomplete && direntries.length === 0) {
            oncomplete();
          } else {
            const entry = direntries.shift();
            if (entry.isDirectory) await readDirectory(entry, complete);
            else await processFile(entry, complete);
          }
        }
        await complete();
      } else {
        console.log('treat error readdir');
      }
    }
    await reader.readEntries(on_read, on_error);
  }

  async function processEntries(entries, path, oncomplete) {
    // showDirectoryPicker
    const complete = async () => {
      if (entries.length) {
        const entry = await entries.shift();
        const nestedpath = `${path}/${entry.name}`;
        const kind = (entry.kind) ? entry.kind : (entry instanceof File) ? "file" : "directory";
        if (kind === "file") {
          if (!entry.webkitRelativePath) Object.defineProperty(entry, "webkitRelativePath", {
            configurable: true,
            enumerable: true,
            get: () => nestedpath,
          });
          if (entry instanceof File) entry.file = async (func) => {
            await func(entry, nestedpath);
          }
          else entry.file = async (func) => {
            entry.getFile().then(async file => {
              await func(file, nestedpath);
            });
          }
          await processFile(entry, complete);
        } else if (kind === "directory") {
          const direntries = await Array.fromAsync(entry.values());
          await processEntries(direntries, nestedpath, complete);
        }
      } else if (oncomplete) oncomplete();
    }
    await complete();
  }
  return {
    eventnames,
    processFile,
    processEntries,
    readDirectory
  }
}