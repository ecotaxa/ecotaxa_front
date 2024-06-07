import {
  add_custom_events
} from '../../modules/utils.js';
let instance = null;

export class JsScanDir {
  _events = {};
  eventnames = {
    complete: 'complete',
    processed: 'file.processed',
    error: 'file.error',
  }
  nextaction;
  constructor() {
    if (instance) return instance;
    this.init();
    instance = this;
    return instance;
  }

  init(container) {
    add_custom_events(this);
    this.on(this.eventnames.error, (e) => {
      console.log('scandir receive error message', e)
    })
    this.on(this.eventnames.processed, async (e) => {
      console.log('e', e)
      //  if (this.nextaction) await this.nextaction();
    })
  }

  async processFile(entry, callback = null) {
    console.log('process scandir', entry)
    if (callback) await callback();
  }

  stopOnError(err) {
    console.log('err', err);
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


  async readDirectory(dir, oncomplete) {
    const self = this;
    let errored = false;
    let direntries = [];
    const on_error = onerror ? onerror : (err) => {
      console.log('on_error', err)
      if (!errored) {
        errored = true;
      }
    };
    const reader = dir.createReader();
    console.log('reader', reader)
    const on_read = async function(ents) {
      if (ents.length && !errored) {
        direntries = [...direntries, ...ents];
        await reader.readEntries(on_read, on_error);
      } else if (!errored) {
        const complete = async function() {
          if (oncomplete && direntries.length === 0) {
            console.log('dircomplete', dir.name);
            oncomplete();
          } else {
            const entry = direntries.shift();
            if (entry.isDirectory) await self.readDirectory(entry, complete);
            else await self.processFile(entry, complete);
          }
        }
        await complete();
      } else {
        console.log('treat error readdir');
      }
    }
    await reader.readEntries(on_read, on_error);
  }

  async processEntries(entries, path, oncomplete) {
    // showDirectoryPicker
    const self = this;
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
          await self.processFile(entry, complete);
        } else if (kind === "directory") {
          const direntries = await Array.fromAsync(entry.values());
          await self.processEntries(direntries, nestedpath, complete);
        }
      } else if (oncomplete) oncomplete();
    }
    await complete();
  }

}