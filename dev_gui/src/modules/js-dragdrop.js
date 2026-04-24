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
  const movehandlers=[{
      name: 'dragstart',
      func: (e) => {
        handleDragStart(e);
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
     {name:'keypress',func: (e) => {
          handleAction(e,'keypress');

         }
    }];

  function handleDragStart(e) {
    e.stopImmediatePropagation();
    e.dataTransfer.effectAllowed = 'copy';
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
    if (e.target.hasOwnProperty('contentEditable') && accept.split(',').includes(current.type))  e.preventDefault();
    else return false;
  }
  function handleDragEnd(e) {
    e.preventDefault();
      return;
    //document.getElementById(currentdrag).classList.remove(options.css.dragging);
  }

  function handleDrop(e) {
    /***/
      if (e.target.disabled) return false;
    const el = document.getElementById(e.dataTransfer.getData("text/plain"));
     if (el===null) return;
    const clone=el.cloneNode(true);
    el.dataset.num=(el.dataset.num)?parseInt(el.dataset.num)+1:1;
    clone.id=clone.id+'_'+el.dataset.num;
    clone.contenteditable=false;
    clone.classList.add(options.css.dropped);
    clone.addEventListener('keydown',(e) => {console.log('ecode',e)
       e.preventDefault();
     if ([8,46].includes(e.code)) {const origin=clone.id.split('_');const num=parseInt(origin[1])-1;document.getElementById(origin[0]).dataset.num=num;clone.remove();}});
      pasteHtmlAtCaret(clone,e.target);
      console.log('e.targetvalue', e.target.textContent)
  }
  function handleAction(e, action) {
      let no=false;
      switch(action) {
          case 'focus':
          case 'keypress':
              currentcontainer=e.target;
          break;
          case 'blur':
              no=true;
              currentcontainer=null;
          break;
      }
      const accept =(e.target.dataset.accept)?e.target.dataset.accept:null;
      item.querySelectorAll('[draggable]').forEach(tag => {
      const type=tag.id.split('.')[0];
      if (accept.includes(type)) tag.draggable=true;
      else tag.draggable=no;
      });

  }
  function setCursorAt(container) {
    const selection = window.getSelection();

      console.log('cont', container)
     if(container !==currentcontainer) { console.log('setcursorat')
       const range = document.createRange();
       selection.removeAllRanges();
        range.selectNodeContents(container);
        range.collapse(true);
        selection.addRange(range);
        currentcontainer = container;     }
    container.focus();
  }
function pasteHtmlAtCaret(tag,container) {
    setCursorAt(container);
    const selection = window.getSelection();
    if (selection.getRangeAt && selection.rangeCount) {
        let range = selection.getRangeAt(0);
        range.deleteContents();
        range.insertNode(tag);
        range.setStartAfter(tag);
        range.collapse(true);
        selection.removeAllRanges();
        selection.addRange(range);
    }
    }
     item.querySelectorAll('[draggable]').forEach((tag) =>{
    movehandlers.forEach(listener=> { tag.addEventListener(listener.name,listener.func)});
    })
    item.querySelectorAll('[data-accept]').forEach( (droparea) => { droparea.contentEditable=true;drophandlers.forEach(listener => {droparea.addEventListener(listener.name,listener.func);})});
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
