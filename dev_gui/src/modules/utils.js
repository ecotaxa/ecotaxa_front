function fetchSettings(options) {
  options = options || {};
  options.headers = options.headers || {};
  options.headers['X-Requested-With'] = 'XMLHttpRequest';
  if (!options.credentials) options.credentials = 'same-origin';
  return options;

}

function class_name(selector) {
  return selector.replace('.', '').replace('#', '');
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
      case "not choosen":
      default:
        return `<span data-title="${data}"></span>`;
        break;
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
};

function download_url(data, filename, hide = false) {
  const a = document.createElement('a');
  a.href = data;
  a.innerHTML = 'downloadfilezip';
  a.download = filename;
  document.body.appendChild(a);
  //if (hide) a.classList.add('hidden');
  a.click();
  //  a.remove();
};

/* debounce */
function debounce(func, wait, immediate) {
  var timeout;
  return function() {
    var context = this,
      args = arguments;
    var later = function() {
      timeout = null;
      if (!immediate) func.apply(context, args);
    };
    var callNow = immediate && !timeout;
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
    if (callNow) func.apply(context, args);
  };
};

function is_object(obj) {
  return (!Array.isArray(obj) && typeof obj === 'object' && obj !== null);

}

function toCamelCase(str) {
  return str.toLowerCase()
    .trim()
    .split(/[ -_]/g)
    .map(word => word.replace(word[0], word[0].toString().toUpperCase()))
    .join('')
}
export {
  fetchSettings,
  unescape_html,
  class_name,
  format_license,
  download_blob,
  download_url,
  string_to_boolean,
  is_object,
  debounce
}