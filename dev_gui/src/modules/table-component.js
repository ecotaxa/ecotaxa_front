import DOMPurify from 'dompurify';
import equal from 'deep-equal';
import {
 fetchSettings,
  download_url,
  string_to_boolean,
  sort_items,
  is_object,
  html_spinner,
  generate_uuid
} from '../modules/utils.js';
import {
  ModuleEventEmitter
} from '../modules/module-event-emitter.js';
import {
  TextHighlight
} from '../modules/text-highlight.js';
import {
  AlertBox
} from '../modules/alert-box.js';
import debounce from 'debounce';
import {
  css,
  models,
  default_messages,
} from '../modules/modules-config.js';

const instances = new Map();

// valid fetch urlparts
const fetchfroms = Object.freeze({
  collectionlist: '/gui/collectionlist/',
  prjlist: '/gui/prjlist/',
  prjsamplestats: '/gui/prjsamplestats',
  userslist: '/gui/admin/userslist/',
  guestslist:'/gui/guestslist/',
  organizationslist:'/gui/organizationslist/',
  prjpredict: '/gui/prjsforprediction/'
});

const tablecss = Object.freeze({
  showfull: 'showfull',
  tipinline: "tip-inline",
  searchresults: "search-results",
  selectaction: "selectaction",
  absinput: 'absinput',
  disabled: 'table-disabled',
  ascending: 'table-ascending',
  descending: 'table-descending',
  tipover: 'tipover absolute z-10 text-stone-50 rounded-sm bg-stone-600 px-2 py-0.5 -mt-5 ml-12 ',
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
});

const tableselectors = Object.freeze({
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
});

const NOTFOUND = '#NOTFOUND#';

export class TableComponent {
  uuid = null;
  grid = {
    columns: [],
    active: [],
    hidden: [],
    data: [],
    // when a search filter is active, holds the indexes (into grid.data) that match; null means "show all"
    filteredIndexes: null
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

  _virtualScroll = {
    enabled: false,
    rowHeight: 40,
    visibleRows: 50,
    bufferRows: 10,
    scrollTop: 0,
    startIndex: 0,
    container: null
  };

  _fetching = false;
  _lastSearch = null;
  _rowsRenderedCallbacks = [];
  // Cache des formatters pour éviter de les recréer - doit être par instance : les formatters
  // (ex: "imports" de table-project.js) capturent `this` par closure, donc un cache partagé
  // entre plusieurs tables ayant le même params.from (ex: deux tables "pick" en prjlist, une
  // pour taxo et une pour privileges) réutiliserait à tort les colonnes/boutons de la première.
  _formattersCache = null;

  constructor(container, options = {}) {
    if (!container) return;
    container = container instanceof HTMLElement ? container : document.querySelector(container);
    if (!container) return;

    this.uuid = (container.dataset.uuid) ? container.dataset.uuid : generate_uuid();

    if (!instances.has(this.uuid) || !equal(container.dataset, instances.get(this.uuid).params)) {
      this.init(container);
    } else {
      instances.get(this.uuid).refresh();
    }

    return instances.get(this.uuid);
  }

  init(container) {
    this.params = container.dataset;
    let table = container.querySelector('table');
    if (!table) {
      table = document.createElement('table');
      container.appendChild(table);
    }
    table.id = 'table-' + container.id;
    table.classList.add(tableselectors.table.substring(1))
    this.dom = table;

    let top = {
      nodename: "DIV",
      attributes: {
        class: tableselectors.top.substring(1)
      }
    };

    let wrapper = this.objToElement({
      nodename: 'DIV',
      attributes: {
        class: tableselectors.wrapper.substring(1)
      },
      childnodes: [top]
    });
    container.appendChild(wrapper);
    wrapper.appendChild(table);
    this.wrapper = wrapper;

    // Utiliser Object.assign pour éviter les mutations répétées
    this.labels = Object.assign({}, this.labels, this.params.labels);
    this.cellidname = (this.params.hasOwnProperty("cellid")) ? this.params.cellid : this.cellidname;

    // Sanitize only once
    this.params.from = this.params.from ? DOMPurify.sanitize(this.params.from) : null;
    const from = this.params.from ? (fetchfroms[this.params.from] || null) : null;

    this.dom.classList.add(css.hide);
    if (from) {
      if (this.params.defer) this.deferLoad(container, from);
      else this.fetchData(container, from);
    } else {
      this.tableActivate(container);
    }
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
      // Éviter innerHTML si possible
      this.waitdiv.textContent = '';
      if (type !== null) {
        const alert = document.createElement('div');
        alert.className = `alert is-${type}`;
        alert.textContent = message;
        this.waitdiv.appendChild(alert);
      }
    } else {
      this.waitdiv.classList.add(css.hide);
    }
  }

  deferLoad(container, from) {
    const btn = container.querySelector(this.params.defer);
    if (!btn) return;

    // Utiliser { once: true } pour auto-cleanup
    btn.addEventListener('click', () => {
      this.fetchData(container, from);
      btn.remove();
    }, { once: true });
  }

