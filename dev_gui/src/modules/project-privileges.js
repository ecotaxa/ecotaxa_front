// privileges of a project
// line with member name , priviliege , is contact , and delete functionality
import DOMPurify from 'dompurify';
import {
  alertconfig,
  AlertBox
} from "../modules/alert-boxes.js";
import {
  JsTomSelect
} from "../modules/js-tom-select.js";
import {
  className
} from '../modules/utils.js';
import {
  rights,
  defined_privileges
} from '../modules/modules-config.js';
const err_messages = {
  oneatleast: 'oneatleast',
}
let instance = null;
export class ProjectPrivileges {
  //TODO: rewrite to not depend on DOM select
  options;
  alerts = [];
  // current user id;
  current_uid;
  fieldset;
  fieldset_alert_zone;
  // unique users
  constructor(options = {}) {
    if (!instance) {
      const defaultOptions = {
        groupid: "#section-privileges",
        separ: '.new-privilege',
        addbtn: '[data-add="block"]',
        target: 'member',
        ident: 'member',
        privilege: 'privilege',
        delet: 'delet',
        contact: 'contact',
        contactfieldname: 'contact_user_id',

      };
      this.options = Object.assign({}, defaultOptions, options);
      this.fieldset = document.querySelector(this.options.groupid);
      if (!this.fieldset) return;
      this.fieldset_alert_zone = this.fieldset.querySelector('.tab-content') ? this.fieldset.querySelector('.tab-content') : this.fieldset;
      this.options.separ = this.options.separ instanceof HTMLElement ? this.options.separ : (document.querySelector(this.options.separ) ? document.querySelector(this.options.separ) : null);
      this.options.addbtn = this.options.addbtn instanceof HTMLElement ? this.options.addbtn : document.querySelector(this.options.addbtn);
      if (this.options.addbtn) this.addListener();
      const lines = this.fieldset.querySelectorAll('[data-block="' + this.options.target + '"]');
      this.current_uid = this.fieldset.dataset.u;

      lines.forEach((line) => {
        this.activateEvents(line);
      });
      instance = this;
    }
    return instance;
  }

  newLine(ret = false, check = 0) {
    let line;
    if (check > 0) {
      line = this.getLinePrivilege(check);
      if (line) return line;
    }
    const lines = this.fieldset.querySelectorAll('[data-block="' + this.options.target + '"]');

    if (lines.length === 0) return;
    const n = lines.length - 1;
    line = lines[n];
    if (line !== null) {
      line = this.clearLine(line.cloneNode(true), n, (this.options.separ ? this.options.separ : line));

      this.activateEvents(line);

    }
    if (ret === true) return line;
  }

  addListener() {
    this.options.target = (this.options.addbtn.dataset.target) ? this.options.addbtn.dataset.target : this.options.target;
    this.options.addbtn.addEventListener('click', async (e) => {
      e.preventDefault();
      this.newLine();
    })
  }

