import base64

from django.core.files.base import ContentFile
from django.template import engines
from sekizai.context import SekizaiContext
from cms.api import add_plugin
from cms.models.placeholdermodel import Placeholder
from filer.models.imagemodels import Image as FilerImage
from djangocms_lightbox2.cms_plugins import (
    Lightbox2GalleryPlugin,
    Lightbox2ImagePlugin,
    Lightbox2CarouselPlugin,
)


def render_template(path, context):
    template = engines["django"].get_template(path)
    # context is already a dict/SekizaiContext
    return template.render(context)


def make_context():
    return SekizaiContext({})


def make_filer_image(filename="example.png"):
    data = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAuMB9oNw3iYAAAAASUVORK5CYII="
    )
    file_obj = ContentFile(data, name=filename)
    return FilerImage.objects.create(original_filename=filename, file=file_obj)


def test_gallery_render_includes_assets_without_children(db):
    ph = Placeholder.objects.create(slot="content")
    gallery_plugin = add_plugin(ph, Lightbox2GalleryPlugin, language="en", title="Test")
    instance, plugin_cls = gallery_plugin.get_plugin_instance()
    plugin = plugin_cls(model=plugin_cls.model, admin_site=None)
    ctx = make_context()
    ctx = plugin.render(ctx, instance, ph)
    html = render_template(plugin.render_template, ctx)
    assert "lightbox2/css/lightbox.min.css" in html
    # By default we use bundled jquery
    assert "lightbox2/js/lightbox-plus-jquery.min.js" in html


def test_image_include_assets_only_when_standalone(db):
    ph = Placeholder.objects.create(slot="content")
    # Standalone image
    img_pl = add_plugin(ph, Lightbox2ImagePlugin, language="en")
    instance, plugin_cls = img_pl.get_plugin_instance()
    plugin = plugin_cls(model=plugin_cls.model, admin_site=None)
    ctx = make_context()
    ctx = plugin.render(ctx, instance, ph)
    assert ctx.get("include_assets") is True

    # Child image: assets should be False
    gal_pl = add_plugin(ph, Lightbox2GalleryPlugin, language="en", title="G")
    child_img = add_plugin(ph, Lightbox2ImagePlugin, language="en", target=gal_pl)
    child_instance, child_cls = child_img.get_plugin_instance()
    child_plugin = child_cls(model=child_cls.model, admin_site=None)
    ctx2 = make_context()
    ctx2 = child_plugin.render(ctx2, child_instance, ph)
    assert ctx2.get("include_assets") is False


def test_carousel_controls_toggle(db):
    ph = Placeholder.objects.create(slot="content")
    carousel_pl = add_plugin(
        ph,
        Lightbox2CarouselPlugin,
        language="en",
        title="Carousel",
        show_fullscreen_button=True,
        show_download_button=False,
    )
    image = make_filer_image()
    add_plugin(
        ph,
        Lightbox2ImagePlugin,
        language="en",
        target=carousel_pl,
        image=image,
        alt_text="Example",
    )
    instance, plugin_cls = carousel_pl.get_plugin_instance()
    plugin = plugin_cls(model=plugin_cls.model, admin_site=None)
    ctx = make_context()
    ctx = plugin.render(ctx, instance, ph)
    html = render_template(plugin.render_template, ctx)
    assert "dclb2-fullscreen" in html
    assert "dclb2-download" not in html


def test_carousel_controls_can_be_hidden(db):
    ph = Placeholder.objects.create(slot="content")
    carousel_pl = add_plugin(
        ph,
        Lightbox2CarouselPlugin,
        language="en",
        title="Carousel",
        show_fullscreen_button=False,
        show_download_button=False,
    )
    image = make_filer_image("hidden.png")
    add_plugin(
        ph,
        Lightbox2ImagePlugin,
        language="en",
        target=carousel_pl,
        image=image,
        alt_text="Example",
    )
    instance, plugin_cls = carousel_pl.get_plugin_instance()
    plugin = plugin_cls(model=plugin_cls.model, admin_site=None)
    ctx = make_context()
    ctx = plugin.render(ctx, instance, ph)
    html = render_template(plugin.render_template, ctx)
    assert "dclb2-controls" not in html
