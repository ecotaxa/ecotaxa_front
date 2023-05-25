//from css tricks
// used in tables about project stats details
// used in tables imports when cells contains lots of data
// apply mostly to details tags
export class JsAccordion {
  // animation and specific display on accordions list / details tag open 
  constructor(el, callbackopen = null, callbackclose = null, content = null, options = {}, summary = null) {
    // Store the <details> element
    this.el = el;
    this.summary = (summary) ? ((summary instanceof HTMLElement) ? summary : el.querySelector(summary)) : ((el.querySelector('summary')) ? el.querySelector('summary') : el);
    if (!this.summary) return;
    this.content = (content) ? ((content instanceof HTMLElement) ? content : el.querySelector(content)) : el.nextElementSibling;
    if (!this.content) return;
    const defaultOptions = {
      shrink: {
        opacity: [100, 0],
        scaleY: [1, 0]
      },
      expand: {
        opacity: [0, 100],
        scaleY: [0, 1]
      }
    }
    this.options = Object.assign(defaultOptions, options);
    Object.freeze(this.options);
    this.animation = null;
    this.isClosing = false;
    this.isExpanding = false;
    this.summary.addEventListener('click', (e) => this.onClick(e));
    this.callbackopen = callbackopen;
    this.callbackclose = callbackclose;
  }
  onClick(e) {
    e.preventDefault();
    // Check if the element is being closed or is already closed
    if (this.isClosing || !this.el.open) {
      // for fetching data or other op.
      if (this.callbackopen) {
        this.callbackopen(this.el, () => {
          this.open();
        });
      } else this.open();
      // Check if the element is being openned or is already open
    } else if (this.isExpanding || this.el.open) {
      this.shrink();

    }

  }
  // close the content with an animation
  shrink() {
    this.isClosing = true;
    if (this.animation) this.animation.cancel();
    // Start a WAAPI animation
    this.animation = this.content.animate(this.options.shrink, {
      duration: 400,
      easing: 'ease-out'
    });
    this.animation.onfinish = () => this.onAnimationFinish(false);
    this.animation.oncancel = () => this.isClosing = false;
    if (this.callbackclose) this.callbackclose(this.el);
  }

  open() {
    this.el.open = true;
    window.requestAnimationFrame(() => this.expand());
  }
  expand() {
    this.isExpanding = true;
    if (this.animation) this.animation.cancel();
    // Start a WAAPI animation
    this.animation = this.content.animate(this.options.expand, {
      duration: 400,
      easing: 'ease-out'
    });
    this.animation.onfinish = () => this.onAnimationFinish(true);
    this.animation.oncancel = () => this.isExpanding = false;
  }

  onAnimationFinish(open) {
    this.el.open = open;
    this.animation = null;
    this.isClosing = false;
    this.isExpanding = false;
  }
}