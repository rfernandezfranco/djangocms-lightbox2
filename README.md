# djangocms-lightbox2

Django CMS plugin that integrates [Lightbox2](https://github.com/lokesh/lightbox2/).

The project takes inspiration from *djangocms-light-gallery* and ships a gallery plugin with image children that rely on Lightbox2 `data-lightbox` attributes.

## Features

- "Lightbox2 Gallery" plugin that groups image children.
- "Lightbox2 Image" plugin for each gallery item.
- Local assets (CSS/JS/images) served from the project's `static/` directory.
- Integration with `sekizai` to inject CSS/JS just once per page.
- Gallery layouts: Grid, Masonry, and Justified.
- Deep linking: open a specific image via `#lb=<group>:<index>` and keep the URL in sync while browsing.
- Performance tweaks: thumbnails use `loading="lazy"`, `decoding="async"`, and basic `srcset`/`sizes` attributes.
- Mobile experience: swipe gestures on the overlay.
- Accessibility improvements: `role="dialog"`, `aria-modal`, live region, focus trap, and proper labels.

## Requirements and compatibility

- Django: 3.2 or 4.2 (tested in CI on both).
- django CMS: 3.11, 4.x, and 5.x (tested in CI with 3.11, 4.1, and 5.0).
- Other apps: `django-filer`, `easy-thumbnails`, `sekizai`, `django-treebeard`.

## Installation

1. Install dependencies in your Django project (quick example):
   - `pip install django djangocms django-filer easy-thumbnails`
2. Add the apps to `INSTALLED_APPS` inside your project's `settings.py`:

   ```python
   INSTALLED_APPS = [
       # ...
       'easy_thumbnails',
       'filer',
       'mptt',
       'cms',
       'menus',
       'treebeard',
       'sekizai',
       'djangocms_lightbox2',
   ]
   ```

   Compatibility notes:
   - CMS 4/5: optionally add `djangocms-admin-style` for the admin UI.
   - Include `sekizai` and render the blocks in your base template.

3. Run migrations and collectstatic:
   - `python manage.py migrate`
   - `python manage.py collectstatic`

4. Make sure your base template renders the `sekizai` blocks:

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

- Add a "Lightbox2 Gallery" plugin to a placeholder.
- Inside the gallery, add one or more "Lightbox2 Image" plugins and select images from `django-filer`.
- You can also use a single image outside a gallery; it still works and creates its own lightbox group per instance.

### Plugin fields and layouts

- Gallery:
  - `layout`: choose Grid, Masonry, or Justified.
  - `columns_desktop/tablet/mobile` (Grid/Masonry): number of columns per breakpoint.
  - `gutter`: spacing between items (px).
  - `show_captions`: render the caption underneath each thumbnail.
  - `justified_row_height` and `justified_tolerance` (Justified): target row height and tolerance.
  - `limit_items`: limit how many images are rendered.
  - Lightbox2 options per gallery: `album_label`, `always_show_nav_on_touch_devices`, `fade_duration`, `fit_images_in_viewport`, `image_fade_duration`, `position_from_top`, `resize_duration`, `show_image_number_label`, `wrap_around`, `disable_scrolling`, `max_width`, `max_height`.

- Image:
  - `caption` and `alt_text` for title/alt text.
  - `thumbnail_width` and `thumbnail_height` to generate thumbnails (depending on the layout, derived sizes are used by height or width).

### Deep linking and counter

- Link directly to an image using `#lb=<group>:<index>` (1-based), for example `#lb=gallery-42:3`.
- While browsing the lightbox, the URL updates to reflect the current state.
- The overlay counter displays "i of N" in sync with navigation.

### Touch gestures

- On touch devices, swipe left/right to navigate between images within the overlay.

### Performance

- Thumbnails use `loading="lazy"` and `decoding="async"`.
- A basic `srcset` (480/960/1440w) and matching `sizes` attribute improve sharpness and load times.

## Local assets

- Templates include assets from `static/djangocms_lightbox2/lightbox2/`.
- The repository bundles the official Lightbox2 files (CSS, JS, images) for version 2.11.5 under `static/`.

Expected paths:
- CSS: `static/djangocms_lightbox2/lightbox2/css/lightbox.min.css`
- JS: `static/djangocms_lightbox2/lightbox2/js/lightbox-plus-jquery.min.js`
- Img: `static/djangocms_lightbox2/lightbox2/images/{close.png,loading.gif,next.png,prev.png}`

## Notes

- For advanced Lightbox2 configuration, adapt `templates/djangocms_lightbox2/includes/assets.html` or add an initialization file under `static/djangocms_lightbox2/js/`.
- When upgrading Lightbox2, replace the files in `static/djangocms_lightbox2/lightbox2/` and keep the version reference in sync.

Upgrade from previous releases:
- Run migrations to include the layout fields: `python manage.py migrate` (this covers `0003_layout_fields`).
- Run `collectstatic` again to include the updated gallery assets.

## Configuration

- `DJANGOCMS_LIGHTBOX2_USE_BUNDLED_JQUERY` (default: `True`)
  - `True`: include `lightbox-plus-jquery.min.js` (bundles jQuery). Useful when your project does not load jQuery separately.
  - `False`: include `lightbox.min.js` (without jQuery). Requires jQuery to be loaded elsewhere.

- `DJANGOCMS_LIGHTBOX2_OPTIONS` (dict)
  - Override Lightbox2 defaults globally.
  - Supported keys: `albumLabel`, `alwaysShowNavOnTouchDevices`, `fadeDuration`, `fitImagesInViewport`, `imageFadeDuration`, `positionFromTop`, `resizeDuration`, `showImageNumberLabel`, `wrapAround`, `disableScrolling`, `maxWidth`, `maxHeight`.

## I18N

- For releases, compile `.mo` files in CI and include them in the distribution (already handled via `MANIFEST.in`).
- During development, you can run `django-admin compilemessages -l <lang>` or use `msgfmt` from gettext.