  clearLine(line, n, separ = null) {
    /*clean line element */

    let has_autocomplete = null;
    line.dataset.mod = '';
    line.disabled = false;
    const elems = line.querySelectorAll('[data-elem]');
    elems.forEach((elem) => {
      // change loop index - necessary for tailwindcss peerchecked to work otherwise not if name ends with []
      //remove components
      const rms = elem.querySelectorAll('[data-component]')
      rms.forEach((rm) => {
        switch (rm.dataset.component) {
          case 'tom-select':
            rm.remove();
            break;
        }
      })
      // clean and reset events
      const els = elem.querySelectorAll('input, select, label');
      els.forEach((el) => {

        el.disabled = false;
        if (separ) { // change names and id when adding a new row - not if clear only
          const keys = ['id', 'for', 'aria-controls', 'name'];
          keys.forEach((key) => {
            let val = el.getAttribute(key);
            if (val !== null) {
              if (key === 'name') val = val.replace('[' + n + ']', '[' + (n + 1) + ']');
              else val = val.replace('_' + n, '_' + (n + 1));
              el.setAttribute(key, val);
            }
          });
        }
        switch (el.tagName.toLowerCase()) {
          case 'input':
            //el.indeterminate = true;
            el.checked = false;
            // disable contact as privilege is empty
            if (el.name == this.options.contactfieldname) {
              el.value = "0";
              el.disabled = true;
            }
            break;
          case 'select':
            el.selectedIndex = -1;
            break;
          case 'label':
            el.classList.remove('peer-checked');
            break;
        }
        if (el.tomselect) {
          has_autocomplete = el;
          el.tomselect.clear();
          el.tomselect.destroy();

        }
        if (el.classList.contains('tomselected')) {
          has_autocomplete = el;
          el.classList.forEach(cl => {
            if (cl.indexOf('ts-') == 0) el.classList.remove(cl);
          })
          el.classList.remove('tomselected');
          if (el.type == "select-one") delete el.type;

        }

      })

    })
    /* add functionnalities */
    if (separ) {
      line.classList.add('new');
      separ.after(line);
    }
    /* clear and add tom-select functionalities - only after adding line to the dom*/
    if (has_autocomplete !== null) {
      const jsTomSelect = new JsTomSelect();
      jsTomSelect.apply(has_autocomplete);
      has_autocomplete.tomselect.clearOptions();
      let options = this.fieldset.dataset.options;
      options = (options) ? options : [];
      has_autocomplete.tomselect.addOptions(options);
    };


    return line;
  }

