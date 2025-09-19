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

  function applyOverlayCss($overlay) {
    if (!$overlay || typeof $overlay.css !== 'function') {
      return;
    }
    var toolbarHeight = getToolbarHeight();
    var css = {
      width: '100%',
      minHeight: ''
    };
    if (toolbarHeight > 0) {
      css.top = toolbarHeight + 'px';
      css.height = 'calc(100% - ' + toolbarHeight + 'px)';
    } else {
      css.top = '0';
      css.height = '100%';
    }
    $overlay.css(css);
  }

  function refreshOverlayIfVisible() {
    if (!$) {
      return;
    }
    var $overlay = $('#lightboxOverlay');
    if (!$overlay.length || $overlay.css('display') === 'none') {
      return;
    }
    applyOverlayCss($overlay);
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
        applyOverlayCss(self.$overlay);
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