  async fetchData(container, fromurl, pagestart = 0) {
    if (this._fetching && pagestart === 0) return;
    this._fetching = true;

    this.waitActivate(container);
    let pagesize = parseInt(this.params.pagesize) || 0;
    let from = fromurl;

    if (this.params.fromid) from += '/' + DOMPurify.sanitize(this.params.fromid);

    let query = this.params.import ? {
      typeimport: DOMPurify.sanitize(this.params.import),
      gz: true,
    } : {};

    if (pagesize) {
      query.window_start = pagestart;
      query.window_size = pagesize;
    }

    if (this.params.listall) query.listall = this.params.listall;

    // Optimisation : utiliser URLSearchParams une seule fois
    const queryparams = new URLSearchParams(window.location.search);
    const querykeys = this.cellidname + 's';
    for (const [key, value] of queryparams) {
      if (querykeys.indexOf(key) >= 0) query[key] = value;
    }

    if (Object.keys(query).length) from += '?' + new URLSearchParams(query);

    try { let now = Date.now();


      const response = await fetch(from, fetchSettings());
      this.dt = Date.now();
      console.log('seconds to fetch ', (Date.now() - now) / 1000);
      if (!response.ok) throw response;
      const tabledef = await response.json();
      if (this.waitdiv) {
        this.waitdiv.textContent = this.waitdiv.dataset.loaded ?
          DOMPurify.sanitize(this.waitdiv.dataset.loaded) :
          default_messages.dataloaded;
      }

      if (pagestart > 0) {
        if (tabledef.data?.length) {
          // Ajouter les données sans recréer tout le DOM
          this.appendRowsToTbody(tabledef);
        } else {
          pagesize = 0;
        }
      }

      if (pagesize === 0) {
        if (tabledef.data?.length || pagestart > 0) {
          await this.tableActivate(container, tabledef);
        } else {
          this.waitDeactivate('no result', 'default');
        }
        console.log('dispalyed ', (Date.now() - this.dt) / 1000);
      } else {
        // Pagination : libérer la référence avant le prochain fetch
        this._fetching = false;
        await this.fetchData(container, fromurl, pagestart + pagesize);
        return;
      }
    } catch (err) {
      AlertBox.addAlert({
        type: AlertBox.alertconfig.types.danger,
        content: err.status ? `${err.status} ${err.statusText}` : err,
        dismissible: true,
      });
      this.waitDeactivate(err.status ? `${err.status} ${err.statusText}` : 'error', 'error');
    } finally {
      this._fetching = false;
    }
  }

  appendRowsToTbody(tabledef) {
    const tbody = this.dom.tBodies[0];
    if (!tbody) return;

    const fragment = document.createDocumentFragment();
    const startIndex = this.grid.data.length;
    const batchSize = 100;
    let processedCount = 0;

    const processBatch = () => {
      const endIndex = Math.min(startIndex + processedCount + batchSize, startIndex + tabledef.data.length);

      for (let i = startIndex + processedCount; i < endIndex; i++) {
        const dataIndex = i - startIndex;
        const row = this.isJsonData(tabledef) ?
          this.createRowFromJson(tabledef.data[dataIndex], tabledef.columns) :
          tabledef.data[dataIndex];

        this.grid.data.push(row);
        fragment.appendChild(this.createTableRow(row, i));
      }

      processedCount += (endIndex - startIndex - processedCount);

      if (processedCount < tabledef.data.length) {
        requestAnimationFrame(processBatch);
      } else {
        tbody.appendChild(fragment);
      }
    };
    requestAnimationFrame(processBatch);
  }

  async dataToTable(tabledef) {
    if (!tabledef.data) return;

    if (tabledef.columns) {
      await this.convertColumns(tabledef);

      // Créer thead une seule fois
      let thead = this.dom.tHead || document.createElement('thead');
      let tr = thead.querySelector('tr') || document.createElement('tr');
      tr.textContent = ''; // Plus rapide que innerHTML = ''

      let tbody = this.dom.tBodies[0] || document.createElement('tbody');
      this.tbody=tbody;
      if (!this.dom.tBodies[0]) this.dom.appendChild(tbody);

      const isjson = this.isJsonData(tabledef);
      const fragment = document.createDocumentFragment();

      // Construire les headers
      this.grid.columns.forEach((column) => {
        if (!column.hidden) {
          const th = document.createElement('th');
          th.innerHTML = DOMPurify.sanitize(column.label); // textContent plus sûr et plus rapide que innerHTML

          if (column.sort) th.dataset.sort = column.sort;
          if (column.format) th.dataset.type = column.type;
          if (column.name) th.dataset.name = column.name;

          if (this.params.import) {
            ['selectcells', 'what', 'autocomplete', 'parts', 'value'].forEach(prop => {
              if (column.hasOwnProperty(prop)) th.dataset[prop] = column[prop];
            });
          }

          th.dataset.sortable = column.sortable || false;
          tr.appendChild(th);
          this.grid.active.push(column.index);
        } else {
          this.grid.hidden.push(column.index);
        }
      });

      thead.appendChild(tr);
      if (!this.dom.tHead) this.dom.appendChild(thead);

      // Traiter les données
      if (isjson) {
        this.grid.data = [];
        // Référence directe aux colonnes pour éviter les recherches répétées
        const columnEntries = Object.entries(tabledef.columns);

        for (let i = 0; i < tabledef.data.length; i++) {
          const data = tabledef.data[i];
          const row = this.createRowFromJson(data, columnEntries);
          this.grid.data.push(row);
        }
      } else {
        // Référence directe
        this.grid.data = tabledef.data;
      }
      // Activer le scroll virtuel si nécessaire
      if (this.grid.data.length > 1000) {
        this.enableVirtualScroll(tbody);
      } else {
        this.renderFullTbody(tbody);
      }

      // Nettoyer tfoot si nécessaire
      const tfoot = this.dom.tFoot;
      if (this.grid.active.length === 0) {
        tbody.textContent = `<tr><td>${this.labels.noRows}</td></tr>`;
        if (tfoot) tfoot.remove();
        return;
      } else if (tfoot?.querySelector('tr')) {
        const tfootCells = tfoot.querySelector('tr').childNodes;
        this.grid.hidden.forEach(i => tfootCells[i]?.remove());
      }

    }
  }

