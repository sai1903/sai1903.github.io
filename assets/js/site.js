/* site.js — small, dependency-free. Theme, nav, reveal, tabs. */
(function () {
  'use strict';

  var root = document.documentElement;
  var STORE = 'bssk-theme';

  /* ---- theme ---------------------------------------------------- */
  // The inline script in <head> sets the initial value so there is no flash.
  // This only wires up the toggle.
  var toggle = document.querySelector('[data-theme-toggle]');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      toggle.setAttribute('aria-label', next === 'dark' ? 'Switch to light theme' : 'Switch to dark theme');
      try { localStorage.setItem(STORE, next); } catch (e) { /* private mode */ }
    });
  }

  /* ---- header shadow on scroll ---------------------------------- */
  var head = document.querySelector('.site-head');
  if (head) {
    var onScroll = function () {
      head.classList.toggle('is-stuck', window.scrollY > 8);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* ---- mobile nav ----------------------------------------------- */
  var navBtn = document.querySelector('[data-nav-toggle]');
  var nav = document.getElementById('nav');
  if (navBtn && nav) {
    var setNav = function (open) {
      nav.classList.toggle('is-open', open);
      navBtn.setAttribute('aria-expanded', String(open));
    };
    navBtn.addEventListener('click', function () {
      setNav(navBtn.getAttribute('aria-expanded') !== 'true');
    });
    nav.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') setNav(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') setNav(false);
    });
  }

  /* ---- reveal on scroll ----------------------------------------- */
  var targets = document.querySelectorAll('.reveal');
  var stillMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (!('IntersectionObserver' in window) || stillMotion) {
    Array.prototype.forEach.call(targets, function (el) { el.classList.add('is-in'); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        // stagger siblings a touch so a grid doesn't pop in all at once
        var i = Number(entry.target.dataset.revealIndex || 0);
        entry.target.style.transitionDelay = Math.min(i * 60, 240) + 'ms';
        entry.target.classList.add('is-in');
        io.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });

    Array.prototype.forEach.call(targets, function (el) { io.observe(el); });
  }

  /* ---- tabs (HRMS deep dive) ------------------------------------ */
  var tablist = document.querySelector('[role="tablist"]');
  if (tablist) {
    var tabs = Array.prototype.slice.call(tablist.querySelectorAll('[role="tab"]'));

    var select = function (tab, focus) {
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute('aria-selected', String(on));
        t.tabIndex = on ? 0 : -1;
        var panel = document.getElementById(t.getAttribute('aria-controls'));
        if (panel) panel.hidden = !on;
      });
      if (focus) tab.focus();
    };

    tabs.forEach(function (tab) {
      tab.addEventListener('click', function () { select(tab, false); });
    });

    tablist.addEventListener('keydown', function (e) {
      var i = tabs.indexOf(document.activeElement);
      if (i < 0) return;
      var next = null;
      if (e.key === 'ArrowRight') next = tabs[(i + 1) % tabs.length];
      if (e.key === 'ArrowLeft') next = tabs[(i - 1 + tabs.length) % tabs.length];
      if (e.key === 'Home') next = tabs[0];
      if (e.key === 'End') next = tabs[tabs.length - 1];
      if (next) { e.preventDefault(); select(next, true); }
    });
  }

  /* ---- ticker: duplicate the track so the loop is seamless ------- */
  var track = document.querySelector('.ticker__track');
  if (track && !stillMotion) {
    track.innerHTML += track.innerHTML;
  }


  /* ---- scroll progress bar --------------------------------------- */
  var bar = document.querySelector('.progress');
  if (bar) {
    var tick = function () {
      var h = document.documentElement.scrollHeight - window.innerHeight;
      bar.style.transform = 'scaleX(' + (h > 0 ? window.scrollY / h : 0) + ')';
    };
    tick();
    window.addEventListener('scroll', tick, { passive: true });
    window.addEventListener('resize', tick);
  }

  /* ---- count up the stat numbers once they scroll in ------------- */
  var nums = document.querySelectorAll('[data-count]');
  if (nums.length) {
    var run = function (el) {
      var target = parseFloat(el.dataset.count);
      var suffix = el.dataset.suffix || '';
      var dec = (el.dataset.count.split('.')[1] || '').length;
      if (stillMotion) { el.textContent = target.toFixed(dec) + suffix; return; }
      var t0 = null, dur = 1400;
      var step = function (t) {
        if (!t0) t0 = t;
        var k = Math.min((t - t0) / dur, 1);
        k = 1 - Math.pow(1 - k, 3);                       // ease-out cubic
        el.textContent = (target * k).toFixed(dec) + suffix;
        if (k < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    };

    if (!('IntersectionObserver' in window)) {
      Array.prototype.forEach.call(nums, run);
    } else {
      var cio = new IntersectionObserver(function (es) {
        es.forEach(function (e) {
          if (!e.isIntersecting) return;
          run(e.target);
          cio.unobserve(e.target);
        });
      }, { threshold: 0.5 });
      Array.prototype.forEach.call(nums, function (el) { cio.observe(el); });
    }
  }


  /* ---- carousel ---------------------------------------------------
     Scrolling is native (scroll-snap); the buttons and dots only nudge
     scrollLeft, so touch, trackpad and keyboard all keep working.     */
  Array.prototype.forEach.call(document.querySelectorAll('[data-carousel]'), function (root) {
    var view  = root.querySelector('.carousel__viewport');
    var track = root.querySelector('.carousel__track');
    var prev  = root.querySelector('[data-car-prev]');
    var next  = root.querySelector('[data-car-next]');
    var dots  = root.querySelector('.carousel__dots');
    var count = root.querySelector('[data-car-count]');
    if (!view || !track) return;

    var items = Array.prototype.slice.call(track.children);
    if (!items.length) return;

    var step = function () {
      // one card plus the flex gap
      var gap = parseFloat(getComputedStyle(track).columnGap || getComputedStyle(track).gap) || 0;
      return items[0].getBoundingClientRect().width + gap;
    };
    var perView = function () {
      return Math.max(1, Math.round(view.clientWidth / step()));
    };
    var pages = function () {
      return Math.max(1, Math.ceil(items.length / perView()));
    };
    var page = function () {
      return Math.min(pages() - 1, Math.round(view.scrollLeft / (step() * perView())));
    };

    // dots are built from the page count, so they survive a resize
    var buildDots = function () {
      if (!dots) return;
      var n = pages();
      if (dots.children.length === n) return;
      dots.innerHTML = '';
      for (var i = 0; i < n; i++) {
        var b = document.createElement('button');
        b.type = 'button';
        b.className = 'carousel__dot';
        b.setAttribute('aria-label', 'Go to slide ' + (i + 1));
        (function (idx) {
          b.addEventListener('click', function () {
            view.scrollTo({ left: idx * step() * perView(), behavior: stillMotion ? 'auto' : 'smooth' });
          });
        })(i);
        dots.appendChild(b);
      }
    };

    var sync = function () {
      buildDots();
      var p = page(), n = pages();
      if (dots) {
        Array.prototype.forEach.call(dots.children, function (d, i) {
          d.setAttribute('aria-current', String(i === p));
        });
      }
      if (count) count.textContent = (p + 1) + ' / ' + n;
      // a 2px slack keeps the end state stable on fractional widths
      if (prev) prev.disabled = view.scrollLeft <= 2;
      if (next) next.disabled = view.scrollLeft >= view.scrollWidth - view.clientWidth - 2;
    };

    var nudge = function (dir) {
      view.scrollBy({ left: dir * step() * perView(), behavior: stillMotion ? 'auto' : 'smooth' });
    };

    if (prev) prev.addEventListener('click', function () { nudge(-1); });
    if (next) next.addEventListener('click', function () { nudge(1); });

    view.addEventListener('scroll', function () {
      window.clearTimeout(view._t);
      view._t = window.setTimeout(sync, 90);
    }, { passive: true });

    window.addEventListener('resize', sync);

    root.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') { e.preventDefault(); nudge(1); }
      if (e.key === 'ArrowLeft')  { e.preventDefault(); nudge(-1); }
    });

    sync();
  });

  /* ---- year stamp ------------------------------------------------ */
  Array.prototype.forEach.call(document.querySelectorAll('[data-year]'), function (el) {
    el.textContent = String(new Date().getFullYear());
  });
})();
