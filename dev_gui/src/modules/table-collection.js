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
      td.html = `<a href="/gui/collection/edit/${id}" class="small-caps text-stone-50 rounded p-1 shadow bg-mainblue-700">Edit</a>`
      return td;
    },
    user: (value, rowIndex, cellIndex, td = {}) => {
      console.log('value provider', value.email)

      td.html = `<a href="mailto:${value.email}" class="font-normal text-mainblue-700">${value.name}</a>`
      return td;
    },
    user_list: (value, rowIndex, cellIndex, td = {}) => {
      console.log('value', Object.values(value))
      let html = {
        users: [],
        orgs: []
      };

      Object.entries(value).forEach(([k, vals]) => {

        if (k.indexOf('_users') > 0) {
          vals.forEach(v => {
            console.log('v', v.name)
            const t = `<a href="mailto:${v.email}" class="font-normal text-stone-700">${v.name}</a>`
            html.users.push(t);
          });
        } else {
          vals.forEach(v => {
            console.log('v', v)
            html.orgs.push(v);
          });
        }

      });
      td.html = `users : ${html.users.join(', ')} <br>organisations : ${html.orgs.join(', ')}`;
      return td;
    },
    project_list: (value, rowIndex, cellIndex, td = {}) => {
      console.log('value', value)
      value = (Array.isArray(value)) ? value : [];
      let html = [];
      value.forEach(v => {
        html.push(`<a href="/gui/prj/about:${v}" class="font-normal text-stone-800">${v}</a>`);
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