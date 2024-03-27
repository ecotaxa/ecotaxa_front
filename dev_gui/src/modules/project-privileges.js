// privileges of a project
// line with member name , priviliege , is contact , and delete functionality
import DOMPurify from 'dompurify';
import {
  FormSubmit,
} from "../modules/form-submit.js";
import {
  JsTomSelect
} from "../modules/js-tom-select.js";
import {
  rights,
  defined_privileges,
  domselectors,
  css
} from '../modules/modules-config.js';
const dynamics = {};
export class ProjectPrivileges {
  //TODO: rewrite to not depend on DOM select
  options;
  // current user id;
  keymessages = {
    oneatleast: 'oneatleast',
    nomanager: 'nomanager',
    nocontact: 'nocontact',
    uhasnopriv: 'uhasnopriv',
    importpriverror: 'importpriverror',
    emptyname: 'emptyname'
  };
  current_uid;
  fieldset;
  fieldset_alert_zone;
  linemodel;
  currentlist = {};
  // unique users
  constructor(item, options = {}) {
    if (item === null || (item instanceof HTMLElement === false)) return;
    if (!item.jsprivileges) {
      const defaultOptions = {
        separ: '.new-privilege',
        addbtn: '[data-add="block"]',
        target: 'member',
        ident: 'member',
        privilege: 'privilege',
        delet: 'delet',
        contact: 'contact',
        contactfieldname: 'contact_user_id',
        domselectors: {
          tabcontent: '.tab-content'
        }
      };
      this.options = Object.assign({}, defaultOptions, options);
      // attach messages for fields and alerts system
      this.fieldset = item;
      if (!this.fieldset) return window.alertbox.classError();
      this.fieldset_alert_zone = item.querySelector(this.options.domselectors.tabcontent) ? item.querySelector(this.options.domselectors.tabcontent) : item;
      this.options.separ = this.options.separ instanceof HTMLElement ? this.options.separ : (document.querySelector(this.options.separ) ? document.querySelector(this.options.separ) : null);
      this.options.addbtn = this.options.addbtn instanceof HTMLElement ? this.options.addbtn : document.querySelector(this.options.addbtn);
      if (this.options.addbtn) this.addListener();
      const lines = this.fieldset.querySelectorAll('[data-block="' + this.options.target + '"]');
      if (lines.length === 0) return window.alertbox.classError();
      this.linemodel = this.clearLine(lines[0].cloneNode(true), 0, -1);
      this.linemodel.classList.add(css.hide);
      this.linecontainer = lines[0].parentElement;
      if (this.linecontainer === null) return window.alertbox.classError();
      this.current_uid = this.fieldset.dataset.u;
      lines.forEach((line, i) => {
        line.dataset.n = i;
        this.activateEvents(line);
      });
      // add messaging functionalities
      const form = this.fieldset.closest('form');
      if (form) {
        if (form.formsubmit) {
          form.formsubmit.addHandler('validate', () => {
            return this.validateFields();
          });
          form.formsubmit.addHandler('submit', () => {
            return this.formatPrivileges();
          });
        } else form.addEventListener('submit', async (e) => {
          const resp = this.validateFields();
          if (resp === false) e.preventDefault();
          else return this.formatPrivileges();
        });
      };
      this.orderRows();
      item.jsprivileges = this;
    }
    return item.jsprivileges;
  }

  newLine(ret = false, check = 0) {
    const lines = this.linecontainer.children;
    let newline;
    if (lines.length && check > 0) newline = this.getLinePrivilege(check);
    if (newline) return newline;
    newline = this.linemodel.cloneNode(true);
    newline.classList.remove(css.hide);
    if (newline) {
      this.linecontainer.append(newline);
      const nn = (this.fieldset.dataset.n) ? parseInt(this.fieldset.dataset.n) + 1 : lines.length;
      newline = this.clearLine(newline, -1, nn, (this.options.separ ? this.options.separ : null));
      newline.dataset.n = nn;
      this.fieldset.dataset.n = nn;
      this.activateEvents(newline, (check === 0));

      if (ret === true) return newline;
    }
    return null;
  }

