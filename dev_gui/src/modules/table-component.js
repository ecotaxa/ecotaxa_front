import {
  DataTable
} from "simple-datatables";
import DOMPurify from 'dompurify';
import equal from 'deep-equal';
import {
  ActivItems
} from "../modules/activ-items.js";
import {
  DataImport
} from '../modules/data-import.js';

import {
  JsAccordion
} from '../modules/js-accordion.js';
import {
  JsDetail
} from '../modules/js-detail.js';
import {
  fetchSettings,
} from '../modules/utils.js';
import {
  css,
  domselectors,
  models
} from '../modules/modules-config.js';
let instance = null;
// valid fetch urlparts
const fetchfroms = ['prjlist'];
const tablecss = Object.assign(css, {
  tipinline: 'tip-inline',

});
const dom_selectors = Object.assign(domselectors, {
  datatable: '.dataTable-table',
  datatable_top: '.dataTable-top',
  datatable_search: '.dataTable-input',
  table_filters: 'table-filters',
  wait: 'wait-please'
});
Object.freeze(tablecss);
Object.freeze(dom_selectors);

export class TableComponent {
  columns = [];
  datas = [];
  grid = null;
  params = null;
  last_used = null;
  importfields = null;

  constructor(container, options = {}) {
    if (!container) return;
    container = container instanceof HTMLElement ? container : document.querySelector(container);

    if (!instance || !equal(container.dataset, instance.params)) {
      this.init(container);
    } else this.refresh();
    return instance;
  }

  init(container) {
    // valid from values - fetchfroms
    let from = (container.dataset.from) ? ((fetchfroms.indexOf(container.dataset.from) >= 0) ? '/gui/' + DOMPurify.sanitize(container.dataset.from) + '/' : null) : null;
    if (!from) return;
    if (container.dataset.import) from += '?' + new URLSearchParams({
      typeimport: DOMPurify.sanitize(container.dataset.import),
      gz: true,
    });
    this.waitActivate(container);
    fetch(from, fetchSettings()).then(response => response.json()).then(tabledef => {
      this.waitdiv.innerHTML = ((this.waitdiv.dataset.loaded) ? DOMPurify.sanitize(this.waitdiv.dataset.loaded) : 'Data loaded. Displaying...');
      this.columns = tabledef.columns;
      this.params = container.dataset;
      this.datas = tabledef.data;
      this.last_used = tabledef.last_used; // table activate
      this.tableActivate(container, this.convertColumns());
      // dismiss table when dismiss modal
      container.addEventListener('dissmisstable', (e) => {
        console.log('destroy table');
        this.destroy();
      });

      this.grid.on('datatable.init', () => {
        // hide and move waitdiv in the wrapper for inner elements display
        this.waitdiv.classList.add(tablecss.hide);
        // move import zones and/or search zone - reorg the page display
        this.grid.wrapper.append(this.waitdiv);
        container.style.top = container.offsetTop + 'px';
        // fetch once the same table
        container.dataset.table = this.params.table = true;
        this.grid.table.classList.remove(tablecss.hide);
        const search = this.grid.wrapper.querySelector(dom_selectors.datatable_search);
        // like any other form element
        search.classList.add(tablecss.input);
        if (this.importfields) {
          this.initImport(container.dataset.import);
          this.waitdiv.remove();
        } else {
          const top = this.grid.wrapper.querySelector(dom_selectors.datatable_top);
          if (top) {
            const filters = document.querySelector(dom_selectors.table_filters);
            // insert  filters node  in datatable top
            if (filters) top.prepend(filters);
          }
          if (container.dataset.caption && item.querySelector('caption')) container.querySelector('caption').contentText = item.dataset.caption;
        }
        // init about if exists
        this.initDetails();
        this.activItems = new ActivItems();
        this.activItems.apply(this.grid.table);
      });
      this.grid.on('datatable.search', (query, matched) => {
        return this.search(query, matched);
      });
      this.grid.on('datatable.refresh', (e) => {
        return this.refresh(e);
      });
      //

      instance = this;
    }).catch(err => {
      console.log('err', err);
    })
  }
  waitActivate(container) {
    const waitdiv = container.querySelector('#' + dom_selectors.wait);
    if (!waitdiv) {
      waitdiv = document.createElement('div');
      waitdiv.id = dom_selectors.wait;
      container.append(waitdiv);
    }
    this.waitdiv = waitdiv;
  }
  tableActivate(container, cols) {
    const table = container.querySelector('table');
    if (!table) {
      table = document.createElement('table');
      container.append(table);
    }
    table.id = 'table-' + container.id;
    const grid = new DataTable(table, {
      data: {
        headings: cols.map(column => ((column.name) ? column.name : ``)),
        data: this.datas
      },
      columns: cols,
      searchable: true,
      fixedHeight: false,
      paging: false,
      perPage: 100000,
      perPageSelect: false,
      scrollY: (this.importfields) ? true : false,
      layer: {
        top: "{search}",
        bottom: "{pagination}"
      }

    });
    this.grid = grid;
  }
  destroy() {
    if (this.dataImport) this.dataImport = null;
    if (this.activItems) this.ActivItems = null;
    this.grid = null;
    instance = null;
  }
  refresh(e) {
    this.selectors.forEach(selector => {
      if (this.disabled) this.disabled = false;
    });
  }
  search(query, matched) {
    if (query.trim().length < 3) return;
    console.log('searching', this.grid.searching)
    console.log('query', query);
    console.log('matched', matched);
    console.log('searching', this.grid.searching)
  }