  // Helper pour éviter la duplication de code
  isJsonData(tabledef) {
    return !tabledef.hasOwnProperty('data') || (tabledef.type === "json");
  }

  createRowFromJson(data, columnEntries) {
    const row = [];
    let j = 0;

    for (const [key, column] of columnEntries) {
      if (!column.hasOwnProperty('emptydata')) {
        if (data.hasOwnProperty(key)) row[j] = data[key];
        else if (column.field && data.hasOwnProperty(column.field)) row[j] = data[column.field];
        else row[j] = null;
        j++;
      }
    }

    return row;
  }

  // Nombre de lignes actuellement visibles (tient compte d'un filtre de recherche actif)
  getVisibleRowCount() {
    return this.grid.filteredIndexes ? this.grid.filteredIndexes.length : this.grid.data.length;
  }

  // Convertit une position dans la vue (filtrée ou non) en index réel dans grid.data
  resolveRowIndex(position) {
    return this.grid.filteredIndexes ? this.grid.filteredIndexes[position] : position;
  }

  // Permet à un plugin (ex: initDetails) de se re-brancher chaque fois que les <tr> sont
  // recréés : le scroll virtuel détruit et reconstruit les <tr>/<td> à chaque scroll, donc tout
  // listener attaché à l'ancien DOM (accordéon "about", etc.) doit être re-attaché sur le nouveau.
  onRowsRendered(callback) {
    this._rowsRenderedCallbacks.push(callback);
  }

  notifyRowsRendered() {
    this._rowsRenderedCallbacks.forEach(cb => cb());
  }

  // Scroll virtuel pour grands datasets
  enableVirtualScroll(tbody) {
    const wrapper = this.wrapper;
    const rowHeight = this._virtualScroll.rowHeight;
    const visibleRows = this._virtualScroll.visibleRows;
    const viewportHeight= rowHeight * visibleRows;
     wrapper.style.maxHeight = `${viewportHeight}px`;
    // Créer un conteneur fantôme pour la hauteur totale
    let phantom = wrapper.querySelector('.virtual-scroll-phantom');
    if (!phantom) {
      phantom = document.createElement('div');
      phantom.className = 'virtual-scroll-phantom';
      phantom.style.position = 'relative';
      wrapper.style.position = 'relative';
      wrapper.style.overflowY = 'auto';
      wrapper.appendChild(phantom);
    }

    this._virtualScroll.enabled = true;

    let lastStartIndex=-1;
    let lastEndIndex=-1;
    let rafid=null;

    const updatePhantomHeight = () => {
      const totalHeight = this.getVisibleRowCount() * rowHeight;
      phantom.style.height = `${Math.max(totalHeight - viewportHeight, 0)}px`;
    };

    const renderVisibleRows = (scrollTop) => {
      const totalRows = this.getVisibleRowCount();
      const startIndex = Math.floor(scrollTop / rowHeight);
      const visibleCount = Math.ceil(wrapper.clientHeight / rowHeight);
      const bufferStart = Math.max(0, startIndex - this._virtualScroll.bufferRows);
      const bufferEnd = Math.min(totalRows, startIndex + visibleCount + this._virtualScroll.bufferRows);
      if( bufferStart===lastStartIndex && bufferEnd===lastEndIndex) {rafid=null;return;}
      lastStartIndex=bufferStart;
      lastEndIndex=bufferEnd;
      while(tbody.firstChild) {tbody.removeChild(tbody.firstChild);}
      const fragment = document.createDocumentFragment();
      for (let i = bufferStart; i < bufferEnd; i++) {
        const actualIndex= this.resolveRowIndex(i);
        const tr = this.createTableRow(this.grid.data[actualIndex], actualIndex);
        fragment.appendChild(tr);
      }
      tbody.style.transform =`translateY(${bufferStart*rowHeight}px)`;
      //tbody.style.height=`${(bufferEnd-bufferStart)*rowHeight}px`;
      tbody.appendChild(fragment);
      rafid=null;
      this.notifyRowsRendered();
    };

    // Recalcule la hauteur totale (ex: après un filtre de recherche) et force un nouveau rendu
    this._virtualScroll.refresh = () => {
      lastStartIndex = -1;
      lastEndIndex = -1;
      updatePhantomHeight();
      if (rafid!==null) cancelAnimationFrame(rafid);
      rafid = requestAnimationFrame(()=> {renderVisibleRows(wrapper.scrollTop);});
    };

    // Debounce pour les performances de scroll
     wrapper.addEventListener('scroll', ()=> {
           const scrollTop = wrapper.scrollTop;
       if(rafid!==null) cancelAnimationFrame(rafid);
         rafid=requestAnimationFrame(()=> {renderVisibleRows(scrollTop);});
       },{passive:true} );
    updatePhantomHeight();
    renderVisibleRows(wrapper.scrollTop);
  }

