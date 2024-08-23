import DOMPurify from 'dompurify';
import equal from 'deep-equal';
import {
  fetchSettings,
  download_url,
  string_to_boolean,
  sort_items,
  is_object,
  html_spinner
} from '../modules/utils.js';
import debounce from 'debounce';
import {
  EventEmitter
} from '../modules/event-emitter.js';
import {
  css,
  models,
  domselectors,
  default_messages
} from '../modules/modules-config.js';
let instance = [];
// valid fetch urlparts
const fetchfroms = {
  collectionlist: '/gui/collectionlist/',
  prjlist: '/gui/prjlist/',
  prjsamplestats: '/gui/prjsamplestats',
  userslist: '/gui/admin/userslist/',
  prjpredict: '/gui/prjsforprediction/'
};
// specifc css
const tablecss = {
  showfull: 'showfull',
  tipinline: "tip-inline",
  searchresults: "search-results",
  selectaction: "selectaction",
  absinput: 'absinput',
  disabled: 'table-disabled',
  ascending: 'table-ascending',
  descending: 'table-descending',
  tipover: 'tipover absolute z-10 text-stone-50 rounded bg-stone-600 px-2 py-0.5 -mt-5 ml-12 ',
  hide: 'hide',
  nowrap: 'truncate',
  buttonexpand: 'button-expand',
  bordert: 'border-t',
  borderb: 'border-b',
  maxtabstath: 'max-tabstat-h',
  overflowyhidden: 'overflow-y-hidden',
  icochevrondown: 'icon-chevron-down',
  iconchevronup: 'icon-chevron-up',
  pointer: 'cursor-pointer',
  hidden: 'hidden',
};
const tableselectors = {
  table: '.table-table',
  wrapper: '.table-wrapper',
  top: '.table-top',
  input: '.table-input',
  search: '.table-search',
  export: '.button-export',
  filters: '.table-filters',
  sorter: '.table-sorter',
  details: 'details[data-what="about"]',
  tip: '.' + css.component.table.tip,
  tipover: '.tipover',
  wait: 'wait-please',
  sorton: '.sorton',
};

Object.freeze(tablecss);
Object.freeze(tableselectors);
const dynamics = {};

export class TableComponent {
  instanceid = null;
  grid = {
    columns: [],
    active: [],
    hidden: [],
    data: []
  };
  domdef = {
    columns: [],
    data: [],
  };
  wrapper = null;
  dom = null;
  params = null;
  _events = {};
  eventnames = {
    init: "table.init",
    update: "table.update",
    refresh: "table.refresh",
    resize: "table.resize",
    search: "table.search",
    searchend: "table.searchend",
    sorting: "table.sorting",
    sorted: "table.sorted",
    load: "table.loaded",
    dismiss: 'table.dismiss'
  }
  labels = {
    placeholder: "Search...",
    perPage: "{select} entries per page",
    noRows: "No entries found",
    info: "Showing {start} to {end} of {rows} entries",
    noResults: "No result match your search query"
  };
  cellidname = "id";
  searching = false;
  sorting = false;
  initialized = false;
  plugins = {};
  constructor(container, options = {}) {
    if (!container) return;
    container = container instanceof HTMLElement ? container : document.querySelector(container);
    if (!container) return;
    //can select multiples tables in one page  or load data in the same table
    this.instanceid = (container.dataset.instanceid) ? container.dataset.instanceid : document.querySelectorAll('table').length;
    if (!instance[this.instanceid] || !equal(container.dataset, instance[this.instanceid].params)) {
      this.init(container);
    } else this.refresh();
    return instance[this.instanceid];

  }
  init(container) {
    this.eventEmitter = new EventEmitter();
    this.params = container.dataset;
    let table = container.querySelector('table');
    if (!table) {
      table = document.createElement('table');
      container.appendChild(table);
    }
    table.id = 'table-' + container.id;
    table.classList.add(tableselectors.table.substr(1))
    this.dom = table;
    let top = {
      nodename: "DIV",
      attributes: {
        class: tableselectors.top.substr(1)
      }
    };
    if (this.params.searchable) top.childnodes = [{
      nodename: "DIV",
      attributes: {
        class: tableselectors.search.substr(1)
      },
      html: `<input type="search" name="table-search" placeholder="${this.labels.placeholder}" class="${tableselectors.input.substr(1)}  ${css.input}" hidden="">`
    }];
    let wrapper = this.objToElement({
      nodename: 'DIV',
      attributes: {
        class: tableselectors.wrapper.substr(1)
      },
      childnodes: [top]
    });
    container.appendChild(wrapper);
    wrapper.appendChild(table);
    this.wrapper = wrapper;

    this.labels = (this.params.labels) ? this.params.labels : this.labels;
    // cellid
    this.cellidname = (this.params.hasOwnProperty("cellid")) ? this.params.cellid : this.cellidname;
    // only valid from values - fetchfroms
    this.params.from = (this.params.from) ? DOMPurify.sanitize(this.params.from) : null;

    const from = (this.params.from) ? ((Object.keys(fetchfroms).indexOf(this.params.from) >= 0) ? fetchfroms[this.params.from] : null) : null;
    if (from) {
      if (this.params.defer) this.deferLoad(container, from);
      else this.fetchData(container, from);
    } else this.tableActivate(container);
    this.dt = Date.now();
  }

  waitActivate(container) {
    let waitdiv = container.querySelector('#' + tableselectors.wait);
    if (!waitdiv) {
      waitdiv = document.createElement('div');
      waitdiv.id = tableselectors.wait;
      container.append(waitdiv);
    }
    this.waitdiv = waitdiv;
  }

