const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const manifestPath = path.join(__dirname, 'lightbox2-assets.json');
const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));

for (const asset of manifest.assets) {
  const assetPath = path.join(root, asset.path);
  assert.ok(fs.existsSync(assetPath), `Missing Lightbox2 asset: ${asset.path}`);
  const digest = crypto
    .createHash('sha256')
    .update(fs.readFileSync(assetPath))
    .digest('hex');
  assert.equal(digest, asset.sha256, `Checksum mismatch: ${asset.path}`);
}

console.log(
  `Lightbox2 ${manifest.upstream.tag} asset manifest: ${manifest.assets.length} files verified`,
);
