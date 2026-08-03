import pytest
from django.core.exceptions import ValidationError

from djangocms_lightbox2.models import Lightbox2Gallery, Lightbox2Image


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("columns_desktop", 0),
        ("columns_tablet", 13),
        ("gutter", 201),
        ("justified_row_height", 0),
        ("justified_tolerance", 1.1),
        ("limit_items", 1001),
        ("max_width", 10001),
        ("position_from_top", -1),
        ("resize_duration", 10001),
    ],
)
def test_gallery_rejects_out_of_bounds_configuration(field, value):
    gallery = Lightbox2Gallery(**{field: value})

    with pytest.raises(ValidationError):
        gallery.full_clean(validate_unique=False)


def test_gallery_accepts_documented_boundaries():
    gallery = Lightbox2Gallery(
        columns_desktop=1,
        columns_tablet=12,
        columns_mobile=1,
        gutter=200,
        justified_row_height=2000,
        justified_tolerance=1,
        limit_items=0,
        max_width=10000,
        max_height=1,
        position_from_top=2000,
        fade_duration=10000,
        image_fade_duration=0,
        resize_duration=10000,
    )

    gallery.full_clean(validate_unique=False)


@pytest.mark.parametrize("field", ["thumbnail_width", "thumbnail_height"])
def test_image_rejects_invalid_thumbnail_dimensions(field):
    image = Lightbox2Image(**{field: 4097})

    with pytest.raises(ValidationError):
        image.full_clean(validate_unique=False)
