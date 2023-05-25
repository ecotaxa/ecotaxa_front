export class ScrollSpy {
  pos = 0;
  throttle = false;
  menu = null;
  constructor(callback, options = {}) {
    if (!callback) return;
    if (typeof options !== 'object') return;
    const defaultOptions = {
      menu: null,
      container: null,
      offset: 0,
      activeClass: 'active',
      menuItemClass: 'nav-item',
      smoothScroll: {}
    }
    options = Object.assign({}, defaultOptions, options);
    options.smoothScroll = (options.smoothScroll === true && {}) || options.smoothScroll;

    this.options = Object.assign({}, defaultOptions, options);
    this.menu = options.menu instanceof HTMLElement ? options.menu : document.querySelector(options.menu);

    this.scrolltarget = (this.options.container) ? this.options.container instanceof HTMLElement ? this.options.container : document.querySelector(this.options.container) : window;

    this.scrollListener(callback);
  }

  scrollListener(callback) {
    this.scrolltarget.addEventListener('scroll', (e) => {
      this.pos = this.scrolltarget.scrollY;
      if (!this.throttle) {
        this.scrolltarget.requestAnimationFrame(() => {
          callback(this.pos);
          this.throttle = false;
        });
      }
      this.throttle = true;
    })

  }

}


/*
onScroll() {
  const section = this.getSectionInView()
  const menuItem = this.getMenuItemBySection(section)

  if (menuItem) {
    this.removeCurrentActive({
      ignore: menuItem
    })
    this.setActive(menuItem)
  }
}

}
constructor(menu, options = {}) {
  if (!menu) {
    throw new Error('First argument is query selector to your navigation.')
  }

  if (typeof options !== 'object') {
    throw new Error('Second argument must be instance of Object.')
  }

  let defaultOptions = {
    menuActiveTarget: 'li > a',
    offset: 0,
    hrefAttribute: 'href',
    activeClass: 'active',
    scrollContainer: '',
    smoothScroll: {},
  }

  options.smoothScroll = options.smoothScroll === true && {} || options.smoothScroll

  this.menuList = menu instanceof HTMLElement ? menu : document.querySelector(menu)
  this.options = Object.assign({}, defaultOptions, options)

  if (this.options.scrollContainer) {
    this.scroller = this.options.scrollContainer instanceof HTMLElement ? this.options.scrollContainer : document.querySelector(this.options.scrollContainer)
  } else {
    this.scroller = window
  }

  this.sections = document.querySelectorAll(this.options.sectionClass)

  this.attachEventListeners()
}

attachEventListeners() {
  if (this.scroller) {
    this.scroller.addEventListener('scroll', () => this.onScroll())

    // smooth scroll
    if (this.options.smoothScroll) {
      const menuItems = this.menuList.querySelectorAll(this.options.menuActiveTarget)
      menuItems.forEach((item) => item.addEventListener('click', this.onClick.bind(this)))
    }
  }
}

onClick(event) {
  const targetSelector = event.target.getAttribute(this.options.hrefAttribute)
  const targetElement = document.querySelector(targetSelector)

  if (targetElement && this.options.smoothScroll) {
    // prevent click event
    event.preventDefault()
    // handle smooth scrolling to 'targetElement'
    this.scrollTo(targetElement)
  }
}

scrollTo(targetElement) {
  const smoothScrollBehavior = typeof this.options.smoothScrollBehavior === 'function' && this.options.smoothScrollBehavior

  if (smoothScrollBehavior) {
    smoothScrollBehavior(targetElement, this.options.smoothScroll)
  } else {
    targetElement.scrollIntoView({
      ...this.options.smoothScroll,
      behavior: 'smooth',
    })
  }
}

getMenuItemBySection(section) {
  if (!section) return
  const sectionId = section.getAttribute('id')
  return this.menuList.querySelector(`[${this.options.hrefAttribute}="#${sectionId}"]`)
}

getSectionInView() {
  for (let i = 0; i < this.sections.length; i++) {
    const startAt = this.sections[i].offsetTop
    const endAt = startAt + this.sections[i].offsetHeight
    let currentPosition = (document.documentElement.scrollTop || document.body.scrollTop) + this.options.offset

    if (this.options.scrollContainer && this.scroller) {
      currentPosition = (this.scroller.scrollTop) + this.options.offset
    }

    const isInView = currentPosition > startAt && currentPosition <= endAt
    if (isInView) return this.sections[i]
  }
}

setActive(activeItem) {
  const isActive = activeItem.classList.contains(this.options.activeClass)
  if (!isActive) activeItem.classList.add(this.options.activeClass)
}

removeCurrentActive({
  ignore
}) {
  const {
    hrefAttribute,
    menuActiveTarget,
    activeClass
  } = this.options
  const items = `${menuActiveTarget}.${activeClass}:not([${hrefAttribute}="${ignore.getAttribute(hrefAttribute)}"])`
  const menuItems = this.menuList.querySelectorAll(items)

  menuItems.forEach((item) => item.classList.remove(this.options.activeClass))
}
}*/