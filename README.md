# djangocms-lightbox2

Plugin de Django CMS para integrar Lightbox2 (https://github.com/lokesh/lightbox2/).

Esta implementación se inspira en djangocms-light-gallery y proporciona un plugin de galería con elementos de imagen como hijos, utilizando los atributos `data-lightbox` de Lightbox2.

## Características

- Plugin "Lightbox2 Gallery" que agrupa imágenes hijas.
- Plugin "Lightbox2 Image" para cada elemento de la galería.
- Assets locales (CSS/JS/imagenes) servidos desde `static/` del proyecto.
- Integración con `sekizai` para inyectar CSS/JS sin duplicados.
- Layouts de galería: Grid, Masonry y Justified.
- Filmstrip (cinta de miniaturas) dentro del lightbox, sincronizada con la imagen activa.
- Deep-linking: abrir una imagen específica vía `#lb=<grupo>:<indice>` y actualizar la URL al navegar.
- Rendimiento: miniaturas con `loading="lazy"`, `decoding="async"`, `srcset/sizes` básicos.
- Experiencia móvil: gestos táctiles (swipe izquierda/derecha) en el overlay del lightbox.
- Accesibilidad mejorada: `role=dialog`, `aria-modal`, live region, focus trap y labels.

## Requisitos y compatibilidad

- Django: 3.2 o 4.2 (probado en CI con ambas)
- django CMS: 3.11, 4.x y 5.x (probado en CI con 3.11, 4.1 y 5.0)
- Otras apps: `django-filer`, `easy-thumbnails`, `sekizai`, `django-treebeard`

## Instalación

1. Instala dependencias en tu proyecto Django (ejemplo rápido):
   - `pip install django djangocms django-filer easy-thumbnails`
2. Añade a `INSTALLED_APPS` en `settings.py` de tu proyecto:

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

   Notas de compatibilidad:
   - CMS 4/5: opcionalmente `djangocms-admin-style` para un admin estilizado.
   - Asegúrate de incluir `sekizai` y renderizar los bloques en tu plantilla base.

3. Ejecuta migraciones y collectstatic:
   - `python manage.py migrate`
   - `python manage.py collectstatic`

4. Asegúrate de que tu plantilla base renderiza los bloques de `sekizai`:

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

## Uso

- Añade un plugin "Lightbox2 Gallery" en un placeholder.
- Dentro de la galería, añade uno o más plugins "Lightbox2 Image" y selecciona imágenes de `django-filer`.
- Opcionalmente, usa una sola imagen fuera de una galería; seguirá funcionando, creando su propio grupo de lightbox por instancia.

### Campos del plugin y layouts

- Galería:
  - `layout`: selecciona Grid, Masonry o Justified.
  - `columns_desktop/tablet/mobile` (Grid/Masonry): número de columnas por breakpoint.
  - `gutter`: separación entre elementos (px).
  - `show_captions`: muestra el caption debajo de cada miniatura.
  - `justified_row_height` y `justified_tolerance` (Justified): alto objetivo por fila y tolerancia de ajuste.
  - `limit_items`: limita la cantidad de imágenes renderizadas.
  - Opciones de Lightbox2 por galería: `album_label`, `always_show_nav_on_touch_devices`, `fade_duration`, `fit_images_in_viewport`, `image_fade_duration`, `position_from_top`, `resize_duration`, `show_image_number_label`, `wrap_around`, `disable_scrolling`, `max_width`, `max_height`.

- Imagen:
  - `caption` y `alt_text` para título/alternativo.
  - `thumbnail_width` y `thumbnail_height` para generar miniaturas (según layout se usan tamaños derivados por alto o por ancho cuando aplica).

### Deep-linking y contador

- Puedes enlazar directamente a una imagen con `#lb=<grupo>:<indice>` (1-based), por ejemplo: `#lb=gallery-42:3`.
- Al navegar en el lightbox, la URL se actualiza manteniendo el estado actual.
- El contador en el overlay muestra "i de N" sincronizado con la navegación.

### Filmstrip (cinta de miniaturas)

- Al abrir el lightbox, se muestra una tira de miniaturas debajo del área principal.
- Clic en una miniatura salta a esa imagen. La miniatura activa se resalta y se centra automáticamente.

### Gestos táctiles

- En dispositivos táctiles, desliza a izquierda/derecha para navegar entre imágenes dentro del overlay.

### Rendimiento

- Las miniaturas usan `loading="lazy"` y `decoding="async"`.
- Se genera un `srcset` básico (480/960/1440w) y un atributo `sizes` acorde al layout para mejorar nitidez y tiempos de carga.

## Assets locales

- Los templates incluyen los assets desde `static/djangocms_lightbox2/lightbox2/`.
- Este repositorio incluye los archivos oficiales de Lightbox2 (CSS, JS e imágenes) de la versión 2.11.5 ya integrados en `static/`.

Rutas esperadas:
- CSS: `static/djangocms_lightbox2/lightbox2/css/lightbox.min.css`
- JS:  `static/djangocms_lightbox2/lightbox2/js/lightbox-plus-jquery.min.js`
- Img: `static/djangocms_lightbox2/lightbox2/images/{close.png,loading.gif,next.png,prev.png}`

## Notas

- Si necesitas opciones avanzadas de configuración de Lightbox2, adáptalas en `templates/djangocms_lightbox2/includes/assets.html` o añade un fichero JS de inicialización en `static/djangocms_lightbox2/js/`.
- Si actualizas a una versión nueva de Lightbox2, recuerda reemplazar los archivos en `static/djangocms_lightbox2/lightbox2/` y mantener la correspondencia con la versión de Lightbox2 indicada en este paquete.

Actualización desde versiones previas:
- Ejecuta migraciones para incorporar los campos de layout: `python manage.py migrate` (incluye `0003_layout_fields`).
- Vuelve a ejecutar `collectstatic` para incluir los nuevos assets de galería y filmstrip.

## Configuración

- `DJANGOCMS_LIGHTBOX2_USE_BUNDLED_JQUERY` (por defecto: `True`)
  - `True`: incluye `lightbox-plus-jquery.min.js` (contiene jQuery). Útil si tu proyecto no inyecta jQuery aparte.
  - `False`: incluye `lightbox.min.js` (sin jQuery). Requiere que jQuery esté ya cargado en la página.

- `DJANGOCMS_LIGHTBOX2_OPTIONS` (dict)
  - Permite sobreescribir opciones por defecto de Lightbox2 de forma global.
  - Claves soportadas: `albumLabel`, `alwaysShowNavOnTouchDevices`, `fadeDuration`, `fitImagesInViewport`, `imageFadeDuration`, `positionFromTop`, `resizeDuration`, `showImageNumberLabel`, `wrapAround`, `disableScrolling`, `maxWidth`, `maxHeight`.



## I18N

- Recomendado para releases: compilar `.mo` en CI y publicarlos en la distribución (ya están incluidos por `MANIFEST.in`).
- En desarrollo: puedes usar `django-admin compilemessages -l <lang>` o `msgfmt` de gettext.
