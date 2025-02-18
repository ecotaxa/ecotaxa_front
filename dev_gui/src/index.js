import stylecss from '../src/css/style.css';
import {
  AlertBox
} from '../src/modules/alert-box.js';
import {
  JsComponents
} from '../src/modules/js-components.js';
import {
  ActivItems
} from '../src/modules/activ-items.js';
import {
  ActivRequest
} from "../src/modules/activ-request.js";
// initializze tools and triggered tools
function loadUI() {
  async function handler() {
    // enhance ui activate components  js js-componentname
    await JsComponents.applyTo(document);
    /* fetch request -modal - contextual help */
    ActivRequest.applyTo(document);
    /*** activate data-action  **/
    ActivItems.applyTo(document);
    // global alert dialog system
    AlertBox.applyTo(document);
  };
  if (document.readyState === "complete") {
    handler();
  } else {
    window.addEventListener('load', handler);
    return () => window.removeEventListener('load', handler);
  }
}
loadUI();
// 'unload'do not use for the moment as it changes history back
/*window.addEventListener('unload', (e) => {
  //  ecotaxaStorage.clear();
});*/
/*
function beforeUnloadListener(event) {
  event.preventDefault();
  return event.returnValue = 'Are you sure you want to exit?';
};

// A function that invokes a callback when the page has unsaved changes.
onPageHasUnsavedChanges(() => {
  window.addEventListener('beforeunload', beforeUnloadListener);
});

// A function that invokes a callback when the page's unsaved changes are resolved.
onAllChangesSaved(() => {
  window.removeEventListener('beforeunload', beforeUnloadListener);
});*/