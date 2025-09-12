from djangocms_lightbox2 import conf


class DummyGallery:
    def __init__(
        self,
        album_label="",
        always_show_nav_on_touch_devices=False,
        fade_duration=600,
        fit_images_in_viewport=True,
        image_fade_duration=600,
        position_from_top=50,
        resize_duration=700,
        show_image_number_label=True,
        wrap_around=False,
        disable_scrolling=False,
        max_width=None,
        max_height=None,
    ):
        self.album_label = album_label
        self.always_show_nav_on_touch_devices = always_show_nav_on_touch_devices
        self.fade_duration = fade_duration
        self.fit_images_in_viewport = fit_images_in_viewport
        self.image_fade_duration = image_fade_duration
        self.position_from_top = position_from_top
        self.resize_duration = resize_duration
        self.show_image_number_label = show_image_number_label
        self.wrap_around = wrap_around
        self.disable_scrolling = disable_scrolling
        self.max_width = max_width
        self.max_height = max_height


def test_build_options_defaults_match():
    g = DummyGallery()
    opts = conf.build_options_from_gallery(g)
    for k, v in conf.DEFAULT_OPTIONS.items():
        if k in ("maxWidth", "maxHeight"):
            continue
        assert opts[k] == v
    assert "maxWidth" not in opts
    assert "maxHeight" not in opts


def test_build_options_overrides_and_max_dimensions():
    g = DummyGallery(
        album_label="Imagen %1 de %2",
        always_show_nav_on_touch_devices=True,
        fade_duration=100,
        fit_images_in_viewport=False,
        image_fade_duration=200,
        position_from_top=10,
        resize_duration=300,
        show_image_number_label=False,
        wrap_around=True,
        disable_scrolling=True,
        max_width=1024,
        max_height=768,
    )
    opts = conf.build_options_from_gallery(g)
    assert opts["albumLabel"] == "Imagen %1 de %2"
    assert opts["alwaysShowNavOnTouchDevices"] is True
    assert opts["fadeDuration"] == 100
    assert opts["fitImagesInViewport"] is False
    assert opts["imageFadeDuration"] == 200
    assert opts["positionFromTop"] == 10
    assert opts["resizeDuration"] == 300
    assert opts["showImageNumberLabel"] is False
    assert opts["wrapAround"] is True
    assert opts["disableScrolling"] is True
    assert opts["maxWidth"] == 1024
    assert opts["maxHeight"] == 768

