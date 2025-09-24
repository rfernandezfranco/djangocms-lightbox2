import base64

from cms.api import add_plugin
from cms.models.placeholdermodel import Placeholder
from django.core.files.base import ContentFile
from django.template import Context, engines
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
    template = engines["django"].get_template("djangocms_lightbox2/includes/assets.html")
    ctx = Context({"include_assets": True, "use_bundled_jquery": True, "lb_options_json": ''})
    output = template.render(ctx)
    assert 'lightbox.min.css' in output
    assert 'lightbox-plus-jquery.min.js' in output



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
