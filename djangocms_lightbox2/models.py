import logging

from cms.models.pluginmodel import CMSPlugin
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from easy_thumbnails.files import get_thumbnailer
from filer.fields.image import FilerImageField

# Fallback when easy_thumbnails exceptions aren't available at import time
try:  # pragma: no cover
    from easy_thumbnails import exceptions as thumbnail_exceptions
except ImportError:  # pragma: no cover
    thumbnail_exceptions = None


logger = logging.getLogger(__name__)

# fmt: off
GROUP_NAME_HELP = _(
    "Group name for 'data-lightbox'. "
    "If empty, 'gallery-<id>' will be used."
)
ALBUM_LABEL_HELP = _(
    "Counter label template. Example: 'Image %1 of %2'. "
    "Leave blank to use the default value."
)
# fmt: on

_EXPECTED_THUMBNAIL_ERRORS = [OSError]
if thumbnail_exceptions:  # pragma: no branch - executed when dependency is installed
    for _name in ("InvalidImageFormatError", "EasyThumbnailsError"):
        _exc = getattr(thumbnail_exceptions, _name, None)
        if _exc:
            _EXPECTED_THUMBNAIL_ERRORS.append(_exc)
EXPECTED_THUMBNAIL_ERRORS = tuple(_EXPECTED_THUMBNAIL_ERRORS)

MAX_LIGHTBOX_DURATION = 10000
MAX_POSITION_FROM_TOP = 2000
MAX_LIGHTBOX_DIMENSION = 10000
MAX_COLUMNS = 12
MAX_GUTTER = 200
MAX_JUSTIFIED_ROW_HEIGHT = 2000
MAX_LIMIT_ITEMS = 1000
MAX_THUMBNAIL_DIMENSION = 4096


def _handle_thumbnail_exception(instance, exc, operation):
    fallback = getattr(getattr(instance, "image", None), "url", "")
    if isinstance(exc, EXPECTED_THUMBNAIL_ERRORS):
        logger.warning(
            "Lightbox2Image %s: %s failed (%s)",
            instance.pk,
            operation,
            exc,
        )
    else:  # pragma: no cover - unexpected paths are hard to exercise
        logger.exception(
            "Lightbox2Image %s: unexpected error during %s",
            instance.pk,
            operation,
        )
    return fallback


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
        help_text=GROUP_NAME_HELP,
    )
    # Lightbox2 options (per gallery)
    album_label = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text=ALBUM_LABEL_HELP,
    )
    always_show_nav_on_touch_devices = models.BooleanField(
        default=False,
        help_text=_("Always show navigation on touch devices."),
    )
    fade_duration = models.PositiveIntegerField(
        default=600,
        validators=[MinValueValidator(0), MaxValueValidator(MAX_LIGHTBOX_DURATION)],
        help_text=_("Overlay fade duration (ms)."),
    )
    fit_images_in_viewport = models.BooleanField(
        default=True,
        help_text=_("Fit images to the viewport."),
    )
    image_fade_duration = models.PositiveIntegerField(
        default=600,
        validators=[MinValueValidator(0), MaxValueValidator(MAX_LIGHTBOX_DURATION)],
        help_text=_("Image fade duration (ms)."),
    )
    position_from_top = models.PositiveIntegerField(
        default=50,
        validators=[MinValueValidator(0), MaxValueValidator(MAX_POSITION_FROM_TOP)],
        help_text=_("Offset from the top (px)."),
    )
    resize_duration = models.PositiveIntegerField(
        default=700,
        validators=[MinValueValidator(0), MaxValueValidator(MAX_LIGHTBOX_DURATION)],
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
        validators=[MinValueValidator(1), MaxValueValidator(MAX_LIGHTBOX_DIMENSION)],
        help_text=_(
            "Maximum image width (px). Leave blank to use the Lightbox2 default."
        ),
    )
    max_height = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(MAX_LIGHTBOX_DIMENSION)],
        help_text=_(
            "Maximum image height (px). Leave blank to use the Lightbox2 default."
        ),
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
    show_fullscreen_button = models.BooleanField(
        default=True,
        verbose_name=_("Show fullscreen button"),
        help_text=_("Display the fullscreen control in the carousel overlay."),
    )
    show_download_button = models.BooleanField(
        default=True,
        verbose_name=_("Show download button"),
        help_text=_("Display the download control in the carousel overlay."),
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
    columns_desktop = models.PositiveIntegerField(
        default=4,
        validators=[MinValueValidator(1), MaxValueValidator(MAX_COLUMNS)],
        help_text=_("Columns on desktop (Grid, 1-12)."),
    )
    columns_tablet = models.PositiveIntegerField(
        default=2,
        validators=[MinValueValidator(1), MaxValueValidator(MAX_COLUMNS)],
        help_text=_("Columns on tablet (Grid, 1-12)."),
    )
    columns_mobile = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(MAX_COLUMNS)],
        help_text=_("Columns on mobile (Grid, 1-12)."),
    )
    gutter = models.PositiveIntegerField(
        default=8,
        validators=[MinValueValidator(0), MaxValueValidator(MAX_GUTTER)],
        help_text=_("Spacing between items (px, 0-200)."),
    )
    show_captions = models.BooleanField(
        default=False, help_text=_("Show captions under thumbnails.")
    )
    justified_row_height = models.PositiveIntegerField(
        default=220,
        validators=[MinValueValidator(1), MaxValueValidator(MAX_JUSTIFIED_ROW_HEIGHT)],
        help_text=_("Target row height (Justified, px, 1-2000)."),
    )
    justified_tolerance = models.FloatField(
        default=0.25,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text=_("Row adjustment tolerance (0-1)."),
    )
    limit_items = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(MAX_LIMIT_ITEMS)],
        help_text=_("Limit of images to display (0-1000; blank for all)."),
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
        return mapping.get(
            self.carousel_aspect_ratio, mapping[self.CAROUSEL_ASPECT_RATIO_4_3]
        )

    def copy_relations(self, oldinstance):
        self.group_name = oldinstance.group_name

    def __str__(self):
        return self.title or f"Lightbox2 Gallery #{self.pk}"


