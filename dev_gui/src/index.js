import stylecss from './css/style.css';
import {
  AlertBox
} from '../src/modules/alert-boxes.js';
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

window.addEventListener('load', async () => {
  // global alert dialog system
  window.alertbox = await new AlertBox(document);
  // enhance ui activate components  js js-componentname
  const jsComponents = new JsComponents();
  jsComponents.applyTo();
  /*** activate data-action  **/
  const activItems = new ActivItems();
  activItems.applyTo(document);
  /* fetch request -modal - contextual help */
  const activRequest = new ActivRequest();
  activRequest.applyTo(document);
  window.alertbox.activateAll();
});
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