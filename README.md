# djangocms-lightbox2

Plugin de Django CMS para integrar Lightbox2 (https://github.com/lokesh/lightbox2/).

Esta implementación se inspira en djangocms-light-gallery y proporciona un plugin de galería con elementos de imagen como hijos, utilizando los atributos `data-lightbox` de Lightbox2.

## Características

- Plugin "Lightbox2 Gallery" que agrupa imágenes hijas.
- Plugin "Lightbox2 Image" para cada elemento de la galería.
- Assets locales (CSS/JS/imagenes) servidos desde `static/` del proyecto.
- Integración con `sekizai` para inyectar CSS/JS sin duplicados.

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
