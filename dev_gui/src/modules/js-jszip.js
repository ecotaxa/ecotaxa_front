let instance = null;
import JSZip from 'jszip';
import {
  download_blob
} from '../modules/utils.js';
export class JsJSZip {
  type = "uint8array";
  streamHelper;
  zip;
  zipname;
  constructor(dirname) {
    if (!dirname) return;
    if (!instance) {
      this.init(dirname);
      instance = this;
    }
    return instance;
  }
  init(dirname) {
    this.zipname = dirname + '.zip';
    this.zip = new JSZip();
    this.addRoot(dirname);
  }
  addRoot(foldername) {
    return this.zip.folder(foldername);
  }
  addFolder(foldername, folder = false) {
    folder = (folder) ? folder : this.zip;
    return folder.folder(foldername);
  }
  generateZip() {
    this.zip.generateAsync({
      type: this.type,
      streamFiles: true
    }).then((content) => {
      this.downloadZip(content);

    });

  }
  downloadZip(content) {
    download_blob(content, this.zipname, 'application/zip');
  }
  addFile(filepath, data, type, folder = false) {
    folder = (folder) ? folder : this.zip;
    switch (type) {
      case 'image/jpeg':
        folder.file(filepath, data, {
          base64: true
        });
        break;
      case 'text/tsv':
        folder.file(filepath, data);
        break;
      default:
        console.log('no---filetype' + filepath + '-' + type, data)
        break;
    }

  }
  createStream() {
    this.streamHelper = this.zip
      .generateInternalStream({
        type: this.type
      }).accumulate(function updateCallback(metadata) {
        console.log('acc_metadata', metadata)
        // metadata contains for example currentFile and percent, see the generateInternalStream doc.
      }).then((data) => {
        console.log('zipped', this.zip);
        this.downloadZip(data);
        let file = new File([data], this.zipname, {
          type: "application/zip",
          lastModified: new Date().getTime()
        });
        let container = new DataTransfer();
        container.items.add(file);
        document.querySelector('#uploadfile').files = container.files;
        // data contains here the complete zip file as a uint8array (the type asked in generateInternalStream)
      });

  }
  saveZip() {
    this.zip.generateAsync({
        type: this.type
      })
      .then(function(content) {
        this.zip.saveAs(content, this.zipname);
      });
  }
}