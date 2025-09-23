# djangocms-lightbox2

Lightweight collection of Django CMS plugins that ship [Lightbox2](https://github.com/lokesh/lightbox2/) with local assets and gallery helpers. The app provides gallery, carousel, and standalone image plugins that are ready to drop into any CMS placeholder.

## Highlights

- **Lightbox2 Gallery** plugin with grid, masonry, and justified layouts.
- **Lightbox2 Carousel** plugin reusing the gallery model with extra carousel controls (aspect ratio, background, object-fit, button toggles).
- **Lightbox2 Image** plugin for standalone usage or as a gallery/carousel child.
- Bundled Lightbox2 2.11.5 assets (CSS/JS/images) and slim overrides that are injected via `sekizai` once per page.
- Easy-thumbnails integration for per-image thumbnail generation and responsive helpers (basic `srcset` for retina displays).
- Configurable Lightbox2 options per gallery (wrap-around, fade durations, max size, scroll locking, etc.), plus global overrides with Django settings.

## Compatibility

- Django 3.2 and 4.2 (CI test matrix).
- django CMS 3.11, 4.1, and 5.0 (CI matrix with version confirmation for CMS 4+).
- Required companion apps: `django-filer`, `django-mptt`, `easy-thumbnails`, `django-sekizai`, and the CMS stack (`cms`, `menus`, `treebeard`).

## Installation

1. Install the dependencies in your project virtualenv:

   ```bash
   pip install django-cms django-filer easy-thumbnails django-mptt django-sekizai djangocms-lightbox2
   ```

2. Register the applications in `INSTALLED_APPS` (order matters for the CMS stack):

   ```python
   INSTALLED_APPS = [
       # Django contrib apps…
       'django.contrib.admin',
       'django.contrib.auth',
       'django.contrib.contenttypes',
       'django.contrib.sessions',
       'django.contrib.messages',
       'django.contrib.staticfiles',

       # django CMS core
       'cms',
       'menus',
       'treebeard',
       'sekizai',

       # filer stack
       'easy_thumbnails',
       'filer',
       'mptt',

       # this app
       'djangocms_lightbox2',
   ]
   ```

   > Tip: on django CMS 4/5 you may also add `djangocms_admin_style` for themed admin forms.

3. Apply migrations and collect the bundled static assets:

   ```bash
   python manage.py migrate
   python manage.py collectstatic
   ```

4. Ensure your base template renders sekizai blocks so the assets land in the correct places:

   ```django
   {% load sekizai_tags %}
   <head>
     {% render_block "css" %}
   </head>
   <body>
     {% cms_toolbar %}
     {% placeholder "content" %}
     {% render_block "js" %}
   </body>
   ```

## Usage

1. **Gallery:** add “Lightbox2 Gallery” to a placeholder, choose a layout, and drop “Lightbox2 Image” children into it. The gallery will render a responsive thumbnail grid/masonry layout or a justified collage using the bundled JS helper.
2. **Carousel:** add “Lightbox2 Carousel”. The plugin reuses the same children and options as the gallery but exposes carousel-specific settings (aspect ratio, background colour, object-fit, fullscreen/download toggles). It still renders a gallery view and reuses Lightbox2 for the overlay.
3. **Standalone image:** drop “Lightbox2 Image” directly into a placeholder. When not parented by a gallery/carousel it still loads the required assets and builds its own Lightbox group.

## Plugin reference

### Gallery (`Lightbox2GalleryPlugin`)

- **Layout** – `grid`, `masonry`, or `justified`.
- **Columns & gutter** – per-breakpoint column counts (`columns_desktop/tablet/mobile`) and `gutter` (px).
- **Captions** – toggle inline captions below thumbnails.
- **Justified options** – `justified_row_height`, `justified_tolerance` control the collage builder.
- **Limit** – `limit_items` caps the number of child images rendered.
- **Lightbox options** – per-gallery overrides for: album label, touch navigation, fade/resize durations, viewport fit, position from top, wrap-around, scroll locking, max width/height.
- **Carousel appearance** (used when a carousel plugin subclasses the gallery): aspect ratio presets, background color (hex), object-fit, fullscreen/download buttons.

### Carousel (`Lightbox2CarouselPlugin`)

- Shares all gallery fields.
- Adds `carousel_aspect_ratio`, `carousel_background_color`, `carousel_object_fit`, `show_fullscreen_button`, `show_download_button`.
- Includes the gallery options and still outputs Lightbox-bound markup so thumbnails open the standard overlay.

### Image (`Lightbox2ImagePlugin`)

- Chooses the source image via `django-filer`.
- Optional `caption` and `alt_text`.
- `thumbnail_width` / `thumbnail_height` – used to build thumbnails for grid/masonry layouts; justified layout derives sizes from the configured row height.
- When the image is standalone (no parent gallery), Lightbox assets are injected automatically and global defaults are used.

## Assets and overrides

- Static assets live under `static/djangocms_lightbox2/`.
- `templates/djangocms_lightbox2/includes/assets.html` is included by gallery/image templates and pushes CSS/JS into sekizai blocks.
- JavaScript helpers:
  - `lightbox2/js/lightbox-plus-jquery.min.js` or `lightbox.min.js` (depending on the `USE_BUNDLED_JQUERY` setting).
  - `lightbox2/js/lightbox-overrides.js` patches Lightbox sizing so it plays nicely with the CMS toolbar.
  - `gallery/justified.js` arranges justified layouts responsively.

## Configuration knobs

- `DJANGOCMS_LIGHTBOX2_USE_BUNDLED_JQUERY` (default `True`)
  - `True`: serve `lightbox-plus-jquery.min.js` so Lightbox works without a site-wide jQuery.
  - `False`: serve `lightbox.min.js` only; the host project must load jQuery.
- `DJANGOCMS_LIGHTBOX2_OPTIONS`
  - Dict merged into the default Lightbox2 options before per-gallery overrides are applied.
- Per-gallery fields (see above) let editors fine-tune Lightbox behaviour without touching settings.

## Development

- Tests live in `tests/` and use `pytest`/`pytest-django` with `tests.settings` (remember to expose it via `DJANGO_SETTINGS_MODULE` and `PYTHONPATH`).
- Formatting and import order are enforced with Black and isort; linting uses flake8. See `AGENTS.md` for the command overview run by CI.

## Static bundle checksum

- CSS: `static/djangocms_lightbox2/lightbox2/css/lightbox.min.css`
- JS (bundled): `static/djangocms_lightbox2/lightbox2/js/lightbox-plus-jquery.min.js`
- JS (standalone): `static/djangocms_lightbox2/lightbox2/js/lightbox.min.js`
- Images: `static/djangocms_lightbox2/lightbox2/images/{close.png, loading.gif, next.png, prev.png}`

Replace these files if you upgrade Lightbox2 upstream, and re-run `collectstatic` so deployments receive the updates.
