export const models = {
  user: 'user',
  collection: 'collection',
  id: 'id',
  project: 'project',
  projid: 'projid',
  sampleid: 'sampleid',
  contact: 'contact',
  managers: 'managers',
  annotators: 'annotators',
  about: 'about',
  viewers: 'viewers',
  instr: 'instr',
  taxo: 'taxo',
  taxotree: 'taxotree',
  settings: 'settings',
  help: 'help',
  privileges: 'privileges',
  fields: 'fields',
  jobs: 'jobs,',
  controls: "controls",
  imports: "imports",
};
// to remove
export const alertconfig = {
  danger: 'danger',
  info: 'info',

  warning: 'warning',
  css: {
    alert: 'alert',
    confirm: 'confirm',
    inverse: 'inverse',
  },
  types: {
    confirm: 'confirm',
    info: 'info',
    warning: 'warning',
    danger: 'danger',
    error: 'error'
  },
  dismiss_selector: '[data-dismiss]',
  selector: '.alert',
  domselectors: {
    alert: '.js-alert',
    action: '[data-action="alert-confirm"]',
    buttons: '.btn-group',
    message: '.message',
  },
  confirm_selector: '.alert-confirm'

}
export const typeimport = {
  taxo: models.taxo,
  privileges: models.privileges,
  settings: models.settings
};
export const css = {
  hide: 'hide',
  right: 'align-right',
  number: "number",
  input: 'form-input',
  selected: 'selected',
  disabled: 'disabled',
  error: 'err',
  wait: 'wait',
  active: 'active',
  modal: 'modal',
  centered: 'centered',
  open: 'open',
  progress: "progress",
  peerchecked: 'peer-checked',
  hidevscroll: 'hidevscroll',
  component: {
    tabs: {
      name: 'js-tabs'
    },
    autocomplete: {
      tomselected: 'tomselected'
    },
    table: {
      tip: 'tip',
      controls: 'is-controls'
    }
  }
};
export const domselectors = {
  close: '.close',
  projid: 'projid',
  component: {
    tabs: {
      ident: 'js-tabs',
      tab: '.tab',
      tabcontent: '.tab-content',
      tabcontrol: '.tab-control'
    },
    modal: {
      ident: 'js-modal',
      help: '.modal-help',
      mainhelp: '#main-help',
      modaltitle: '.modal-title',
      modalimportzone: '.modal-title',
      modalcontent: '.modal-content',
      modaloverlay: '.modal-overlay',
      modalcontainer: '.modal-container',
      popup: '.modal-popup',
    },
    tomselect: {
      ident: 'js-autocomplete',
      item: '.item',
      tsdelet: '.ts-delet'
    },
    import: {
      zoneimport: '.zone-import'
    },
    navigation: {
      burgermenu: '.burger',
    },
    tree: {
      ident: 'simple-tree'
    }
  }
};
export const default_messages = {
  wait: 'Please wait...',
  dataloaded: 'Data loaded. Displaying...'
};
export const rights = {
  manage: "Manage",
  annotate: "Annotate",
  view: "View"
};
export const defined_privileges = {
  managers: rights.manage,
  viewers: rights.view,
  annotators: rights.annotate
}

export const filter_files = {
  images: "png,jpeg,jpg,gif",
  tsv: "txt,tsv,zip, gzip,gz"
}