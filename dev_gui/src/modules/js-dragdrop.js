import DOMPurify from 'dompurify';
export function JsDragDrop(item,options) {
  const defaultOptions = {
      css: {dragging:"dragging", dragover:"dragover",dropped:"dropped",disabled:"disabled"}
  }
  options = { ...defaultOptions,
    ...options
  };
  Object.freeze(options);
  let currentcontainer=null, current={id:null, type:null};
  let caretpos=null;
  const movehandlers=[{
      name: 'dragstart',
      func: (e) => {
        handleDragStart(e,'copy');
      }
    }, {
      name: 'dragend',
      func: (e) => {
        handleDragEnd(e);
      }
    }];

 const drophandlers =[{
      name: 'dragover',
      func: (e) => {
        handleDragOver(e);
      }
    }, {
      name: 'drop',
      func: (e) => {
        handleDrop(e);
      }},
     {name:'focus',
        func: (e)=> {
          handleAction(e,'focus');
        }},
     {name:'blur',
        func: (e)=> {
          handleAction(e,'blur');
        }},
     { name:'keypress',func: (e) => {
         // handleAction(e,'keypress');
          handleSelection(e);
         }},
     { name:'mouseup',func: (e) => {
          handleSelection(e);

         }},
     { name:'keyup',func: (e) => {
          handleSelection(e);

         }},
     { name:'selectionchange',func: (e) => {
          handleSelection(e);

         }
    }];

  function handleDragStart(e,effect) {
    e.stopImmediatePropagation();
    e.dataTransfer.effectAllowed = effect;
    current.id=e.target.id;
    current.type=e.target.textContent.split('.')[0];
    e.dataTransfer.setData("text/plain",current.id);
    /*item.querySelectorAll('[data-accept]').forEach( drop => {
        const accept =(drop.dataset.accept)?drop.dataset.accept:null;
        console.log('accept'+current.type,accept.split(',').includes(current.type))
        if (accept.split(',').includes(current.type)) {drop.contentEditable=true; drop.classList.remove(options.css.disabled); }
        else {delete drop.contentEditable;drop.classList.add(options.css.disabled);}
    });*/
    }

  function handleDragOver(e) {
    const accept =(e.target.dataset.accept)?e.target.dataset.accept:null;
    e.preventDefault();
    if (accept!==null && e.target.isContentEditable && accept.split(',').includes(current.type))  {e.target.focus();return true;}
    e.target.blur();return false;
  }
  function handleDragEnd(e) {
    e.preventDefault();
      return;
  }
  function getSelectionNodeInfo(e) {
      const selection =window.window.getSelection();
    const range = document.createRange();
    selection.removeAllRanges();
    selection.addRange(range);
    const x = e.pageX;
    const y= e.pageY;
    const elem = document.elementFromPoint(x,y );
    let startnode = (elem.childNodes.length>0?elem.childNodes[0]:elem);
    let startcharindex = -1;
    let rect;
    do {
        startcharindex++;
        range.setStart(startnode, startcharindex);
        range.setEnd(startnode, startcharindex+1);
        rect = range.getBoundingClientRect();
    } while (rect.left<x && startcharindex<startnode.length-1);

    return {node:startnode, offsetInsideNode:startcharindex};
}
  function handleDrop(e) {
    /***/
    if (currentcontainer!==e.target) {e.target.disabled=true;console.log('dropfalsefalse') ;return; }
    const el = document.getElementById(e.dataTransfer.getData("text/plain"));
     if (el===null) return;
     let clone=null;
     if (!el.classList.contains(options.css.dropped)) {
     clone=el.cloneNode(true);
    el.dataset.num=(el.dataset.num)?parseInt(el.dataset.num)+1:1;
    clone.id=clone.id+'_'+el.dataset.num;
    clone.contentEditable=false;
    clone.classList.add(options.css.dropped);
    // clone.draggable=false;
     clone.addEventListener('dblclick',(e) => {console.log('ecode',e)
       e.preventDefault();
         e.stopImmediatePropagation();
         clone.remove();
         });
        clone.addEventListener('dragstart', (e) => {handleDragStart(e,'move');});
     } else clone=el;


       pasteElementAtCaret(clone,e);
  }
  function handleAction(e, action) {
      let no=false;
      switch(action) {
          case 'focus':
              currentcontainer=e.target;
          break;
          case 'keypress':
             currentcontainer=e.target;
             caretpos=getCaretPos(e.target);
          break;
          case 'blur':
              no=true;
              currentcontainer=null;
              caretpos=null;
          break;
      }
      const accept =(e.target.dataset.accept)?e.target.dataset.accept:null;
      item.querySelectorAll('[draggable]').forEach(tag => {
      const type=tag.id.split('.')[0];
      if (accept.includes(type)) tag.draggable=true;
      else tag.draggable=no;
      });

  }
    function handleSelection(e) {
      currentcontainer=e.target;
      let selection = window.getSelection();
      const startpos=window.getSelection().anchorOffset;
      const endpos = window.getSelection().focusOffset;
      caretpos= {start:startpos,end:endpos};
  }

  function getCaretPos() {
    const selection = window.getSelection();
    const range = selection.getRangeAt(0);
    const startpos = range.startOffset;
    const endpos = range.endOffset;
    return {start:startpos,end:endpos};
}

  function pasteElementAtCaret(tag,e) {
      const container=e.target;
     if (currentcontainer!==container) return;
     if (caretpos===null || caretpos.start===caretpos.end) {
         const nodeinfo=getSelectionNodeInfo(e);
        caretpos=getCaretPos(container);
     } else if(caretpos.end>caretpos.start) selection.extend(caretpos.end-caretpos.start);
     const selection = window.getSelection();
     const range =selection.getRangeAt(0);
     range.setStart(selection.focusNode,caretpos.start);
     range.setEnd(selection.focusNode,caretpos.end);
     if (caretpos.end > caretpos.start) range.deleteContents();
     range.insertNode(tag);
     range.setStartAfter(tag);
     range.collapse(true);
     selection.removeAllRanges();
     selection.addRange(range);
      }

     item.querySelectorAll('[draggable]').forEach((tag) =>{
    movehandlers.forEach(listener=> { tag.addEventListener(listener.name,listener.func)});
    })
    item.querySelectorAll('[data-accept]').forEach( (droparea) => {
        droparea.contentEditable=true;
        drophandlers.forEach(listener => {droparea.addEventListener(listener.name,listener.func);})});
   if(item.dataset.hasOwnProperty('formhandler')) {
       const form=item.closest('form');
       if (form.formsubmit) form.formsubmit.addHandler('submit',() =>{
           item.querySelectorAll('[data-accept]').forEach(droparea=> {
            const input = document.createElement('input');
            input.type='hidden';
            input.name=droparea.id;
            input.value=droparea.textContent;
            form.append(input);
           });
       });

   } }
