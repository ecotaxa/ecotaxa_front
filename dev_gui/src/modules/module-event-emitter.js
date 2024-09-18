function createModuleEventEmitter(event, callback) {
  /**
   * Add custom event listener
   * @param  {String} event
   * @param  {Function} callback
   * @return {Void}
   */
  const _events = {};

  function on(event, callback) {
    _events[event] = _events[event] || []
    _events[event].push(callback)
  }

  function once(event, callback) {
    callback.once = true;
    on(event, callback);
  }

  function off(event, callback) {
    if (event in _events === false) return;
    _events[event].splice(_events[event].indexOf(callback), 1)
  }

  function emit(event, ...args) {
    if (event in _events === false) return;
    else {
      for (const action of _events[event]) {
        action(...args);
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
export {
  ModuleEventEmitter
}