from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import gettext_lazy as _

from .models import Lightbox2Gallery, Lightbox2Image
from . import conf
from django.utils.safestring import mark_safe
import json


@plugin_pool.register_plugin
class Lightbox2GalleryPlugin(CMSPluginBase):
    model = Lightbox2Gallery
    name = _("Lightbox2 Gallery")
    render_template = "djangocms_lightbox2/plugins/gallery.html"
    allow_children = True
    child_classes = ["Lightbox2ImagePlugin"]

    fieldsets = (
        (None, {"fields": ("title", "group_name")}),
        (
            _("Opciones de Lightbox2"),
            {
                "classes": ("collapse",),
                "fields": (
                    "album_label",
                    "always_show_nav_on_touch_devices",
                    "fade_duration",
                    "fit_images_in_viewport",
                    "image_fade_duration",
                    "position_from_top",
                    "resize_duration",
                    "show_image_number_label",
                    "wrap_around",
                    "disable_scrolling",
                    "max_width",
                    "max_height",
                ),
            },
        ),
    )

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        context["use_bundled_jquery"] = conf.USE_BUNDLED_JQUERY
        # Build Lightbox2 options from instance + defaults
        options = conf.build_options_from_gallery(instance)
        context["lb_options_json"] = mark_safe(json.dumps(options))
        return context


@plugin_pool.register_plugin
class Lightbox2ImagePlugin(CMSPluginBase):
    model = Lightbox2Image
    name = _("Lightbox2 Image")
    render_template = "djangocms_lightbox2/plugins/image.html"
    require_parent = False
    parent_classes = ["Lightbox2GalleryPlugin"]

    fieldsets = (
        (None, {"fields": ("image", "caption", "alt_text")}),
        (_("Thumbnail"), {"fields": ("thumbnail_width", "thumbnail_height")}),
    )

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        include_assets = True
        try:
            parent_instance = instance.parent and instance.parent.get_plugin_instance()[0]
            from .models import Lightbox2Gallery  # local import to avoid circular

            if isinstance(parent_instance, Lightbox2Gallery):
                include_assets = False
        except Exception:
            include_assets = True
        context["include_assets"] = include_assets
        context["use_bundled_jquery"] = conf.USE_BUNDLED_JQUERY
        # For standalone images, use global default options
        if include_assets:
            context["lb_options_json"] = mark_safe(json.dumps(conf.DEFAULT_OPTIONS))
        return context
