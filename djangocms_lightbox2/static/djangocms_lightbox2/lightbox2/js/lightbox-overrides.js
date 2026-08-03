/* Overlay sizing tweaks to integrate with Django CMS. */
(function (window, document) {
  'use strict';

  var $ = window.jQuery;

  function clearOverlayInlineStyles(overlayEl) {
    if (!overlayEl || !overlayEl.style) {
      return;
    }
    overlayEl.style.removeProperty('width');
    overlayEl.style.removeProperty('height');
    overlayEl.style.removeProperty('top');
    overlayEl.style.removeProperty('min-height');
  }

  function resetOverlayStyles($overlay) {
    if (!$overlay || !$overlay.length) {
      return;
    }
    clearOverlayInlineStyles($overlay[0]);
  }

  function getOptionsForElement(element) {
    if (!element || !element.getAttribute) {
      return null;
    }
    var optionsId = element.getAttribute('data-dclb2-options-id');
    if (!optionsId || !document.getElementById) {
      return null;
    }
    var optionsElement = document.getElementById(optionsId);
    if (!optionsElement) {
      return null;
    }
    try {
      return JSON.parse(optionsElement.textContent || optionsElement.innerText || '{}');
    } catch (e) {
      return null;
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
    resetOverlayStyles($overlay);
  }

  function patchLightbox(instance) {
    if (!instance || !instance.constructor || !instance.constructor.prototype) {
      return false;
    }
    var proto = instance.constructor.prototype;
    if (proto.__djangocmsLightboxPatched) {
      return true;
    }
    var originalSizeOverlay = proto.sizeOverlay;
    proto.sizeOverlay = function () {
      if (typeof originalSizeOverlay === 'function') {
        originalSizeOverlay.apply(this, arguments);
      }
      var self = this;
      window.setTimeout(function () {
        resetOverlayStyles(self.$overlay);
      }, 0);
    };

    var originalStart = proto.start;
    proto.start = function (element) {
      var options = getOptionsForElement(element && element[0] ? element[0] : element);
      if (options && typeof this.option === 'function') {
        this.option(options);
      }
      if (typeof originalStart === 'function') {
        return originalStart.apply(this, arguments);
      }
    };
    proto.__djangocmsLightboxPatched = true;
    return true;
  }

  var attempts = 0;
  function attemptPatch() {
    attempts += 1;
    if (window.lightbox && patchLightbox(window.lightbox)) {
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