  setLine(line, mb = {
    key: '',
    value: ''
  }, priv, ct) {

    priv = defined_privileges[priv] ? defined_privileges[priv] : defined_privileges.viewers;
    if (!priv) return;
    const {
      member,
      privs,
      contact,
      delet
    } = this.getInputs(line, priv);

    if (!member || !privs || !contact || !delet) return;
    // sanitize

    mb.key = DOMPurify.sanitize(mb.key);
    mb.value = DOMPurify.sanitize(mb.value);
    if (member.tomselect) {

      let addmb = {}
      addmb[member.tomselect.settings.valueField] = mb.key;
      addmb[member.tomselect.settings.labelField] = mb.value;
      if (!member.tomselect.getOption(mb.key)) member.tomselect.addOption(addmb);
      member.tomselect.addItem(mb.key, false);
      member.tomselect.refreshOptions();
    } else {
      const selected = member.querySelector('select option[value="' + mb.key + '"]');
      if (selected) selected.selected = true;
      else member.insertAdjacentHTML('beforeend', '<option value="' + mb.key + '" selected>' + mb.value + '</option>');

    }
    privs.checked = true;
    contact.value = mb.key;
    if (priv === rights.manage) {
      contact.disabled = false;
      if (ct === true) contact.checked = true;
    }

  }
  getInputs(line, priv = false) {

    const member = line.querySelector("[name*='[" + this.options.ident + "]']");

    let privs;
    if (priv) {
      privs = line.querySelector('input[name*="[' + this.options.privilege + ']"][value="' + priv + '"]');
    } else privs = line.querySelectorAll('input[name*="[' + this.options.privilege + ']"]');
    const contact = line.querySelector('input[name="' + this.options.contactfieldname + '"]');
    const delet = line.querySelector("input[name*='[" + this.options.delet + "]']");

    return {
      member: member,
      privs: privs,
      contact: contact,
      delet: delet
    };
  }
  async importPrivileges(privileges, clear = false, contact = null, importedtag = null, dismiss = null) {
    let lastline = (clear === true) ? null : true;
    try {
      Object.entries(privileges).forEach(([priv, members]) => {
        members.forEach((member) => {
          if (!lastline) lastline = this.clearAll(true);
          else lastline = this.newLine(true, member.id);

          if (lastline) {

            this.setLine(lastline, {
              key: member.id,
              value: member.name,
            }, priv, (contact && (parseInt(contact.id) === parseInt(member.id))));
            if (importedtag) importedtag(lastline);
            if (dismiss) dismiss();
          }

        });

      });
      return true;
    } catch (err) {

      await new AlertBox().build('importpriverror', alertconfig.danger, 'importpriv', {
        dismissible: true
      });
      console.log('err', err)
      return false;
    }
  }
  activateEvents(line) {
    if (!line) return;
    const {
      member,
      privs,
      contact,
      delet
    } = this.getInputs(line);
    if (!member || !privs || !contact || !delet) {
      return;
    }
    const siblings = s => [...s.parentElement.children].filter(c => c.nodeType == 1 && c != s && c.classList.contains('row') && c.dataset.block !== null && c.dataset.block === this.options.target);

    // enable/disable contact when privilege changes
    const lineSettings = (pr, ct, dl, synchro = false) => {

      if (pr && pr.value === rights.manage) {
        // manager - can't delete line - can choose as contact
        dl.disabled = true;
        ct.disabled = false;
        //  if (ct.checked) ct.checked = true;
      } else {
        // not manager - can delet line - cannot chose as contact
        //  if (ct.checked === true) ct.dispatchEvent(new Event('click'));
        ct.checked = false;
        dl.disabled = false;
        ct.disabled = true;
      }

      if (synchro === true) {
        synchroSiblings(line);
      }
    }
    const synchroSiblings = (line) => {
      const lns = siblings(line);
      lns.forEach((ln) => {
        const dl = ln.querySelector("input[name*='[" + this.options.delet + "]']");
        const ct = ln.querySelector('input[name="' + this.options.contactfieldname + '"]');
        const pr = ln.querySelector('input[name*="[' + this.options.privilege + ']"]:checked');
        lineSettings(pr, ct, dl, false);

      })
    }

    member.addEventListener('change', (e) => {
      contact.value = member.value;
    })

    privs.forEach((priv) => {
      priv.addEventListener('change', (e) => {
        if (priv.checked) lineSettings(priv, contact, delet, false);
      });

      if (priv.checked) lineSettings(priv, contact, delet, false);
    })

    contact.addEventListener('change', (e) => {
      if (e.target.checked) delet.disabled = true;
      else delet.disabled = false;
      const priv = line.querySelector('input[name*="[' + this.options.privilege + ']"]:checked');
      lineSettings(priv, contact, delet, true);
      // enable otherwise

    })

    // delet ok for all when new line
    //
    delet.addEventListener('click', (e) => {
      // at least one priv line

      const lines = this.fieldset.querySelectorAll('[data-block="' + this.options.target + '"]:not([data-mod="remove"])');
      if (lines.length <= 1 && e.target.checked) {
        delet.disabled = true;
        delet.checked = false;
        new AlertBox(this.alerts[err_messages.oneatleast]).build(err_messages.oneatleast, alertconfig.warning, (e.target.id || '0'), {
          dismissible: true,
        });
        return;
      } else if (e.target.checked) {
        this.dissmissMessage(err_messages.oneatleast);
        if (line.classList.contains('new')) {
          line.remove();
        } else {
          line.setAttribute('data-mod', 'remove');
          privs.forEach(priv => {
            priv.disabled = true;
            priv.checked = false;
          })
          contact.checked = false;
          contact.disabled = true;
          member.disabled = true;
        }
      } else {
        line.removeAttribute('data-mod');
        privs.forEach(priv => priv.disabled = false);
        contact.disabled = false;
        member.disabled = false;
      }
    });
    // delet mouseover - explain why it is disabled when manage is checked
    delet.addEventListener('mouseover', (e) => {
      if (e.target.disabled) {
        let pr = line.querySelector('input[name*="[' + this.options.privilege + ']"]:checked');
        if (!pr) return;
        pr = pr.value.toLowerCase()
        e.target.title = (e.target.dataset[pr]) ? e.target.dataset[pr] : e.target.title
      }
    })
    // disable delet if user is the only manager
    if (this.current_uid === member.value) delet.disabled = true;


  }

