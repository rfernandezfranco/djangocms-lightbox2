import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("djangocms_lightbox2", "0005_carousel_controls"),
    ]

    operations = [
        migrations.AlterField(
            model_name="lightbox2gallery",
            name="columns_desktop",
            field=models.PositiveIntegerField(
                default=4,
                help_text="Columns on desktop (Grid, 1-12).",
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(12),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="lightbox2gallery",
            name="columns_mobile",
            field=models.PositiveIntegerField(
                default=1,
                help_text="Columns on mobile (Grid, 1-12).",
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(12),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="lightbox2gallery",
            name="columns_tablet",
            field=models.PositiveIntegerField(
                default=2,
                help_text="Columns on tablet (Grid, 1-12).",
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(12),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="lightbox2gallery",
            name="fade_duration",
            field=models.PositiveIntegerField(
                default=600,
                help_text="Overlay fade duration (ms).",
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(10000),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="lightbox2gallery",
            name="gutter",
            field=models.PositiveIntegerField(
                default=8,
                help_text="Spacing between items (px, 0-200).",
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(200),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="lightbox2gallery",
            name="image_fade_duration",
            field=models.PositiveIntegerField(
                default=600,
                help_text="Image fade duration (ms).",
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(10000),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="lightbox2gallery",
            name="justified_row_height",
            field=models.PositiveIntegerField(
                default=220,
                help_text="Target row height (Justified, px, 1-2000).",
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(2000),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="lightbox2gallery",
            name="justified_tolerance",
            field=models.FloatField(
                default=0.25,
                help_text="Row adjustment tolerance (0-1).",
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(1),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="lightbox2gallery",
            name="limit_items",
            field=models.PositiveIntegerField(
                blank=True,
                default=None,
                help_text="Limit of images to display (0-1000; blank for all).",
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(1000),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="lightbox2gallery",
            name="max_height",
            field=models.PositiveIntegerField(
                blank=True,
                help_text=(
                    "Maximum image height (px). Leave blank to use the Lightbox2 "
                    "default."
                ),
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(10000),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="lightbox2gallery",
            name="max_width",
            field=models.PositiveIntegerField(
                blank=True,
                help_text=(
                    "Maximum image width (px). Leave blank to use the Lightbox2 "
                    "default."
                ),
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(10000),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="lightbox2gallery",
            name="position_from_top",
            field=models.PositiveIntegerField(
                default=50,
                help_text="Offset from the top (px).",
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(2000),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="lightbox2gallery",
            name="resize_duration",
            field=models.PositiveIntegerField(
                default=700,
                help_text="Resize duration (ms).",
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(10000),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="lightbox2image",
            name="thumbnail_height",
            field=models.PositiveIntegerField(
                default=300,
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(4096),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="lightbox2image",
            name="thumbnail_width",
            field=models.PositiveIntegerField(
                default=400,
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(4096),
                ],
            ),
        ),
    ]
