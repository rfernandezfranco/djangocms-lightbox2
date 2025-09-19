/* Ajustes de tamaño del overlay para integrarse con Django CMS. */
(function (window, document) {
  'use strict';

  var $ = window.jQuery;

  function getToolbarHeight() {
    var toolbar = document.getElementById('cms-toolbar');
    if (!toolbar) {
      return 0;
    }
    var height = toolbar.offsetHeight || 0;
    if (!height) {
      return 0;
    }
    if (toolbar.offsetParent === null) {
      var expandedClass = 'cms-toolbar-expanded';
      var html = document.documentElement;
      var body = document.body;
      if (!(html && html.classList && html.classList.contains(expandedClass)) &&
          !(body && body.classList && body.classList.contains(expandedClass))) {
        return 0;
      }
    }
    return height;
  }

  function setToolbarHeightVar(height) {
    var value = height > 0 ? height + 'px' : '0px';
    if (document.documentElement && document.documentElement.style) {
      document.documentElement.style.setProperty('--dclb2-toolbar-height', value);
    }
  }

  function clearOverlayInlineStyles(overlayEl) {
    if (!overlayEl || !overlayEl.style) {
      return;
    }
    overlayEl.style.removeProperty('width');
    overlayEl.style.removeProperty('height');
    overlayEl.style.removeProperty('top');
    overlayEl.style.removeProperty('min-height');
  }

  function updateOverlayState($overlay) {
    if (!$overlay || !$overlay.length) {
      return;
    }
    var overlayEl = $overlay[0];
    clearOverlayInlineStyles(overlayEl);
    var toolbarHeight = getToolbarHeight();
    setToolbarHeightVar(toolbarHeight);
    if (toolbarHeight > 0) {
      overlayEl.classList.add('dclb2-toolbar-visible');
    } else {
      overlayEl.classList.remove('dclb2-toolbar-visible');
    }
  }

  function refreshOverlayIfVisible() {
    if (!$) {
      return;
    }
    var $overlay = $('#lightboxOverlay');
    if (!$overlay.length || $overlay.css('display') === 'none') {
      return;
    }
    updateOverlayState($overlay);
  }

  function patchLightbox(instance) {
    if (!instance || !instance.constructor || !instance.constructor.prototype) {
      return false;
    }
    var proto = instance.constructor.prototype;
    if (proto.__djangocmsLightboxPatched) {
      return true;
    }
    proto.sizeOverlay = function () {
      var self = this;
      window.setTimeout(function () {
        updateOverlayState(self.$overlay);
      }, 0);
    };
    proto.__djangocmsLightboxPatched = true;
    return true;
  }

  var observer;
  function setupToolbarObserver() {
    if (observer || !('MutationObserver' in window)) {
      return;
    }
    observer = new MutationObserver(function (mutations) {
      for (var i = 0; i < mutations.length; i += 1) {
        if (mutations[i].attributeName === 'class') {
          refreshOverlayIfVisible();
          break;
        }
      }
    });
    if (document.documentElement) {
      observer.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['class']
      });
    }
    if (document.body) {
      observer.observe(document.body, {
        attributes: true,
        attributeFilter: ['class']
      });
    }
  }

  var attempts = 0;
  function attemptPatch() {
    attempts += 1;
    if (window.lightbox && patchLightbox(window.lightbox)) {
      try {
        window.lightbox.option({ disableScrolling: true });
      } catch (err) {
        // noop: mantener compatibilidad si option no está disponible
      }
      setupToolbarObserver();
      refreshOverlayIfVisible();
      return;
    }
    if (attempts < 50) {
      window.setTimeout(attemptPatch, 100);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', attemptPatch);
  } else {
    attemptPatch();
  }
})(window, document);
