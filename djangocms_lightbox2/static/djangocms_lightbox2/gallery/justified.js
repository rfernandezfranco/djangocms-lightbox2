/* Builds justified galleries while tolerating hidden containers and lazy images. */

(function() {
  var containers = new Set();
  var TABLET_BREAKPOINT = 1024;
  var MOBILE_BREAKPOINT = 640;

  function readPositiveNumber(value, fallback) {
    var str = value;
    if (str === undefined || str === null) {
      str = '';
    }
    if (typeof str !== 'string') {
      str = String(str);
    }
    str = str.trim();
    if (!str) return fallback;
    var n = parseFloat(str);
    if (!isFinite(n) || n <= 0) return fallback;
    return n;
  }

  function getColumnsConfig(container, styles) {
    styles = styles || window.getComputedStyle(container);
    var desktop = readPositiveNumber(container.getAttribute('data-cols-desktop'), readPositiveNumber(styles.getPropertyValue('--dclb2-cols-desktop'), 4));
    var tablet = readPositiveNumber(container.getAttribute('data-cols-tablet'), readPositiveNumber(styles.getPropertyValue('--dclb2-cols-tablet'), desktop));
    var mobile = readPositiveNumber(container.getAttribute('data-cols-mobile'), readPositiveNumber(styles.getPropertyValue('--dclb2-cols-mobile'), 1));
    return {
      desktop: Math.max(1, Math.round(desktop)),
      tablet: Math.max(1, Math.round(tablet)),
      mobile: Math.max(1, Math.round(mobile))
    };
  }

  function pickColumnsForWidth(width, columns) {
    if (width <= MOBILE_BREAKPOINT) return columns.mobile;
    if (width <= TABLET_BREAKPOINT) return columns.tablet;
    return columns.desktop;
  }

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

    var styles = window.getComputedStyle(container);
    var gutter = parseInt(styles.getPropertyValue('--dclb2-gutter') || '8', 10);
    if (isNaN(gutter) || gutter < 0) gutter = 0;

    var columnsConfig = getColumnsConfig(container, styles);
    var targetColumns = pickColumnsForWidth(width, columnsConfig);
    if (!targetColumns || targetColumns < 1) targetColumns = 1;

    var tolerance = parseFloat(container.getAttribute('data-tolerance') || '0.25');
    if (!isFinite(tolerance) || tolerance < 0) tolerance = 0.25;
    var clampedTolerance = Math.max(0, tolerance);

    var rowHeightAttr = parseFloat(container.getAttribute('data-row-height') || '220');
    if (!isFinite(rowHeightAttr) || rowHeightAttr <= 0) rowHeightAttr = 220;

    var allowAutoHeight = container.getAttribute('data-row-height-auto') !== 'false';
    var manualRowHeight = allowAutoHeight ? null : rowHeightAttr;

    var fallbackHeight = rowHeightAttr || 220;
    var fallbackAspect = 1.5;
    var totalAspectForAvg = 0;

    items.forEach(function(item) {
      var img = item.querySelector('img');
      var w = img && (img.naturalWidth || img.width);
      var h = img && (img.naturalHeight || img.height);
      if (!isFinite(h) || h <= 0) {
        h = fallbackHeight;
      }
      if (!isFinite(w) || w <= 0) {
        w = h * fallbackAspect;
      }
      if (!isFinite(h) || h <= 0) {
        h = fallbackHeight || 220;
      }
      totalAspectForAvg += w / h;
    });

    var avgAspect = totalAspectForAvg / items.length;
    if (!isFinite(avgAspect) || avgAspect <= 0) {
      avgAspect = fallbackAspect;
    }

    var desiredColumns = Math.max(1, targetColumns);
    var gutterTotal = gutter * Math.max(0, desiredColumns - 1);
    var widthForImages = Math.max(1, width - gutterTotal);
    var autoRowHeight = widthForImages / (desiredColumns * avgAspect);

    var baseRowHeight;
    if (manualRowHeight && manualRowHeight > 0) {
      baseRowHeight = manualRowHeight;
    } else if (isFinite(autoRowHeight) && autoRowHeight > 0) {
      baseRowHeight = autoRowHeight;
    } else {
      baseRowHeight = rowHeightAttr;
    }

    if (!isFinite(baseRowHeight) || baseRowHeight <= 0) {
      baseRowHeight = 220;
    }

    var minHeight;
    var maxHeight;
    if (manualRowHeight && manualRowHeight > 0) {
      minHeight = maxHeight = baseRowHeight;
    } else {
      var toleranceClamp = Math.min(clampedTolerance, 0.95);
      minHeight = Math.max(1, baseRowHeight * (1 - toleranceClamp));
      maxHeight = Math.max(minHeight, baseRowHeight * (1 + clampedTolerance));
    }

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
        var w = img && (img.naturalWidth || img.width);
        var h = img && (img.naturalHeight || img.height);
        if (!isFinite(h) || h <= 0) h = baseRowHeight;
        if (!isFinite(w) || w <= 0) w = h * fallbackAspect;
        totalAspect += w / h;
      });

      var gapTotal = gutter * Math.max(0, row.length - 1);
      var widthForRow = Math.max(1, (container.clientWidth || availableWidth) - gapTotal);
      var targetHeight = baseRowHeight;

      if (totalAspect > 0 && (!manualRowHeight || manualRowHeight <= 0)) {
        targetHeight = widthForRow / totalAspect;
        if (!isFinite(targetHeight) || targetHeight <= 0) {
          targetHeight = baseRowHeight;
        }
        if (targetHeight > maxHeight) targetHeight = maxHeight;
        if (targetHeight < minHeight) targetHeight = minHeight;
      } else {
        targetHeight = baseRowHeight;
      }

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
      var w = img && (img.naturalWidth || img.width);
      var h = img && (img.naturalHeight || img.height);
      if (!isFinite(h) || h <= 0) h = baseRowHeight;
      if (!isFinite(w) || w <= 0) w = h * fallbackAspect;
      var aspect = w / h;

      currentRow.push(item);
      currentAspect += aspect;

      var gapTotal = gutter * Math.max(0, currentRow.length - 1);
      var expectedWidth = currentAspect * baseRowHeight + gapTotal;
      if (expectedWidth >= availableWidth * (1 - clampedTolerance)) {
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

  function initWithin(root) {
    if (!root || !root.querySelectorAll) {
      return;
    }
    root.querySelectorAll('.dclb2-justified').forEach(function(container) {
      if (!container._dclb2JustifiedInit) {
        container._dclb2JustifiedInit = true;
        containers.add(container);
        observeContainer(container);
        bindImageEvents(container);
      }
      scheduleBuild(container, 0);
    });
  }

  function init() {
    initWithin(document);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  if (typeof window !== 'undefined') {
    window.dclb2JustifiedInit = init;
  }

  if (typeof MutationObserver === 'function') {
    var observer = new MutationObserver(function(mutations) {
      mutations.forEach(function(mutation) {
        mutation.addedNodes.forEach(function(node) {
          if (!node || node.nodeType !== 1) {
            return;
          }
          if (node.matches && node.matches('.dclb2-justified')) {
            initWithin(node);
          } else if (node.querySelectorAll) {
            initWithin(node);
          }
        });
      });
    });
    var target = document.documentElement || document.body;
    if (target) {
      observer.observe(target, { childList: true, subtree: true });
    }
  }

  if (typeof document !== 'undefined') {
    ['cms-content-refresh', 'cms-structure-update'].forEach(function(evt) {
      document.addEventListener(evt, init, false);
    });
  }
})();
