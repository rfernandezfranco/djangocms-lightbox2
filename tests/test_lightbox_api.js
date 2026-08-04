const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const source = fs.readFileSync(
  'djangocms_lightbox2/static/djangocms_lightbox2/lightbox2/js/lightbox-api.js',
  'utf8',
);
const calls = [];
const lightbox = {
  open(...args) { calls.push(['open', args]); },
  close() { calls.push(['close']); },
  next() { calls.push(['next']); },
  prev() { calls.push(['prev']); },
  option(...args) { calls.push(['option', args]); },
  destroy() { calls.push(['destroy']); },
};
const window = { lightbox };

vm.runInNewContext(source, { window });

assert.equal(window.dclb2Lightbox2.isAvailable(), true);
assert.equal(window.dclb2Lightbox2.open([{ link: '/image.jpg' }], 1), true);
assert.equal(window.dclb2Lightbox2.close(), true);
assert.equal(window.dclb2Lightbox2.next(), true);
assert.equal(window.dclb2Lightbox2.prev(), true);
assert.equal(window.dclb2Lightbox2.option({ wrapAround: true }), true);
assert.equal(window.dclb2Lightbox2.destroy(), true);
assert.deepEqual(calls, [
  ['open', [[{ link: '/image.jpg' }], 1]],
  ['close'],
  ['next'],
  ['prev'],
  ['option', [{ wrapAround: true }]],
  ['destroy'],
]);

const unavailableWindow = {};
vm.runInNewContext(source, { window: unavailableWindow });
assert.equal(unavailableWindow.dclb2Lightbox2.isAvailable(), false);
assert.equal(unavailableWindow.dclb2Lightbox2.next(), false);

console.log('Lightbox2 public API wrapper: OK');
