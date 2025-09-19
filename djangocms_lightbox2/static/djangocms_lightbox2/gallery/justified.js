/* Builds justified galleries while tolerating hidden containers and lazy images. */
(function() {
  var containers = new Set();

  function scheduleBuild(container, delay) {
    if (!container || !container.isConnected) return;
    if (container._dclb2JustifiedScheduled) return;

    container._dclb2JustifiedScheduled = true;

    var runner = function() {
      container._dclb2JustifiedScheduled = false;
      container._dclb2JustifiedTimer = null;
      container._dclb2JustifiedRaf = null;
      buildJustified(container);
    };

    if (delay) {
      container._dclb2JustifiedTimer = window.setTimeout(runner, delay);
      return;
    }

    if (typeof window.requestAnimationFrame === 'function') {
      container._dclb2JustifiedRaf = window.requestAnimationFrame(runner);
    } else {
      container._dclb2JustifiedTimer = window.setTimeout(runner, 16);
    }
  }

  function bindImageEvents(container) {
    container.querySelectorAll('img').forEach(function(img) {
      if (img._dclb2JustifiedBound) return;
      img._dclb2JustifiedBound = true;
      var handler = function() {
        scheduleBuild(container, 0);
      };
      img.addEventListener('load', handler);
      img.addEventListener('error', handler);
      if (img.complete && img.naturalWidth) {
        scheduleBuild(container, 0);
      }
    });
  }

  function observeContainer(container) {
    if (container._dclb2JustifiedObserved) return;
    container._dclb2JustifiedObserved = true;

    if (typeof window.ResizeObserver === 'function') {
      var ro = new window.ResizeObserver(function(entries) {
        entries.forEach(function(entry) {
          if (container._dclb2JustifiedBuilding) return;
          if (entry.contentRect && entry.contentRect.width <= 0) {
            scheduleBuild(container, 200);
          } else {
            scheduleBuild(container, 0);
          }
        });
      });
      ro.observe(container);
      container._dclb2JustifiedResizeObserver = ro;
    } else if (!window._dclb2JustifiedResizeFallbackBound) {
      window.addEventListener('resize', function() {
        containers.forEach(function(c) {
          scheduleBuild(c, 0);
        });
      });
      window._dclb2JustifiedResizeFallbackBound = true;
    }

    if (typeof window.IntersectionObserver === 'function') {
      var io = new window.IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
          if (entry.isIntersecting) {
            scheduleBuild(container, 0);
          }
        });
      }, { threshold: 0 });
      io.observe(container);
      container._dclb2JustifiedIntersectionObserver = io;
    }
  }

  function buildJustified(container) {
    if (!container || !container.isConnected) return;

    container._dclb2JustifiedBuilding = true;

    var width = container.clientWidth;
    if (width <= 0) {
      container._dclb2JustifiedBuilding = false;
      scheduleBuild(container, 250);
      return;
    }

    var items = Array.prototype.slice.call(container.querySelectorAll('.dclb2-item'));
    if (!items.length) {
      container._dclb2JustifiedBuilding = false;
      return;
    }

    var rowHeight = parseInt(container.getAttribute('data-row-height') || '220', 10);
    if (!rowHeight || rowHeight < 1) rowHeight = 220;

    var tolerance = parseFloat(container.getAttribute('data-tolerance') || '0.25');
    if (isNaN(tolerance) || tolerance < 0) tolerance = 0.25;

    var gutter = parseInt(window.getComputedStyle(container).getPropertyValue('--dclb2-gutter') || '8', 10);
    if (isNaN(gutter) || gutter < 0) gutter = 0;

    items.forEach(function(item) {
      if (item.parentNode) {
        item.parentNode.removeChild(item);
      }
      item.style.height = '';
      item.style.display = '';
      item.style.flex = '';
      item.style.flexBasis = '';
    });

    container.innerHTML = '';

    var currentRow = [];
    var currentAspect = 0;
    var availableWidth = width;

    function flushRow() {
      if (!currentRow.length) return;
      var row = currentRow;
      currentRow = [];
      var rowEl = document.createElement('div');
      rowEl.className = 'dclb2-row';

      var totalAspect = 0;
      row.forEach(function(item) {
        var img = item.querySelector('img');
        var w = img && (img.naturalWidth || img.width) || 1;
        var h = img && (img.naturalHeight || img.height) || rowHeight;
        totalAspect += w / h;
      });

      var gapTotal = gutter * Math.max(0, row.length - 1);
      var widthForImages = Math.max(1, availableWidth - gapTotal);
      var targetHeight = rowHeight;
      if (totalAspect > 0) {
        targetHeight = widthForImages / totalAspect;
      }

      var maxHeight = rowHeight * (1 + tolerance);
      if (targetHeight > maxHeight) targetHeight = maxHeight;
      if (targetHeight < 1) targetHeight = 1;

      row.forEach(function(item) {
        item.style.height = targetHeight + 'px';
        item.style.display = 'block';
        item.style.flex = '0 0 auto';
        rowEl.appendChild(item);
      });

      container.appendChild(rowEl);
      availableWidth = container.clientWidth || availableWidth;
    }

    items.forEach(function(item) {
      var img = item.querySelector('img');
      var w = img && (img.naturalWidth || img.width) || 400;
      var h = img && (img.naturalHeight || img.height) || rowHeight;
      var aspect = w / h;

      currentRow.push(item);
      currentAspect += aspect;

      var gapTotal = gutter * Math.max(0, currentRow.length - 1);
      var expectedWidth = currentAspect * rowHeight + gapTotal;
      if (expectedWidth >= availableWidth * (1 - tolerance)) {
        flushRow();
        currentAspect = 0;
        availableWidth = container.clientWidth || width;
      }
    });

    if (currentRow.length) {
      flushRow();
      currentAspect = 0;
    }

    bindImageEvents(container);
    container._dclb2JustifiedBuilding = false;
  }

  function init() {
    document.querySelectorAll('.dclb2-justified').forEach(function(container) {
      if (!container._dclb2JustifiedInit) {
        container._dclb2JustifiedInit = true;
        containers.add(container);
        observeContainer(container);
        bindImageEvents(container);
      }
      scheduleBuild(container, 0);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
