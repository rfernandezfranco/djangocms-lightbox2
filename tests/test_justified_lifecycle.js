const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const source = fs.readFileSync(
  'djangocms_lightbox2/static/djangocms_lightbox2/gallery/justified.js',
  'utf8',
);

const resizeObservers = [];
const intersectionObservers = [];
const cancelledFrames = [];
let nextFrame = 1;

function Observer(list) {
  this.disconnected = false;
  list.push(this);
}

Observer.prototype.observe = function () {};
Observer.prototype.disconnect = function () {
  this.disconnected = true;
};

const imageNodes = [];
const container = {
  isConnected: true,
  matches(selector) {
    return selector === '.dclb2-justified';
  },
  querySelectorAll(selector) {
    return selector === 'img' ? imageNodes : [];
  },
};

const document = {
  readyState: 'loading',
  domContentLoadedListeners: 0,
  addEventListener(type) {
    if (type === 'DOMContentLoaded') this.domContentLoadedListeners += 1;
  },
  querySelectorAll() {
    return [container];
  },
};

const window = {
  addEventListener() {},
  removeEventListener() {},
  clearTimeout() {},
  requestAnimationFrame() {
    return nextFrame++;
  },
  cancelAnimationFrame(id) {
    cancelledFrames.push(id);
  },
  ResizeObserver: function (callback) {
    this.callback = callback;
    Observer.call(this, resizeObservers);
  },
  IntersectionObserver: function (callback) {
    this.callback = callback;
    Observer.call(this, intersectionObservers);
  },
};

window.ResizeObserver.prototype = Observer.prototype;
window.IntersectionObserver.prototype = Observer.prototype;

const context = { window, document };
vm.runInNewContext(source, context);
vm.runInNewContext(source, context);
assert.equal(document.domContentLoadedListeners, 1);

window.dclb2JustifiedInit();
assert.equal(resizeObservers.length, 1);
assert.equal(intersectionObservers.length, 1);

window.dclb2JustifiedDestroy(container);
assert.equal(resizeObservers[0].disconnected, true);
assert.equal(intersectionObservers[0].disconnected, true);
assert.deepEqual(cancelledFrames, [1]);

window.dclb2JustifiedInit();
assert.equal(resizeObservers.length, 2);
assert.equal(intersectionObservers.length, 2);

container.isConnected = false;
window.dclb2JustifiedInit();
assert.equal(resizeObservers[1].disconnected, true);
assert.equal(intersectionObservers[1].disconnected, true);

console.log('justified lifecycle cleanup: OK');
