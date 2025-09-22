(function() {
  function groupAnchors() {
    var map = {};
    var anchors = document.querySelectorAll('a[data-lightbox]');
    anchors.forEach(function(a) {
      var group = a.getAttribute('data-lightbox') || 'default';
      if (!map[group]) map[group] = [];
      var img = a.querySelector('img');
      var thumb = img ? img.getAttribute('src') : a.getAttribute('href');
      map[group].push({ anchor: a, href: a.getAttribute('href'), thumb: thumb });
    });
    return map;
  }

  var state = { group: null, index: 0, groups: {} };

  function ensureFilmstrip(lightboxEl, groupName) {
    var existing = lightboxEl.querySelector('.dclb2-filmstrip');
    if (existing) return existing;
    var fs = document.createElement('div');
    fs.className = 'dclb2-filmstrip';
    var strip = document.createElement('div');
    strip.className = 'dclb2-strip';
    fs.appendChild(strip);
    var list = state.groups[groupName] || [];
    list.forEach(function(item, i) {
      var btn = document.createElement('button');
      btn.className = 'dclb2-thumb';
      btn.setAttribute('type', 'button');
      btn.dataset.index = i;
      btn.setAttribute('aria-label', 'Ver imagen ' + (i + 1) + ' de ' + (list.length || 0));
      var img = document.createElement('img');
      img.src = item.thumb;
      img.alt = '';
      btn.appendChild(img);
      btn.addEventListener('click', function(e) {
        e.preventDefault();
        navigateTo(i);
      });
      strip.appendChild(btn);
    });
    var dataContainer = lightboxEl.querySelector('.lb-dataContainer') || lightboxEl;
    dataContainer.parentNode.insertBefore(fs, dataContainer.nextSibling);
    return fs;
  }

  function updateActive() {
    var lightboxEl = document.getElementById('lightbox');
    if (!lightboxEl) return;
    var thumbs = lightboxEl.querySelectorAll('.dclb2-thumb');
    thumbs.forEach(function(t) { t.classList.remove('active'); });
    var active = lightboxEl.querySelector('.dclb2-thumb[data-index="' + state.index + '"]');
    if (active) {
      active.classList.add('active');
      try { active.scrollIntoView({ block: 'nearest', inline: 'center', behavior: 'smooth' }); } catch (e) {}
    }
    updateHash();
  }

  function navigateTo(i) {
    state.index = i;
    if (window.lightbox && typeof window.lightbox.changeImage === 'function') {
      window.lightbox.changeImage(i);
    } else {
      var list = state.groups[state.group] || [];
      var item = list[i];
      if (item && item.anchor) item.anchor.click();
    }
    updateActive();
  }

  function attachSync(lightboxEl) {
    // ARIA roles and live region
    lightboxEl.setAttribute('role', 'dialog');
    lightboxEl.setAttribute('aria-modal', 'true');
    var dataLive = lightboxEl.querySelector('.lb-data');
    if (dataLive) dataLive.setAttribute('aria-live', 'polite');

    var prev = lightboxEl.querySelector('.lb-prev');
    var next = lightboxEl.querySelector('.lb-next');
    if (prev && !prev._dclb2Bound) {
      prev._dclb2Bound = true;
      prev.addEventListener('click', function() {
        var list = state.groups[state.group] || [];
        if (!list.length) return;
        state.index = (state.index - 1 + list.length) % list.length;
        updateActive();
      });
    }
    if (next && !next._dclb2Bound) {
      next._dclb2Bound = true;
      next.addEventListener('click', function() {
        var list = state.groups[state.group] || [];
        if (!list.length) return;
        state.index = (state.index + 1) % list.length;
        updateActive();
      });
    }
    // Swipe gestures
    attachSwipe(lightboxEl);

    var img = lightboxEl.querySelector('.lb-image');
    if (img && !img._dclb2Observer) {
      var obs = new MutationObserver(function(mutations) {
        mutations.forEach(function(m) {
          if (m.type === 'attributes' && m.attributeName === 'src') {
            var src = img.getAttribute('src');
            var list = state.groups[state.group] || [];
            var idx = list.findIndex(function(it) { 
              return it.href === src || (it.href && src && it.href.split('?')[0] === src.split('?')[0]); 
            });
            if (idx >= 0) { state.index = idx; updateActive(); }
          }
        });
      });
      obs.observe(img, { attributes: true, attributeFilter: ['src'] });
      img._dclb2Observer = obs;
    }

    var closeBtn = lightboxEl.querySelector('.lb-close');
    if (closeBtn && !closeBtn._dclb2Bound) {
      closeBtn._dclb2Bound = true;
      closeBtn.setAttribute('aria-label', 'Cerrar');
      closeBtn.addEventListener('click', function() {
        clearHash();
      });
    }

    attachA11y(lightboxEl);
  }

  function bind() {
    state.groups = groupAnchors();
    document.body.addEventListener('click', function(e) {
      var target = e.target;
      if (!target) return;
      var a = (target.closest && target.closest('a[data-lightbox]')) || null;
      if (!a) return;
      var group = a.getAttribute('data-lightbox') || 'default';
      var list = state.groups[group] || [];
      var index = 0;
      for (var i = 0; i < list.length; i++) { if (list[i].anchor === a) { index = i; break; } }
      state.group = group;
      state.index = index;
      setTimeout(function() {
        var lb = document.getElementById('lightbox');
        if (!lb) return;
        ensureFilmstrip(lb, group);
        updateActive();
        attachSync(lb);
      }, 0);
    }, true);

    // Deep link on load
    handleDeepLink();
    window.addEventListener('hashchange', handleDeepLink);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bind);
  } else {
    bind();
  }

  function parseLbToken(token) {
    if (!token) return null;
    try { token = decodeURIComponent(token); } catch (e) {}
    var group = token, idx = 1;
    if (token.indexOf(':') !== -1) {
      var parts = token.split(':');
      group = parts[0];
      idx = parseInt(parts[1] || '1', 10);
    }
    if (!group) return null;
    return { group: group, index: Math.max(0, (idx || 1) - 1) };
  }

  function getLbParam() {
    var hash = window.location.hash || '';
    var m = hash.match(/lb=([^&]+)/);
    if (m) return parseLbToken(m[1]);
    var params = new URLSearchParams(window.location.search);
    if (params.has('lb')) return parseLbToken(params.get('lb'));
    return null;
  }

  function handleDeepLink() {
    var p = getLbParam();
    if (!p) return;
    state.groups = state.groups && Object.keys(state.groups).length ? state.groups : groupAnchors();
    var list = state.groups[p.group] || [];
    if (!list.length) return;
    state.group = p.group;
    state.index = Math.min(p.index, list.length - 1);
    // If lightbox is open, navigate; otherwise click anchor to open
    var lb = document.getElementById('lightbox');
    if (lb && lb.style.display !== 'none') {
      navigateTo(state.index);
    } else {
      var item = list[state.index];
      if (item && item.anchor) item.anchor.click();
      setTimeout(function(){
        var lb2 = document.getElementById('lightbox');
        if (lb2) { ensureFilmstrip(lb2, state.group); updateActive(); attachSync(lb2); }
      }, 0);
    }
  }

  function updateHash() {
    if (!state.group) return;
    var token = state.group + ':' + (state.index + 1);
    try {
      history.replaceState(null, '', window.location.pathname + window.location.search + '#lb=' + encodeURIComponent(token));
    } catch (e) {
      window.location.hash = 'lb=' + token;
    }
  }

  function clearHash() {
    try {
      history.replaceState(null, '', window.location.pathname + window.location.search);
    } catch (e) {
      // Fallback: blank out hash
      window.location.hash = '';
    }
  }

  function attachA11y(lightboxEl) {
    if (lightboxEl._dclb2A11yBound) return;
    lightboxEl._dclb2A11yBound = true;
    lightboxEl.addEventListener('keydown', function(e){
      if (e.key !== 'Tab') return;
      var focusables = lightboxEl.querySelectorAll('a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])');
      focusables = Array.prototype.filter.call(focusables, function(el){ return !el.hasAttribute('disabled') && el.tabIndex !== -1 && el.offsetParent !== null; });
      if (!focusables.length) return;
      var first = focusables[0];
      var last = focusables[focusables.length - 1];
      if (e.shiftKey) {
        if (document.activeElement === first) { last.focus(); e.preventDefault(); }
      } else {
        if (document.activeElement === last) { first.focus(); e.preventDefault(); }
      }
    });
    // Move initial focus to close or next
    var initial = lightboxEl.querySelector('.lb-close, .lb-next, .lb-prev');
    if (initial) {
      try { initial.focus(); } catch (e) {}
    }
  }

  function attachSwipe(lightboxEl) {
    var surface = lightboxEl.querySelector('.lb-outerContainer') || lightboxEl;
    if (!surface || surface._dclb2SwipeBound) return;
    surface._dclb2SwipeBound = true;
    var startX = 0, startY = 0, tracking = false;
    surface.addEventListener('touchstart', function(e){
      if (!e.touches || e.touches.length !== 1) return;
      tracking = true;
      startX = e.touches[0].clientX;
      startY = e.touches[0].clientY;
    }, { passive: true });
    surface.addEventListener('touchend', function(e){
      if (!tracking) return; tracking = false;
      var t = e.changedTouches && e.changedTouches[0];
      if (!t) return;
      var dx = t.clientX - startX;
      var dy = t.clientY - startY;
      if (Math.abs(dx) > 40 && Math.abs(dx) > Math.abs(dy)) {
        var list = state.groups[state.group] || [];
        if (!list.length) return;
        if (dx < 0) {
          // swipe left -> next
          state.index = (state.index + 1) % list.length;
          if (window.lightbox && typeof window.lightbox.changeImage === 'function') window.lightbox.changeImage(state.index);
        } else {
          // swipe right -> prev
          state.index = (state.index - 1 + list.length) % list.length;
          if (window.lightbox && typeof window.lightbox.changeImage === 'function') window.lightbox.changeImage(state.index);
        }
        updateActive();
      }
    });
  }
})();
