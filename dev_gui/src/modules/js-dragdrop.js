export function JsDragDrop(item, options) {
  const defaultOptions = {
    pointstr: '.',
    replacestr: '§§',
    css: {
      dragging: 'dragging',
      dragover: 'dragover',
      dropped: 'dropped',
      disabled: 'disabled'
    }
  };

  options = { ...defaultOptions, ...options };
  Object.freeze(options);

  // state of the tag currently being dragged
  const current = { id: null, type: null, move: false, savedRange: null };

  // --- helpers -------------------------------------------------------------

  const asElement = (node) =>
    node && node.nodeType === Node.ELEMENT_NODE
      ? node
      : (node ? node.parentElement : null);

  // resolve the editable drop container from whatever node the event hit
  // (text node, nested <em>, an already dropped chip, ...)
  const dropArea = (node) => {
    const el = asElement(node);
    return el ? el.closest('[data-accept]') : null;
  };

  const accepts = (area, type) =>
    !!area &&
    !!type &&
    (area.dataset.accept || '')
      .split(',')
      .map((s) => s.trim())
      .includes(type);

  // last caret / selection seen inside one of this instance's drop areas. the
  // browser moves the live selection to follow the pointer while dragging over a
  // contenteditable, so a drop has to fall back on this pre-drag snapshot to know
  // where the user's cursor actually was (whether it was a selection to replace
  // or just a collapsed insertion point).
  let lastAreaRange = null;

  const rangeInArea = (range, area) =>
    !!range && !!area && area.contains(range.commonAncestorContainer);

  document.addEventListener('selectionchange', () => {
    if (!item.isConnected) return; // container gone: stale listener, ignore
    // don't let the browser's drop-caret updates wipe the snapshot mid-drag
    if (current.id) return;
    const sel = window.getSelection();
    if (!sel || !sel.rangeCount) return;
    const range = sel.getRangeAt(0);
    const host = asElement(range.commonAncestorContainer);
    if (!host || !host.closest('[data-accept]') || !item.contains(host)) return;
    lastAreaRange = range.cloneRange();
  });

  // real caret position under the pointer, cross browser
  function caretRangeFromPoint(x, y) {
    if (document.caretRangeFromPoint) {
      return document.caretRangeFromPoint(x, y);
    }
    if (document.caretPositionFromPoint) {
      const pos = document.caretPositionFromPoint(x, y);
      if (!pos) return null;
      const range = document.createRange();
      range.setStart(pos.offsetNode, pos.offset);
      range.collapse(true);
      return range;
    }
    return null;
  }

  // --- drag source -------------------------------------------------------------

  function handleDragStart(e, effect) {
    const source = e.currentTarget; // the [draggable] chip, never the inner <em>
    if (!source || !source.id) return;

    e.stopPropagation();

    // Safari needs setData with a valid format
    e.dataTransfer.effectAllowed = effect;
    e.dataTransfer.setData('text/plain', source.id);

    current.id = source.id;
    current.type = source.id.split(options.replacestr)[0];
    current.move = effect === 'move';

    // freeze where the cursor was (a selection to replace, or a plain caret to
    // insert at): the snapshot kept by selectionchange, else whatever is live now
    current.savedRange = lastAreaRange ? lastAreaRange.cloneRange() : null;
    if (!current.savedRange) {
      const sel = window.getSelection();
      if (sel && sel.rangeCount) {
        const r = sel.getRangeAt(0);
        const host = asElement(r.commonAncestorContainer);
        if (host && host.closest('[data-accept]')) {
          current.savedRange = r.cloneRange();
        }
      }
    }

    // Safari: custom drag image to avoid rendering glitches
    const dragImage = source.cloneNode(true);
    dragImage.style.position = 'absolute';
    dragImage.style.top = '-9999px';
    document.body.appendChild(dragImage);
    e.dataTransfer.setDragImage(dragImage, 0, 0);
    setTimeout(() => document.body.removeChild(dragImage), 0);
  }

  function handleDragEnd() {
    current.id = null;
    current.type = null;
    current.move = false;
    current.savedRange = null;
    item
      .querySelectorAll('.' + options.css.dragover)
      .forEach((el) => el.classList.remove(options.css.dragover));
  }

  // --- drop target -------------------------------------------------------------

  function handleDragOver(e) {
    const area = dropArea(e.target);
    if (area && accepts(area, current.type)) {
      // preventing the default is what actually allows the drop
      e.preventDefault();
      e.stopPropagation();
      e.dataTransfer.dropEffect = current.move ? 'move' : 'copy';
      area.classList.add(options.css.dragover);
      return;
    }
    if (e.dataTransfer) e.dataTransfer.dropEffect = 'none';
  }

  function handleDragLeave(e) {
    const area = dropArea(e.target);
    if (area && !area.contains(e.relatedTarget)) {
      area.classList.remove(options.css.dragover);
    }
  }

  function handleDrop(e) {
    const area = dropArea(e.target);
    if (!area) return;

    e.preventDefault();
    e.stopPropagation();
    area.classList.remove(options.css.dragover);

    const data =
      e.dataTransfer.getData('text/plain') || e.dataTransfer.getData('text');
    if (!data) return;

    const source = document.getElementById(data);
    if (!source) return;

    const type = current.type || source.id.split(options.replacestr)[0];
    if (!accepts(area, type)) return;

    let chip;
    if (source.classList.contains(options.css.dropped)) {
      chip = source; // relocating an existing chip
    } else {
      chip = createClone(source);
      cloneEvents(chip);
    }

    const range = dropRange(chip, e.clientX, e.clientY, area);
    if (!range) return;

    // replace whatever the range spans (the selected text, or nothing)
    range.deleteContents();
    range.insertNode(chip);
    lastAreaRange = null; // consumed - don't reuse it on the next drop

    // leave the caret right after the freshly inserted chip
    const after = document.createRange();
    after.setStartAfter(chip);
    after.collapse(true);
    const selection = window.getSelection();
    if (selection) {
      selection.removeAllRanges();
      selection.addRange(after);
    }
    area.focus();
    area.dispatchEvent(new Event('input', { bubbles: true }));
    if (area._ddHistory) area._ddHistory.commit();
  }

  // where the dropped chip goes:
  //  1. the cursor position the field had before the drag - a selection (which
  //     gets replaced) or a plain caret (insert there)
  //  2. else the caret under the pointer
  //  3. else the end of the field
  function dropRange(node, x, y, area) {
    // relocating an existing chip always follows the pointer, not a stale caret
    const saved = current.move ? null : current.savedRange;
    if (rangeInArea(saved, area)) {
      const clash =
        node.parentElement &&
        typeof saved.intersectsNode === 'function' &&
        saved.intersectsNode(node);
      if (!clash) return saved.cloneRange();
    }

    // 2. caret under the pointer
    let range = caretRangeFromPoint(x, y);
    if (range && area.contains(range.startContainer)) {
      // never land inside an existing chip, nor inside the node being moved
      const host = asElement(range.startContainer);
      const chip = host && host.closest('.' + options.css.dropped);
      const insideMoved =
        node === range.startContainer || node.contains(range.startContainer);
      if ((chip && area.contains(chip)) || insideMoved) {
        range.setStartAfter(chip && area.contains(chip) ? chip : node);
      }
      range.collapse(true);
      return range;
    }

    // 3. pointer landed outside any text: append at the end of the field
    range = document.createRange();
    range.selectNodeContents(area);
    range.collapse(false);
    return range;
  }

  // --- chips -------------------------------------------------------------

  function createClone(el) {
    const clone = el.cloneNode(true);
    el.dataset.num = el.dataset.num ? parseInt(el.dataset.num, 10) + 1 : 1;
    clone.id = clone.id + '_' + el.dataset.num;
    clone.setAttribute('contenteditable', 'false');
    clone.contentEditable = false;
    clone.setAttribute('draggable', 'true');
    clone.draggable = true;
    clone.classList.add(options.css.dropped);
    return clone;
  }

  function cloneEvents(clone) {
    const remove = (e) => {
      e.preventDefault();
      e.stopImmediatePropagation();
      const area = clone.closest('[data-accept]');
      const parent = clone.parentElement;
      clone.removeEventListener('dblclick', remove);
      clone.removeEventListener('dragstart', dragStartMove);
      clone.remove();
      const notify = area || parent;
      if (notify) notify.dispatchEvent(new Event('input', { bubbles: true }));
      if (area && area._ddHistory) area._ddHistory.commit();
    };
    const dragStartMove = (e) => handleDragStart(e, 'move');

    clone.addEventListener('dblclick', remove);
    clone.addEventListener('dragstart', dragStartMove);
  }

  // --- per-field undo / redo (ctrl+z, ctrl+shift+z / ctrl+y) ----------------
  // dropping and deleting chips mutate the DOM directly, which the browser's
  // native undo never records. keep a small innerHTML history per editable area
  // and drive undo/redo from it; plain typing is coalesced into the same stack
  // so both kinds of edit undo consistently.
  function attachHistory(area) {
    const undo = [];
    const redo = [];
    let currentHTML = area.innerHTML;
    let typingTimer = null;
    const LIMIT = 100;

    const commit = () => {
      if (typingTimer) {
        clearTimeout(typingTimer);
        typingTimer = null;
      }
      const html = area.innerHTML;
      if (html === currentHTML) return;
      undo.push(currentHTML);
      if (undo.length > LIMIT) undo.shift();
      redo.length = 0;
      currentHTML = html;
    };

    const restore = (html) => {
      area.innerHTML = html;
      currentHTML = html;
      area
        .querySelectorAll('.' + options.css.dropped)
        .forEach((chip) => cloneEvents(chip));
      const range = document.createRange();
      range.selectNodeContents(area);
      range.collapse(false);
      const sel = window.getSelection();
      if (sel) {
        sel.removeAllRanges();
        sel.addRange(range);
      }
      area.focus();
      area.dispatchEvent(new Event('input', { bubbles: true }));
    };

    area.addEventListener('input', () => {
      if (typingTimer) clearTimeout(typingTimer);
      typingTimer = setTimeout(commit, 500);
    });

    area.addEventListener('keydown', (e) => {
      if (!(e.ctrlKey || e.metaKey) || e.altKey) return;
      const key = (e.key || '').toLowerCase();
      const wantUndo = key === 'z' && !e.shiftKey;
      const wantRedo = (key === 'z' && e.shiftKey) || key === 'y';
      if (!wantUndo && !wantRedo) return;
      e.preventDefault();
      commit(); // fold any pending typing into the stack first
      if (wantUndo && undo.length) {
        redo.push(currentHTML);
        restore(undo.pop());
      } else if (wantRedo && redo.length) {
        undo.push(currentHTML);
        restore(redo.pop());
      }
    });

    return { commit };
  }

  // --- rehydrate a saved formula string back into chips ----------------------

  // build the list of {token, type, tag} the loaded text may contain.
  // acquisition/process columns are stored/loaded with the "subsample." prefix
  // (both map to "ssm." on the back-end), so both spellings are indexed.
  function buildChipIndex() {
    const subsamples = ['acquisition', 'process'];
    const entries = [];
    sortedtags.forEach((tag) => {
      const type = tag.id.split(options.replacestr)[0];
      const col = tag.textContent
        .split(options.pointstr)
        .slice(1)
        .join(options.pointstr);
      if (!col) return;
      const tokens = new Set([type + options.pointstr + col]);
      if (subsamples.includes(type)) {
        tokens.add('subsample' + options.pointstr + col);
      }
      tokens.forEach((token) => entries.push({ token, type, tag }));
    });
    // longest token first: a name that is a prefix of another can never win
    entries.sort((a, b) => b.token.length - a.token.length);
    return entries;
  }

  // index of `token` in `text` that is not glued to another identifier
  function tokenAt(text, token) {
    const idpart = /[A-Za-z0-9_.]/;
    let i = text.indexOf(token);
    while (i > -1) {
      const before = i > 0 ? text[i - 1] : '';
      const after =
        i + token.length < text.length ? text[i + token.length] : '';
      if (!idpart.test(before) && !idpart.test(after)) return i;
      i = text.indexOf(token, i + 1);
    }
    return -1;
  }

  function firstMatch(text, index) {
    let best = null;
    for (const entry of index) {
      const i = tokenAt(text, entry.token);
      if (i < 0) continue;
      if (
        !best ||
        i < best.i ||
        (i === best.i && entry.token.length > best.entry.token.length)
      ) {
        best = { i, entry };
      }
    }
    return best;
  }

  // prefixes that address a mapped column - a "prefix.name" built on one of these,
  // once pass 1 has consumed every one this project actually has, is a reference to
  // a (free) column that exists in the source project but is missing here.
  const COLUMN_PREFIXES = ['sample', 'subsample', 'acquisition', 'process', 'object'];

  function missingTokenRe(accept) {
    const types = COLUMN_PREFIXES.filter((t) => accept.includes(t));
    if (accept.includes('acquisition') || accept.includes('process')) {
      if (!types.includes('subsample')) types.push('subsample');
    }
    if (!types.length) return null;
    types.sort((a, b) => b.length - a.length);
    return new RegExp('\\b(?:' + types.join('|') + ')\\.[A-Za-z_][A-Za-z0-9_]*');
  }

  function rehydrate(area) {
    const accept = (area.dataset.accept || '')
      .split(',')
      .map((s) => s.trim());

    // drop markers from a previous run so both passes recompute from clean text
    area
      .querySelectorAll('.formula-missing')
      .forEach((el) => el.replaceWith(document.createTextNode(el.textContent)));
    area.normalize();

    // --- pass 1: turn known prefix.column tokens into draggable chips ----------
    const index = chipIndex.filter((e) => accept.includes(e.type));
    if (index.length) {
      const walker = document.createTreeWalker(area, NodeFilter.SHOW_TEXT, {
        acceptNode: (n) =>
          n.parentElement && n.parentElement.closest('.' + options.css.dropped)
            ? NodeFilter.FILTER_REJECT
            : NodeFilter.FILTER_ACCEPT
      });

      const starts = [];
      while (walker.nextNode()) starts.push(walker.currentNode);

      starts.forEach((start) => {
        let node = start;
        while (node && node.nodeValue) {
          const match = firstMatch(node.nodeValue, index);
          if (!match) break;
          const tail = node.splitText(match.i);
          tail.nodeValue = tail.nodeValue.slice(match.entry.token.length);
          const clone = createClone(match.entry.tag);
          cloneEvents(clone);
          tail.parentNode.insertBefore(clone, tail);
          node = tail; // keep scanning the remaining text
        }
      });
    }

    // --- pass 2: flag leftover prefix.column tokens with no field here --------
    const missingRe = missingTokenRe(accept);
    if (!missingRe) return;

    const flagWalker = document.createTreeWalker(area, NodeFilter.SHOW_TEXT, {
      acceptNode: (n) =>
        n.parentElement &&
        n.parentElement.closest('.' + options.css.dropped + ', .formula-missing')
          ? NodeFilter.FILTER_REJECT
          : NodeFilter.FILTER_ACCEPT
    });

    const texts = [];
    while (flagWalker.nextNode()) texts.push(flagWalker.currentNode);

    texts.forEach((start) => {
      let node = start;
      while (node && node.nodeValue) {
        const m = node.nodeValue.match(missingRe);
        if (!m) break;
        const tail = node.splitText(m.index);
        const token = tail.nodeValue.slice(0, m[0].length);
        tail.nodeValue = tail.nodeValue.slice(m[0].length);
        const span = document.createElement('span');
        span.className = 'formula-missing';
        span.textContent = token;
        span.title = 'no matching field in this project';
        tail.parentNode.insertBefore(span, tail);
        node = tail;
      }
    });
  }

  // --- init -------------------------------------------------------------

  // longest label first, then alphabetical, so substring names are handled
  // before the names that contain them
  const sortedtags = Array.from(item.querySelectorAll('[draggable]')).sort(
    (a, b) => {
      const ta = a.textContent;
      const tb = b.textContent;
      if (tb.length !== ta.length) return tb.length - ta.length;
      return ta < tb ? -1 : ta > tb ? 1 : 0;
    }
  );

  sortedtags.forEach((tag) => {
    // "." is illegal-ish inside ids we look up with getElementById patterns,
    // swap every dot so "sample.foo" -> "sample§§foo"
    tag.id = tag.id.split(options.pointstr).join(options.replacestr);
    tag.setAttribute('draggable', 'true');
    tag.draggable = true;
    tag.addEventListener('dragstart', (e) => handleDragStart(e, 'copy'));
    tag.addEventListener('dragend', handleDragEnd);
  });

  const chipIndex = buildChipIndex();

  item.querySelectorAll('[data-accept]').forEach((area) => {
    area.setAttribute('contenteditable', 'true');
    area.contentEditable = true;
    area.addEventListener('dragenter', (e) => {
      if (accepts(dropArea(e.target), current.type)) e.preventDefault();
    });
    area.addEventListener('dragover', handleDragOver);
    area.addEventListener('dragleave', handleDragLeave);
    area.addEventListener('drop', handleDrop);
    rehydrate(area);
    if (!area._ddHistory) area._ddHistory = attachHistory(area);
  });

  // let external code (e.g. DataImport) re-chip a field after it writes raw text
  item.jsdragdrop = {
    rehydrate(area) {
      if (area) {
        rehydrate(area);
        return;
      }
      item.querySelectorAll('[data-accept]').forEach((a) => rehydrate(a));
    },
  };

  if (options.formhandler) {
    const form = item.closest('form');
    if (form) {
      const nbsp = / /g;

      const serialize = (area) => {
        let out = '';
        area.childNodes.forEach((n) => {
          if (n.nodeType === Node.TEXT_NODE) out += n.nodeValue;
          else if (n.nodeType === Node.ELEMENT_NODE) out += n.textContent;
        });
        return out.replace(nbsp, ' ').replace(/\s+/g, ' ').trim();
      };

      const writeInputs = () => {
        form
          .querySelectorAll('input[data-dragdrop]')
          .forEach((el) => el.remove());
        item.querySelectorAll('[data-accept]').forEach((area) => {
          const input = document.createElement('input');
          input.type = 'hidden';
          input.name = area.id.split(options.replacestr).join(options.pointstr);
          input.setAttribute('data-dragdrop', '');
          input.value = serialize(area);
          form.appendChild(input);
        });
        return true;
      };

      if (form.formsubmit && typeof form.formsubmit.addHandler === 'function') {
        form.formsubmit.addHandler('submit', writeInputs);
      } else {
        // no FormSubmit component: catch the native submit
        form.addEventListener('submit', writeInputs, true);
      }
    }
  }
}
