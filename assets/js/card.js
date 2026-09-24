/* card.js — vCard download, native share, and a QR of wherever this page lives. */
(function () {
  'use strict';

  var root = document.documentElement;
  var STORE = 'bssk-theme';

  var ME = {
    first: 'Sai Surya Kiran',
    last: 'Baratam',
    full: 'Baratam Sai Surya Kiran',
    title: 'AI & Data Engineer',
    org: 'Commbricks',
    tel: '+918919274754',
    email: 'saisuryakiranbaratam@gmail.com',
    city: 'Hyderabad',
    country: 'India',
    note: 'AI and data engineering, 10+ years. PhD research on quantum computing for AI, AGI and ASI models.'
  };

  /* ---- theme ----------------------------------------------------- */
  var toggle = document.querySelector('[data-theme-toggle]');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem(STORE, next); } catch (e) {}
    });
  }

  /* ---- toast ----------------------------------------------------- */
  var toastEl = document.getElementById('toast');
  var toastTimer;
  function toast(msg) {
    if (!toastEl) return;
    toastEl.textContent = msg;
    toastEl.classList.add('is-up');
    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(function () { toastEl.classList.remove('is-up'); }, 2200);
  }

  /* ---- save to contacts -------------------------------------------
     A real contact.vcf file rather than a Blob built here: iOS Safari
     opens it straight into "Add to Contacts", and it still works with
     JavaScript disabled. Regenerate it with tools/make-vcard.py.      */
  var saveBtn = document.getElementById('save');
  if (saveBtn) {
    saveBtn.addEventListener('click', function () {
      toast('Opening contact card…');
    });
  }

  /* ---- share ------------------------------------------------------ */
  var shareBtn = document.getElementById('share');
  if (shareBtn) {
    shareBtn.addEventListener('click', function () {
      var url = location.href.split('#')[0];
      var data = { title: ME.full, text: ME.full + ' — ' + ME.title, url: url };

      if (navigator.share) {
        navigator.share(data).catch(function (err) {
          // a user cancelling the sheet is not an error worth reporting
          if (err && err.name !== 'AbortError') copyLink(url);
        });
      } else {
        copyLink(url);
      }
    });
  }

  function copyLink(url) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(
        function () { toast('Link copied'); },
        function () { legacyCopy(url); }
      );
    } else {
      legacyCopy(url);
    }
  }

  function legacyCopy(url) {
    var t = document.createElement('textarea');
    t.value = url;
    t.setAttribute('readonly', '');
    t.style.cssText = 'position:absolute;left:-9999px';
    document.body.appendChild(t);
    t.select();
    var ok = false;
    try { ok = document.execCommand('copy'); } catch (e) {}
    t.remove();
    toast(ok ? 'Link copied' : url);
  }

  /* ---- QR of the current page ------------------------------------- */
  var box = document.getElementById('qr');
  var urlOut = document.getElementById('qrurl');
  var url = location.href.split('#')[0];

  if (urlOut) {
    urlOut.textContent = url.replace(/^https?:\/\//, '');
    urlOut.href = url;
  }

  if (box && typeof qrcode === 'function') {
    try {
      var q = qrcode(0, 'M');       // 0 = pick the smallest version that fits
      q.addData(url);
      q.make();
      // createSvgTag scales to the container, so it stays crisp at any size
      box.innerHTML = q.createSvgTag({ cellSize: 4, margin: 0, scalable: true });
      var svg = box.querySelector('svg');
      if (svg) {
        svg.setAttribute('role', 'img');
        svg.setAttribute('aria-label', 'QR code linking to ' + url);
      }
    } catch (e) {
      box.innerHTML = '';
      if (urlOut) urlOut.textContent = url.replace(/^https?:\/\//, '');
    }
  }

  /* ---- year ------------------------------------------------------- */
  Array.prototype.forEach.call(document.querySelectorAll('[data-year]'), function (el) {
    el.textContent = String(new Date().getFullYear());
  });
})();
