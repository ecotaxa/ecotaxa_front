import stylecss from './css/style.css';
import {
  JsComponents
} from '../src/modules/js-components.js';
import {
  AlertBox
} from '../src/modules/alert-boxes.js';
import {
  ActivItems
} from '../src/modules/activ-items.js';
import {
  ActivRequest
} from "../src/modules/activ-request.js";
window.addEventListener('load', async () => {
  /*  const source = new EventSource('/adminstream/');
    source.onmessage = function(event) {
      console.log(event.data)
    }*/
  // initializze tools and triggered tools
  // triggered elements creation and actions
  // dropdowns
  document.querySelectorAll('nav .dropdown').forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      item.classList.toggle('over');
    });
  });
  /* transition new ui old ui - will be removed */
  const page_exists = (href) => {
    href = href.split('prj/');
    if (href.length > 1) {
      href[1] = href[1].split('/');
      if (href[1].length > 1) {
        switch (href[1][0].trim()) {
          case 'edit':
          case 'prjall':
          case '':
            return true;
            break;

        }

      } else {
        switch (href[1][0].trim()) {
          case 'create':
          case 'edit':
          case 'login':
          case 'about':
          case 'privacy':
            return true;
            break;

        }
      }
    }
    return false;
  }

  // enhance ui activate components  js js-componentname

  const jsComponents = new JsComponents();
  jsComponents.applyTo();
  /*** activate data-action  **/
  const activItems = new ActivItems(document);
  /* alert boxes */
  const alertBox = new AlertBox();
  /* fetch requesgt -modal - contextual help */
  const activRequest = new ActivRequest();
  activRequest.applyTo(document);
});
// 'unload' but 'pagehide'
window.addEventListener('pagehide', (e) => {
  //  ecotaxaStorage.clear();
})
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