(function() {
  if (window.dclb2CarouselLoaded) return;
  window.dclb2CarouselLoaded = true;

  var carousels = new Set();

  function forEachCarousel(root, callback) {
    if (!root || !root.querySelectorAll) return;
    if (root.matches && root.matches('.dclb2-carousel')) callback(root);
    root.querySelectorAll('.dclb2-carousel').forEach(callback);
  }

  function init(root) {
    if (root.__dclb2CarouselInitialized) return;
    var slides = Array.prototype.slice.call(root.querySelectorAll('.dclb2-slide'));
    var thumbs = Array.prototype.slice.call(root.querySelectorAll('.dclb2-thumb'));
    if (!slides.length) return;

    var prev = root.querySelector('.dclb2-thumbs-prev') || root.querySelector('.dclb2-prev');
    var next = root.querySelector('.dclb2-thumbs-next') || root.querySelector('.dclb2-next');
    var strip = root.querySelector('.dclb2-thumbs-strip') || root.querySelector('.dclb2-carousel-thumbs');
    var anchors = slides.map(function(slide) {
      return slide.querySelector('.dclb2-item');
    });
    var cleanup = [];
    var previousTabindex = root.getAttribute('tabindex');
    var index = Math.max(0, slides.findIndex(function(s) {
      return s.classList.contains('is-active');
    }));
    if (index === -1) index = 0;

    function listen(target, event, handler) {
      target.addEventListener(event, handler);
      cleanup.push(function() {
        target.removeEventListener(event, handler);
      });
    }

    function activate(i) {
      slides.forEach(function(s) {
        s.classList.remove('is-active');
        s.setAttribute('aria-hidden', 'true');
      });
      thumbs.forEach(function(t) {
        t.classList.remove('active');
        t.setAttribute('aria-selected', 'false');
        t.setAttribute('tabindex', '-1');
      });
      index = (i + slides.length) % slides.length;
      slides[index].classList.add('is-active');
      slides[index].setAttribute('aria-hidden', 'false');
      if (thumbs[index]) {
        var thumbEl = thumbs[index];
        thumbEl.classList.add('active');
        thumbEl.setAttribute('aria-selected', 'true');
        thumbEl.setAttribute('tabindex', '0');
        try {
          if (strip && typeof strip.scrollLeft === 'number') {
            var stripRect = strip.getBoundingClientRect();
            var thumbRect = thumbEl.getBoundingClientRect();
            if (thumbRect.left < stripRect.left || thumbRect.right > stripRect.right) {
              thumbEl.scrollIntoView({behavior: 'smooth', block: 'nearest', inline: 'center'});
            }
          } else if (thumbEl.scrollIntoView) {
            thumbEl.scrollIntoView({behavior: 'smooth', block: 'nearest', inline: 'center'});
          }
        } catch (e) {}
      }
    }

    activate(index);

    thumbs.forEach(function(btn) {
      var i = parseInt(btn.getAttribute('data-index') || '0', 10) || 0;
      listen(btn, 'click', function(e) {
        e.preventDefault();
        activate(i);
      });
      listen(btn, 'keydown', function(e) {
        var nextIndex = null;
        if (e.key === 'ArrowRight' || e.key === 'ArrowDown') nextIndex = i + 1;
        if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') nextIndex = i - 1;
        if (e.key === 'Home') nextIndex = 0;
        if (e.key === 'End') nextIndex = slides.length - 1;
        if (nextIndex === null) return;
        e.preventDefault();
        activate(nextIndex);
        if (thumbs[index]) thumbs[index].focus();
      });
    });
    if (prev) listen(prev, 'click', function() { activate(index - 1); });
    if (next) listen(next, 'click', function() { activate(index + 1); });

    var $ = window.jQuery;
    if ($ && typeof $.fn.on === 'function') {
      var lightboxEvent = 'lightbox:change.dclb2Carousel';
      var syncLightbox = function(event, data) {
        if (!data || !Array.isArray(data.album)) return;
        var current = data.album[data.currentImageIndex];
        if (!current || !current.link) return;
        var matchingIndex = anchors.findIndex(function(anchor) {
          return anchor && anchor.getAttribute('href') === current.link;
        });
        if (matchingIndex !== -1) activate(matchingIndex);
      };
      $(document).on(lightboxEvent, syncLightbox);
      cleanup.push(function() {
        if (typeof $.fn.off === 'function') $(document).off(lightboxEvent, syncLightbox);
      });
    }

    listen(root, 'click', function(e) {
      var fs = e.target.closest && e.target.closest('.dclb2-fullscreen');
      if (!fs || !root.contains(fs)) return;
      e.preventDefault();
      var current = slides[index];
      var a = current && current.querySelector('.dclb2-item');
      if (a) a.click();
    });

    root.setAttribute('tabindex', '0');
    listen(root, 'keydown', function(e) {
      if (e.key === 'ArrowLeft') { e.preventDefault(); activate(index - 1); }
      if (e.key === 'ArrowRight') { e.preventDefault(); activate(index + 1); }
    });

    root.__dclb2CarouselInitialized = true;
    root.__dclb2CarouselDestroy = function() {
      if (!root.__dclb2CarouselInitialized) return;
      cleanup.splice(0).forEach(function(dispose) { dispose(); });
      if (previousTabindex === null) root.removeAttribute('tabindex');
      else root.setAttribute('tabindex', previousTabindex);
      root.__dclb2CarouselInitialized = false;
      root.__dclb2CarouselDestroy = null;
      carousels.delete(root);
    };
    carousels.add(root);
  }

  function destroy(root) {
    if (root && root.__dclb2CarouselDestroy) root.__dclb2CarouselDestroy();
  }

  function initWithin(root) {
    forEachCarousel(root, init);
  }

  function destroyWithin(root) {
    forEachCarousel(root, destroy);
  }

  function cleanupDetachedCarousels() {
    carousels.forEach(function(root) {
      if (!root.isConnected) destroy(root);
    });
  }

  function initAll() {
    cleanupDetachedCarousels();
    initWithin(document);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAll);
  } else {
    initAll();
  }

  window.dclb2CarouselInit = initAll;
  window.dclb2CarouselDestroy = destroyWithin;

  if (typeof MutationObserver === 'function') {
    var observer = new MutationObserver(function(mutations) {
      cleanupDetachedCarousels();
      mutations.forEach(function(mutation) {
        mutation.removedNodes.forEach(function(node) {
          if (node && node.nodeType === 1) destroyWithin(node);
        });
        mutation.addedNodes.forEach(function(node) {
          if (node && node.nodeType === 1) initWithin(node);
        });
      });
    });
    var target = document.documentElement || document.body;
    if (target) observer.observe(target, {childList: true, subtree: true});
  }

  if (typeof document !== 'undefined') {
    ['cms-content-refresh', 'cms-structure-update'].forEach(function(evt) {
      document.addEventListener(evt, initAll, false);
    });
  }
})();
