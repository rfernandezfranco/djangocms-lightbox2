from django.conf import settings

# If True, include Lightbox2 bundle that already includes jQuery.
# If False, include the standalone Lightbox2 JS (jQuery must be loaded separately).
USE_BUNDLED_JQUERY = getattr(settings, "DJANGOCMS_LIGHTBOX2_USE_BUNDLED_JQUERY", True)

# Default Lightbox2 options (match upstream defaults)
DEFAULT_OPTIONS = {
    "albumLabel": "Image %1 of %2",
    "alwaysShowNavOnTouchDevices": False,
    "fadeDuration": 600,
    "fitImagesInViewport": True,
    "imageFadeDuration": 600,
    "positionFromTop": 50,
    "resizeDuration": 700,
    "showImageNumberLabel": True,
    "wrapAround": False,
    "disableScrolling": False,
    # Captions are rendered as text by Lightbox2, never as HTML.
    "sanitizeTitle": True,
    # maxWidth / maxHeight undefined by default; omit when None
}

# Allow overriding defaults globally via settings
DEFAULT_OPTIONS.update(getattr(settings, "DJANGOCMS_LIGHTBOX2_OPTIONS", {}))


def bounded_int(value, default, minimum, maximum):
    """Return an integer constrained to the supported inclusive range."""
    try:
        value = int(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(maximum, value))


def bounded_float(value, default, minimum, maximum):
    """Return a float constrained to the supported inclusive range."""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(maximum, value))


def build_options_from_gallery(gallery_instance):
    """Build Lightbox2 options dict combining defaults with gallery overrides."""
    opts = dict(DEFAULT_OPTIONS)
    if gallery_instance.album_label:
        opts["albumLabel"] = gallery_instance.album_label
    opts["alwaysShowNavOnTouchDevices"] = (
        gallery_instance.always_show_nav_on_touch_devices
    )
    opts["fadeDuration"] = bounded_int(gallery_instance.fade_duration, 600, 0, 10000)
    opts["fitImagesInViewport"] = gallery_instance.fit_images_in_viewport
    opts["imageFadeDuration"] = bounded_int(
        gallery_instance.image_fade_duration, 600, 0, 10000
    )
    opts["positionFromTop"] = bounded_int(
        gallery_instance.position_from_top, 50, 0, 2000
    )
    opts["resizeDuration"] = bounded_int(
        gallery_instance.resize_duration, 700, 0, 10000
    )
    opts["showImageNumberLabel"] = gallery_instance.show_image_number_label
    opts["wrapAround"] = gallery_instance.wrap_around
    opts["disableScrolling"] = gallery_instance.disable_scrolling
    if gallery_instance.max_width is not None:
        opts["maxWidth"] = bounded_int(gallery_instance.max_width, 10000, 1, 10000)
    else:
        opts.pop("maxWidth", None)
    if gallery_instance.max_height is not None:
        opts["maxHeight"] = bounded_int(gallery_instance.max_height, 10000, 1, 10000)
    else:
        opts.pop("maxHeight", None)
    return opts
