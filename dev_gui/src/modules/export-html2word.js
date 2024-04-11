import {
  fetchSettings,
  unescape_html,
} from '../modules/utils.js';

async function get_html(element, pages = [], files = []) {
  pages.push(element.innerHTML);
  console.log('helppages', element.querySelectorAll('[data-request="help"]').length)
  for await (const el of element.querySelectorAll('[data-request="help"]')) {
    if (!el.dataset.file || files.indexOf(el.dataset.file) >= 0) return;
    files.push(el.dataset.file);
    const url = '/gui/help/' + el.dataset.file;
    const response = await fetch(url, fetchSettings());
    const text = await response.text();
    const temp = document.createElement('div');
    temp.innerHTML = text;
    await get_html(temp, pages, files);
  };
  return pages.join(`<br style="page-break-before: always">`);
}
export function export_html2word(element, trigger, filename = '') {
  const preHtml = "<html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'><head><meta charset='utf-8'><title>Export HTML To Doc</title></head><body>";
  const postHtml = "</body></html>";
  get_html(element).then(html => {
    html = preHtml + html + postHtml;
    const blob = new Blob(['\ufeff', html], {
      type: 'application/msword'
    });
    // Specify link url
    const url = 'data:application/vnd.ms-word;charset=utf-8,' + encodeURIComponent(html);
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
  });
}