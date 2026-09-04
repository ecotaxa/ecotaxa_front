export const models = {
  user: 'user',
  person:'person',
  collection: 'collection',
  id: 'id',
  project: 'project',
  projid: 'projid',
  sampleid: 'sampleid',
  contact: 'contact',
  contact_user:'contact_user',
  managers: 'managers',
  annotators: 'annotators',
  about: 'about',
  viewers: 'viewers',
  instr: 'instr',
  taxo: 'taxo',
  transforms:'transforms',
  recastid:'recast_id',
  taxotree: 'taxotree',
  settings: 'settings',
  help: 'help',
  privileges: 'privileges',
  fields: 'fields',
  jobs: 'jobs,',
  controls: "controls",
  imports: "imports",
  commonserver: 'commonserver',
  organisation: 'organisation',
  renamingrules: 'renamingrules',
  formulae: 'formulae'
};

export const typeimport = {
  taxo: models.taxo,
  privileges: models.privileges,
  settings: models.settings,
  project: models.project,
  renamingrules:models.renamingrules,
  formulae: models.formulae
};
export const css = {
  hide: 'hide',
  right: 'align-right',
  relative: 'relative',
  number: "number",
  input: 'form-input',
  selected: 'selected',
  disabled: 'disabled',
  error: 'err',
  console: 'console',
  icon: 'icon',
  wait: 'wait',
  active: 'active',
  modal: 'modal',
  absolute: 'absolute',
  open: 'open',
  progress: "progress",
  peerchecked: 'peer-checked',
  hidevscroll: 'hidevscroll',
  tip: 'tip',
  tooltip:'tooltip',
  worms:'worms',
  deprecated:'deprecated',
  notused:'notused',
  component: {
    tabs: {
      name: 'js-tabs'
    },
    autocomplete: {
      tomselected: 'tomselected',

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
    form: {
      ident: '.js-submit',
      formbox: '.form-box'
    },
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
      name: 'tom-select',
      ident: 'js-autocomplete',
      item: '.item',
      tsdelet: '.ts-delet',
      line:'.ts-line'
    },
    privileges: {
      ident: 'js-privileges',
    },
    import: {
      zoneimport: '.zone-import'
    },
    navigation: {
      burgermenu: '.burger',
    },
    tree: {
      ident: 'simple-tree'
    },
    alert: {
      ident: '.alert',
      danger: '.alert.danger'
    },
  }
};
export const objaccept = {
  "image/*": [".png", ".jpeg", ".jpg", ".gif"],
  "text/plain": [".txt"],
  "text/tab-separated-values": [".tsv"],
  "application/zip": [".zip"],
  "application/gzip": [".gz"],
  "application/x-bzip": [".bz"],
  "application/x-bzip2": [".bz2"]
};
export const filter_files = {
  images: objaccept["image/*"].map(ext => ext.slice(1)).join(','),
  tsv: Object.entries(objaccept)
    .filter(([mime]) => mime !== "image/*")
    .flatMap(([, exts]) => exts.map(ext => ext.slice(1)))
    .join(',')
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