  renderFullTbody(tbody) {
     while(tbody.firstChild) {tbody.removeChild(tbody.firstChild);}
    const fragment = document.createDocumentFragment();
    const l = this.grid.data.length;

    // Rendu par lots pour ne pas bloquer l'UI
    const batchSize = 200;
    let offset = 0;

    const renderBatch = () => {
      const end = Math.min(offset + batchSize, l);
      for (let i = offset; i < end; i++) {
        fragment.appendChild(this.createTableRow(this.grid.data[i], i));
      }
      offset = end;

      if (offset < l) {
        requestAnimationFrame(renderBatch);
      } else {
        tbody.appendChild(fragment);
      }
    };

    requestAnimationFrame(renderBatch);
  }

  tableToData() {
    if (!this.dom.querySelector('thead')) {
      this.dom.classList.remove(css.hide);
      return;
    }

    this.dom.classList.add(css.hide);

    // Optimisation : utiliser des sélecteurs plus spécifiques
    const theadRow = this.dom.querySelector('thead tr');
    const ths = theadRow ? theadRow.children : [];
    const trs = this.dom.querySelectorAll('tbody tr');

    // Vider les tableaux existants sans créer de nouveaux objets
    this.grid.columns.length = 0;
    this.grid.active.length = 0;
    this.grid.hidden.length = 0;
    this.grid.data.length = 0;

    const find_label = (el) => {
      while (el.firstChild?.nodeType === 1) el = el.firstChild;
      return el.textContent || '';
    };

    Array.from(ths).forEach((th, index) => {
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

      if (col.hidden) {
        this.grid.hidden.push(index);
      } else {
        this.grid.active.push(index);
      }
      this.grid.columns.push(col);
    });

    const cellid = this.getCellId(this.cellidname);

    // Pré-allouer le tableau si possible
    if (trs.length > 10000) {
      this.grid.data = new Array(trs.length);
    }

    Array.from(trs).forEach((tr, i) => {
      if (cellid < 0) {
        tr.dataset[this.cellidname] = i;
      } else if (i === cellid) {
        tr.dataset[this.cellidname] = this.getCellData(i, this.cellidname, cellid);
      }

      const cells = tr.children;
      const data = new Array(this.grid.columns.length);

      for (let j = 0; j < cells.length; j++) {
        if (this.grid.columns[j]?.mask) cells[j].classList.add(tablecss.hidden);
        if (this.grid.hidden.indexOf(j) >= 0) {
          cells[j].remove();
        } else {
          data[j] = cells[j].textContent;
        }
      }

      this.grid.data[i] = data;
    });
    this.dom.classList.remove(css.hide);
  }

  renderTbody(tbody) {
    const l = this.grid.data.length;
    const fragment = document.createDocumentFragment();

    for (let i = 0; i < l; i++) {
      fragment.appendChild(this.createTableRow(this.grid.data[i], i));
    }

    tbody.appendChild(fragment);
  }

  async tableActivate(container, tabledef = null) {
    const loadHandler = () => {
      this.initPlugins(container);
      this.initSearch();
      this.initSort();
      this.waitDeactivate();
      this.dom.classList.remove(css.hide);
      if (this.afterLoad) this.afterLoad();
      container.dataset.table = this.params.table = true;
      this.initialized = true;
    };
    ModuleEventEmitter.once(this.eventnames.load, loadHandler, this.uuid);
    ModuleEventEmitter.once(this.eventnames.dismiss, () => this.destroy(), this.uuid);
    if (tabledef) await this.dataToTable(tabledef);
    else await this.tableToData();
    ModuleEventEmitter.emit(this.eventnames.load, {}, this.uuid);
    instances.set(this.uuid, this);
  }

  destroy() {
    // Nettoyer les références pour le garbage collector
    if (this.dataImport) {
      this.dataImport.resetSelectors?.();
      this.dataImport = null;
    }

    // Nettoyer les event listeners
    ModuleEventEmitter.off(this.eventnames.load, this.uuid);
    ModuleEventEmitter.off(this.eventnames.dismiss, this.uuid);
      this.grid.data.length = 0;
    this.grid.columns.length = 0;
    this.grid.active.length = 0;
    this.grid.hidden.length = 0;
    this.grid.filteredIndexes = null;
    this._rowsRenderedCallbacks.length = 0;

    this.dom = null;
    this.wrapper = null;
    this.waitdiv = null;
    instances.delete(this.uuid);
  }

  refresh(e) {
    if (this.dataImport) this.dataImport.resetSelectors?.();
  }

  labelFormatter(column) {
    let align = '';
    if (['number', 'progress', 'decimal'].includes(column.format)) {
      align = css.right;
    }

    if (column.subfield) {
      return `${column.label} <span class="sublabel">${column.sublabel}</span>`;
    } else if (column.label) {
      return `<span class="${align}">${column.label}</span>`;
    }
    return '';
  }

  getCellId(name) {
    const col = this.grid.columns.find(column => column.name === name);
    return col ? col.index : -1;
  }

  getCellData(rowIndex, name, cellIndex = null) {
    cellIndex = cellIndex ?? this.getCellId(name);
    if (cellIndex < 0 || !this.grid.data.length) return null;
    return this.grid.data[rowIndex]?.[cellIndex] ?? null;
  }

