const assert = require('node:assert/strict');
const { pathToFileURL } = require('node:url');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

const bundlePath =
  'djangocms_lightbox2/static/djangocms_lightbox2/lightbox2/js/' +
  'lightbox-plus-jquery.min.js';
const bundle = fs.readFileSync(bundlePath, 'utf8').replace(/<\/script/gi, '<\\/script');

function findChrome() {
  const candidates = [
    process.env.CHROME_BIN,
    'google-chrome',
    'chromium',
    'chromium-browser',
  ].filter(Boolean);

  for (const candidate of candidates) {
    const result = spawnSync(candidate, ['--version'], { encoding: 'utf8' });
    if (result.status !== 0) {
      continue;
    }
    const smoke = spawnSync(
      candidate,
      [
        '--headless=new',
        '--no-sandbox',
        '--disable-gpu',
        '--disable-dev-shm-usage',
        '--dump-dom',
        'data:text/html,<html></html>',
      ],
      { encoding: 'utf8', timeout: 10000 },
    );
    if (smoke.status === 0) {
      return candidate;
    }
  }
  return null;
}

const chrome = findChrome();
if (!chrome) {
  if (process.env.CI) {
    throw new Error('Chrome/Chromium is required for the Lightbox2 runtime smoke test');
  }
  console.log('Lightbox2 v2.12.0 runtime smoke: SKIP (no functional headless browser)');
  process.exit(0);
}

const temporaryDirectory = fs.mkdtempSync(
  path.join(os.tmpdir(), 'djangocms-lightbox2-'),
);
const imagePath = path.join(temporaryDirectory, 'fixture.svg');
const pagePath = path.join(temporaryDirectory, 'fixture.html');
const imageUrl = pathToFileURL(imagePath).href;
const brokenImageUrl = pathToFileURL(
  path.join(temporaryDirectory, 'missing.png'),
).href;

fs.writeFileSync(
  imagePath,
  '<svg xmlns="http://www.w3.org/2000/svg" width="8" height="6">' +
    '<rect width="8" height="6" fill="red"/></svg>',
);

const browserTest = `
  (async function () {
    const $ = window.jQuery;
    const events = [];
    const trigger = document.getElementById('trigger-b');

    function check(condition, message) {
      if (!condition) {
        throw new Error(message);
      }
    }

    function waitFor(condition, message) {
      return new Promise((resolve, reject) => {
        const started = Date.now();
        const poll = () => {
          if (condition()) {
            resolve();
            return;
          }
          if (Date.now() - started > 3000) {
            reject(new Error(message));
            return;
          }
          window.setTimeout(poll, 20);
        };
        poll();
      });
    }

    $(document).on('lightbox:open', () => events.push('open'));
    $(document).on('lightbox:change', () => events.push('change'));
    $(document).on('lightbox:close', () => events.push('close'));

    window.lightbox.option({
      fadeDuration: 0,
      imageFadeDuration: 0,
      resizeDuration: 0,
      wrapAround: true,
    });

    trigger.focus();
    window.lightbox.start($(trigger));
    await waitFor(
      () => window.lightbox.currentImageIndex === 1 &&
        document.querySelector('.lb-image').getAttribute('alt') === 'Beta',
      'the initial Lightbox image did not load',
    );

    const lightbox = document.getElementById('lightbox');
    check(lightbox.getAttribute('role') === 'dialog', 'missing dialog role');
    check(lightbox.getAttribute('aria-modal') === 'true', 'missing aria-modal');
    check(
      lightbox.getAttribute('aria-label') === 'Image lightbox',
      'missing dialog label',
    );
    check(
      document.querySelector('.lb-image').getAttribute('aria-describedby') ===
        'lb-caption',
      'missing caption association',
    );
    check(
      document.querySelector('.lb-number').getAttribute('aria-live') === 'polite',
      'missing live counter',
    );
    check(
      document.querySelector('.lb-next').getAttribute('role') === 'button',
      'missing next button role',
    );
    check(events.includes('open') && events.includes('change'), 'missing open/change events');
    check(window.lightbox.album.length === 3, 'selector-safe album grouping failed');

    const firstFocusable = document.querySelector('.lb-prev');
    const lastFocusable = document.querySelector('.lb-close');
    lastFocusable.focus();
    lastFocusable.dispatchEvent(
      new KeyboardEvent('keydown', {
        bubbles: true,
        cancelable: true,
        key: 'Tab',
        keyCode: 9,
      }),
    );
    check(document.activeElement === firstFocusable, 'focus did not wrap forward');

    firstFocusable.focus();
    firstFocusable.dispatchEvent(
      new KeyboardEvent('keydown', {
        bubbles: true,
        cancelable: true,
        key: 'Tab',
        keyCode: 9,
        shiftKey: true,
      }),
    );
    check(document.activeElement === lastFocusable, 'focus did not wrap backward');

    window.lightbox.next();
    await waitFor(
      () => window.lightbox.currentImageIndex === 2 &&
        document.querySelector('.lb-image').getAttribute('alt') === 'Gamma',
      'next() did not load the following image',
    );
    window.lightbox.next();
    await waitFor(
      () => window.lightbox.currentImageIndex === 0 &&
        document.querySelector('.lb-image').getAttribute('alt') === 'Alpha',
      'wrap-around navigation failed',
    );

    lightbox.dispatchEvent(
      new KeyboardEvent('keyup', {
        bubbles: true,
        key: 'Escape',
        keyCode: 27,
      }),
    );
    await waitFor(
      () => events.includes('close') && document.activeElement === trigger,
      'Escape did not close the dialog and restore focus',
    );

    window.lightbox.open([{ link: ${JSON.stringify(brokenImageUrl)}, alt: 'Broken' }]);
    await waitFor(
      () => !document.querySelector('.lb-loader').getClientRects().length &&
        !document.querySelector('.lb-outerContainer').classList.contains('animating'),
      'broken image did not recover from the loading state',
    );

    document.getElementById('result').textContent = 'LIGHTBOX_RUNTIME_SMOKE: PASS';
  })().catch((error) => {
    document.getElementById('result').textContent =
      'LIGHTBOX_RUNTIME_SMOKE: FAIL: ' + error.message;
  });
`;

const page = `<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <style>
      #lightbox { width: 100px; height: 100px; }
      #lightbox [tabindex="0"] { display: block; width: 1px; height: 1px; }
    </style>
  </head>
  <body>
    <a id="trigger-a" data-lightbox="group[0]" data-alt="Alpha" href="${imageUrl}#alpha">A</a>
    <a id="trigger-b" data-lightbox="group[0]" data-alt="Beta" href="${imageUrl}?cache=1#beta">B</a>
    <a id="trigger-c" data-lightbox="group[0]" data-alt="Gamma" href="${imageUrl}#gamma">C</a>
    <pre id="result"></pre>
    <script>${bundle}</script>
    <script>${browserTest}</script>
  </body>
</html>`;

try {
  fs.writeFileSync(pagePath, page);
  const result = spawnSync(
    chrome,
    [
      '--headless=new',
      '--no-sandbox',
      '--disable-gpu',
      '--disable-dev-shm-usage',
      '--allow-file-access-from-files',
      '--dump-dom',
      '--virtual-time-budget=5000',
      pathToFileURL(pagePath).href,
    ],
    { encoding: 'utf8' },
  );

  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /LIGHTBOX_RUNTIME_SMOKE: PASS/);
  console.log('Lightbox2 v2.12.0 runtime smoke: OK');
} finally {
  fs.rmSync(temporaryDirectory, { recursive: true, force: true });
}
