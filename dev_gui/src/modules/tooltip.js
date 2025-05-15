import DOMPurify from 'dompurify';
import {
  css
} from '../modules/modules-config.js';
import {
  create_box,
  generate_uuid,
} from '../modules/utils.js';

export function ToolTip() {
const uuid=generate_uuid();
    const tip = create_box('div', {
            id: uuid,
            text: "",
            class: css.tooltip
          },document.body);
  function computePosition( item, tip, options={placement:'bottom-start',offset:{x:2,y:2}}) {
    const rect = item.getBoundingClientRect();
    const placement=options.placement.split('-');
    let y=parseInt(rect.top);
    switch(placement[0]) {
        case 'bottom':
            y+=parseInt(rect.height);
        break;
        case 'center':
            y+=Math.round(parseInt(rect.height)/2);
        break;
    }
    let x=parseInt(rect.left);
    switch(placement[1]) {
        case 'center':
        x+=Math.round(parseInt(rect.width)/2);
        break;
        case 'end':
        x+=parseInt(rect.width);
        break;
    }
    Object.assign(tip.style, {
    left: `${x}px`,
    top: `${y}px`,
    });
  }
  function applyTo(item,text,check=null) {
          item.addEventListener('mouseenter', () => {
          if(check!==null && !check()) return;
          computePosition(item, tip, {
            placement: 'top-center',
          });
          setTimeout(function() {tip.classList.remove(css.hide);
          tip.textContent=text;},100);
        });
        item.addEventListener('mouseout', () => {
            if(check!==null && !check()) return;
          setTimeout(function() { tip.classList.add(css.hide);
          tip.textContent="";},600);
        });
  }
  return {applyTo};
}