class Lightbox2Image(CMSPlugin):
    image = FilerImageField(
        on_delete=models.CASCADE, related_name="+", null=True, blank=True
    )
    caption = models.CharField(max_length=255, blank=True, default="")
    alt_text = models.CharField(max_length=255, blank=True, default="")
    thumbnail_width = models.PositiveIntegerField(
        default=400,
        validators=[MinValueValidator(1), MaxValueValidator(MAX_THUMBNAIL_DIMENSION)],
    )
    thumbnail_height = models.PositiveIntegerField(
        default=300,
        validators=[MinValueValidator(1), MaxValueValidator(MAX_THUMBNAIL_DIMENSION)],
    )

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
        except EXPECTED_THUMBNAIL_ERRORS as exc:
            return _handle_thumbnail_exception(self, exc, "thumbnail generation")
        except (
            Exception
        ) as exc:  # pragma: no cover - unexpected paths should be visible
            return _handle_thumbnail_exception(self, exc, "thumbnail generation")

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
        except EXPECTED_THUMBNAIL_ERRORS as exc:
            return _handle_thumbnail_exception(self, exc, "height scaling")
        except Exception as exc:  # pragma: no cover
            return _handle_thumbnail_exception(self, exc, "height scaling")

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
        except EXPECTED_THUMBNAIL_ERRORS as exc:
            return _handle_thumbnail_exception(self, exc, "width scaling")
        except Exception as exc:  # pragma: no cover
            return _handle_thumbnail_exception(self, exc, "width scaling")

    def copy_relations(self, oldinstance):
        self.caption = oldinstance.caption
        self.alt_text = oldinstance.alt_text
        self.thumbnail_width = oldinstance.thumbnail_width
        self.thumbnail_height = oldinstance.thumbnail_height

    def __str__(self):
        if self.image:
            return self.image.label or self.image.original_filename
        return f"Lightbox2 Image #{self.pk}"
