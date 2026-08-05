const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const source = fs.readFileSync(
  'djangocms_lightbox2/static/djangocms_lightbox2/gallery/justified.js',
  'utf8',
);

const frames = [];
const imageNodes = [];
const items = [];
const rows = [];

function makeImage(width, height) {
  return {
    naturalWidth: width,
    naturalHeight: height,
    complete: false,
    addEventListener() {},
    removeEventListener() {},
  };
}

function makeItem(image) {
  const item = {
    parentNode: null,
    style: {},
    querySelector(selector) {
      return selector === 'img' ? image : null;
    },
  };
  imageNodes.push(image);
  items.push(item);
  return item;
}

const container = {
  isConnected: true,
  clientWidth: 600,
  style: {},
  attributes: {
    'data-row-height': '220',
    'data-row-height-auto': 'true',
    'data-tolerance': '0',
    'data-cols-desktop': '3',
    'data-cols-tablet': '2',
    'data-cols-mobile': '1',
  },
  matches(selector) {
    return selector === '.dclb2-justified';
  },
  getAttribute(name) {
    return this.attributes[name] || null;
  },
  querySelectorAll(selector) {
    if (selector === '.dclb2-item') return items;
    if (selector === 'img') return imageNodes;
    return [];
  },
  removeChild(child) {
    child.parentNode = null;
  },
  appendChild(row) {
    rows.push(row);
    row.parentNode = this;
  },
};

Object.defineProperty(container, 'innerHTML', {
  set() {
    rows.length = 0;
  },
});

// The first three images are portrait-oriented while the remaining images are
// landscape-oriented. This makes the old tolerance-based grouping add a
// fourth item to a configured three-column row.
[
  [500, 1000],
  [500, 1000],
  [500, 1000],
  [1500, 1000],
  [1500, 1000],
].forEach(([width, height]) => {
  const item = makeItem(makeImage(width, height));
  item.parentNode = container;
});

const document = {
  readyState: 'complete',
  documentElement: {clientWidth: 1440},
  querySelectorAll(selector) {
    return selector === '.dclb2-justified' ? [container] : [];
  },
  addEventListener() {},
  createElement() {
    return {
      className: '',
      children: [],
      appendChild(child) {
        this.children.push(child);
        child.parentNode = this;
      },
    };
  },
};

const window = {
  innerWidth: 1440,
  addEventListener() {},
  removeEventListener() {},
  clearTimeout() {},
  requestAnimationFrame(callback) {
    frames.push(callback);
    return frames.length;
  },
  getComputedStyle() {
    return {
      getPropertyValue(name) {
        if (name === '--dclb2-gutter') return '8px';
        return '';
      },
    };
  },
};

const context = {window, document};
vm.runInNewContext(source, context);
assert.equal(frames.length, 1);
frames.shift()();

assert.deepEqual(
  rows.map((row) => row.children.length),
  [3, 2],
  'justified rows must not exceed the configured desktop column count',
);

console.log('justified configured columns: OK');
