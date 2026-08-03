import base64
from types import SimpleNamespace

from cms.api import add_plugin
from cms.models.placeholdermodel import Placeholder
from django.core.files.base import ContentFile
from django.template import engines
from django.test import RequestFactory
from filer.models.imagemodels import Image as FilerImage
from sekizai.context import SekizaiContext

from djangocms_lightbox2.cms_plugins import (
    Lightbox2CarouselPlugin,
    Lightbox2GalleryPlugin,
    Lightbox2ImagePlugin,
)


def render_template(path, context):
    django_engine = engines["django"]
    wrapper = django_engine.from_string(
        """{% load sekizai_tags %}{% include '"""
        + path
        + """' %}{% render_block 'css' %}{% render_block 'js' %}"""
    )
    if hasattr(context, "get"):
        request = context.get("request")
        if request is not None:
            context["request"] = request
    return wrapper.template.render(context)


def make_context():
    request = RequestFactory().get("/")
    return SekizaiContext({"request": request})


def make_filer_image(filename="example.png"):
    data = base64.b64decode(
        (
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAuMB9o"
            "Nw3iYAAAAASUVORK5CYII="
        )
    )
    file_obj = ContentFile(data, name=filename)
    return FilerImage.objects.create(original_filename=filename, file=file_obj)


def test_assets_template_fallback_without_sekizai():
    template = engines["django"].get_template(
        "djangocms_lightbox2/includes/assets.html"
    )
    ctx = {"include_assets": True, "use_bundled_jquery": True, "lb_options": ""}
    output = template.render(ctx)
    assert "lightbox.min.css" in output
    assert "lightbox-plus-jquery.min.js" in output


def test_gallery_template_handles_missing_sekizai():
    template = engines["django"].get_template(
        "djangocms_lightbox2/plugins/gallery.html"
    )
    ctx = {
        "instance": SimpleNamespace(pk=1),
        "gallery_layout": "grid",
        "gallery_gutter": 8,
        "gallery_cols": {"desktop": 4, "tablet": 2, "mobile": 1},
        "gallery_row_height": 220,
        "gallery_row_height_auto": True,
        "gallery_tolerance": 0.25,
        "items": [],
        "group_name": "group",
        "sizes_attr": "100vw",
        "gallery_show_captions": False,
        "include_assets": True,
        "use_bundled_jquery": True,
        "lb_options": "",
    }
    output = template.render(ctx)
    assert "gallery.css" in output
    assert "justified.js" in output


def test_carousel_template_handles_missing_sekizai():
    template = engines["django"].get_template(
        "djangocms_lightbox2/plugins/gallery_carousel.html"
    )
    ctx = {
        "instance": SimpleNamespace(
            pk=1, show_fullscreen_button=False, show_download_button=False
        ),
        "items": [],
        "group_name": "group",
        "carousel_background_color": "#fff",
        "carousel_aspect_ratio_css": "4 / 3",
        "carousel_object_fit": "cover",
        "include_assets": True,
        "use_bundled_jquery": True,
        "lb_options": "",
    }
    output = template.render(ctx)
    assert "carousel.css" in output
    assert "carousel.js" in output


def test_gallery_render_includes_assets_without_children(db):
    ph = Placeholder.objects.create(slot="content")
    gallery_plugin = add_plugin(
        ph,
        Lightbox2GalleryPlugin.__name__,
        language="en",
        title="Test",
    )
    instance, plugin = gallery_plugin.get_plugin_instance()
    assert plugin is not None
    ctx = make_context()
    ctx = plugin.render(ctx, instance, ph)
    html = render_template(plugin.render_template, ctx)
    assert "lightbox2/css/lightbox.min.css" in html
    # By default we use bundled jquery
    assert "lightbox2/js/lightbox-plus-jquery.min.js" in html


def test_gallery_options_escape_script_content(db):
    ph = Placeholder.objects.create(slot="content")
    payload = "</script><script>window.pwned = true</script>"
    gallery_plugin = add_plugin(
        ph,
        Lightbox2GalleryPlugin.__name__,
        language="en",
        title="Test",
        album_label=payload,
    )
    instance, plugin = gallery_plugin.get_plugin_instance()
    ctx = plugin.render(make_context(), instance, ph)

    html = render_template(plugin.render_template, ctx)

    assert payload not in html
    assert r"\u003C/script\u003E" in html
    assert "window.pwned = true" in html


