# Changelog

This project follows Keep a Changelog and Semantic Versioning for plugin releases.

## [Unreleased]
- Updated the bundled Lightbox2 assets to v2.12.0, including the fixed-position overlay, accessibility improvements, lifecycle fixes, and matching source maps.
- Removed obsolete overlay sizing overrides that targeted the pre-2.12.0 positioning model.
- Propagated image alternative text to every Lightbox trigger through `data-alt`, with caption fallback support.
- Added a Chrome headless smoke test for the v2.12.0 dialog, accessibility, navigation, events, image loading, and selector-safe album contracts.
- Synchronized carousel slides and thumbnails with Lightbox2 overlay navigation events.
- Guarded Lightbox and justified-gallery assets against duplicate loading when multiple plugin instances use Sekizai.
- Added dynamic carousel initialization and teardown for CMS refreshes and DOM insertions/removals.
- Avoided generating unused responsive thumbnail variants for carousel slides.
- Improved carousel accessibility with tab/tabpanel semantics, keyboard thumbnail navigation, and visible focus indicators.
- Added a pinned Lightbox2 asset manifest with SHA-256 verification in CI.
- Pinned the i18n workflow actions and build tooling for reproducible checks.
- Reconciled the historical model state so migration checks remain clean.
- Removed the obsolete `default_app_config` declaration.
- Clamped legacy gallery, Lightbox, and thumbnail values safely during rendering.
- Added the documented `window.dclb2Lightbox2` wrapper for programmatic Lightbox control.

## [0.2.0] - 2026-08-03 (Lightbox2 2.11.5)
- Use viewport width for justified galleries so column breakpoints follow the page layout.
- Ensure Lightbox assets and plugin templates render when Sekizai context data is unavailable (search indexing, admin previews).
- Harmonised carousel CSS variables by plugging theme tokens into controls/thumbs and dropping unused masonry inline var.
- Added Lightbox2 source maps next to the minified JavaScript bundles for browser debugging.
- Prevent stored XSS in inline Lightbox2 options by serializing them with Django's `json_script` filter.
- Render Lightbox captions as text instead of HTML to prevent stored XSS payloads.
- Apply Lightbox2 options per gallery when its album opens instead of changing a global configuration at page load.
- Release observers, timers and image handlers when justified galleries leave the DOM.
- Validate gallery, Lightbox and thumbnail dimensions before rendering or generating assets.
- Propagate unexpected thumbnail and plugin-parent errors instead of hiding programming failures.
- Pin CI actions and tooling, audit Python dependencies, and keep mirror tokens out of repository URLs.
- Add regressions for captions, source-map references, Lightbox option isolation and justified cleanup.


### Minor Changes
- Relax Lightbox overlay height to 100% to avoid gaps when scrolling stays enabled.
- Localize the “Lightbox2 Carousel” plugin label across all bundled languages.


## [0.1.0] - 2025-09-23 (Lightbox2 2.11.5)
- Initial release of the Django CMS plugin aligned with Lightbox2 v2.11.5 assets.
- Establishes that plugin releases record the bundled Lightbox2 version for traceability.
