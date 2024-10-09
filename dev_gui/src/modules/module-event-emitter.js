import {
  AlertBox
} from '../modules/alert-box.js';
import {
  generate_uuid
} from '../modules/utils.js';

function CustomEventEmitter(event, detail) {
  /**
   * Add custom event listener
   * @param  {Object} event {name:{String}, listener:{Object}}
   * @param  {Object} detail
   * @return {Void}
   */
  const custom = new CustomEvent(event.name, {
    detail: detail,
  })
  event.listener.dispatchEvent(custom);
}


function ObjectEventEmitter(event, callback, listener = window) {
  /**
   * Add custom event listener
   * @param  {String} event
   * @param  {Function} callback
   * @param  {Object} listener
   * @return {Object} listener
   */
  listener.on = function(event, callback) {
    this._events = this._events || {}
    this._events[event] = this._events[event] || []
    this._events[event].push(callback)
  }
  listener.once = function(event, callback) {
    callback.once = true;
    self.on(event, callback);
  }
  listener.off = function(event, callback) {
    this._events = this._events || {}
    if (event in this._events === false) return;
    this._events[event].splice(this._events[event].indexOf(callback), 1)
  }
  listener.emit = function(event, ...args) {
    if (event in this._events === false) return;
    else {
      for (const action of this._events[event]) {
        action(...args);
        if (action.once) break;
      }
    }
  }
  return listener;
}

function createModuleEventEmitter(event, callback) {
  /**
   * Add event bus global or with listener
   * @param  {String} event
   * @param  {Function} callback
   * @return {Void}
   */
  const _events = [];
  const all = 'ALL_EVENTS';

  function on(event, callback, listener = all) {
    _events[listener] = _events[listener] || [];
    _events[listener][event] = _events[listener][event] || [];
    _events[listener][event].push(callback);
  }

  function once(event, callback, listener = all) {
    callback.once = true;
    on(event, callback, listener);
  }

  function off(event, callback, listener = all) {
    if (event in _events[listener] === false) return;
    _events[listener][event].splice(_events[listener][event].indexOf(callback), 1);
  }

  function emit(event, e = {}, listener = all) {
    _events[listener] = _events[listener] || [];
    if (event in _events[listener] === false) return;
    else {
      for (const action of _events[listener][event]) {
        action(e);
        if (action.once) break;
      }
    }
  }

  return {
    on,
    once,
    off,
    emit
  }
}

const ModuleEventEmitter = await createModuleEventEmitter();
// each function or class which communicates need and event object and optional emitEvent function

// global capture errors
const eventnames = {
  error: 'error'
}
ModuleEventEmitter.on(eventnames.error, (e) => {
  AlertBox.renderAlert({
    type: AlertBox.alertconfig.types.error,
    content: e,
    inverse: true,
    dismissible: true
  });
});
export {
  ModuleEventEmitter
}