  rowAttributes(tr, index) {
    const id = this.getCellData(index, this.cellidname);
    tr.dataset[this.cellidname] = id;
    // absolute index into grid.data - virtual scroll only keeps a moving window of <tr>s in
    // the DOM, so plugins (eg. DataImport) can't resolve a row's position from DOM order alone.
    tr.dataset.rowindex = index;
    return this.setRowAttributes ? this.setRowAttributes(this, tr, id) : tr;
  }

  createTableRow(row, index, isheader = false) {
    const tr = document.createElement('tr');

    // Réutiliser le même objet td quand c'est possible
    let td;
    for (const column of this.grid.columns) {
      if (column.hidden) continue;

      const cell = row[column.index];
      if (column.render) {
        td = column.render(cell, index, column.index);
        td.nodename = isheader ? 'TH' : 'TD';
        td = this.objToElement(td);
      } else {
        td = document.createElement(isheader ? 'th' : 'td');
        td.textContent = cell ?? '';
      }

      tr.appendChild(td);
    }

    return this.rowAttributes(tr, index);
  }

  objToElement(obj) {
    if (obj.nodename === "#text") {
      return document.createTextNode(obj.data ?? '');
    }

    const el = document.createElement(obj.nodename);

    if (obj.html) {
      el.innerHTML = obj.html;
    } else if (obj.data !== undefined) {
      el.textContent = obj.data;
    }

    if (obj.attributes) {
      for (const [attr, value] of Object.entries(obj.attributes)) {
        el.setAttribute(attr, value);
      }
    }

    if (obj.childnodes) {
      const fragment = document.createDocumentFragment();
      for (const child of obj.childnodes) {
        fragment.appendChild(this.objToElement(child));
      }
      el.appendChild(fragment);
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
    // Retourner le cache si disponible
    if (this._formattersCache && this.params.from === this._formattersCache.from) {
      return this._formattersCache.formatters;
    }

    const formatters = {
      controls: (value, rowIndex, cellIndex, td = {}) => {
        const column = this.grid.columns[cellIndex];
        const id = this.getCellData(rowIndex, column.field);
        const actions = column.actions;
        if (!actions) return '';

        const controls = Object.entries(actions).map(([key, action]) => ({
          nodename: "A",
          attributes: {
            class: `btn is-${key}`,
            href: `${action.link}${id}`
          },
          childnodes: [this.setTextNode(action.label)]
        }));

        td.attributes = td.attributes || {};
        td.attributes.class = css.component.table.controls;
        td.childnodes = controls;
        return td;
      },

      select: (value, rowIndex, cellIndex, td = {}) => {
        const column = this.grid.columns[cellIndex];
        value = isNaN(value) ? this.getCellData(rowIndex, column.field) : value;

        td.childnodes = [{
          nodename: "INPUT",
          attributes: {
            type: "radio",
            name: `${this.uuid}select`,
            value: String(value)
          }
        }];
        return td;
      },

      selectmultiple: (value, rowIndex, cellIndex, td = {}) => {
        const column = this.grid.columns[cellIndex];
        value = isNaN(value) ? (column.field ? this.getCellData(rowIndex, column.field) : value) : value;

        td.childnodes = [{
          nodename: "INPUT",
          attributes: {
            type: "checkbox",
            name: `${this.uuid}select[]`,
            value: String(value)
          }
        }];
        return td;
      },

      decimal: (value, rowIndex, cellIndex, td = {}) => {
        value = isNaN(value) ? 0 : parseFloat(value).toFixed(2);
        if (value - parseInt(value) === 0) value = parseInt(value);

        td.attributes = td.attributes || {};
        td.attributes.class = css.number;
        td.childnodes = [this.setTextNode(value)];
        return td;
      },

      number: (value, rowIndex, cellIndex, td = {}) => {
        value = isNaN(value) ? 0 : value;

        td.attributes = td.attributes || {};
        td.attributes.class = css.number;
        td.childnodes = [this.setTextNode(value)];
        return td;
      },

      check: (value, rowIndex, cellIndex, td = {}) => {
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
            class: `icon-sm icon-${value}check`
          }
        };

        const column = this.grid.columns[cellIndex];
        const id = this.getCellData(rowIndex, this.cellidname);

        if (column.toggle) {
          td.childnodes = [{
            nodename: "A",
            attributes: {
              "data-request": "toggle",
              "data-action": `${column.toggle.link}/${id}`,
              "href": "javascript:void()"
            },
            childnodes: [icon]
          }];
        } else {
          td.childnodes = [icon];
        }
        return td;
      },

      text: (value, rowIndex, cellIndex, td = {}) => {
        if (value === null || value === undefined) {
          td.childnodes = [];
        } else {
          value = value.replaceAll('\r\n', ', ');
          if (value !== '') {
            td.childnodes = [{
              nodename: "DIV",
              attributes: {
                class: css.component.table.tip
              },
              childnodes: [this.setTextNode(value)]
            }];
          } else {
            td.childnodes = [];
          }
        }
        return td;
      },

      default: (value, rowIndex, cellIndex, td = {}) => {
        if (value === null || value === undefined || value === '') {
          td.childnodes = [];
        } else {
          td.childnodes = [this.setTextNode(value)];
        }
        return td;
      }
    };

    // Mise en cache des formatters spécifiques
    let tablecustom = null;
    const pluginLoaders = {
      collectionlist: () => import('../modules/table-collection.js'),
      prjlist: () => import('../modules/table-project.js'),
      prjsamplestats: () => import('../modules/table-sample.js'),
      prjpredict: () => import('../modules/table-prediction.js')
    };

