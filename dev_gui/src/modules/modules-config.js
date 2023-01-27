export const models = {
  user: 'user',
  projid: 'projid',
  project: 'project',
  contact: 'contact',
  instr: 'instr',
  taxo: 'taxo',
  settings: 'settings',
  help: 'help',
  privileges: 'privileges',
  fields: 'fields'
};
// to remove
export const alertconfig = {
  danger: 'danger',
  info: 'info',
  warning: 'warning',
  dismiss_selector: '[data-dismiss]',
  selector: '.alert',
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
  input: 'form-input',
  selected: 'selected',
};
export const domselectors = {
  close: '.close',
};
export const default_messages = {
  wait: 'Please wait...'
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