  waitDeactivate(message = null, type = 'info') {
    if (!this.waitdiv) return;
    if (message) {
      this.waitdiv.classList.remove(css.hide);
      if (type === null) this.waitdiv.innerHTML = `${message}`;
      this.waitdiv.innerHTML = `<div class="alert is-${type}">${message}</div>`;
    } else this.waitdiv.classList.add(css.hide);
  }

  deferLoad(container, from) {
    const btn = container.querySelector(this.params.defer);
    if (!btn) return;

    btn.addEventListener('click', (e) => {
      this.fetchData(container, from);
      btn.remove();
    });
  }

  fetchData(container, fromurl, pagestart = 0) {
    this.waitActivate(container);
    const pagesize = (this.params.pagesize) ? this.params.pagesize : 0;
    let from = fromurl;
    if (this.params.fromid) from += '/' + this.params.fromid;

    let query = (this.params.import) ? {
      typeimport: DOMPurify.sanitize(this.params.import),
      window_start: pagestart,
      window_size: pagesize,
      gz: true,
    } : ((pagesize) ? {
      window_start: pagestart,
      window_size: pagesize,
      listall: ((this.params.listall) ? this.params.listall : false)
    } : ((this.params.listall) ? {
      listall: ((this.params.listall) ? this.params.listall : false)
    } : {}));
    const queryparams = new URLSearchParams(window.location.search);
    const querykeys = this.cellidname + 's';
    if (querykeys.length) {
      for (const entry of queryparams.entries()) {
        if (querykeys.indexOf(entry[0]) >= 0) query[entry[0]] = entry[1];
      }
    }
    if (Object.keys(query).length) from += '?' + new URLSearchParams(query);
    this.dt = Date.now();
    fetch(from, fetchSettings()).then(response => {
      if (response.ok) return response.json();
      else return Promise.reject(response);
    }).then(async tabledef => {
      if (this.waitdiv) this.waitdiv.innerHTML = ((this.waitdiv.dataset.loaded) ? DOMPurify.sanitize(this.waitdiv.dataset.loaded) : default_messages.dataloaded);
      if (pagestart === 0) {
        let now = Date.now();
        console.log('seconds to fetch', (Date.now() - this.dt) / 1000);
        this.dt = now;
        await this.tableActivate(container, tabledef);
        now = Date.now();
        console.log('plugins loaded', (Date.now() - this.dt) / 1000);
        this.dt = now;
      } else if (tabledef.length) this.domInsertRows(tabledef);
      else pagesize = 0;
      if (pagesize > 0) this.fetchData(container, fromurl, pagestart + pagesize);
    }).catch((err) => { /* print error from response */
      console.log('error', err)
      this.waitDeactivate(err.status + ` ` + err.statusText, 'error');
    })
  }
  async dataToTable(tabledef) {

    if (!tabledef.data) return;
    if (tabledef.columns) {
      await this.convertColumns(tabledef);
      let tr;
      let thead = this.dom.tHead;
      if (!thead) {
        // create table headings
        thead = document.createElement('thead');
        tr = document.createElement('tr');
        this.dom.appendChild(thead);
      } else if (!thead.querySelector('tr')) {
        tr = document.createElement('tr');

      } else {
        tr = thead.querySelector('tr');
        tr.innerHTML = ``;
      }
      let tbody = (this.dom.tBodies.length) ? this.dom.tBodies[0] : null;
      if (!tbody) {
        tbody = document.createElement('tbody');
        this.dom.appendChild(tbody);
      }
      const isjson = (!tabledef.hasOwnProperty('data') || (tabledef.hasOwnProperty('type') && tabledef.type === "json"));

      this.grid.columns.forEach((column, index) => {

        if (!column.hidden) {
          const th = document.createElement('th');
          th.innerHTML = DOMPurify.sanitize(column.label);
          if (column.sort) th.dataset.sort = column.sort;
          if (column.format) th.dataset.type = column.type;
          if (column.name) th.dataset.name = column.name;
          // TODO - find a place to define col import props
          // set headings dataset values for import module
          if (this.params.import)['selectcells', 'what', 'autocomplete', 'parts', 'value'].forEach(prop => {
            if (column.hasOwnProperty(prop)) th.dataset[prop] = column[prop];
          });
          th.dataset.sortable = (column.sortable) ? true : false;
          tr.appendChild(th);
          this.grid.active.push(index);
        } else this.grid.hidden.push(index);

      });


      thead.appendChild(tr);
      const datalastused = (this.params.lastused && this.params.lastused.length > 0) ? [] : null;
      //#TODO lastused reorder
      if (isjson) {
        this.grid.data = [];
        tabledef.data.forEach((data, i) => {
          const row = [];
          let j = 0;
          Object.entries(tabledef.columns).forEach(([key, column], i) => {
            if (!column.hasOwnProperty('emptydata')) {
              if (data.hasOwnProperty(key)) row[j] = data[key];
              else if (column.field && data.hasOwnProperty(column.field)) row[j] = data[column.field];
              else row[j] = null;
              j++;
            }
          });
          this.grid.data.push(row);
        });
      } else this.grid.data = tabledef.data;

      const tfoot = this.dom.tFoot;
      if (this.grid.active.length === 0) {
        tbody.innerHTML = `<tr><td>${this.labels.noRows}</td</tr>`;
        if (tfoot) tfoot.remove();
        return;
      } else if (tfoot && tfoot.querySelector('tr')) {
        const tf = tfoot.querySelector('tr').childNodes;
        this.grid.hidden.forEach(i => {
          tf[i].remove();
        });
      };

      this.renderTbody(tbody);
    }
  }

