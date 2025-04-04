import {
  format_license
} from '../modules/utils.js';
import {
  models,
  css
} from '../modules/modules-config.js';

export default function(state) {
  return {
    contact_user: (value, rowIndex, cellIndex, td = {}) => {
      const about = (Array.isArray(value)) ? Boolean(value[1]) : false;
      value = (Array.isArray(value)) ? String(value[0]).trim() : String(value).trim();
      if (value === null) value = ``;
      let node = [];
      //cell value is an array with title and  boolean which tells if about is autho or not
      // display stats and info about the project if ok
      const id = state.getCellData(rowIndex, models.id);
      // contact
      let contact = state.getCellData(rowIndex, models.contact_user);
      const iscontact = (contact!==null);
      if (contact) {
        const nodecontact = {
          nodename: "A",
          attributes: {
            href: `mailto:${contact.email}`,
            class: "contact",
            target: "_blank"
          },
          childnodes: [state.setTextNode(contact.name)]
        };
        if (iscontact) nodecontact.attributes["data-contact"] = iscontact;
        node = [state.setTextNode(value), nodecontact];
      } else node = [state.setTextNode(value)];
      if (about === true) {
        td.childnodes = [{
          nodename: "DETAILS",
          attributes: {
            "data-id": id,
            "data-what": models.about
          },
          childnodes: [{
            nodename: "SUMMARY",
            childnodes: node
          }]
        }];
      } else td.childnodes = node;
      return td;
    },
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
            html.orgs.push(v.name);
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