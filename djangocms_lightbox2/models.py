from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from cms.models.pluginmodel import CMSPlugin
from filer.fields.image import FilerImageField
from easy_thumbnails.files import get_thumbnailer


class Lightbox2Gallery(CMSPlugin):
    CAROUSEL_ASPECT_RATIO_16_9 = "16-9"
    CAROUSEL_ASPECT_RATIO_4_3 = "4-3"
    CAROUSEL_ASPECT_RATIO_1_1 = "1-1"
    CAROUSEL_ASPECT_RATIO_3_2 = "3-2"
    CAROUSEL_ASPECT_RATIO_21_9 = "21-9"
    CAROUSEL_ASPECT_RATIO_CHOICES = (
        (CAROUSEL_ASPECT_RATIO_16_9, _("16:9 (widescreen)")),
        (CAROUSEL_ASPECT_RATIO_4_3, _("4:3 (standard)")),
        (CAROUSEL_ASPECT_RATIO_1_1, _("1:1 (square)")),
        (CAROUSEL_ASPECT_RATIO_3_2, _("3:2 (classic photo)")),
        (CAROUSEL_ASPECT_RATIO_21_9, _("21:9 (cinematic)")),
    )

    CAROUSEL_OBJECT_FIT_CHOICES = (
        ("cover", _("cover")),
        ("contain", _("contain")),
        ("fill", _("fill")),
        ("none", _("none")),
        ("scale-down", _("scale-down")),
    )

    HEX_COLOR_VALIDATOR = RegexValidator(
        regex=r"^#(?:[0-9a-fA-F]{3}){1,2}$",
        message=_("Enter a valid hex color in the format #RRGGBB."),
    )
    title = models.CharField(max_length=150, blank=True, default="")
    group_name = models.CharField(
        max_length=100,
        blank=True,
        help_text=(
            _("Group name for 'data-lightbox'. If empty, 'gallery-<id>' will be used.")
        ),
    )
    # Lightbox2 options (per gallery)
    album_label = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text=_("Counter label template. Example: 'Image %1 of %2'. Leave blank to use the default value."),
    )
    always_show_nav_on_touch_devices = models.BooleanField(
        default=False,
        help_text=_("Always show navigation on touch devices."),
    )
    fade_duration = models.PositiveIntegerField(
        default=600,
        help_text=_("Overlay fade duration (ms)."),
    )
    fit_images_in_viewport = models.BooleanField(
        default=True,
        help_text=_("Fit images to the viewport."),
    )
    image_fade_duration = models.PositiveIntegerField(
        default=600,
        help_text=_("Image fade duration (ms)."),
    )
    position_from_top = models.PositiveIntegerField(
        default=50,
        help_text=_("Offset from the top (px)."),
    )
    resize_duration = models.PositiveIntegerField(
        default=700,
        help_text=_("Resize duration (ms)."),
    )
    show_image_number_label = models.BooleanField(
        default=True,
        help_text=_("Show image number label."),
    )
    wrap_around = models.BooleanField(
        default=False,
        help_text=_("Allow wrap-around navigation."),
    )
    disable_scrolling = models.BooleanField(
        default=False,
        help_text=_("Disable background scrolling when open."),
    )
    max_width = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_("Maximum image width (px). Leave blank to use the Lightbox2 default."),
    )
    max_height = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_("Maximum image height (px). Leave blank to use the Lightbox2 default."),
    )
    carousel_aspect_ratio = models.CharField(
        max_length=10,
        choices=CAROUSEL_ASPECT_RATIO_CHOICES,
        default=CAROUSEL_ASPECT_RATIO_4_3,
        verbose_name=_("Aspect ratio"),
        help_text=_("Aspect ratio for the main carousel area."),
    )
    carousel_background_color = models.CharField(
        max_length=7,
        default="#F8F8F8",
        validators=[HEX_COLOR_VALIDATOR],
        verbose_name=_("Background color"),
        help_text=_("Background color applied to the main carousel area."),
    )
    carousel_object_fit = models.CharField(
        max_length=10,
        choices=CAROUSEL_OBJECT_FIT_CHOICES,
        default="cover",
        verbose_name=_("Object fit"),
        help_text=_("CSS object-fit value used for images in the carousel."),
    )

    # Layout options
    LAYOUT_GRID = "grid"
    LAYOUT_MASONRY = "masonry"
    LAYOUT_JUSTIFIED = "justified"
    LAYOUT_CHOICES = (
        (LAYOUT_GRID, _("Grid")),
        (LAYOUT_MASONRY, _("Masonry")),
        (LAYOUT_JUSTIFIED, _("Justified")),
    )
    layout = models.CharField(
        max_length=12,
        choices=LAYOUT_CHOICES,
        default=LAYOUT_GRID,
        help_text=_("Gallery layout on the page."),
    )
    columns_desktop = models.PositiveIntegerField(default=4, help_text=_("Columns on desktop (Grid)."))
    columns_tablet = models.PositiveIntegerField(default=2, help_text=_("Columns on tablet (Grid)."))
    columns_mobile = models.PositiveIntegerField(default=1, help_text=_("Columns on mobile (Grid)."))
    gutter = models.PositiveIntegerField(default=8, help_text=_("Spacing between items (px)."))
    show_captions = models.BooleanField(default=False, help_text=_("Show captions under thumbnails."))
    justified_row_height = models.PositiveIntegerField(
        default=220,
        help_text=_("Target row height (Justified, px)."),
    )
    justified_tolerance = models.FloatField(
        default=0.25,
        help_text=_("Row adjustment tolerance (0-1)."),
    )
    limit_items = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_("Limit of images to display (optional)."),
    )

    def get_group(self):
        return self.group_name or f"gallery-{self.pk or 'new'}"

    def get_carousel_aspect_ratio_css(self):
        mapping = {
            self.CAROUSEL_ASPECT_RATIO_16_9: "16 / 9",
            self.CAROUSEL_ASPECT_RATIO_4_3: "4 / 3",
            self.CAROUSEL_ASPECT_RATIO_1_1: "1 / 1",
            self.CAROUSEL_ASPECT_RATIO_3_2: "3 / 2",
            self.CAROUSEL_ASPECT_RATIO_21_9: "21 / 9",
        }
        return mapping.get(self.carousel_aspect_ratio, mapping[self.CAROUSEL_ASPECT_RATIO_4_3])

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

    def get_scaled_by_height_url(self, target_height):
        if not self.image:
            return ""
        options = {
            "size": (9999, int(target_height or self.thumbnail_height)),
            "crop": False,
            "upscale": False,
        }
        try:
            thumbnailer = get_thumbnailer(self.image)
            thumb = thumbnailer.get_thumbnail(options)
            return thumb.url
        except Exception:
            return self.image.url

    def get_scaled_by_width_url(self, target_width):
        if not self.image:
            return ""
        options = {
            "size": (int(target_width or self.thumbnail_width), 9999),
            "crop": False,
            "upscale": False,
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
