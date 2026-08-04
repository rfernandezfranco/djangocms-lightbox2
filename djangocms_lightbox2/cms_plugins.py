from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _

from . import conf
from .models import Lightbox2Gallery, Lightbox2Image


def _grid_size_entry(columns, gutter, breakpoint=None):
    """Build a responsive sizes entry for the gallery."""
    base = f"calc(100vw/{columns} - {gutter}px)"
    if breakpoint is None:
        return base
    return f"(max-width: {breakpoint}px) {base}"


class Lightbox2CarouselForm(forms.ModelForm):
    class Meta:
        model = Lightbox2Gallery
        fields = "__all__"
        widgets = {
            "carousel_background_color": forms.TextInput(attrs={"type": "color"}),
        }


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
            _("Gallery layout and items"),
            {
                "classes": ("collapse",),
                "fields": (
                    "layout",
                    "show_captions",
                    "gutter",
                    ("columns_desktop", "columns_tablet", "columns_mobile"),
                    ("justified_row_height", "justified_tolerance"),
                    "limit_items",
                ),
            },
        ),
        (
            _("Lightbox2 options"),
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
        context["lb_options"] = options
        context["lb_options_id"] = f"dclb2-options-{instance.pk}"
        # Build items for rendering according to layout
        images_qs = (
            Lightbox2Image.objects.filter(parent=instance)
            .select_related("image")
            .order_by("position", "pk")
        )
        layout = instance.layout
        if layout not in (
            instance.LAYOUT_GRID,
            instance.LAYOUT_MASONRY,
            instance.LAYOUT_JUSTIFIED,
        ):
            layout = instance.LAYOUT_GRID
        limit_items = conf.bounded_int(instance.limit_items, None, 0, 1000)
        if limit_items is not None:
            images_qs = images_qs[:limit_items]

        columns = {
            "desktop": conf.bounded_int(instance.columns_desktop, 4, 1, 12),
            "tablet": conf.bounded_int(instance.columns_tablet, 2, 1, 12),
            "mobile": conf.bounded_int(instance.columns_mobile, 1, 1, 12),
        }
        gutter = conf.bounded_int(instance.gutter, 8, 0, 200)
        row_height = conf.bounded_int(instance.justified_row_height, 220, 1, 2000)
        tolerance = conf.bounded_float(instance.justified_tolerance, 0.25, 0, 1)

        items = []
        for image_plugin in images_qs:
            if not getattr(image_plugin, "image", None):
                continue

            img_href = getattr(image_plugin.image, "url", "")
            if layout == instance.LAYOUT_JUSTIFIED:
                thumb = image_plugin.get_scaled_by_height_url(row_height)
            elif layout == instance.LAYOUT_MASONRY:
                thumb = image_plugin.get_scaled_by_width_url(
                    image_plugin.thumbnail_width
                )
            else:
                thumb = image_plugin.get_thumbnail_url()

            # The carousel renders the full image in its main slide and only
            # uses the thumbnail as a background for the thumb strip. It does
            # not render srcset, so avoid generating three unused variants.
            srcset = ""
            if not isinstance(self, Lightbox2CarouselPlugin):
                srcset_parts = []
                for width in (480, 960, 1440):
                    url_w = image_plugin.get_scaled_by_width_url(width)
                    if url_w:
                        srcset_parts.append(f"{url_w} {width}w")
                srcset = ", ".join(srcset_parts) if srcset_parts else ""

            items.append(
                {
                    "href": img_href,
                    "thumb": thumb,
                    "srcset": srcset,
                    "caption": getattr(image_plugin, "caption", ""),
                    "alt": getattr(image_plugin, "alt_text", "")
                    or getattr(image_plugin, "caption", ""),
                }
            )
        default_row_height = Lightbox2Gallery._meta.get_field(
            "justified_row_height"
        ).default

        context.update(
            {
                "gallery_layout": layout,
                "gallery_show_captions": instance.show_captions,
                "gallery_gutter": gutter,
                "gallery_cols": columns,
                "gallery_row_height": row_height,
                "gallery_row_height_auto": row_height == default_row_height,
                "gallery_tolerance": tolerance,
                "items": items,
                "group_name": instance.get_group(),
                "sizes_attr": (
                    ", ".join(
                        [
                            _grid_size_entry(
                                columns["mobile"],
                                gutter,
                                breakpoint=640,
                            ),
                            _grid_size_entry(
                                columns["tablet"],
                                gutter,
                                breakpoint=1024,
                            ),
                            _grid_size_entry(columns["desktop"], gutter),
                        ]
                    )
                    if layout == instance.LAYOUT_GRID
                    else "100vw"
                ),
            }
        )
        # Ensure Lightbox assets are always included for gallery render
        context["include_assets"] = True
        return context


@plugin_pool.register_plugin
class Lightbox2CarouselPlugin(Lightbox2GalleryPlugin):
    """Carousel variant that uses the same items as the gallery."""

    name = _("Lightbox2 Carousel")
    module = _("Lightbox2")
    render_template = "djangocms_lightbox2/plugins/gallery_carousel.html"
    allow_children = True
    child_classes = ["Lightbox2ImagePlugin"]
    form = Lightbox2CarouselForm

    fieldsets = (
        (None, {"fields": ("title", "group_name")}),
        (
            _("Carousel appearance"),
            {
                "classes": ("collapse",),
                "fields": (
                    "carousel_aspect_ratio",
                    "carousel_background_color",
                    "carousel_object_fit",
                    ("show_fullscreen_button", "show_download_button"),
                ),
            },
        ),
        (
            _("Lightbox2 options"),
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
        context = super().render(context, instance, placeholder)
        context["carousel_background_color"] = (
            instance.carousel_background_color or "#F8F8F8"
        )
        context["carousel_aspect_ratio_css"] = instance.get_carousel_aspect_ratio_css()
        context["carousel_object_fit"] = instance.carousel_object_fit or "cover"
        return context


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
            parent_instance = (
                instance.parent and instance.parent.get_plugin_instance()[0]
            )
            from .models import Lightbox2Gallery  # local import to avoid circular

            if isinstance(parent_instance, Lightbox2Gallery):
                include_assets = False
        except ObjectDoesNotExist:
            include_assets = True
        context["include_assets"] = include_assets
        context["use_bundled_jquery"] = conf.USE_BUNDLED_JQUERY
        # For standalone images, use global default options
        if include_assets:
            context["lb_options"] = conf.DEFAULT_OPTIONS
            context["lb_options_id"] = f"dclb2-options-{instance.pk}"
        return context