  tableToData() {
    if (!this.dom.querySelector('thead')) return;
    const datalastused = (this.params.lastused && this.params.lastused.length > 0) ? [] : null;
    this.dom.classList.add(css.hide);
    const cell_to_obj = (cell) => {
      const celltext = cell.innerText;
      const obj = {
        data: celltext,
      }
      const cellhtml = cell.innerHTML;
      if (celltext !== cellhtml) obj.html = cellhtml;
      return obj;
    }
    const ths = (this.dom.querySelectorAll('thead tr th').length) ? this.dom.querySelectorAll('thead tr th') : this.dom.querySelectorAll('thead tr td');
    const trs = this.dom.querySelectorAll('tbody tr');
    let active = 0,
      hidden = 0;

    function find_label(th) {
      if (th.childNodes.length) return find_label(th.childNodes[0]);
      else return th.innerText;
    }
    ths.forEach((th, index) => {
      const col = Object.assign({}, th.dataset);
      if (col.mask) th.classList.add(tablecss.hidden);
      if (col.hidden && string_to_boolean(col.hidden)) {
        col.hidden = true;
        th.remove();
      }
      col.label = find_label(th);
      if (col.type) {
        col.format = col.type;
        delete col.type;
      }
      col.index = index;
      if (col.hidden) this.grid.hidden.push(index);
      else this.grid.active.push(index);
      this.grid.columns.push(col);
    });
    const cellid = this.getCellId(this.cellidname);
    trs.forEach((tr, i) => {
      if (cellid < 0) tr.dataset[this.cellidname] = i;
      else if (i === cellid) tr.dataset[this.cellidname] = this.getCellData(i, this.cellidname, cellid);
      const data = [];
      tr.querySelectorAll('th,td').forEach((td, index) => {
        if (this.grid.columns[index].hasOwnProperty('mask')) td.classList.add(tablecss.hidden);
        if (this.grid.hidden.indexOf(index) >= 0) td.remove();
        data.push(td.innerText);
      });
      this.grid.data.push(data)
    });

    this.dom.querySelectorAll('tfoot tr th').forEach((td, index) => {
      if (this.grid.columns[index].hasOwnProperty('mask')) td.classList.add(tablecss.hidden);
      if (this.grid.hidden.indexOf(index) >= 0) td.remove();
    });
    this.dom.classList.remove(css.hide);
    return;
  }
  renderTbody(tbody) {
    const l = this.grid.data.length;
    for (let i = 0; i < l; i++) {
      const tr = this.createTableRow(this.grid.data[i], i);
      tbody.append(tr);
    };



  }
  async tableActivate(container, tabledef = null) {
    this.eventEmitter.on(this.eventnames.load, () => {
      this.initPlugins(container);
      this.initSearch();
      this.initSort();
      this.waitDeactivate();
      // hide and move waitdiv in the wrapper for inner elements display
      this.dom.classList.remove(css.hide);
      if (this.afterLoad) this.afterLoad();
      // move import zones and/or search zone - reorg the page display
      // fetch once the same table
      container.dataset.table = this.params.table = true;
      this.initialized = true;
    });
    // dismiss table when dismiss modal
    this.eventEmitter.on(this.eventnames.dismiss, (e) => {
      this.destroy();
    });

    if (tabledef) tabledef = await this.dataToTable(tabledef);
    else await this.tableToData();
    if (this.grid.data.length) this.eventEmitter.emit(this.eventnames.load);
    instance[this.instanceid] = this;
  }

  tableAppendRows(rows) {
    console.log('rows');
  }
  destroy() {
    if (this.dataImport) this.dataImport = null;
    this.dom = null;
    delete instance[this.instanceid];
  }
  refresh(e) {
    if (this.dataImport && this.dataImport.selectors) this.dataImport.selectors.forEach(selector => {
      if (this.disabled) this.disabled = false;
    });
  }
  labelFormatter(column) {
    let align = ``;
    if (['number', 'progress', 'decimal'].find(format => format === column.format)) align = css.right;
    if (column.subfield) return `${column.label} <span class="sublabel">${column.sublabel}</span>`;
    else if (column.label) return `<span class="${align}">${column.label}</span>`;
    else return ``;
  }
  getCellId(name, state = null) {
    let cols = this.grid.columns.filter(column => (column.name === name));
    return (cols.length) ? cols[0].index : -1;
  }

  getCellData(rowIndex, name, cellIndex = null) {
    cellIndex = (cellIndex === null) ? this.getCellId(name) : cellIndex;
    if (cellIndex < 0) return null;
    return (this.grid.data.length) ? ((this.grid.data[rowIndex]) ? this.grid.data[rowIndex][cellIndex] : null) : null;
  }

  rowAttributes(tr, index) {
    const id = this.getCellData(index, this.cellidname);
    tr.dataset[this.cellidname] = id;
    if (this.setRowAttributes) tr = this.setRowAttributes(this, tr, id);
    return tr;
  }

  createTableRow(row, index, isheader = false) {
    const tr = document.createElement('tr');
    let td;
    this.grid.columns.forEach(column => {
      if (column.hasOwnProperty('hidden') && column.hidden === true) return;
      const cell = row[column.index];
      if (column.hasOwnProperty("render")) {
        td = column.render(cell, index, column.index);
        td.nodename = (isheader) ? 'TH' : 'TD';
        td = this.objToElement(td);
      } else {
        td = (isheader) ? document.createElement('th') : document.createElement('td');
        td.appendChild(document.createTextNode(cell));
      }
      tr.appendChild(td);
    })
    return this.rowAttributes(tr, index);
  }