  labelFormatter(column) {
    let align = ``;
    if (['number', 'progress', 'decimal'].find(format => format === column.format)) align = css.right;
    if (column.subfield) return `${column.label} <span class="sublabel">${column.sublabel}</span>`;
    else if (column.label) return `<span class="col-${column.field} ${align}">${column.label}</span>`;
    else return ``;
  }
  getCellData(cell, row) {
    //get json data directly from fetched data
    cell.data = ``;
    return this.datas[row.dataIndex][cell.cellIndex];
  }
  getFormatter(format, column, table = 'projects') {
    //formatters for diff tables - one for the moment - formats sepcified in gui/project/projects_list_interface.py
    const contactcellid = this.columns.findIndex((column) => column.field == models.contact);
    const cellid = this.columns.findIndex((column) => column.field == models.projid);
    const formatters = {
      'contact': (data, cell, row) => {
        data = this.getCellData(cell, row);
        let value;
        const id = this.datas[row.dataIndex][cellid];
        if (column.request && column.request == 'about') {

          //cell is an array with title and  boolean which tells if about is autho or not
          // display stats and info about the project if ok
          if (data[1]) value = `<details data-id=${id} data-what=${column.request}><summary>${data[0]} [${id}]</summary></details>`;
          else value = data[0] + ' [' + id + ']';
        } else value = data + ' [' + id + ']';
        const contact = this.datas[row.dataIndex][contactcellid];
        if (contact) {
          const iscontact = (contact.contact) ? `data-contact=${contact.contact}` : ``;
          return `<div class="ellipsis">${value} <a href="mailto:${contact.email}" class="contact" ${iscontact}>${contact.name}</a></div>`;
        } else return value;
      },
      'imports': (data, cell, row) => {
        data = this.getCellData(cell, row);
        const id = this.datas[row.dataIndex][cellid];
        row.dataset.id = id;
        if (!column.select || !column.selectcells) return data;
        let btns = ``,
          txt = (this.params.btn) ? this.params.btn : 'import';

        switch (column.select) {
          case models.taxo:
            ((column.parts) ? column.parts : column.selectcells).forEach((value, index) => {
              let impid = this.columns.findIndex((column) => column.field == value);
              impid = ((impid < 0 || this.datas[row.dataIndex][impid] === "{}") ? `disabled` : ``);
              if (index > 0) txt = (this.params.btn1) ? this.params.btn1 : 'extra';
              btns += `<button class="btn is-preset ${impid}"  ${impid}><i class="icon-md ${((impid === '')? `icon-plus-sm`:``)}"></i>${txt}</button>`;
            });
            break;
          case models.settings:
          case models.privileges:
          case models.fields:
            btns = `<button class="btn is-preset">${txt}</button>`;
            break;
        }
        return btns;
      },
      'controls': (data, cell, row) => {
        data = this.getCellData(cell, row);
        const id = this.datas[row.dataIndex][cellid];
        const index = this.last_used.indexOf(parseInt(id));

        if (index >= 0) {
          row.classList.add('last-used');
          this.last_used[index] = row;
        }
        let controls = ``;
        for (const [key, action] of Object.entries(data)) {
          switch (key) {
            case "A":
              controls += `<a class = "btn is-annotate order-1" href = "/prj/${id}">${action}</a>`;
              break;
            case "V":
              controls += `<a class = "btn is-view order-1" href = "/prj/${id}">${action}</a>`;
              break;
            case "M":
              controls += `<a class = "btn is-manage order-2" href = "/gui/prj/edit/${id}">${action}</a>`;
              break;
            case "R":
              const contact = this.datas[row.dataIndex][contactcellid];
              controls += `<a class = "btn is-request order-2" href = "mailto:${contact.email}?${id}">${action}</a>`;
              break;
          }
        };
        return `<div class="is-controls">` + controls + `</div>`;
      },
      'decimal': (data, cell, row) => {
        data = this.getCellData(cell, row);
        if (data === 'None' || data === '' || data === null) return ``;
        data = parseFloat(data).toFixed(2);
        if (data - parseInt(data) === 0) data = parseInt(data);
        cell.classList.add(column.format);
        return data;
        //return `<div class="${column.format}">${data}</div>`;
      },
      'number': (data, cell, row) => {
        data = this.getCellData(cell, row);
        if (data === 'None' || data === '' || data === null) return ``;
        cell.classList.add(column.format);
        return parseInt(data);
        //  return `<div class="${column.format}">${parseInt(data)}</div>`;
      },
      'check': (data, cell, row) => {
        data = this.getCellData(cell, row);
        let val;
        switch (data) {
          case true:
          case 'Y':
          case 1:
            val = "";
            break;
          default:
            val = "no-";
            break;
        }
        return `<i class="icon-sm icon-${val}check"></i>`;
      },
      'progress': (data, cell, row) => {
        data = this.getCellData(cell, row);

        if (data === 'None' || data === '' || data === null) return ``;
        data = parseFloat(data).toFixed(2);
        if (data - parseInt(data) === 0) data = parseInt(data);
        return `<data class="${column.format}" style="width:${data}%">${data}</data>`;
      },
      'license': (data, cell, row) => {
        data = this.datas[row.dataIndex][cell.cellIndex];
        const tbcell = {
          "CC0 1.0": "ca",
          "CC BY 4.0": "cb",
          "CC BY-NC 4.0": "cbn"
        }
        if (tbcell[data]) return `<span class="cc" data-title="${data}">${tbcell[data]}</span>`;
        else {
          switch (data) {
            case "Copyright":
              return `<span class="txcc"  data-title="${data}">&copy;</span>`;
            case "not choosen":
              return `<span data-title="${data}"></span>`;
              break;
          }

        }
        return data;
      },
      'privileges': (data, cell, row) => {
        data = this.getCellData(cell, row);
        let rights = ``;
        for (const [right, members] of Object.entries(data)) {
          let mb = [];
          if (members.length) {
            for (const member of members) {
              mb.push(member.name);
            }
            rights += `<div class="rights" data-r=${right}>${mb.join(`, `)}</div>`;
          }
        }
        return rights;
      },
      'taxons': (data, cell, row) => {
        data = this.getCellData(cell, row);
        cell.classList.add('tip');
        const num = Object.keys(data).length;
        if (num > 0) {
          data = Object.values(data).join(', ');
          return `<div  data-num="${num}">${data}</div>`;
        } else return ``;
      },
      'text': (data, cell, row) => {
        data = this.getCellData(cell, row);
        if (data) {
          cell.classList.add('tip');
          data = data.replaceAll('\r\n', ', ');
          if (data !== '') return `<div >${data}</div>`;
        }
      }
    };

    return formatters[format];
  }

