import DOMPurify from 'dompurify';
import {
  v4 as uuidv4
} from 'uuid';
const dirseparator = "/";
const urlseparator = "/";

function browser_version() {
  const user_agent = navigator.userAgent;

  console.log(user_agent);
}

function generate_uuid() {
  return uuidv4();
}

function fetchSettings(options) {
  options = options || {};
  options.headers = options.headers || {};
  options.headers['X-Requested-With'] = 'XMLHttpRequest';
  if (!options.credentials) options.credentials = 'include';
  options.redirect = "error";
  options.cache = "no-cache";
  return options;
}
function set_cursor_editable(el,chars=0) {
function create_range(node, chars, range) {
    if (!range) {
        range = document.createRange();
        range.selectNode(node);
        range.setStart(node, 0);
    }
    if (chars.count === 0) {
        range.setEnd(node, chars.count);
    } else if (node && chars.count >0) {
        if (node.nodeType === Node.TEXT_NODE) {
            if (node.textContent.length < chars.count) {
                chars.count -= node.textContent.length;
            } else {
                 range.setEnd(node, chars.count);
                 chars.count = 0;
            }
        } else {
            for (const lp = 0; lp < node.childNodes.length; lp++) {
                range = create_range(node.childNodes[lp], chars, range);
                if (chars.count === 0) {
                   break;
                }
            }
        }
   }
   return range;
};
    if (chars >= 0) {
        const selection = window.getSelection();
        const range = create_range(el, { count: chars });
        if (range) {
            range.collapse(false);
            selection.removeAllRanges();
            selection.addRange(range);
        }
    }

}

function string_to_boolean(str) {
  if (typeof str === 'boolean') return str;
  if (!str) return false;
  switch (str.toLowerCase().trim()) {
    case "true":
    case "yes":
    case "1":
      return true;

    case "false":
    case "no":
    case "0":
    case null:
    case undefined:
      return false;

    default:
      return JSON.parse(str);
  }

}
// unescape from tom-select escape_html
function unescape_html(str) {
  return (str + '')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"');
}

function decode_HTMLEntities(text) {
  const area = document.createElement('textarea');
  area.innerHTML = text;
  return area.value;
}

function format_license(data, withlink = false) {
  const tbcell = {
    "CC0 1.0": ["ca", "https://creativecommons.org/publicdomain/zero/1.0/"],
    "CC BY 4.0": ["cb", "https://creativecommons.org/licenses/by/4.0/"],
    "CC BY-NC 4.0": ["cbn", "https://creativecommons.org/licenses/by-nc/4.0/"]
  }

  if (tbcell[data]) {
    if (withlink) return `<a href="${tbcell[data][1]}" target="creative-commons" class="relative"><span class="cc" data-title="${data}">${tbcell[data][0]}</span></a>`;
    else return `<span class="cc" data-title="${data}">${tbcell[data][0]}</span>`;
  } else {
    switch (data) {
      case "Copyright":
        return `<span class="txcc"  data-title="${data}">©</span>`;
      case "not chosen":
      default:
        return `<span data-title="${data}"></span>`;
    }

  }

}
function download_blob(data, filename, mimetype) {
  let blob, url;
  if (!Array.isArray(data)) data = [data];
  blob = new Blob(data, {
    type: mimetype
  });
  url = window.URL.createObjectURL(blob);
  console.log('downlad', filename)
  download_url(url, filename);
  setTimeout(() => {
    return window.URL.revokeObjectURL(url);
  }, 1000);
}

function download_url(data, filename, hide = false) {
  const a = document.createElement('a');
  a.href = data;
  a.innerHTML = 'downloadfilezip';
  a.download = filename;
  document.body.appendChild(a);
  if (hide) a.classList.add('hidden');
  a.click();
  //  a.remove();
}

function format_bytes(bytes, decimals = 2) {
  if (!+bytes) return '0 Bytes';
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
}

function is_object(obj) {
  return (!Array.isArray(obj) && typeof obj === 'object' && obj !== null);

}

function input_read_only(item) {
  item.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopImmediatePropagation();
    return false;
  });
}

function create_box(tag, attrs, parent = null, sep = ``) {
  let el = document.createElement(tag);

  Object.entries(attrs).forEach(([attr, value]) => {
    switch (attr) {
      case 'dataset':
        Object.entries(value).forEach(([k, v]) => {
          el.dataset[k] = v;
        });
        break;
      case 'text':
        el.textContent = DOMPurify.sanitize(value);
        break;
      case 'class':
        if (Array.isArray(value)) {
          value.forEach(cl => {
            el.classList.add(cl);
          })
        } else {
          el.classList.add(value);
        }
        break;
      default:
        el.setAttribute(attr, value);
        break;
    }
  });
  if (parent !== null) {
    sep = (parent.children.length) ? sep : null;
    parent.append(el);
    if (sep) parent.insertBefore(document.createTextNode(sep), el);
  }
  return el;
}

function dom_purify(item, type = null) {

  switch (type) {
    case 'dataset':
      Object.entries(item.dataset).forEach(([k, v]) => {
        item.dataset[k] = v;
      });
      break;
    case 'json':
      break;
    default:
      return DOMPurify.sanitize(item);
      break;
  }

}

function html_spinner(addons = 'text-white', size = 'h-5 w-5') {
  return `<svg class="animate-spin  ${size} ${addons}" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>`
}

function stop_on_error(message, callback = null) {
  if (callback) callback;
  throw new Error(message);
}

export {
  generate_uuid,
  fetchSettings,
  unescape_html,
  format_license,
  download_blob,
  download_url,
  string_to_boolean,
  is_object,
  input_read_only,
  dom_purify,
  create_box,
  decode_HTMLEntities,
  html_spinner,
  format_bytes,
  stop_on_error,
  dirseparator,
  urlseparator,
  set_cursor_editable
}