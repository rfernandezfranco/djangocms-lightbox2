/* Minimal justified rows builder. It groups items into rows so that
 * sum(width/height) scaled to target fills container width within tolerance. */
(function() {
  function buildJustified(container) {
    var rowHeight = parseInt(container.getAttribute('data-row-height') || '220', 10);
    var tolerance = parseFloat(container.getAttribute('data-tolerance') || '0.25');
    var gutter = parseInt(getComputedStyle(container).getPropertyValue('--dclb2-gutter') || '8', 10);
    var items = Array.prototype.slice.call(container.querySelectorAll(':scope > .dclb2-item'));
    if (!items.length) return;

    // Move items into a document fragment and clear container
    var frag = document.createDocumentFragment();
    items.forEach(function(it){ frag.appendChild(it); });
    container.innerHTML = '';

    function flushRow(row) {
      var rowEl = document.createElement('div');
      rowEl.className = 'dclb2-row';
      var containerWidth = container.clientWidth;
      var totalAspect = row.reduce(function(sum, it) {
        var img = it.querySelector('img');
        var w = img.naturalWidth || img.width || 1;
        var h = img.naturalHeight || img.height || 1;
        return sum + (w / h);
      }, 0);
      var targetH = Math.max(1, Math.min(rowHeight * (containerWidth / (totalAspect * rowHeight)), rowHeight * (1 + tolerance)));
      row.forEach(function(it, idx) {
        var img = it.querySelector('img');
        it.style.height = targetH + 'px';
        it.style.display = 'block';
        it.style.flex = '0 0 auto';
        rowEl.appendChild(it);
      });
      container.appendChild(rowEl);
    }

    var row = [];
    var currentAspect = 0;
    var containerWidth = container.clientWidth;
    items.forEach(function(it) {
      var img = it.querySelector('img');
      // If image not loaded, we approximate using element size
      var w = img.naturalWidth || img.width || 400;
      var h = img.naturalHeight || img.height || rowHeight;
      var aspect = w / h;
      row.push(it);
      currentAspect += aspect;
      var expectedWidth = currentAspect * rowHeight + gutter * (row.length - 1);
      if (expectedWidth >= containerWidth * (1 - tolerance)) {
        flushRow(row);
        row = [];
        currentAspect = 0;
        containerWidth = container.clientWidth;
      }
    });
    if (row.length) {
      flushRow(row);
    }
  }

  function init() {
    document.querySelectorAll('.dclb2-justified').forEach(buildJustified);
    var resizeTimer;
    window.addEventListener('resize', function(){
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(function(){
        document.querySelectorAll('.dclb2-justified').forEach(function(c){
          // Rebuild
          buildJustified(c);
        });
      }, 150);
    });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

