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
    const selection =window.getSelection();
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
        rect = range.getBoundingClientRect();
        const offset=(rect.left<x && startcharindex<startnode.length-1)?startcharindex+1:startcharindex;
        range.setEnd(startnode, offset);
        rect = range.getBoundingClientRect();
    } while (rect.left<x && startcharindex<startnode.length-1);

    return {node:startnode, offsetInsideNode:startcharindex};
}
  function createClone(el) {
    const clone=el.cloneNode(true);
    el.dataset.num=(el.dataset.num)?parseInt(el.dataset.num)+1:1;
    clone.id=clone.id+'_'+el.dataset.num;
    clone.contentEditable=false;
    clone.classList.add(options.css.dropped);
    return clone;
  }
  function cloneEvents(clone,add=false) {
       clone.addEventListener('dblclick',(e) => {
       e.preventDefault();
         e.stopImmediatePropagation();
         clone.remove();
         });
       clone.addEventListener('dragstart', (e) => {handleDragStart(e,'move');});
    }
  function handleDrop(e) {
    /***/
    if (currentcontainer!==e.target) return;
    const el = document.getElementById(e.dataTransfer.getData("text/plain"));
     if (el===null) return;
     let clone=null;
     if (!el.classList.contains(options.css.dropped)) {
       clone = createClone(el);
       cloneEvents(clone);
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
          break;
          case 'blur':
              no=true;
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
      const startpos=selection.anchorOffset;
      const endpos = selection.focusOffset;
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
      const container = e.target;
     if (currentcontainer!==container) return;
     if (caretpos===null ) {// || caretpos.start===caretpos.end
        const nodeinfo=getSelectionNodeInfo(e);
        if (nodeinfo && nodeinfo.node && nodeinfo.node===tag) return;
     } //else if(caretpos.end>caretpos.start) selection.extend(caretpos.end-caretpos.start);
     caretpos=getCaretPos(container);
     const selection = window.getSelection();
     const range =selection.getRangeAt(0);
     range.setStart(selection.focusNode,caretpos.start);
     range.setEnd(selection.focusNode,caretpos.end);
     if (caretpos.end > caretpos.start) range.deleteContents();
      range.insertNode(tag);
      range.setStartAfter(tag);
      selection.removeAllRanges();
      selection.addRange(range);
      }
    function replaceByTags(container) {
       const accept =(container.dataset.accept)?container.dataset.accept:null;
       const subsamples=['process','acquisition'];
        let content,html,index;
       const replace_by=function(tagvalue,tag) {
           let clone;
         while(index>=0 ) {
            clone=createClone(tag);
            html =content.substr(0,index)+ clone.outerHTML + content.substr(index+tagvalue.length);
            index=content.indexOf(tagvalue,index+ clone.outerHTML.length);
            container.innerHTML=html;
            clone=document.getElementById(clone.id);
            cloneEvents(clone);
         }
        }
      item.querySelectorAll('[draggable]').forEach(tag => {
      const type=tag.id.split('.')[0];
      if (!accept.includes(type))  return;
      content=container.innerHTML;
      let tagvalue =tag.textContent;
      index=content.indexOf(tagvalue);
      replace_by(tagvalue,tag);
      if(subsamples.includes(type)) {
        subsamples.forEach(sub => {tagvalue=tagvalue.replace(sub+'.','subsample.');tagvalue=tagvalue.replace(sub+'.</em>','subsample.</em>');});
        content=container.innerHTML;
        index=content.indexOf(tagvalue);
        replace_by(tagvalue,tag);
      }
      });
    }
     item.querySelectorAll('[draggable]').forEach((tag) =>{
    movehandlers.forEach(listener=> { tag.addEventListener(listener.name,listener.func)});
    })
    item.querySelectorAll('[data-accept]').forEach( (droparea) => {
        droparea.contentEditable=true;
        drophandlers.forEach(listener => {droparea.addEventListener(listener.name,listener.func);});
        replaceByTags(droparea);
    });
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
           return true;
       });

   } }