    if (this.params.from && pluginLoaders[this.params.from]) {
      tablecustom = await pluginLoaders[this.params.from]();

      // Définir cellidname selon le modèle
      const modelIds = {
        collectionlist: models.id,
        prjlist: models.projid,
        prjsamplestats: models.sampleid,
        prjpredict: models.projid
      };

      if (modelIds[this.params.from]) {
        this.cellidname = modelIds[this.params.from];
      }
    }

    const finalFormatters = tablecustom ?
      Object.assign({}, formatters, tablecustom.default(this)) :
      formatters;

    // Mettre en cache
    this._formattersCache = {
      from: this.params.from,
      formatters: finalFormatters
    };

    return finalFormatters;
  }

  async convertColumns(tabledef) {
    const columns = tabledef.columns || (this.params.columns ? JSON.parse(this.params.columns) : null);
    if (!columns) return;

    const formatters = await this.getFormatters();

    // Préparer les champs une seule fois
    const fields = Object.keys(tabledef.columns).filter(key =>
      !tabledef.columns[key].hasOwnProperty('emptydata')
    );

    const map_column = (key, column, index) => {
      if (!column) {
        return { index, name: key, hidden: true };
      }

      let col = {
        index: column.hasOwnProperty('emptydata') ? fields.indexOf(column.emptydata) : fields.indexOf(key),
        name: key,
        label: this.labelFormatter(column),
        sortable: !column.notsortable
      };

      if (column.sortable) col.sort = column.sortable;
      col.searchable = !column.notsearchable;

      if (column.hidden) {
        col.hidden = string_to_boolean(column.hidden);
      }

      if (['number', 'decimal'].includes(column.format)) {
        col.type = 'number';
      }

      // Gérer les colonnes spéciales
      if (key === 'select') {
        const select = column.select === "controls" ? "controls" :
                      (column.selectcells ? "imports" : column.select);
        if (select) {
          col = Object.assign({}, column, col);
          col.sortable = false;
          col.searchable = false;
        }
      }

      // Assigner le renderer si pas caché
      if (!column.hidden) {
        const select = column.select === models.controls ? models.controls :
                      (column.selectcells ? models.imports : column.select);
        const format = column.format || column.subfield || select || "default";

        if (formatters[format]) {
          col.render = formatters[format];
        }
      }

      return col;
    };

    this.grid.columns = Object.entries(columns).map(([key, column], index) =>
      map_column(key, column, index)
    );
  }

  initEvents() {
    ModuleEventEmitter.on(this.eventnames.update, () => {
      this.dom.classList.remove(css.hide);
    }, this.uuid);
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
        a.classList.add(tableselectors.sorter.substring(1));
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

    ModuleEventEmitter.on(this.eventnames.sorting, (req) => {
      if (this.plugins.jsDetail) this.plugins.jsDetail.activeDetail(false);
      this.dom.querySelectorAll('.table-sorter').forEach((a, i) => {
        a.classList.add(((i === req.index) ? css.wait : css.disabled));
      });
      this.sorting = true;
    }, this.uuid);

    ModuleEventEmitter.on(this.eventnames.sorted, (req) => {
      this.dom.querySelectorAll('.table-sorter').forEach((a, i) => {
        a.classList.remove(((i === req.index) ? css.wait : css.disabled))
      });
      this.sorting = false;
    }, this.uuid);
  }

  sortColumn(th, index, dir = null) {
    dir = (dir === null) ? ((th.classList.contains(tablecss.ascending)) ? false : (th.classList.contains(tablecss.descending)) ? true : ((th.dataset.sort) ? false : true)) : dir;
    th.classList.toggle(tablecss.ascending);
    th.classList.toggle(tablecss.descending);

    ModuleEventEmitter.emit(this.eventnames.sorting, {
      dir: dir,
      index: th.cellIndex
    }, this.uuid);

    // Trier les données
    let rows = this.grid.data.map((row, i) => {
      const cell = is_object(row[index]) ? JSON.stringify(row[index]) : ((Array.isArray(row[index])) ? row[index][0] : row[index]);
      return {
        value: typeof cell === "string" ? cell.toLowerCase() : ((cell === null) ? 0 : cell),
        row: i
      }
    });

    if (dir === false) {
      th.classList.remove(tablecss.ascending);
      th.classList.add(tablecss.descending);
      th.setAttribute("aria-sort", "descending");
    } else {
      th.classList.remove(tablecss.descending);
      th.classList.add(tablecss.ascending);
      th.setAttribute("aria-sort", "ascending");
    }

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
    });

    rows.sort((a, b) => {
      return collator.compare((dir ? a.value : b.value), (dir ? b.value : a.value))
    });

    // Réorganiser les données selon le tri
    const sorted = rows.map(r => this.grid.data[r.row]);
    this.grid.data = sorted;

    // Si le virtual scroll est actif, on refait juste le rendu
    if (this._virtualScroll.enabled) {
      // grid.data has been rebuilt in-place, so any previous filteredIndexes (positions) are stale.
      // indexes in _lastSearch are id/value based, so recomputing against the new order fixes them.
      if (this._lastSearch && this._lastSearch.queries.length) {
        this.displaySelected(this._lastSearch.queries, this._lastSearch.indexes, this._lastSearch.cellid);
      } else {
        this.grid.filteredIndexes = null;
        this.wrapper.scrollTop = 0;
        if (this._virtualScroll.refresh) this._virtualScroll.refresh();
      }
    } else {
      // Comportement original pour les petits datasets
      const tbody = this.dom.querySelector('tbody');
      const trs = tbody.querySelectorAll('tr');

      while (tbody.firstChild) {
        tbody.removeChild(tbody.firstChild);
      }

      const fragment = document.createDocumentFragment();
      rows.forEach((r, i) => {
        fragment.appendChild(trs[r.row]);
      });

      tbody.appendChild(fragment);
    }

    ModuleEventEmitter.emit(this.eventnames.sorted, {
      dir: dir,
      index: th.cellIndex
    }, this.uuid);
  }
  displaySelected(queries, indexes, cellid, filtered = false) {
    const reset = (queries.length === 0 && indexes.length === 0);

    if (this._virtualScroll.enabled) {
      // Only a window of rows exists in the DOM at any time, so filtering must operate on the
      // underlying data (grid.filteredIndexes) rather than on individual <tr> elements.
      if (reset) {
        this.grid.filteredIndexes = null;
      } else if (queries.length > 0 && indexes.length === 0) {
        this.grid.filteredIndexes = [];
      } else {
        this.grid.filteredIndexes = [];
        this.grid.data.forEach((row, i) => {
          const val = (cellid >= 0 && row[cellid] !== undefined && row[cellid] !== null) ? String(row[cellid]) : String(i);
          if (indexes.indexOf(val) >= 0) this.grid.filteredIndexes.push(i);
        });
      }
      this.wrapper.scrollTop = 0;
      if (this._virtualScroll.refresh) this._virtualScroll.refresh();
      return;
    }

    const trs = this.dom.querySelectorAll('tbody tr');
    const toggle=(this.toggle) ? this.toggle : function(tr, value, idx,filtered=false) {
     if (!tr.dataset.checked || !value) tr.hidden = value;
    }
    trs.forEach((tr, index) => {
      if (reset) toggle(tr, false,index,filtered);
      else {
        const val = (queries.length > 0 && indexes.length === 0) ? NOTFOUND : (tr.dataset[this.cellidname] !== null) ? tr.dataset[this.cellidname] : tr.cells[cellid].textContent;
        const idx = indexes.indexOf(val);
        if (idx < 0) toggle(tr, true, idx,filtered);
        else toggle(tr, false, idx, filtered);
      }
    });
  };

  initSearch() {
    const top = this.wrapper.querySelector(tableselectors.top);
    if (!this.params.searchable || top === null) return;
    if (this.grid.data.length < 10) return this.toggleAddOns();
    else this.toggleAddOns([tableselectors.search + ' input'], false);
    this.searching = false;
    const cellid = this.getCellId(this.cellidname);
    // search items
    let searchbox = top.querySelector(tableselectors.search);
    if (searchbox === null) {
      searchbox = this.objToElement({
        nodename: 'DIV',
        attributes: {
          class: tableselectors.search.substring(1)
        },
        childnodes: [{
          nodename: 'input',
          attributes: {
            type: 'search',
            name: 'table-search',
            placeholder: this.labels.placeholder,
            class: `${tableselectors.input.substring(1)} ${css.input}`
          }
        }]
      });
      top.appendChild(searchbox);
    }
    const searchinput = searchbox.querySelector('input');
    if (!searchinput) return;
    let searchstring = ``;
    const table_search = debounce((searchstring, casesensitive = false) => {
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
      ModuleEventEmitter.emit(this.eventnames.search, {
        searchstring: searchstring,
        queries: queries
      }, this.uuid);
      let datas = this.grid.data,
        indexes = [];
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
                 AlertBox.addAlert({
                  type: AlertBox.alertconfig.types.danger,
                    content: err.status ? `${err.status} ${err.statusText}` : err,
                  dismissible: true,
                });
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
      ModuleEventEmitter.emit(this.eventnames.searchend, {
        queries: queries,
        indexes: indexes,
        cellid: cellid
      }, this.uuid);
    }, 300);
    const display_search = (queries, indexes, cellid) => {
      this.displaySelected(queries, indexes, cellid);
    };
    const clear_search = debounce(() => {
      this.searching = true;
      this._lastSearch = null;
      if (this._virtualScroll.enabled) {
        this.grid.filteredIndexes = null;
        this.wrapper.scrollTop = 0;
        if (this._virtualScroll.refresh) this._virtualScroll.refresh();
      } else {
        const trs = this.dom.querySelectorAll('tbody tr[hidden=""]');
        trs.forEach((tr, index) => {
          tr.hidden = false;
        });
      }
      this.searching = false;
      searchinput.classList.remove(css.wait);
    }, 500);

    const search_input = (value) => {
      if (value !== searchstring) {
        searchinput.classList.add(css.wait);
        searchstring = value;
        if (value === '') {
          clear_search();
        } else if (value.length > 2) {
          table_search(value);
        }
      }
    }
    searchinput.addEventListener("input", (e) => {
      search_input(e.target.value);
    });
    searchinput.addEventListener("click", (e) => {
      search_input(e.target.value);
    });
    ModuleEventEmitter.on(this.eventnames.search, (req) => {
      console.log('searchevent')
      //  request {searchstring:searchstring, queries:queries}
      if (this.searching === false) {
       // if (this.plugins.jsDetail) this.plugins.jsDetail.activeDetail(false);
      }
      this.searching = true;
    }, this.uuid);
    ModuleEventEmitter.on(this.eventnames.searchend, (req) => {
      // req {queries:queries,indexes: indexes, cellid:cellid}
      this._lastSearch = { queries: req.queries, indexes: req.indexes, cellid: req.cellid };
      display_search(req.queries, req.indexes, req.cellid);
      searchinput.classList.remove(css.wait);
      this.searching = false;
    }, this.uuid);
    ModuleEventEmitter.on(this.eventnames.update, () => {
      if (this.searching === false) {
        setTimeout(() => {
          refresh_details();
        }, 300);
      }
    }, this.uuid);
    this.toggleAddOns([tableselectors.search + ' input'], true);
  }
  initSelect(container) {
    const inputs = this.dom.querySelectorAll('input[name^="' + this.uuid + '"]');
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
        else if (this.dom.querySelectorAll('input[name^="' + this.uuid + '"]:checked').length === 0) popup_selected(null, null, true);
      });
    });
    if (this.dom.querySelectorAll('input[name^="' + this.uuid + '"]:checked').length > 0) {
      selectaction.classList.remove(css.hide);
      popup_selected(null, null);
    }
  }
  async initDetails() { // TODO : generic
    // about - one div to display cell details make it appear as table row expanding
    let _fetchingdetails=false;
    const wrapper = this.wrapper;
    const about = wrapper.querySelector('#' + tablecss.tipinline) ? wrapper.querySelector('#' + tablecss.tipinline) : tablecss.tipinline;
    if (!this.plugins.JsDetail) {
      const {
        JsDetail
      } = await
      import('../modules/js-detail.js');
      this.plugins.JsDetail = JsDetail;
    }

    if (!this.plugins.JsAccordion) {
      const {
        JsAccordion
      } = await import('../modules/js-accordion.js');
      this.plugins.JsAccordion = JsAccordion;
    }
    const jsDetail = this.plugins.JsDetail({
      waitdiv: this.waitdiv
    });

    const detail = jsDetail.applyTo(about, wrapper); // specific to about details in table
    // hide / show disable details zone
    const callbackclose = (el, callback = null) => {
      const current = jsDetail.activeDetail(false);
      if (callback) callback();
    }

    const callbackopen = (el, callback = null) => {
      let current = jsDetail.activeDetail(true);
      if (current && current === el) {
        current = jsDetail.expandDetail(el);
        if (callback) callback();
      } else {
        if (current) current.querySelector('summary').click();
        const url = this.params.detailsurl + el.dataset.id + '?' +
          new URLSearchParams({
            partial: true
          });
        current = jsDetail.activeDetail(true);
        // append to cell details and display
        if(_fetchingdetails) return;
        _fetchingdetails=true;
        fetch(url, fetchSettings()).then(response => response.text()).then(html => {
          current = jsDetail.expandDetail(el, html);
          if (callback) callback();
        }).catch((err) => {
      AlertBox.addAlert({
        type: AlertBox.alertconfig.types.danger,
        content: err.status ? `${err.status} ${err.statusText}` : err,
        dismissible: true,
      });
    }).finally(()=> {
      _fetchingdetails=false;});
      }

    }

    const refresh_details = () => {
      const details = this.dom.querySelectorAll(tableselectors.details);
      if (!details) return;
      /*details.forEach(item => {
        if (!item.dataset.id) return;
        item =new this.plugins.JsAccordion(item, callbackopen, callbackclose, detail);
      });*/
      this.plugins.JsAccordion.applyTo(details, callbackopen, callbackclose, detail);
    }
    // virtual scroll destroys and recreates <tr>/<td> on every scroll, so re-bind whenever
    // that happens, not just once at setup - otherwise rows scrolled into view later never
    // get their "about" click handler attached.
    this.onRowsRendered(refresh_details);
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
      const asc = col.classList.contains(tablecss.ascending);
      const desc = col.classList.contains(tablecss.descending);
      if (parseInt(col.dataset.sortactive) === parseInt(coltosort)) {
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
    let exclude_columns = [];
    const noexport=(this.params.noexport)?(this.params.noexport.split(',')):[];
    noexport.forEach((v,k) => {noexport[k]=v.trim();});
    noexport.push('select');
    this.grid.columns.forEach((column, index) => {
      if (noexport.indexOf(column.name) >=0) exclude_columns.push(column.index);
    });
    const exporthidden=(this.params.exportvisible)?false:true;
    btn.addEventListener('click', async (e) => {
      e.preventDefault();
      if (!this.plugins.exportCSV) {
        const {
          exportCSV // or exportJSON, exportSQL
        } = await
        import("../modules/export-csv.js");

        this.plugins.exportCSV = exportCSV;
      }
      let str = this.plugins.exportCSV(this, {
        download: false,
        linedelimiter: "\n",
        columndelimiter: "\t",
        skipcolumns: exclude_columns
      },exporthidden);
      str = encodeURI(`data:text/tsv;charset=utf-8,${str}`);

      download_url(str, ((container.id) ? container.id : 'stats_proj') + '.tsv');

    });
  }
  initTips() {
    // show big cell content
    let current = null;
    this.dom.querySelectorAll(tableselectors.tip).forEach(tip => {
      tip.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopImmediatePropagation();
        const parent = e.target.parentElement;
        if (current !== null) current.classList.remove(tablecss.showfull);
        if (current !== parent) {
          parent.classList.add(tablecss.showfull);
          current = parent;
        } else current = null;

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