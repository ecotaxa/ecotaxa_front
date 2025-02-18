import {
  format_license
} from '../modules/utils.js';
import {
  models,
  css
} from '../modules/modules-config.js';

export default function(state) {
  return {
    select: (value, rowIndex, cellIndex, td = {}) => {
      const id = state.getCellData(rowIndex, models.id);
      const html = [];
      Object.entries(value).forEach(([k, v]) => {
        html.push(`<a href="/gui/collection/${k}/${id}" class="small-caps text-stone-50 rounded-sm p-1 shadow bg-mainblue-700 btn is-${k}">${v}</a>`)
      })
      td.html = html.join(``);
      return td;
    },
    user: (value, rowIndex, cellIndex, td = {}) => {
      td.html = (value) ? (value.email) ? `<a href="mailto:${value.email}" class="font-normal text-mainblue-700">${value.name}</a>` : value.name : ``;
      return td;
    },
    user_list: (value, rowIndex, cellIndex, td = {}) => {
      let html = {
        users: [],
        orgs: []
      };

      Object.entries(value).forEach(([k, vals]) => {
        if (k.indexOf('_users') > 0) {
          vals.forEach(v => {
            const t = (v.email) ? `<a href="mailto:${v.email}" class="font-normal text-stone-700">${v.name}</a>` : v.name;
            html.users.push(t);
          });
        } else {
          vals.forEach(v => {
            html.orgs.push(v);
          });
        }

      });
      td.html = `users : ${html.users.join(', ')} <br>organisations : ${html.orgs.join(', ')}`;
      return td;
    },
    project_list: (value, rowIndex, cellIndex, td = {}) => {
      value = (Array.isArray(value)) ? value : [];
      let html = [];
      value.forEach(v => {
        html.push(`<a href="/gui/prj/about/${v}?" data-action= class="font-normal text-stone-800">${v}</a>`);
      })

      td.html = html.join(', ');
      return td;
    },
    license: (value, rowIndex, cellIndex, td = {}) => {
      td.html = format_license(value, true);
      return td;
    },
  }
}