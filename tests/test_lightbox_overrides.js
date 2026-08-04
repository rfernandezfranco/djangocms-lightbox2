const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const source = fs.readFileSync(
  'djangocms_lightbox2/static/djangocms_lightbox2/lightbox2/js/lightbox-overrides.js',
  'utf8',
);
const cssSource = fs.readFileSync(
  'djangocms_lightbox2/static/djangocms_lightbox2/lightbox2/css/lightbox-overrides.css',
  'utf8',
);

const options = {
  'dclb2-options-first': { textContent: '{"fadeDuration":100}' },
  'dclb2-options-second': { textContent: '{"fadeDuration":900}' },
};

const document = {
  readyState: 'complete',
  getElementById(id) {
    return options[id] || null;
  },
};

function Lightbox() {
  this.options = {};
  this.started = [];
}

Lightbox.prototype.option = function (values) {
  Object.assign(this.options, values);
};

const originalSizeOverlay = function () {};
Lightbox.prototype.sizeOverlay = originalSizeOverlay;

Lightbox.prototype.start = function (element) {
  this.started.push(element);
};

const lightbox = new Lightbox();
const window = { lightbox, jQuery: null, setTimeout };

vm.runInNewContext(source, { window, document });

const firstLink = {
  getAttribute(name) {
    return name === 'data-dclb2-options-id' ? 'dclb2-options-first' : null;
  },
};
const secondLink = {
  getAttribute(name) {
    return name === 'data-dclb2-options-id' ? 'dclb2-options-second' : null;
  },
};

lightbox.start(firstLink);
assert.equal(lightbox.options.fadeDuration, 100);
assert.equal(lightbox.started.length, 1);

lightbox.start(secondLink);
assert.equal(lightbox.options.fadeDuration, 900);
assert.equal(lightbox.started.length, 2);
assert.equal(lightbox.sizeOverlay, originalSizeOverlay);

assert.doesNotMatch(cssSource, /\.lightboxOverlay\s*\{/);
assert.doesNotMatch(cssSource, /body\s*\{/);
assert.match(cssSource, /#lightbox \.lb-nav a\.lb-prev/);

console.log('lightbox-overrides options isolation: OK');