  mapColumn(column, index) {
    const col = {
      select: index,
      sortable: true,
      searchable: true,
      hidden: false,
      name: this.labelFormatter(column)
    };
    if (column.notsortable) col.sortable = "false";
    if (!column.notsearchable) col.searchable = true;
    if (column.hidden === "true") col.hidden = "true";
    if (column.request) col.request = column.request;
    if (['number', 'progress', 'decimal'].find(format => format === column.format)) col.type = 'number';
    switch (column.field) {
      case 'select':
        const select = (column.select && column.select == "controls") ? "controls" : ((column.selectcells) ? "imports" : null)
        if (select) {
          this.importfields = column.selectcells;
          col.render = this.getFormatter(select, column);
          col.sortable = "false";
          col.searchable = "false";
        }
        break;
      default:
        if (column.format) {
          col.render = this.getFormatter(column.format, column);
        } else if (column.subfield) {
          col.render = this.getFormatter(column.subfield, column);
        } else col.render = (data, cell, row) => {
          return this.getCellData(cell, row);
        }
        break;
    }
    return col;
  }

  convertColumns() {
    return this.columns.map((column, index) => this.mapColumn(column, index));
  }

  initDetails() { // TODO : generic
    // about - one div to display cell details make it appear as table row expanding
    const wrapper = this.grid.wrapper;
    let about = wrapper.querySelector('#' + tablecss.tipinline) ? wrapper.querySelector('#' + tablecss.tipinline) : tablecss.tipinline;
    const options = {
      waitdiv: this.waitdiv
    };
    const jsDetail = new JsDetail(about, wrapper, options); // specific to about details in table
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
        const url = '/gui/prj/about/' + el.dataset.id + '?' +
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
    const activate_details = () => {
      for (let item of this.grid.table.querySelectorAll('details[data-what="about"]')) {
        const projid = item.dataset.id;
        if (!item.dataset.id) return;
        item = new JsAccordion(item, callbackopen, callbackclose, jsDetail.detail);
      };
    }
    activate_details();
    // remove details when sorting
    this.grid.on('datatable.sort', function(column, direction) {
      jsDetail.activeDetail(false);
      activate_details();
    });

  }
  initImport(what) {
    //  // add resizer to enable full view of imported datas
    /*
              let rs = this.doc.closest(this.content_selector);
              rs = (rs) ? rs.previousElementSibling : null;
              if (rs) {

                rs = rs.children[0];
                if (rs) {
                  const search = this.doc.parentElement.querySelector('.dataTable-search');
                  if (search) rs.insertBefore(search, rs.lastChild);
                }
              }*/
    this.columns.forEach((column, index) => {
      if (this.importfields.indexOf(column.field) >= 0) {
        this.grid.headings[index].dataset.name = column.field;

      }
      if (column.selectcells) this.grid.headings[index].dataset.selectcells = column.selectcells;
      if (column.data) {
        for (const [key, value] of Object.entries(column.data)) {
          this.grid.headings[index].setAttribute('data-' + key, value);
        }
      }
    });

    this.dataImport = new DataImport(this.grid, what);

  }
  /*initShowTip() {
    for (const tip of this.grid.table.querySelectorAll('.tip')) {
      const showtip = tip.firstElementChild;
      if (showtip && showtip.scrollHeight > showtip.offsetHeight) {
        showtip.addEventListener('click', (e) => {
          if (tip.classList.contains('showfull')) tip.classList.remove('showfull');
          else tip.classList.add('showfull');
        });

      } else tip.classList.remove('tip');
    }
  }*/
}