  // send clean data on submit
  async cleanPrivileges() {
    // check managers and contact_user_id on submit

    const checkContact = async () => {
      // check if one manager at least
      const managers = this.fieldset.querySelectorAll('[name*="[' + this.options.privilege + ']"][value="' + rights.manage + '"]:checked');
      let n = managers.length;

      if (n === 0) {
        await new AlertBox().build('nomanager', alertconfig.danger, id, {
          dismissible: true,
        });
        return false;
      }
      // check contact
      const contact = this.fieldset.querySelector('[name="' + this.options.contactfieldname + '"]:checked');

      if (contact === null) {
        this.alerts[err_messages.nocontact] = new AlertBox(this.alerts[err_messages.nocontact]).build(err_messages.nocontact, alertconfig.danger, this.fieldset_alert_zone, {
          dismissible: true
        });
        return false;
      }
      if (this.alerts[err_messages.nocontact]) this.alerts[err_messages.contact].dismissAlert();
      return true;
    }
    const hasMember = (line) => {
      const member = line.querySelector('[name*="[' + this.options.ident + ']"]');
      return (member.value);
    }
    const hasPriv = (line) => {
      const priv = line.querySelector('[name*="[' + this.options.privilege + ']"]:checked');
      if (priv && priv.value) return true;
      return false;
    }
    const formatPrivilege = (line) => {

      const els = line.querySelectorAll('[name*="members["');
      els.forEach((el) => {
        let name = el.name;
        name = name.split('[');
        name.pop();
        el.name = name.join('[');
        if (el.name.indexOf('[' + this.options.privilege + ']') > 0) {
          el.type = 'checkbox';
          el.classList.add('hidden');
        }

      })
    }
    const hascontact = await checkContact();
    if (hascontact === true) {
      const lines = this.fieldset.querySelectorAll('[data-block="' + this.options.target + '"]');
      let n = lines.length;
      let verif = true;
      for (const line of lines) {
        if (line.dataset.mod && line.dataset.mod === 'remove') {
          if (n > 1) {
            line.remove();
            n--;
          } else return false;
        } else if (!hasMember(line)) {
          const lineno = line.querySelector('[name*="[' + this.options.ident + ']"]');
          lineno.focus();
          if (lineno.tomselect) lineno.tomselect.focus();
          this.alerts[err_messages.emptyname] = await new AlertBox(this.alerts[err_messages.emptyname]).build(err_messages.emptyname, alertconfig.warning, line, {
            dismissible: true,
            insertafter: true,
          });
          const resp = false; // no confimbox just wait for user action
          // callback when confirmbox response is chosen if 'confirm'
          if (resp === true) {
            if (n > 1) {
              line.remove();
              n--;
            } else return false;

          } else return false;
        } else if (!hasPriv(line)) {
          await new AlertBox().build('uhasnopriv', alertconfig.warning, line, {
            dismissible: true,
            insertafter: true,
          });
          verif = false;
        }
      }
      if (!verif) return verif;
      for (const line of lines) {
        formatPrivilege(line);
      }

      if (n === 0) {
        // to position error messages correctly when js-tabs is activated

        await new AlertBox().build('nobody', alertconfig.danger, this.fieldset_alert_zone, {
          dismissible: true,
        });
        return false;
      }
      return true;
    } else return false;
  }
  getLinePrivilege(id) {
    let privilege = null;
    const lines = this.fieldset.querySelectorAll('[data-block="' + this.options.target + '"]')
    for (const line of lines) {
      if (parseInt(line.querySelector('[name*="[' + this.options.ident + ']"]').value) === parseInt(id)) {
        privilege = line;
        break;
      }
    }

    return privilege;
  }

  clearAll(ret = false) {
    const lines = this.fieldset.querySelectorAll('[data-block="' + this.options.target + '"]');

    lines.forEach((line, index) => {
      const {
        member,
        privs,
        contact,
        delet
      } = this.getInputs(line);
      if (index > 0 && (this.current_uid !== member.value)) line.remove();
    });
    //
    this.clearLine(lines[0], 0);
    this.activateEvents(lines[0]);
    if (ret === true) return lines[0];
  }
  // hook on form submit verify privileges
  async submitPrivileges() {
    const resp = await this.cleanPrivileges();
    return resp;
  }
}