  objToElement(obj) {
    if (obj.nodename === "#text") return document.createTextNode(obj.data);
    const el = document.createElement(obj.nodename);
    if (obj.hasOwnProperty("html")) el.innerHTML = obj.html;
    else el.textContent = obj.data;
    if (obj.hasOwnProperty("attributes")) {
      for (const attr in obj.attributes) {
        el.setAttribute(attr, obj.attributes[attr]);
      }
    }
    if (obj.hasOwnProperty("childnodes")) {
      obj.childnodes.forEach(childnode => {

        el.appendChild(this.objToElement(childnode));
      });

    }
    return el;
  }

  setTextNode(value) {
    return {
      nodename: "#text",
      data: value
    };
  }
  async getFormatters() {
    let formatters = {
      controls: (value, rowIndex, cellIndex, td = {}) => {
        const column = this.grid.columns[cellIndex];
        const id = this.getCellData(rowIndex, column.field);
        const actions = (column.actions) ? column.actions : null;
        if (!actions) return ``;
        let controls = [];
        Object.entries(actions).forEach(([key, action]) => {
          controls.push({
            nodename: "A",
            attributes: {
              class: `btn is-${key} `,
              href: `${action.link}${id}`
            },
            childnodes: [this.setTextNode(action.label)]
          });

        });
        if (!td.hasOwnProperty('attributes')) td.attributes = {};
        td.attributes.class = css.component.table.controls;
        td.childnodes = controls;
        return td;
      },
      select: (value, rowIndex, cellIndex, td = {}) => {
        const column = this.grid.columns[cellIndex];
        value = (isNaN(value)) ? this.getCellData(rowIndex, column.field) : value;

        td.childnodes = [{
          nodename: "INPUT",
          attributes: {
            type: "radio",
            name: `${this.instanceid}select`,
            value: String(value)
          }
        }];
        return td;
      },
      selectmultiple: (value, rowIndex, cellIndex, td = {}) => {
        const column = this.grid.columns[cellIndex];
        value = (isNaN(value)) ? ((column.hasOwnProperty('field')) ? this.getCellData(rowIndex, column.field) : value) : value;
        td.childnodes = [{
          nodename: "INPUT",
          attributes: {
            type: "checkbox",
            name: `${this.instanceid}select[]`,
            value: String(value)
          }
        }];
        return td;
      },
      decimal: (value, rowIndex, cellIndex, td = {}) => {
        if (isNaN(value)) value = 0;
        value = parseFloat(value).toFixed(2);
        if (value - parseInt(value) === 0) value = parseInt(value);
        if (!td.hasOwnProperty('attributes')) td.attributes = {};
        td.attributes.class = css.number;
        td.childnodes = [this.setTextNode(value)];
        return td;
      },
      number: (value, rowIndex, cellIndex, td = {}) => {
        if (isNaN(value)) value = 0;
        if (!td.hasOwnProperty('attributes')) td.attributes = {};
        td.attributes.class = css.number;
        td.childnodes = [this.setTextNode(value)];
        return td;
      },
      check: (value, rowIndex, cellIndex, td = {}) => {
        if (isNaN(value)) value = ``;
        switch (value) {
          case true:
          case 'Y':
          case 1:
            value = "";
            break;
          default:
            value = "no-";
            break;
        }
        const icon = {
          nodename: "I",
          attributes: {
            class: `icon-sm  icon-${value}check `
          },
          childnodes: []
        }
        const column = this.grid.columns[cellIndex];
        const id = this.getCellData(rowIndex, this.cellidname);
        if (column.hasOwnProperty("toggle")) td.childnodes = [{
          nodename: "A",
          attributes: {
            "data-request": "toggle",
            "data-action": `${column.toggle.link}/${id}`,
            "href": "javascript:void()"

          },
          childnodes: [icon]

        }]
        else td.childnodes = [icon];
        return td;
      },
      text: (value, rowIndex, cellIndex, td = {}) => {
        if (value === null) td.childnodes = [];
        else {
          value = value.replaceAll('\r\n', ', ');
          if (value !== ``) td.childnodes = [{
            nodename: "DIV",
            attributes: {
              class: css.component.table.tip
            },
            childnodes: [this.setTextNode(value)]
          }];
          else td.childnodes = [];
        }
        return td;
      },
      default: (value, rowIndex, cellIndex, td = {}) => {
        if (value === null || value === ``) td.childnodes = [];
        else td.childnodes = [this.setTextNode(value)];
        return td;
      }

    }
    let tablecustom = null;

    switch (this.params.from) {
      case 'collectionlist':
        tablecustom = await import('../modules/table-collection.js');
        this.cellidname = models.id;
        break;
      case 'prjlist':
        tablecustom = await import('../modules/table-project.js');
        this.cellidname = models.projid;
        break;
      case 'prjsamplestats':
        tablecustom = await import('../modules/table-sample.js');
        this.cellidname = models.sampleid;
        break;
      case "prjpredict":
        tablecustom = await import('../modules/table-prediction.js');
        this.cellidname = models.projid;

        break;
    }

    return (tablecustom) ? { ...formatters,
      ...tablecustom.default(this)
    } : formatters;


  }
  async convertColumns(tabledef) {
    const columns = (tabledef.columns) ? tabledef.columns : ((this.params.columns) ? JSON.parse(this.params.columns) : null);
    if (!columns) return;
    const formatters = await this.getFormatters();
    //
    const fields = [];
    Object.entries(tabledef.columns).forEach(([key, column]) => {
      if (!column.hasOwnProperty('emptydata')) fields.push(key);
    });
    const map_column = (key, column, index) => {
      if (!column) return {
        index: index,
        name: key,
        hidden: true
      };
      let col = {
        index: index,
        name: key,
        label: this.labelFormatter(column),
        sortable: true,

      };
      col.index = (column.hasOwnProperty('emptydata')) ? fields.indexOf(column.emptydata) : fields.indexOf(key);
      if (column.notsortable) col.sortable = false;
      else if (column.sortable) col.sort = col.sortable;
      col.searchable = (col.notsearchable) ? false : true;
      if (column.hidden) col.hidden = string_to_boolean(column.hidden);
      if (['number', 'decimal'].find(format => format === column.format)) col.type = 'number';
      let render = null;
      switch (key) {
        case 'select':
          const select = (column.select && column.select == "controls") ? "controls" : ((column.selectcells) ? "imports" : column.select);
          if (select) {
            col = { ...column,
              ...col
            }

            col.sortable = col.searchable = false;
          }
          break;
      }
      if (!column.hasOwnProperty('hidden')) {
        const select = (column.select && column.select == models.controls) ? models.controls : ((column.selectcells) ? models.imports : column.select)
        const format = (column.format) ? column.format : ((column.subfield) ? column.subfield : ((select) ? select : "default"));
        if (formatters && formatters[format]) col.render = formatters[format];

      }
      return col;
    }

    this.grid.columns = Object.entries(columns).map(([key, column], index) => map_column(key, column, index));
  }
  initEvents() {
    this.eventEmitter.on(this.eventnames.update, () => {
      this.dom.classList.remove(css.hide);
    });
  }
  initPlugins(container) {
    if (!this.grid.data.length) return;
    if (this.params.import && this.initImport) this.initImport(this);
    if (this.params.expand) this.makeExpandable(container);
    if (this.params.export) this.makeExportable(container);
    if (this.params.details || this.dom.querySelector(tableselectors.details)) {
      this.initDetails();
    } else this.initEvents();
    if (this.params.onselect) this.initSelect(container);
    if (this.dom.querySelectorAll('thead [data-altsort]').length) this.initAlternateSort(this.dom.querySelectorAll('thead [data-altsort]'));
    if (this.params.filters) {
      const top = this.wrapper.querySelector(tableselectors.top);
      if (top && top.children.length) {
        const filters = document.querySelector(tableselectors.filters);
        // insert  filters node  in datatable top
        if (filters) top.prepend(filters);
      }
    }
    if (this.dom.querySelector(tableselectors.tip)) {
      this.initTips();
    }

  }
  initSort() {

    const ths = this.dom.querySelectorAll('thead th');
    let index = 0;
    this.grid.columns.forEach((column, i) => {
      if (column.hasOwnProperty('hidden')) return;
      if (column.sortable) {
        const th = ths[index];
        const a = document.createElement('a');
        a.classList.add(tableselectors.sorter.substr(1));
        a.appendChild(th.childNodes[0]);
        th.appendChild(a);
        th.childNodes.forEach(child => {
          th.appendChild(child);
        });

        a.addEventListener('click', (e) => {
          e.stopImmediatePropagation();
          if (this.sorting === true || this.searching === true) {
            e.preventDefault();
            return false;
          }
          this.sortColumn(th, column.index);
        });
      }
      index++;
    });
    this.sorting = false;
    // remove details when sorting
    this.eventEmitter.on(this.eventnames.sorting, (direction, index) => {

      if (this.plugins.hasOwnProperty('jsDetail')) this.plugins['jsDetail'].activeDetail(false);
      this.dom.querySelectorAll('.table-sorter').forEach((a, i) => {
        a.classList.add(((i === index) ? css.wait : css.disabled));
      });
      this.sorting = true;
    });
    // remove details when sorting
    this.eventEmitter.on(this.eventnames.sorted, (direction, index) => {
      this.dom.querySelectorAll('.table-sorter').forEach((a, i) => {
        a.classList.remove(((i === index) ? css.wait : css.disabled))
      });
      this.sorting = false;
    });
  }
  sortColumn(th, index, dir = null) {
    dir = (dir === null) ? ((th.classList.contains(tablecss.ascending)) ? false : (th.classList.contains(tablecss.descending)) ? true : ((th.dataset.sort) ? false : true)) : dir;
    th.classList.toggle(tablecss.ascending);
    th.classList.toggle(tablecss.descending);
    this.eventEmitter.emit(this.eventnames.sorting, dir, th.cellIndex);
    let rows = this.grid.data.map((row, i) => {
      const cell = is_object(row[index]) ? JSON.stringify(row[index]) : ((Array.isArray(row[index])) ? row[index][0] : row[index]);
      return {
        value: typeof cell === "string" ? cell.toLowerCase() : ((cell === null) ? 0 : cell),
        row: i
      }
    });

    const compare_coldata = function(a, b) {
      const x = (dir ? a.value : b.value);
      const y = (dir ? b.value : a.value);
      return x.localeCompare(y, undefined, {
        numeric: true,
        sensitivity: 'base'
      });

    };

    if (dir === false) {
      th.classList.remove(tablecss.ascending);
      th.classList.add(tablecss.descending);
      th.setAttribute("aria-sort", "descending");
    } else {
      th.classList.remove(tablecss.descending);
      th.classList.add(tablecss.ascending);
      th.setAttribute("aria-sort", "ascending");
    }

    /* Clear asc/desc class names from the last sorted column's th if it isn't the same as the one that was just clicked */
    if (this.dom.dataset.lastth !== undefined && th.cellIndex != this.dom.dataset.lastth) {
      const headings = this.dom.querySelectorAll("thead th");
      headings[this.dom.dataset.lastth].classList.remove(tablecss.descending);
      headings[this.dom.dataset.lastth].classList.remove(tablecss.ascending);
      headings[this.dom.dataset.lastth].removeAttribute("aria-sort");

    }
    this.dom.dataset.lastth = th.cellIndex;
    const collator = new Intl.Collator(undefined, {
      numeric: true,
      sensitivity: 'base'
    })
    rows.sort((a, b) => {
      return collator.compare((dir ? a.value : b.value), (dir ? b.value : a.value))
    });
    /*rows.sort((a, b) => {
      return compare_coldata(a, b);
    });*/
    const tbody = this.dom.querySelector('tbody');
    const clone = tbody.cloneNode();
    const trs = tbody.querySelectorAll('tr');
    tbody.innerHTML = ``;
    const sorted = [];
    rows.forEach((r, i) => {
      clone.appendChild(trs[r.row]);
      sorted.push(this.grid.data[r.row]);

    });
    this.grid.data = sorted;
    this.dom.replaceChild(clone, tbody);

    this.eventEmitter.emit(this.eventnames.sorted, dir, th.cellIndex);


  }