  addListener() {
    this.options.target = (this.options.addbtn.dataset.target) ? this.options.addbtn.dataset.target : this.options.target;
    this.options.addbtn.addEventListener('click', async (e) => {
      e.preventDefault();
      this.newLine();
    })
  }
  indexElement(el, n, nn) {
    // order is important
    const keys = ['id', 'name', 'for', 'aria-controls'];
    keys.forEach((key) => {
      let val = el.getAttribute(key);
      if (val !== null) {
        if (key === 'name') val = val.replace('[' + n + ']', '[' + (nn) + ']');
        else val = val.replace('_' + n, '_' + (nn));
        el.setAttribute(key, val);
      }
    });
    return el;
  }
  indexLine(line, n, nn = null) {
    nn = (nn === null) ? n + 1 : nn;
    const elems = line.querySelectorAll('[data-elem]');
    elems.forEach((elem) => {
      // change loop index - necessary for tailwindcss peerchecked to work otherwise not if name ends with []
      // clean and reset events
      const els = elem.querySelectorAll('input, select, label, div');
      els.forEach((el) => {
        if (n !== null) el = this.indexElement(el, n, nn);
      });
    });
    line.dataset.n = parseInt(nn);
    this.fieldset.dataset.n = (this.fieldset.dataset.n && this.fieldset.dataset.n >= nn) ? this.fieldset.dataset.n : nn;
    return line;
  }
  clearLine(line, n = null, nn = null, separ = null) {
    /*clean line element */
    line.dataset.mod = '';
    line.disabled = false;
    const elems = line.querySelectorAll('[data-elem]');
    elems.forEach((elem) => {
      // change loop index - necessary for tailwindcss peerchecked to work otherwise not if name ends with []
      // clean and reset events
      const els = elem.querySelectorAll('input, select, label, div');
      els.forEach((el) => {
        el.disabled = false;
        if (n !== null) { // change names and id when adding a new row - not if clear only
          nn = (nn === null) ? n + 1 : nn;
          el = this.indexElement(el, n, nn);
        }
        switch (el.tagName.toLowerCase()) {
          case 'input':
            el.checked = false;
            // disable contact as privilege is empty
            if (el.name == this.options.contactfieldname) {
              el.value = "0";
              el.disabled = true;
            }
            break;
          case 'select':
            // remove options except the first one with select
            Array.from(el.options).forEach(option => {
              if (parseInt(option.value) > 0) option.remove();
            });
            // todo shoulkd have been removed
            el.selectedIndex = 0;
            if (!el.tomselect) {
              ['tom-select', 'tomselected', 'ts-hidden-accessible'].forEach(cl => {
                el.classList.remove(cl);
              });
            } else el.tomselect.destroy();
            break;
          case 'div':
            if (n !== null && el.dataset.component) el.remove();
            break;
        }

      })

    })
    /* add functionnalities */
    if (separ) {
      line.classList.add('new');
      separ.after(line);
    }

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

    let option = member.querySelector('option[value="' + mb.key + '"]');
    if (option === null) {
      option = document.createElement('option');
      option.value = mb.key;
      option.text = mb.value;
      member.append(option);
    }
    option.selected = true;
    if (!member.tomselect) {
      const jsTomSelect = new JsTomSelect();
      jsTomSelect.applyTo(member);
    }
    privs.checked = true;
    contact.value = mb.key;
    if (priv === rights.manage) {
      contact.disabled = false;
      if (ct === true && !contact.checked) contact.checked = true;
    } else {
      contact.disabled = true;
      contact.checked = false;
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
  async importPrivileges(privileges, replace = false, contact = null, importedtag = null, dismiss = null) {
    if (replace === true) this.clearAll();
    try {
      Object.entries(privileges).forEach(([priv, members]) => {
        members.forEach((member) => {
          const lastline = this.newLine(true, member.id);
          if (lastline) {
            this.setLine(lastline, {
              key: member.id,
              value: member.name,
            }, priv, (contact !== null && (contact.id === member.id)));
            if (importedtag) importedtag(lastline);
          }
          replace = false;
        });
      });
      if (dismiss) dismiss();
      window.alertbox.dismissAlert(this.keymessages.importpriverror);

      this.orderRows();
      return true;
    } catch (err) {
      window.alertbox.renderMessage({
        type: window.alertbox.alertconfig.types.error,
        content: this.keymessages.importpriverror,
        dismissible: true,
        inverse: true
      });
      console.log('err', err);
      return false;
    }
  }
  activateEvents(line, ts = false) {
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
    // activate tom select if needed
    // enable/disable contact when privilege changes
    if (!member.currentlist) member.currentlist = this.currentlist;
    if (member.value && !this.currentlist[member.value]) this.currentlist[member.value] = true;
    if (ts === true && !member.tomselect) {
      const jsTomSelect = new JsTomSelect();
      jsTomSelect.applyTo(member);
    }
    const lineSettings = (pr, ct, dl, synchro = false) => {
      if (pr && pr.checked) {
        pr.checked = true;
        if (window.alertbox.hasMessages(line)) window.alertbox.removeMessage(window.alertbox.alertconfig.types.danger, line, this.keymessages.uhasnopriv);
      }
      if (pr && pr.value === rights.manage) {
        // manager - can't delete line - can choose as contact
        dl.disabled = true;
        ct.disabled = false;
        window.alertbox.dismissAlert(this.keymessages.nomanager);
        if (ct.checked) {
          window.alertbox.dismissAlert(this.keymessages.nocontact);
          ct.dispatchEvent(new Event('valid'));
        }
      } else {
        // not manager - can delet line - cannot chose as contact
        ct.checked = false;
        dl.disabled = false;
        ct.disabled = true;
      }

      if (synchro === true) {
        synchroSiblings(line);
      }
      // dismiss alerts
      if (!dl.ckecked) {
        window.alertbox.dismissAlert(this.keymessages.nobody);
        if (window.alertbox.hasMessages(line)) window.alertbox.removeMessage(window.alertbox.alertconfig.types.danger, line, this.keymessages.oneatleast);
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
      if (parseInt(member.value) > 0 && window.alertbox.hasMessages(member)) window.alertbox.removeMessage(window.alertbox.alertconfig.types.danger, member, this.keymessages.emptyname);
    })
    privs.forEach((priv) => {
      priv.addEventListener('change', (e) => {
        if (priv.checked) lineSettings(priv, contact, delet, false);
      });

      if (priv.checked) lineSettings(priv, contact, delet, false);
    })

    contact.addEventListener('change', (e) => {
      if (contact.checked) {
        delet.disabled = true;
      } else delet.disabled = false;
      const priv = line.querySelector('input[name*="[' + this.options.privilege + ']"]:checked');
      lineSettings(priv, contact, delet, true);
      // enable otherwise
    })
    // delet ok for all when new line
    //

    delet.addEventListener('click', (e) => {
      // at least one priv line
      const deletlabel = delet.closest('label');
      const lines = this.fieldset.querySelectorAll('[data-block="' + this.options.target + '"]:not([data-mod="remove"])');
      if (lines.length <= 1 && e.target.checked) {
        e.preventDefault();
        line.removeAttribute('data-mod');
        member.disabled = false;
        e.target.disabled = true;
        window.alertbox.addMessage(window.alertbox.alertconfig.types.danger, line, this.keymessages.oneatleast, 3000);
        return;
      } else if (e.target.checked) {
        if (window.alertbox.hasMessages(member)) window.alertbox.removeMessage(window.alertbox.alertconfig.types.danger, member);
        if (line.classList.contains('new')) {
          line.remove();
        } else {
          if (deletlabel && deletlabel.dataset.restore) deletlabel.dataset.title = deletlabel.dataset.restore;
          line.setAttribute('data-mod', 'remove');
          privs.forEach(priv => {
            priv.dataset.checked = priv.checked;
            priv.checked = false;
            priv.disabled = true;
          })
          contact.checked = false;
          contact.disabled = true;
          member.disabled = true;
        }
      } else {
        if (deletlabel && deletlabel.dataset.remove) deletlabel.dataset.title = deletlabel.dataset.remove;
        line.removeAttribute('data-mod');
        privs.forEach(priv => {
          priv.disabled = false;
          if (priv.dataset.checked === "true") priv.checked = true;
          else priv.checked = false;
        });

        member.disabled = false;
      }
    });
    // delet mouseover - explain why it is disabled when manage is checked
    delet.addEventListener('mouseover', (e) => {
      if (e.target.disabled) {
        let pr = line.querySelector('input[name*="[' + this.options.privilege + ']"]:checked');
        if (!pr) return;
        pr = pr.value.toLowerCase()
        e.target.dataset.title = (e.target.dataset[pr]) ? e.target.dataset[pr] : e.target.dataset.title
      }
    })
    // disable delet if user is the only manager
    if (this.current_uid === member.value) delet.disabled = true;
  }

  validateFields(add = false) { // check managers and contact_user_id on submit
    const check_contact = () => {
      // check if one manager at least
      const managers = this.fieldset.querySelectorAll('[name*="[' + this.options.privilege + ']"][value="' + rights.manage + '"]:checked');
      if (managers.length === 0) {
        window.alertbox.renderMessage({
          type: window.alertbox.alertconfig.types.error,
          content: this.keymessages.nomanager,
          dismissible: true,
          inverse: true
        });
        this.tabError(true);
        return false;
      } else {
        window.alertbox.dismissAlert(this.keymessages.nomanager);
        this.tabError(false);
      }
      // check contact

      const contact = this.fieldset.querySelector('[name="' + this.options.contactfieldname + '"]:checked');
      if (contact === null) {
        window.alertbox.renderMessage({
          type: window.alertbox.alertconfig.types.danger,
          content: this.keymessages.nocontact,
          dismissible: true,
          inverse: true
        });
        this.tabError(true);
        return false;
      }
      window.alertbox.dismissAlert(this.keymessages.nocontact);
      this.tabError(false);
      return true;
    }
    const has_member = (member) => {
      return (member.value);
    }
    const has_priv = (line) => {
      const priv = line.querySelector('[name*="[' + this.options.privilege + ']"]:checked');
      if (priv && priv.value) return true;
      return false;
    }
    const lines = this.fieldset.querySelectorAll('[data-block="' + this.options.target + '"]');
    let n = lines.length;
    let verif = true;
    for (const line of lines) {
      const member = line.querySelector('[name*="[' + this.options.ident + ']"]');
      if (line.dataset.mod && line.dataset.mod === 'remove') {
        if (n > 1) {
          line.remove();
          n--;
        } else return false;
      } else if (!has_member(member)) {
        window.alertbox.addMessage(window.alertbox.alertconfig.types.danger, member, this.keymessages.emptyname);
        member.focus();
        const resp = false; // no confimbox just wait for user action
        // callback if confirmbox response is chosen if 'confirm'
        if (resp === true) {
          if (n > 1) {
            line.remove();
            n--;
          } else return false;
        } else return false;
      }
      if (!has_priv(line)) {
        window.alertbox.addMessage(window.alertbox.alertconfig.types.danger, line, this.keymessages.uhasnopriv);
        verif = false;
      } else if (window.alertbox.hasMessages(line)) window.alertbox.removeMessage(window.alertbox.alertconfig.types.danger, line, this.keymessages.uhasnopriv);

    }
    if (n === 0) {
      window.alertbox.renderMessage({
        type: window.alertbox.alertconfig.types.danger,
        content: this.keymessages.nobody,
        dismissible: true,
        inverse: true
      });
      return false;
    } else window.alertbox.dismissAlert(this.keymessages.nobody);
    const hascontact = check_contact();
    return (hascontact && verif);
  }

  formatPrivileges() {
    const lines = this.fieldset.querySelectorAll('[data-block="' + this.options.target + '"]');
    const format_privilege = (line) => {
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

      });
    }

    lines.forEach(line => {
      format_privilege(line);
    });
    return true;
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
  clearAll() {
    let lines = this.fieldset.querySelectorAll('[data-block="' + this.options.target + '"]');
    lines.forEach((line, index) => {
      line.remove();
    });

  }
  orderRows() {
    const lines = Array.from(this.fieldset.querySelectorAll('[data-block="' + this.options.target + '"]'));
    if (lines.length > 2) {
      try {
        const rightssorted = Object.values(rights);
        lines.sort((linea, lineb) => {
          const a = this.getInputs(linea);
          const b = this.getInputs(lineb);
          const nameb = new String(b.member.options[b.member.selectedIndex].text).toLowerCase().split(' ')
          const namea = new String(a.member.options[a.member.selectedIndex].text).toLowerCase().split(' ');
          const priva = Array.from(a.privs).filter(priv => (priv.checked));
          const privb = Array.from(b.privs).filter(priv => (priv.checked));
          const compa = (+!a.contact.checked) + ` ` + rightssorted.indexOf(((priva.length) ? priva[0].value : null)) + ` ` + ((namea.length > 1) ? namea.pop() + ` ` + namea[0] : namea[0]);
          const compb = (+!b.contact.checked) + ` ` + rightssorted.indexOf(((privb.length) ? privb[0].value : null)) + ` ` + ((nameb.length > 1) ? nameb.pop() + ` ` + nameb[0] : nameb[0]);
          if (compb > compa) return -1;
          else if (compa > compb) return 1;
          else return 0;
        })
        const clone = this.linecontainer;
        lines.forEach((line, i) => {
          clone.appendChild(line);
        });
      } catch (err) {
        console.log('err not sorted', err);
      }
    }
  }

  tabError(on) {
    const tab = (this.fieldset.classList.contains(domselectors.component.tabs.tab.substr(1))) ? this.fieldset : ((this.fieldset.parentElement.classList.contains(domselectors.component.tabs.tab.substr(1))) ? this.fieldset.parentElement : null);
    if (tab === null) return;
    if (on === true) tab.classList.add(css.error);
    else tab.classList.remove(css.error);
  }
}