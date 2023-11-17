/* modified from BotDetector for mouse /  detect*/
import {
  fetchSettings
} from '../modules/utils.js';
import BotDetect from '../modules/botdetect-clean.min.js';
const detect_device = function() {
  const matchmobs = [/Android/i, /webOS/i, /iPhone/i, /iPad/i, /iPod/i, /BlackBerry/i, /Windows Phone/i];
  if (matchmobs.some((item) => {
      return navigator.userAgent.match(item);
    })) return 'mobile';
  return 'desktop';
}
class JsCaptcha {
  counts = {};
  is_bot = false;
  detect_level = 500;

  constructor(container, options = {}) {
    const defaultOptions = {
      captcha: true,
      eventnames: {
        'desktop': ['keyup', 'mousemove', 'scroll', 'wheel'],
        'mobile': ['swipe', 'touchstart', 'touchmove', 'touchend', 'gesture', 'gyroscope', 'devicemotion', 'deviceorientation', 'MozOrientation']
      },
    };
    this.options = Object.assign(defaultOptions, options);
    this.checks = {};
    let passive = false;
    try {
      let options = Object.defineProperty({}, "passive", {
        get: function() {
          passive = true;
        },
      });

      window.addEventListener("test", null, options);
      window.removeEventListener("test", null, options);
    } catch (err) {
      passive = false;
    }
    this.evtopts = {
      once: true,
      passive: passive
    };

    this.form = container.querySelector('input') ? container.querySelector('input').form : (container.dataset.formid) ? document.getElementById(container.dataset.formid) : null;
    this.captcha = container;
    this.device = detect_device();
    this.init();
    this.submitOnCondition();

  }
  addEventFunction(windoc, eventname) {
    const doc = windoc;

    return () => {
      console.log('eventname', eventname)
      const event_func = () => {
        this.counts[eventname] = Date.now() - this.checks[eventname].t;
        console.log('counts' + eventname, this.counts[eventname])
      }
      doc.addEventListener(eventname, event_func, this.evtopts);
    };

  }
  init() {
    this.options.eventnames[this.device].forEach(eventname => {
      let f;
      this.checks[eventname] = {
        t: Date.now(),
        f: null
      };
      switch (eventname) {
        case 'devicemotion':
          f = () => {
            let movement;
            const event_func = (event) => {
              if (event.rotationRate.alpha || event.rotationRate.beta || event.rotationRate.gamma) {
                const userAgent = navigator.userAgent.toLowerCase();
                const isAndroid = userAgent.indexOf('android') != -1;
                const beta = isAndroid ? event.rotationRate.beta : Math.round(event.rotationRate.beta / 10) * 10;
                const gamma = isAndroid ? event.rotationRate.gamma : Math.round(event.rotationRate.gamma / 10) * 10;
                if (!this.lastRotationData) {
                  this.lastRotationData = {
                    beta: beta,
                    gamma: gamma
                  };
                } else {
                  movement = beta != this.lastRotationData.beta || gamma != this.lastRotationData.gamma;
                  if (isAndroid) {
                    movement = movement && (beta > 0.2 || gamma > 0.2);
                  }
                  var args = {
                    beta: beta,
                    gamma: gamma
                  }
                  if (movement) {
                    this.counts[eventname] = Date.now() - this.checks[eventname].t;
                    console.log('counts' + eventname, this.counts[eventname])
                    console.log('evtspe', this.counts)
                  }
                }
              }

            }
            window.addEventListener('devicemotion', event_func, this.evtopts);
          }

          break;
        default:
          f = this.addEventFunction(document, eventname);
          break;
      };
      this.checks[eventname].f = f;
    });

    this.mouseDetect();

  }
  mouseDetect() {
    Object.values(this.checks).forEach(check => {
      console.log('check', check.f)
      check.f();
    });
    let num = 0;
    const keys = Object.keys(this.counts);
    this.options.eventnames[this.device].forEach(eventname => {
      const index = keys.indexOf(eventname);
      if (index === -1) {
        if ((eventname === 'scroll' && keys.indexOf('wheel') !== -1 && this.counts["wheel"].t / 1000 > this.detect_level) || (eventname === 'wheel' && keys.indexOf('scroll') !== -1) && this.counts['scroll'].t / 1000 < this.detect_level) {
          num++;
        }
      } else {
        if (this.counts[eventname].t / 1000 > this.detect_level) num++;
        console.log('detect ' + this.detect_level, (this.counts[eventname].t / 1000))
      }
      console.log('ev' + num, eventname)
    });
    console.log('num' + num, this.options.eventnames[this.device].length * .9);

    if (num < this.options.eventnames[this.device].length * .9) {
      console.log('this.isbot' + num, this.counts);
      return true;
    } else return this.challenge();
  }
  challenge() {
    // hpot suppose that the bot fills an invisible input field
    const resp = this.captcha.dataset.response ? this.captcha.dataset.response : null;
    if (resp === null) return true;
    console.log("challenge" + resp.value, resp.placeholder);
    return (resp.value !== resp.placeholder);
  }
  botDetect() {
    console.log('botdetect', BotDetect)
    if (BotDetect !== undefined) {
      const proof_of_work = (verdict, token) => {
        if (verdict === false) verdict = this.is_bot;
        console.log('verdict', verdict)
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
export {
  JsCaptcha,

};