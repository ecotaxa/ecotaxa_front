/* modified from BotDetector /  detect*/
import {
  fetchSettings
} from '../modules/utils.js';
import BotDetect from '../modules/botdetect-clean.min.js';

const css = {
  submitslider: "submitslider",
  slidermask: "slidermask",
  slider: "slider",
  icoslider: "icoslider",
  cursorgrab: "cursor-grab",
  helptxt: "helptxt"
}
export class JsCaptcha {
  counts = {};
  is_bot = false;
  detect_level = 500;
  constructor(container, options = {}) {
    const defaultOptions = {
      captcha: true,
    };
    this.options = Object.assign(defaultOptions, options);
    this.form = container.querySelector('input') ? container.querySelector('input').form : (container.dataset.formid) ? document.getElementById(container.dataset.formid) : null;
    this.captcha = container;
  }
  init() {
    this.botDetect();
    this.buttonSlider();
    this.submitOnCondition();

  }
  challenge() {
    // hpot suppose that the bot fills an invisible input field
    const resp = this.captcha.dataset.response ? this.captcha.dataset.response : null;
    if (resp === null) return true;
    console.log("challenge" + resp.value, resp.placeholder);
    return (resp.value !== resp.placeholder);
  }
  buttonSlider() {
    const form = this.form;
    let btnsubmit = this.form.querySelector('button[type="submit"]');
    if (btnsubmit !== null) {
      const textsubmit = btnsubmit.contentText;
      btnsubmit.classList.add(css.submitslider);
      const textdiv = document.createElement('div');
      textdiv.classList.add(css.helptxt);
      textdiv.contentText = textsubmit;
      btnsubmit.contentText = "";
      btnsubmit.append(textdiv);
      btnsubmit.style.overflow = "hidden";
      const slidermask = document.createElement('div');
      slidermask.classList.add(css.slidermask);
      const title = this.captcha.dataset.alttext ? this.captcha.dataset.alttext : "slide right to enable form submission";
      slidermask.dataset.title = title;
      btnsubmit.append(slidermask);
      btnsubmit.disabled = "disabled";
      const slider = document.createElement('div');
      slider.classList.add(css.slider);
      btnsubmit.append(slider);
      const ico = document.createElement('i');
      ico.classList.add(css.icoslider);
      slider.append(ico);
      let isdragging = true;

      const slidebtn = new DragSliderBtn(slider, slidermask, btnsubmit, this.form);
    }
    //
  }
  botDetect() {
    if (BotDetect !== undefined) {
      const proof_of_work = (verdict, token) => {
        this.is_bot = verdict;
      };
      BotDetect.detector.setProofOfWorkFn(proof_of_work);
      BotDetect.collector.enableTraps();
      BotDetect.collector.collect().then(results => {
        console.log('result', results);
        const output = BotDetect.detector.detect(results);
        this.is_bot = (output === 'bot');
      });
    } else this.is_bot = this.mouseDetect();
  }

  submitOnCondition() {
    console.log('thisform', this.form)
    if (this.form === null) return;
    if (this.form.classList.contains("js-submit")) {
      console.log('thisbofform', this.is_bot)
      this.form.dataset.isbot = this.is_bot;
    } else this.form.addEventListener('submit', (e) => {
      e.preventDefault();
      if (this.is_bot === false) return this.form.submit();
      return false;
    });
  }
}
class DragSliderBtn {
  // drag horizontally
  constructor(slider, slidermask, btn, form) {
    const boundingrect = slidermask.getBoundingClientRect();
    let isdragging = false;
    let lastx;

    function canMove(x) {
      if (parseInt(slidermask.style.left) >= Math.floor(parseInt(boundingrect.width)) - 4) {
        console.log('enabled', form)
        form.dataset.enabled = true;
        btn.removeAttribute('disabled');
        slidermask.remove();
        slidermask = null;
        slider.remove();
        console.log('slider', slider)
        return false;
      }
      return true;
    }

    function hslide(e) {
      if (isdragging === false) {
        slider.classList.remove(css.cursorgrab);
        return;
      }
      const x = parseInt(e.clientX) - parseInt(boundingrect.x) + 'px';
      slider.style.left = slidermask.style.left = x;
    }

    function onMouseMove(e) {

      //  if (lastx === e.pageX) return;
      lastx = e.clientX;

      if (slidermask !== null && canMove(e.pageX)) {
        hslide(e);
      }
    }
    slider.addEventListener('mousedown', function(e) {

      if (slidermask === null) {
        btn.removeEventListener('mousemove', onMouseMove);
        return false;
      }
      if (e.button === 0) {
        btn.addEventListener('mousemove', onMouseMove);

        isdragging = true;
        slider.classList.add(css.cursorgrab);
      }
    });
    slider.addEventListener('mouseup', function() {
      if (isdragging === true) {
        isdragging = false;
        slider.classList.remove(css.cursorgrab);
        btn.removeEventListener('mousemove', onMouseMove);
        slider.addEventListener('mouseup', function() {
          return null
        });
      }
    });
    slider.addEventListener('dragstart', function() {
      console.log('dragstart')
      return false;
    });
  }

}