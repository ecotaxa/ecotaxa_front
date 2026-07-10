import DOMPurify from "dompurify";

export function JsDragDrop(item, options) {
  const defaultOptions = {
    pointstr: '.',
    replacestr: "§§",
    css: {
      dragging: "dragging",
      dragover: "dragover",
      dropped: "dropped",
      disabled: "disabled"
    }
  };

  options = { ...defaultOptions, ...options };
  Object.freeze(options);

  let currentcontainer = null;
  let current = { id: null, type: null };
  let caretpos = null;

  const movehandlers = [
    {
      name: 'dragstart',
      func: (e) => {
        handleDragStart(e, 'copy');
      }
    },
    {
      name: 'dragend',
      func: (e) => {
        handleDragEnd(e);
      }
    }
  ];

  const drophandlers = [
    {
      name: 'dragover',
      func: (e) => {
        handleDragOver(e);
      }
    },
    {
      name: 'drop',
      func: (e) => {
        handleDrop(e);
      }
    },
    {
      name: 'focus',
      func: (e) => {
        handleAction(e, 'focus');
      }
    },
    {
      name: 'blur',
      func: (e) => {
        handleAction(e, 'blur');
      }
    },
    {
      name: 'keypress',
      func: (e) => {
        handleSelection(e);
      }
    },
    {
      name: 'mouseup',
      func: (e) => {
        handleSelection(e);
      }
    },
    {
      name: 'keyup',
      func: (e) => {
        handleSelection(e);
      }
    },
    {
      name: 'selectionchange',
      func: (e) => {
        handleSelection(e);
      }
    }
  ];

  function handleDragStart(e, effect) {
    e.stopImmediatePropagation();

    // Safari nécessite que setData soit appelé avec un format valide
    e.dataTransfer.effectAllowed = effect;
    e.dataTransfer.setData("text/plain", e.target.id);
    e.dataTransfer.setData("text/html", e.target.outerHTML);

    current.id = e.target.id;
    current.type = e.target.textContent.split(options.pointstr)[0];

    // Safari: définir une image de drag personnalisée pour éviter les problèmes
    const dragImage = e.target.cloneNode(true);
    dragImage.style.position = 'absolute';
    dragImage.style.top = '-9999px';
    document.body.appendChild(dragImage);
    e.dataTransfer.setDragImage(dragImage, 0, 0);
    setTimeout(() => document.body.removeChild(dragImage), 0);
  }

  function handleDragOver(e) {
    // Safari: empêcher le comportement par défaut est crucial
    e.preventDefault();
    e.stopPropagation();

    const accept = (e.target.dataset.accept) ? e.target.dataset.accept : null;
    const isEditable = e.target.getAttribute('contenteditable') === 'true' ||
                        e.target.isContentEditable === true;

    if (accept !== null && isEditable && accept.split(',').includes(current.type)) {
      e.dataTransfer.dropEffect = 'copy';
      e.target.focus();
      return true;
    }

    e.dataTransfer.dropEffect = 'none';
    e.target.blur();
    return false;
  }

  function handleDragEnd(e) {
    e.preventDefault();
    current = { id: null, type: null };
  }

  function getSelectionNodeInfo(e) {
    const selection = window.getSelection();

    // Safari: vérifier que la sélection n'est pas vide
    if (!selection || selection.rangeCount === 0) {
      return null;
    }

    const range = document.createRange();
    selection.removeAllRanges();
    selection.addRange(range);

    const x = e.pageX || e.clientX + window.pageXOffset;
    const y = e.pageY || e.clientY + window.pageYOffset;

    // Safari: elementFromPoint peut retourner null dans les zones contentEditable
    const elem = document.elementFromPoint(x, y);
    if (!elem) return null;

    // Safari: s'assurer qu'on a un nœud de texte
    let startnode = elem;
    if (elem.nodeType === Node.ELEMENT_NODE && elem.childNodes.length > 0) {
      startnode = elem.childNodes[0];
    }

    let startcharindex = -1;
    let rect;

    do {
      startcharindex++;

      // Safari: vérifier les limites
      if (startnode.nodeType === Node.TEXT_NODE && startcharindex > startnode.length) {
        break;
      }

      range.setStart(startnode, Math.min(startcharindex,
        startnode.nodeType === Node.TEXT_NODE ? startnode.length : 0));

      rect = range.getBoundingClientRect();

      if (!rect) break;

      const offset = (rect.left < x && startcharindex <
        (startnode.nodeType === Node.TEXT_NODE ? startnode.length : 1) - 1)
        ? startcharindex + 1
        : startcharindex;

      range.setEnd(startnode, Math.min(offset,
        startnode.nodeType === Node.TEXT_NODE ? startnode.length : 0));
      rect = range.getBoundingClientRect();

    } while (rect && rect.left < x &&
             startnode.nodeType === Node.TEXT_NODE &&
             startcharindex < startnode.length - 1);

    return {
      node: startnode,
      offsetInsideNode: Math.max(0, startcharindex)
    };
  }

  function createClone(el) {
    const clone = el.cloneNode(true);
    el.dataset.num = (el.dataset.num) ? parseInt(el.dataset.num) + 1 : 1;
    clone.id = clone.id + '_' + el.dataset.num;

    // Safari: utiliser setAttribute pour contentEditable
    clone.setAttribute('contenteditable', 'false');
    clone.contentEditable = false;

    clone.classList.add(options.css.dropped);
    return clone;
  }

  function cloneEvents(clone) {
    const handleDblClick = (e) => {
      e.preventDefault();
      e.stopImmediatePropagation();
      cleanup();
      clone.remove();
    };

    const handleDragStartClone = (e) => {
      handleDragStart(e, 'move');
    };

    const cleanup = () => {
      clone.removeEventListener('dblclick', handleDblClick);
      clone.removeEventListener('dragstart', handleDragStartClone);
    };

    clone.addEventListener('dblclick', handleDblClick);
    clone.addEventListener('dragstart', handleDragStartClone);

    // Stocker la fonction de nettoyage
    clone._cleanup = cleanup;
  }

  function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();

    if (currentcontainer !== e.target) return;

    // Safari: récupérer les données correctement
    const data = e.dataTransfer.getData("text/plain") ||
                 e.dataTransfer.getData("text");

    if (!data) return;

    const el = document.getElementById(data);
    if (el === null) return;

    let clone = null;
    if (!el.classList.contains(options.css.dropped)) {
      clone = createClone(el);
      cloneEvents(clone);
    } else {
      clone = el;
    }

    pasteElementAtCaret(clone, e);
  }

  function handleAction(e, action) {
    let draggableState = false;

    switch (action) {
      case 'focus':
        currentcontainer = e.target;
        draggableState = true;
        break;
      case 'keypress':
        currentcontainer = e.target;
        draggableState = true;
        break;
      case 'blur':
        draggableState = false;
        break;
    }

    const accept = (e.target.dataset.accept) ? e.target.dataset.accept : null;

    item.querySelectorAll('[draggable]').forEach(tag => {
      const type = tag.id.split(options.replacestr)[0];

      if (accept && accept.includes(type)) {
        tag.setAttribute('draggable', 'true');
        tag.draggable = true;
      } else {
        // Safari: désactiver le drag
        tag.removeAttribute('draggable');
        tag.draggable = false;
      }
    });
  }

  function handleSelection(e) {
    currentcontainer = e.target;

    // Safari: la sélection peut être asynchrone
    setTimeout(() => {
      const selection = window.getSelection();
      if (!selection || selection.rangeCount === 0) {
        caretpos = null;
        return;
      }

      const range = selection.getRangeAt(0);
      caretpos = {
        start: range.startOffset,
        end: range.endOffset
      };
    }, 0);
  }

  function getCaretPos() {
    const selection = window.getSelection();

    // Safari: vérifier que la sélection existe
    if (!selection || selection.rangeCount === 0) {
      return { start: 0, end: 0 };
    }

    const range = selection.getRangeAt(0);
    return {
      start: range.startOffset,
      end: range.endOffset
    };
  }

  function pasteElementAtCaret(tag, e) {
    const container = e.target;
    if (currentcontainer !== container) return;

    // Safari: s'assurer que le container est éditable
    if (!container.isContentEditable &&
        container.getAttribute('contenteditable') !== 'true') {
      return;
    }

    if (caretpos === null) {
      const nodeinfo = getSelectionNodeInfo(e);
      if (nodeinfo && nodeinfo.node &&
          (nodeinfo.node === tag || nodeinfo.node.contains(tag))) {
        return;
      }
    }

    if (!caretpos || (caretpos.start === caretpos.end)) {
      caretpos = getCaretPos();
    }

    const selection = window.getSelection();
    if (!selection || selection.rangeCount === 0) return;

    const range = selection.getRangeAt(0);

    try {
      // Safari: vérifier que focusNode existe et est un nœud valide
      if (!selection.focusNode || selection.focusNode.nodeType === Node.DOCUMENT_NODE) {
        return;
      }

      const startOffset = Math.min(caretpos.start,
        selection.focusNode.nodeType === Node.TEXT_NODE ?
        selection.focusNode.length : 1);
      const endOffset = Math.min(caretpos.end,
        selection.focusNode.nodeType === Node.TEXT_NODE ?
        selection.focusNode.length : 1);

      range.setStart(selection.focusNode, startOffset);
      range.setEnd(selection.focusNode, endOffset);

      if (caretpos.end > caretpos.start) {
        range.deleteContents();
      }

      // Safari: insérer et replacer le curseur
      range.insertNode(tag);
      range.setStartAfter(tag);
      range.collapse(true);

      selection.removeAllRanges();
      selection.addRange(range);

      // Safari: déclencher un événement input pour la compatibilité
      container.dispatchEvent(new Event('input', { bubbles: true }));

    } catch (error) {
      console.warn('Failed to paste element at caret:', error);
      // Fallback: ajouter à la fin du container
      container.appendChild(tag);
    }
  }

  function replaceByTags(container) {
    const accept = (container.dataset.accept) ? container.dataset.accept : null;
    const subsamples = ['process', 'acquisition'];

    const replace_by = function(tagvalue, tag) {
      let content = container.innerHTML;
      let index = content.indexOf(tagvalue);

      while (index >= 0) {
        const clone = createClone(tag);
        content = content.substring(0, index) +
                  clone.outerHTML +
                  content.substring(index + tagvalue.length);
        index = content.indexOf(tagvalue, index + clone.outerHTML.length - 1);
        container.innerHTML = content;

        const insertedClone = document.getElementById(clone.id);
        if (insertedClone) {
          cloneEvents(insertedClone);
        }
      }
    };

    sortedtags.forEach(tag => {
      const type = tag.id.split(options.replacestr)[0];
      if (!accept || !accept.includes(type)) return;

      let content = DOMPurify.sanitize(container.innerHTML);
      let tagvalue = DOMPurify.sanitize(tag.textContent);

      // Échapper le tagvalue pour l'utilisation dans les expressions régulières si nécessaire
      replace_by(tagvalue, tag);

      if (subsamples.includes(type)) {
        subsamples.forEach(sub => {
          tagvalue = tagvalue.replace(sub + options.pointstr, 'subsample.');
          tagvalue = tagvalue.replace(sub + '.</em>', 'subsample.</em>');
        });

        content = container.innerHTML;
        replace_by(tagvalue, tag);
      }
    });
  }

  // Trier par ordre alphabétique et longueur
  const sortedtags = Array.from(item.querySelectorAll('[draggable]')).sort((a, b) => {
    if (a.textContent < b.textContent) return 1;
    else if (a.textContent > b.textContent) return -1;
    return 0;
  });

  sortedtags.forEach((tag) => {
    tag.id = tag.id.replace(options.pointstr, options.replacestr);

    // Safari: s'assurer que draggable est correctement défini
    tag.setAttribute('draggable', 'true');
    tag.draggable = true;

    movehandlers.forEach(listener => {
      tag.addEventListener(listener.name, listener.func);
    });
  });

  item.querySelectorAll('[data-accept]').forEach((droparea) => {
    // Safari: définir contentEditable des deux façons pour compatibilité
    droparea.setAttribute('contenteditable', 'true');
    droparea.contentEditable = true;

    drophandlers.forEach(listener => {
      droparea.addEventListener(listener.name, listener.func);
    });

    replaceByTags(droparea);
  });

  if (options.formhandler) {
    const form = item.closest('form');
    if (form && form.formsubmit) {
      form.formsubmit.addHandler('submit', () => {
        item.querySelectorAll('[data-accept]').forEach(droparea => {
          const input = document.createElement('input');
          input.type = 'hidden';
          input.name = droparea.id.replace(options.replacestr, options.pointstr);
          input.value = droparea.textContent;
          form.append(input);
        });
        return true;
      });
    }
  }
}