from django.db import models
from django.utils.translation import gettext_lazy as _
from cms.models.pluginmodel import CMSPlugin
from filer.fields.image import FilerImageField
from easy_thumbnails.files import get_thumbnailer


class Lightbox2Gallery(CMSPlugin):
    title = models.CharField(max_length=150, blank=True, default="")
    group_name = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Nombre de grupo para 'data-lightbox'. Si está vacío, se usará 'gallery-<id>'."),
    )
    # Lightbox2 Options (por galería)
    album_label = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text=_("Plantilla de etiqueta del contador. Ej: 'Imagen %1 de %2'. Dejar vacío para usar el valor por defecto."),
    )
    always_show_nav_on_touch_devices = models.BooleanField(
        default=False,
        help_text=_("Mostrar navegación siempre en dispositivos táctiles."),
    )
    fade_duration = models.PositiveIntegerField(
        default=600,
        help_text=_("Duración del fundido de la superposición (ms)."),
    )
    fit_images_in_viewport = models.BooleanField(
        default=True,
        help_text=_("Ajustar imágenes al viewport."),
    )
    image_fade_duration = models.PositiveIntegerField(
        default=600,
        help_text=_("Duración del fundido de la imagen (ms)."),
    )
    position_from_top = models.PositiveIntegerField(
        default=50,
        help_text=_("Separación desde la parte superior (px)."),
    )
    resize_duration = models.PositiveIntegerField(
        default=700,
        help_text=_("Duración del cambio de tamaño (ms)."),
    )
    show_image_number_label = models.BooleanField(
        default=True,
        help_text=_("Mostrar etiqueta de número de imagen."),
    )
    wrap_around = models.BooleanField(
        default=False,
        help_text=_("Permitir navegación circular (wrap around)."),
    )
    disable_scrolling = models.BooleanField(
        default=False,
        help_text=_("Deshabilitar scroll del fondo cuando está abierto."),
    )
    max_width = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_("Ancho máximo de la imagen (px). Vacío usa el defecto de Lightbox2."),
    )
    max_height = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_("Altura máxima de la imagen (px). Vacío usa el defecto de Lightbox2."),
    )

    def get_group(self):
        return self.group_name or f"gallery-{self.pk or 'new'}"

    def copy_relations(self, oldinstance):
        self.group_name = oldinstance.group_name

    def __str__(self):
        return self.title or f"Lightbox2 Gallery #{self.pk}"


class Lightbox2Image(CMSPlugin):
    image = FilerImageField(on_delete=models.CASCADE, related_name="+", null=True, blank=True)
    caption = models.CharField(max_length=255, blank=True, default="")
    alt_text = models.CharField(max_length=255, blank=True, default="")
    thumbnail_width = models.PositiveIntegerField(default=400)
    thumbnail_height = models.PositiveIntegerField(default=300)

    def get_group(self):
        parent = self.parent and self.parent.get_plugin_instance()[0]
        if isinstance(parent, Lightbox2Gallery):
            return parent.get_group()
        return f"plugin-{self.pk or 'new'}"

    def get_thumbnail_url(self):
        if not self.image:
            return ""
        options = {
            "size": (self.thumbnail_width, self.thumbnail_height),
            "crop": True,
        }
        try:
            thumbnailer = get_thumbnailer(self.image)
            thumb = thumbnailer.get_thumbnail(options)
            return thumb.url
        except Exception:
            return self.image.url

    def copy_relations(self, oldinstance):
        self.caption = oldinstance.caption
        self.alt_text = oldinstance.alt_text
        self.thumbnail_width = oldinstance.thumbnail_width
        self.thumbnail_height = oldinstance.thumbnail_height

    def __str__(self):
        if self.image:
            return self.image.label or self.image.original_filename
        return f"Lightbox2 Image #{self.pk}"
