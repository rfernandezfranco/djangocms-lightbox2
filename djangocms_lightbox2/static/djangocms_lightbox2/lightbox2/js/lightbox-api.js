(function(window) {
  'use strict';

  var api = window.dclb2Lightbox2 = window.dclb2Lightbox2 || {};

  function getLightbox() {
    return window.lightbox || null;
  }

  function call(method, args) {
    var lightbox = getLightbox();
    if (!lightbox || typeof lightbox[method] !== 'function') return false;
    lightbox[method].apply(lightbox, args || []);
    return true;
  }

  api.isAvailable = function() {
    return Boolean(getLightbox());
  };
  api.open = function(images, startIndex) {
    return call('open', [images, startIndex]);
  };
  api.close = function() {
    return call('close');
  };
  api.next = function() {
    return call('next');
  };
  api.prev = function() {
    return call('prev');
  };
  api.option = function(options) {
    return call('option', [options]);
  };
  api.destroy = function() {
    return call('destroy');
  };
})(window);