  tableSearch(searchstring, casesensitive = false) {
    function search_string(str, casesensitive) {
      str = (casesensitive) ? str : str.toLowerCase();
      return str;
    }

    function search_queries(str, casesensitive) {
      str = search_string(str, casesensitive);
      let strs = [];
      let phrase;
      while ((phrase = str.match(/"([^"]+)"/)) !== null) {

        strs.push(phrase[1]);
        str = str.substring(0, phrase.index) + str.substring(phrase.index + phrase[0].length);
      }
      // Get remaining space-separated words (if any)
      str = str.trim();
      if (str.length) strs = strs.concat(str.split(/\s+/));
      return strs;
    }
    const queries = search_queries(searchstring);
    this.eventEmitter.emit(this.eventnames.search, searchstring, queries);
    let datas = this.grid.data,
      indexes = [];
    const cellid = this.getCellId(this.cellidname);
    queries.forEach(qry => {
      indexes = [];
      datas = datas.filter((data, j) => {
        const found = data.filter(cell => {
          switch (typeof cell) {
            case 'object':
              cell = (cell) ? cell : ``;
              try {
                cell = JSON.stringify(cell);
              } catch (err) {
                console.log('search', err);
                cell = ``;
              }
              break;
            case 'array':
              cell = cell.join(' ');
              break;
            default:
              cell = String(cell);
              break;
          }

          return ((casesensitive) ? cell.indexOf(qry) > -1 : cell.toLowerCase().indexOf(qry)) > -1;
        });

        if (found.length > 0) {
          if (cellid < 0) indexes.push(String(j));
          else indexes.push(String(data[cellid]));
          return data;
        }
      });
    });
    this.eventEmitter.emit(this.eventnames.searchend, queries, indexes, cellid);
  }