def test_galleries_render_distinct_lightbox_options(db):
    ph = Placeholder.objects.create(slot="content")
    first = add_plugin(
        ph,
        Lightbox2GalleryPlugin.__name__,
        language="en",
        title="First",
        fade_duration=100,
    )
    second = add_plugin(
        ph,
        Lightbox2GalleryPlugin.__name__,
        language="en",
        title="Second",
        fade_duration=900,
    )
    add_plugin(
        ph,
        Lightbox2ImagePlugin.__name__,
        language="en",
        target=first,
        image=make_filer_image("first.png"),
    )
    add_plugin(
        ph,
        Lightbox2ImagePlugin.__name__,
        language="en",
        target=second,
        image=make_filer_image("second.png"),
    )
    first_instance, first_plugin = first.get_plugin_instance()
    second_instance, second_plugin = second.get_plugin_instance()

    first_html = render_template(
        first_plugin.render_template,
        first_plugin.render(make_context(), first_instance, ph),
    )
    second_html = render_template(
        second_plugin.render_template,
        second_plugin.render(make_context(), second_instance, ph),
    )

    first_id = f"dclb2-options-{first_instance.pk}"
    second_id = f"dclb2-options-{second_instance.pk}"
    assert first_id != second_id
    assert f'id="{first_id}"' in first_html
    assert '"fadeDuration": 100' in first_html
    assert f'data-dclb2-options-id="{first_id}"' in first_html
    assert f'id="{second_id}"' in second_html
    assert '"fadeDuration": 900' in second_html
    assert f'data-dclb2-options-id="{second_id}"' in second_html


def test_image_include_assets_only_when_standalone(db):
    ph = Placeholder.objects.create(slot="content")
    # Standalone image
    img_pl = add_plugin(ph, Lightbox2ImagePlugin.__name__, language="en")
    instance, plugin = img_pl.get_plugin_instance()
    assert plugin is not None
    ctx = make_context()
    ctx = plugin.render(ctx, instance, ph)
    assert ctx.get("include_assets") is True

    # Child image: assets should be False
    gal_pl = add_plugin(
        ph,
        Lightbox2GalleryPlugin.__name__,
        language="en",
        title="G",
    )
    child_img = add_plugin(
        ph,
        Lightbox2ImagePlugin.__name__,
        language="en",
        target=gal_pl,
    )
    child_instance, child_plugin = child_img.get_plugin_instance()
    assert child_plugin is not None
    ctx2 = make_context()
    ctx2 = child_plugin.render(ctx2, child_instance, ph)
    assert ctx2.get("include_assets") is False


def test_carousel_controls_toggle(db):
    ph = Placeholder.objects.create(slot="content")
    carousel_pl = add_plugin(
        ph,
        Lightbox2CarouselPlugin.__name__,
        language="en",
        title="Carousel",
        show_fullscreen_button=True,
        show_download_button=False,
    )
    image = make_filer_image()
    add_plugin(
        ph,
        Lightbox2ImagePlugin.__name__,
        language="en",
        target=carousel_pl,
        image=image,
        alt_text="Example",
    )
    instance, plugin = carousel_pl.get_plugin_instance()
    assert plugin is not None
    ctx = make_context()
    ctx = plugin.render(ctx, instance, ph)
    html = render_template(plugin.render_template, ctx)
    assert "dclb2-fullscreen" in html
    assert "dclb2-download" not in html


def test_carousel_controls_can_be_hidden(db):
    ph = Placeholder.objects.create(slot="content")
    carousel_pl = add_plugin(
        ph,
        Lightbox2CarouselPlugin.__name__,
        language="en",
        title="Carousel",
        show_fullscreen_button=False,
        show_download_button=False,
    )
    image = make_filer_image("hidden.png")
    add_plugin(
        ph,
        Lightbox2ImagePlugin.__name__,
        language="en",
        target=carousel_pl,
        image=image,
        alt_text="Example",
    )
    instance, plugin = carousel_pl.get_plugin_instance()
    assert plugin is not None
    ctx = make_context()
    ctx = plugin.render(ctx, instance, ph)
    html = render_template(plugin.render_template, ctx)
    assert "dclb2-controls" not in html
