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
    module = _("Lightbox2")
    render_template = "djangocms_lightbox2/plugins/gallery.html"
    allow_children = True
    child_classes = ["Lightbox2ImagePlugin"]

    fieldsets = (
        (None, {"fields": ("title", "group_name")}),
        (
            _("Layout"),
            {
                "fields": (
                    "layout",
                    "show_captions",
                    "gutter",
                    ("columns_desktop", "columns_tablet", "columns_mobile"),
                    ("justified_row_height", "justified_tolerance"),
                    "limit_items",
                )
            },
        ),
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
        # Build items for rendering according to layout
        children = getattr(instance, "child_plugin_instances", []) or []
        items = []
        count = 0
        for child in children:
            # child is a CMSPlugin instance; get model instance if needed
            try:
                model_inst = getattr(child, "get_plugin_instance", None)
                if callable(model_inst):
                    model_inst = model_inst()[0]
            except Exception:
                model_inst = child
            # Only process our image model
            if getattr(model_inst, "image", None) is None:
                continue
            if instance.limit_items and count >= instance.limit_items:
                break
            count += 1
            img_href = getattr(model_inst.image, "url", "") if getattr(model_inst, "image", None) else ""
            if instance.layout == instance.LAYOUT_JUSTIFIED:
                thumb = model_inst.get_scaled_by_height_url(instance.justified_row_height)
            elif instance.layout == instance.LAYOUT_MASONRY:
                thumb = model_inst.get_scaled_by_width_url(model_inst.thumbnail_width)
            else:
                thumb = model_inst.get_thumbnail_url()

            # Build a simple srcset for better sharpness on retina/responsive
            try:
                srcset_widths = [480, 960, 1440]
                srcset_parts = []
                for w in srcset_widths:
                    url_w = model_inst.get_scaled_by_width_url(w)
                    if url_w:
                        srcset_parts.append(f"{url_w} {w}w")
                srcset = ", ".join(srcset_parts) if srcset_parts else ""
            except Exception:
                srcset = ""
            items.append(
                {
                    "href": img_href,
                    "thumb": thumb,
                    "srcset": srcset,
                    "caption": getattr(model_inst, "caption", ""),
                    "alt": getattr(model_inst, "alt_text", "") or getattr(model_inst, "caption", ""),
                }
            )
        context.update(
            {
                "gallery_layout": instance.layout,
                "gallery_show_captions": instance.show_captions,
                "gallery_gutter": instance.gutter,
                "gallery_cols": {
                    "desktop": instance.columns_desktop,
                    "tablet": instance.columns_tablet,
                    "mobile": instance.columns_mobile,
                },
                "gallery_row_height": instance.justified_row_height,
                "gallery_tolerance": instance.justified_tolerance,
                "items": items,
                "group_name": instance.get_group(),
                "sizes_attr": (
                    f"(max-width: 640px) calc(100vw/{instance.columns_mobile} - {instance.gutter}px), "
                    f"(max-width: 1024px) calc(100vw/{instance.columns_tablet} - {instance.gutter}px), "
                    f"calc(100vw/{instance.columns_desktop} - {instance.gutter}px)"
                    if instance.layout == instance.LAYOUT_GRID
                    else "100vw"
                ),
            }
        )
        return context


@plugin_pool.register_plugin
class Lightbox2CarouselPlugin(Lightbox2GalleryPlugin):
    """Carousel variant that uses the same items as the gallery."""

    name = _("Lightbox2 Carousel")
    module = _("Lightbox2")
    render_template = "djangocms_lightbox2/plugins/gallery_carousel.html"
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
        """Reuse the gallery rendering to build items list and options."""
        return super().render(context, instance, placeholder)


@plugin_pool.register_plugin
class Lightbox2ImagePlugin(CMSPluginBase):
    model = Lightbox2Image
    name = _("Lightbox2 Image")
    module = _("Lightbox2")
    render_template = "djangocms_lightbox2/plugins/image.html"
    require_parent = False
    parent_classes = ["Lightbox2GalleryPlugin", "Lightbox2CarouselPlugin"]

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
