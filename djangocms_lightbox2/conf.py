from django.conf import settings


# If True, include Lightbox2 bundle that already includes jQuery.
# If False, include the standalone Lightbox2 JS (requires jQuery to be loaded elsewhere).
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
    # maxWidth / maxHeight undefined by default; omit when None
}

# Allow overriding defaults globally via settings
DEFAULT_OPTIONS.update(getattr(settings, "DJANGOCMS_LIGHTBOX2_OPTIONS", {}))


def build_options_from_gallery(gallery_instance):
    """Build Lightbox2 options dict combining defaults with gallery overrides."""
    opts = dict(DEFAULT_OPTIONS)
    if gallery_instance.album_label:
        opts["albumLabel"] = gallery_instance.album_label
    opts["alwaysShowNavOnTouchDevices"] = gallery_instance.always_show_nav_on_touch_devices
    opts["fadeDuration"] = gallery_instance.fade_duration
    opts["fitImagesInViewport"] = gallery_instance.fit_images_in_viewport
    opts["imageFadeDuration"] = gallery_instance.image_fade_duration
    opts["positionFromTop"] = gallery_instance.position_from_top
    opts["resizeDuration"] = gallery_instance.resize_duration
    opts["showImageNumberLabel"] = gallery_instance.show_image_number_label
    opts["wrapAround"] = gallery_instance.wrap_around
    opts["disableScrolling"] = gallery_instance.disable_scrolling
    if gallery_instance.max_width is not None:
        opts["maxWidth"] = gallery_instance.max_width
    else:
        opts.pop("maxWidth", None)
    if gallery_instance.max_height is not None:
        opts["maxHeight"] = gallery_instance.max_height
    else:
        opts.pop("maxHeight", None)
    return opts
