/* Lightbox integration tweaks for Django CMS. */
(function (window, document) {
  'use strict';

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

  function patchLightbox(instance) {
    if (!instance || !instance.constructor || !instance.constructor.prototype) {
      return false;
    }
    var proto = instance.constructor.prototype;
    if (proto.__djangocmsLightboxPatched) {
      return true;
    }
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
