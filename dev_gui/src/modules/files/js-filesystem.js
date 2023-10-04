import {
  add_custom_events
} from '../../modules/utils.js';
export const objectEntry = {
  UUID: "",
  entry: {},
  status: 0 | 1 | 2,
  source: 'local' | 'server' | 'zip'
}

export class JsFilesStore {
  name = 'filesstore';
  store;
  writestream;
  _events = {};
  eventnames = {
    added: 'item.added',
    found: 'item.found',
    notfound: 'item.notfound'
  }

  constructor(name = null, callback = null, options = {}) {



    this.name = (name) ? name : this.name;
    this.init(options);

  }

  async init(options) {

    if (navigator.storage && navigator.storage.estimate) {
      const quota = await navigator.storage.estimate();
      // quota.usage -> Number of bytes used.
      // quota.quota -> Maximum number of bytes available.
      const percentageUsed = (quota.usage / quota.quota) * 100;
      console.log(`You've used ${percentageUsed}% of the available storage.`);
      const remaining = quota.quota - quota.usage;
      console.log(`You can write up to ${remaining} more bytes.`);
      console.log('quota', quota)
    }
    /*  const type = (options.type) ? options.type : '.zip';
      const root = await navigator.storage.getDirectory();
      const opts = {
        types: [{
          description: 'Temp file',
          accept: {
            'application/zip': ['.zip'],
          },
        }, ],
        create: true
      };
      this.store = await root.getFileHandle(this.name + type, opts);
      this.writestream = await this.store.createWritable({
        keepExistingData: false
      });*/
  }



  async addItem(item) {
    return true;
  }

  async getItem(key) {
    return true;
  }
  async getFile() {
    return this.store.getFile();
  }
  async addItems(items) {
    if (!Array.isArray(items)) return;
    items.forEach(async item => {
      return true;
    });
  }
  async getItems(source = null, keys = null, keysonly = true, objs = null) {
    if (!Array.isArray(keys)) return;

    if (source === null && keys === null) {
      return true;
    } else if (keys !== null) {
      const items = [];
      if (source !== null) return items.filter(item => (item.source === source));
      else return items;
    } else return [];
  }
  async updateItem(uuid, item) {
    if (!this.getItem(item.uuid)) return false;
    return await this.addItem(item);
  }


  async closeStream() {
    //await this.writestream.close();
    const file = await this.getFile();
    console.log(file)

  }
}