  initSearch() {
    if (this.grid.data.length < 10) return this.toggleAddOns();
    else this.toggleAddOns([tableselectors.search + ' input'], true);
    this.searching = false;
    // search items
    const searchinput = this.wrapper.querySelector(tableselectors.search + ' input');
    if (!searchinput) return;
    let searchstring = ``;
    const display_search = debounce(function(queries, indexes, table, cellidname, cellid) {
      const trs = table.querySelectorAll('tbody tr');
      trs.forEach((tr, index) => {
        const val = (tr.dataset[cellidname] !== null) ? tr.dataset[cellidname] : tr.cells[cellid].textContent;
        if ((queries.length > 0 && indexes.length === 0) || indexes.indexOf(val) < 0) tr.hidden = true;
        else tr.hidden = false;
      });
    }, 50);
    const clear_search = function(table) {
      const trs = table.querySelectorAll('tbody tr[hidden=""]');
      trs.forEach(tr => {
        tr.hidden = false;
      });
    }
    const search_terms = debounce((value) => {
      this.tableSearch(value);
    }, 300);
    searchinput.addEventListener("input", (e) => {
      const value = e.target.value;
      if (value !== searchstring) {
        searchstring = value;
        if (value === '') {
          search_terms.clear();
          clear_search(this.dom);
        } else if (value.length > 2) {
          search_terms(value);
        }
      }
    });
    searchinput.addEventListener("click", (e) => {
      if (e.target.value !== searchstring) {
        search_terms(e.target, this.dom);
        search_terms.clear();
      } else search_terms.flush();

    });
    this.eventEmitter.on(this.eventnames.search, (searchstring, queries) => {
      if (this.searching === false) {
        if (this.plugins.hasOwnProperty('jsDetail')) this.plugins['jsDetail'].activeDetail(false);
      }
      this.searching = true;
    });
    this.eventEmitter.on(this.eventnames.searchend, (queries, indexes, cellid) => {
      display_search(queries, indexes, this.dom, this.cellidname, cellid);
      this.searching = false;
    });
    this.eventEmitter.on(this.eventnames.update, () => {
      if (this.searching === false) {
        setTimeout(() => {
          refresh_details();
        }, 300);
      }
    });
    searchinput.classList.remove(css.hide);
  }
  initSelect(container) {
    const inputs = this.dom.querySelectorAll('input[name^="' + this.instanceid + '"]');
    if (inputs.length === 0) return;
    const inputname = inputs[0].name;
    let selectaction = container.querySelector('.' + tablecss.selectaction);
    if (!selectaction) return;
    document.body.append(selectaction);
    selectaction.querySelector('a').addEventListener('click', (e) => {
      let vals = [];
      inputs.forEach(input => {
        if (input.checked) vals.push(input.value);
      });
      if (selectaction.dataset.input) {
        document.getElementById(selectaction.dataset.input).value = vals.join(',');
        if (selectaction.dataset.form) document.getElementById(selectaction.dataset.form).submit();
      } else e.currentTarget.href = this.params.onselect + encodeURI(vals.join(','));

    });
    const close = selectaction.querySelector('[data-dismiss]');
    if (close) close.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopImmediatePropagation();
      popup_selected(null, null);
    });

    const popup_selected = (top = null, left = null, forceclose = false) => {
      if (selectaction.dataset.close) {
        document.body.append(selectaction);
        close.classList.remove(tablecss.hidden);
        selectaction.classList.add(tablecss.absinput);
      }
      if (top !== null && left !== null) {
        selectaction.classList.remove(css.hide);
        selectaction.style.top = top + 'px';
        selectaction.style.left = left + 'px';

      } else {
        if (forceclose === true) {
          selectaction.classList.add(css.hide);
          delete selectaction.dataset.close;
        } else {
          selectaction.dataset.close = true;
          close.classList.add(tablecss.hidden);
          const toptable = this.wrapper.querySelector(tableselectors.top) ? this.wrapper.querySelector(tableselectors.top) : this.wrapper;
          toptable.prepend(selectaction);
          selectaction.classList.remove(tablecss.absinput);

        }
      }
    }
    inputs.forEach(input => {
      input.addEventListener('change', (e) => {
        if (input.checked) popup_selected(input.offsetTop, input.offsetLeft);
        else if (this.dom.querySelectorAll('input[name^="' + this.instanceid + '"]:checked').length === 0) popup_selected(null, null, true);
      });
    });
    if (this.dom.querySelectorAll('input[name^="' + this.instanceid + '"]:checked').length > 0) {
      selectaction.classList.remove(css.hide);
      popup_selected(null, null);
    }
  }
  async initDetails() { // TODO : generic
    // about - one div to display cell details make it appear as table row expanding
    const wrapper = this.wrapper;

    const about = wrapper.querySelector('#' + tablecss.tipinline) ? wrapper.querySelector('#' + tablecss.tipinline) : tablecss.tipinline;
    if (!dynamics.JsDetail) {
      const {
        JsDetail
      } = await
      import('../modules/js-detail.js');
      dynamics.JsDetail = JsDetail;
    }
    const jsDetail = new dynamics.JsDetail(about, wrapper, {
      waitdiv: this.waitdiv
    }); // specific to about details in table
    // hide / show disable details zone
    const callbackclose = (el, callback = null) => {
      jsDetail.activeDetail(false);
      if (callback) callback();
    }

    const callbackopen = (el, callback = null) => {
      jsDetail.activeDetail(true);
      if (jsDetail.current && jsDetail.current === el) {
        jsDetail.expandDetail(el);
        if (callback) callback();
      } else {
        if (jsDetail.current) jsDetail.current.querySelector('summary').click();
        const url = this.params.detailsurl + el.dataset.id + '?' +
          new URLSearchParams({
            partial: true
          });
        jsDetail.activeDetail(true);
        // append to cell details and display

        fetch(url, fetchSettings()).then(response => response.text()).then(html => {
          jsDetail.expandDetail(el, html);
          if (callback) callback();
        }).catch(err => {
          console.log('request', err);
        })
      }

    }
    if (!dynamics.JsAccordion) {
      const {
        JsAccordion
      } = await import('../modules/js-accordion.js');
      dynamics.JsAccordion = JsAccordion;
    }

    const refresh_details = () => {
      this.dom.classList.remove(css.hide);
      const details = this.dom.querySelectorAll(tableselectors.details);
      if (!details) return;
      details.forEach(item => {
        if (!item.dataset.id) return;

        item = new dynamics.JsAccordion(item, callbackopen, callbackclose, jsDetail.detail);
      });
    }
    this.plugins['jsDetail'] = jsDetail;
    refresh_details();
  }

  initAlternateSort(cols) {

    let tdcols = [];
    cols.forEach(col => {
      const tdcol = col.closest('th');
      Object.entries(col.dataset).forEach(([k, v]) => {
        tdcol.dataset[k] = v;
        col.classList.add('inline-block')
      });
      tdcols.push(tdcol);
    });
    cols = tdcols;
    // end fix

    let coltosort;
    const sortalternate = (col) => {
      let todir;
      // keep the same dir if sort on col changes
      if (parseInt(col.dataset.sortactive) === parseInt(coltosort)) {
        const asc = col.classList.contains(tablecss.ascending);
        const desc = col.classList.contains(tablecss.descending);
        todir = (asc) ? 'desc' : ((desc) ? 'asc' : 'asc');
      } else todir = (asc) ? 'asc' : (desc) ? 'desc' : 'asc';
      this.sortColumn(col, coltosort, todir);
    }
    cols.forEach(col => {
      const altsort = (col.dataset.altsort) ? col.dataset.altsort.split(',') : null;
      if (!altsort) return;
      const csssorter = col.querySelector(tableselectors.sorter);
      if (csssorter) csssorter.classList.add(tablecss.disabled);
      const control = col.querySelector(tableselectors.sorton);
      // prevents imbricated links
      col.append(control);
      const triggers = col.querySelectorAll('[role="button"]');

      col.addEventListener('click', (e) => {
        e.preventDefault();
        sortalternate(col);
      }, false);
      const changecoltosort = (cl, index) => {
        if (index === 0) coltosort = this.grid.columns.findIndex(column => (column.index === cl.cellIndex));
        else coltosort = this.grid.columns.findIndex(column => (column.name === altsort[index - 1]));
      }
      col.dataset.sortactive = col.cellIndex;
      triggers.forEach((trigger, index) => {
        trigger.addEventListener('click', (e) => {
          e.preventDefault();
          const active = e.currentTarget.parentElement.querySelector('.' + css.active);
          if (active) active.classList.remove(css.active);
          e.currentTarget.classList.add(css.active);
          changecoltosort(col, index);
        });
      });
      if (col.dataset.tip) {

        Object.values(this.dom.rows).forEach((row, index) => {
          if (index === 0) return;
          const coltip = this.grid.columns.findIndex(column => (column.name === altsort[parseInt(col.dataset.tip) - 1]));

          if (row.cells.length === 0 || coltip === col.cellIndex) return;
          row.cells[col.cellIndex].addEventListener('mouseenter', (e) => {

            const tip = document.createElement('div');
            tip.setAttribute('class', tablecss.tipover);
            tip.innerHTML = row.cells[coltip].innerHTML;
            e.currentTarget.append(tip);
          });
          row.cells[col.cellIndex].addEventListener('mouseout', (e) => {
            const tip = e.currentTarget.querySelector(tableselectors.tipover);
            if (tip) tip.remove();
          });
        });
      }
    });
  }

  makeExpandable(container) {
    if (container.querySelector('table').offsetHeight < container.offsetHeight) return;
    const btn = document.createElement('div');
    btn.classList.add(tablecss.buttonexpand);
    btn.classList.add(tablecss.bordert);
    btn.title = this.params.expand;
    btn.innerHTML = `<span class="small-caps block mx-auto p-0">${this.params.expand}</span><i class="clear-both p-0 mx-auto icon icon-chevron-down hover:fill-secondblue-500"></i><span class="small-caps block mx-auto p-0 hidden">${
                  this.params.shrink}</span>`;
    container.parentElement.insertBefore(btn, container.nextElementSibling);
    container.classList.add(tablecss.overflowyhidden);
    container.classList.remove(tablecss.maxtabstath);
    container.parentElement.style.height = 'auto';
    const h = parseInt(this.wrapper.querySelector('tbody tr').offsetHeight) * ((this.params.maxrows) ? this.params.maxrows : 20);
    container.classList.add('max-h-[' + h + 'px]');
    container.style.height = h + 'px';
    btn.addEventListener('click', (e) => {
      const ishidden = container.classList.contains(tablecss.overflowyhidden);
      const make_expand = debounce(() => {
        btn.classList.toggle(tablecss.bordert);
        btn.classList.toggle(tablecss.borderb);
        const ico = btn.querySelector('i');
        ico.classList.toggle(tablecss.icochevrondown);
        ico.classList.toggle(tablecss.iconchevronup);
        container.classList.toggle(tablecss.overflowyhidden);
        container.classList.toggle('max-h-[' + h + 'px]');
        btn.querySelectorAll('span').forEach(span => {
          span.classList.toggle(tablecss.hidden);
        });
        if (ishidden) container.style.height = h + 'px';
        else container.style.height = 'auto';
      }, 100);
      make_expand();
    });
  }
  makeExportable(container) {
    const btn = document.createElement('div');
    btn.classList.add(tableselectors.export.slice(1));
    btn.classList.add('is-pick');
    btn.innerHTML = `<i class="icon icon-arrow-down-on-square"></i><span>${((this.params.exportlabel) ? this.params.exportlabel : 'export statistics ')}</span>`;
    this.wrapper.prepend(btn);
    const columns = this.grid.columns;
    let exclude_columns = [];
    this.grid.columns.forEach((column, index) => {
      if (column.name === 'select') exclude_columns.push(column.index);
    });
    btn.addEventListener('click', async (e) => {
      e.preventDefault();
      if (!this.dynamics) this.dynamics = {};
      if (!this.dynamics.exportCSV) {
        const {
          exportCSV // or exportJSON, exportSQL
        } = await
        import("../modules/js-export-csv.js");

        this.dynamics.exportCSV = exportCSV;
      }
      let str = this.dynamics.exportCSV(this, {
        download: false,
        linedelimiter: "\n",
        columndelimiter: "\t",
        skipcolumns: exclude_columns
      });
      str = encodeURI(`data:text/tsv;charset=utf-8,${str}`);

      download_url(str, ((container.id) ? container.id : 'stats_proj') + '.tsv');

    });
  }
  initTips() {
    // show big cell content
    let current = null;
    this.dom.querySelectorAll(tableselectors.tip).forEach(tip => {
      const scrollheight = tip.scrollHeight;
      const parent = tip.parentElement;
      const offsetHeight = tip.offsetHeight;
      const showmore = (scrollheight > offsetHeight);
      if (showmore === false) return;
      requestAnimationFrame(() => {
        tip.classList.add(tablecss.pointer);
      });
      let clicked = false;
      const refresh_tip = (showfull) => {
        if (showfull) {
          parent.classList.remove(tablecss.showfull);
          delete parent.dataset.showfull;
          current = null;
        } else {
          if (current) {
            current.classList.remove(tablecss.showfull);
            delete current.dataset.showfull;
          }
          parent.classList.add(tablecss.showfull);
          parent.dataset.showfull = true;
          current = parent;
        }

      }
      tip.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopImmediatePropagation();
        if (clicked) return;
        const showfull = parent.dataset.showfull;
        clicked = true;
        requestAnimationFrame(() => {
          refresh_tip(showfull);
          clicked = false;
        });
      });
    });
  }
  toggleAddOns(list = null, on = false) {
    list = (list) ? list : [tableselectors.search + ' input', tableselectors.export];
    const addons = [];
    let addon;
    list.forEach(addon => {
      addon = this.wrapper.querySelector(addon);
      if (addon) {
        if (on) addon.classList.remove(css.hide);
        else addon.classList.add(css.hide);
      }
    });
  }

}