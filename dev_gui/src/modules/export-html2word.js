import {
  fetchSettings,
  unescape_html,
} from '../modules/utils.js';
async function get_html(element, pages = [], files = []) {
  pages.push(element.innerHTML);
  for await (const el of element.querySelectorAll('[data-request="help"]')) {
    if (!el.dataset.file || files.indexOf(el.dataset.file) >= 0) return;
    files.push(el.dataset.file);
    const params = {
            partial: true,
            title: (el.dataset.title && el.dataset.title!=='')?el.dataset.title:el.textContent,
          };
    const url = '/gui/help/' +  el.dataset.file + '?' +
            new URLSearchParams(params);
    const response = await fetch(url, fetchSettings());
    const text = await response.text();
    const temp = document.createElement('div');
    temp.innerHTML = text.replaceAll('\n','').replaceAll('\r');
    await get_html(temp, pages, files);
  };
  }
export async function export_html2word(element, trigger, filename = '') {
   const preHtml = "<html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'><head><meta charset='utf-8'><title>Export HTML To Doc</title></head><body>";
   const postHtml = "</body></html>";
   const pages = [];
   await get_html(element,pages);
   const content = preHtml + pages.join(`<br style="page-break-before: always">`) + postHtml;
   const blob = new Blob(['\ufeff', content], {
      type: 'application/msword'
    });
    // Specify link url
   const url = 'data:application/vnd.ms-word;charset=utf-8,' + encodeURIComponent(content);
    // Specify file name
   filename = filename ? filename + '.doc' : 'document.doc';
    // Create download link element
   const downloadLink = document.createElement("a");
   trigger.appendChild(downloadLink);
    if (navigator.msSaveOrOpenBlob) {
      navigator.msSaveOrOpenBlob(blob, filename);
    } else {
      // Create a link to the file
      downloadLink.href = url;
      // Setting the file name
      downloadLink.download = filename;
      //triggering the function
      downloadLink.click();
    }
    trigger.removeChild(downloadLink);
 }