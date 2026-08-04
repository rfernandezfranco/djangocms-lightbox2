(function() {
  function init(root) {
    if (root.__dclb2CarouselInitialized) return;
    var slides = Array.prototype.slice.call(root.querySelectorAll('.dclb2-slide'));
    var thumbs = Array.prototype.slice.call(root.querySelectorAll('.dclb2-thumb'));
    if (!slides.length) return;
    var prev = root.querySelector('.dclb2-thumbs-prev') || root.querySelector('.dclb2-prev');
    var next = root.querySelector('.dclb2-thumbs-next') || root.querySelector('.dclb2-next');
    var strip = root.querySelector('.dclb2-thumbs-strip') || root.querySelector('.dclb2-carousel-thumbs');
    root.__dclb2CarouselInitialized = true;
    var index = Math.max(0, slides.findIndex(function(s){ return s.classList.contains('is-active'); }));
    if (index === -1) index = 0;
    function activate(i) {
      slides.forEach(function(s){ s.classList.remove('is-active'); });
      thumbs.forEach(function(t){ t.classList.remove('active'); t.setAttribute('aria-selected', 'false'); });
      index = (i + slides.length) % slides.length;
      slides[index].classList.add('is-active');
      if (thumbs[index]) {
        var thumbEl = thumbs[index];
        thumbEl.classList.add('active');
        thumbEl.setAttribute('aria-selected', 'true');
        try {
          if (strip && typeof strip.scrollLeft === 'number') {
            var stripRect = strip.getBoundingClientRect();
            var thumbRect = thumbEl.getBoundingClientRect();
            if (thumbRect.left < stripRect.left || thumbRect.right > stripRect.right) {
              thumbEl.scrollIntoView({behavior:'smooth', block:'nearest', inline:'center'});
            }
          } else if (thumbEl.scrollIntoView) {
            thumbEl.scrollIntoView({behavior:'smooth', block:'nearest', inline:'center'});
          }
        } catch(e){}
      }
    }
    // Initial state
    activate(index);

    thumbs.forEach(function(btn) {
      var i = parseInt(btn.getAttribute('data-index') || '0', 10) || 0;
      btn.addEventListener('click', function(e) { e.preventDefault(); activate(i); });
    });
    if (prev) prev.addEventListener('click', function() { activate(index - 1); });
    if (next) next.addEventListener('click', function() { activate(index + 1); });

    // Keep the carousel state aligned with Lightbox2 overlay navigation.
    var $ = window.jQuery;
    if ($ && typeof $.fn.on === 'function') {
      var anchors = slides.map(function(slide) {
        return slide.querySelector('.dclb2-item');
      });
      $(document).on('lightbox:change.dclb2Carousel', function(event, data) {
        if (!data || !Array.isArray(data.album)) return;
        var current = data.album[data.currentImageIndex];
        if (!current || !current.link) return;
        var matchingIndex = anchors.findIndex(function(anchor) {
          return anchor && anchor.getAttribute('href') === current.link;
        });
        if (matchingIndex !== -1) activate(matchingIndex);
      });
    }

    // Fullscreen button: open current slide anchor (Lightbox2)
    root.addEventListener('click', function(e){
      var fs = e.target.closest && e.target.closest('.dclb2-fullscreen');
      if (!fs || !root.contains(fs)) return;
      e.preventDefault();
      var current = slides[index];
      var a = current && current.querySelector('.dclb2-item');
      if (a) a.click();
    });

    // Keyboard support: Left/Right arrows
    root.setAttribute('tabindex', '0');
    root.addEventListener('keydown', function(e){
      if (e.key === 'ArrowLeft') { e.preventDefault(); activate(index - 1); }
      if (e.key === 'ArrowRight') { e.preventDefault(); activate(index + 1); }
    });
  }
  function bind() { document.querySelectorAll('.dclb2-carousel').forEach(init); }
  if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', bind); } else { bind(); }
})();
