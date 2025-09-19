from django.core import validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("djangocms_lightbox2", "0003_layout_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="lightbox2gallery",
            name="carousel_aspect_ratio",
            field=models.CharField(
                choices=[
                    ("16-9", "16:9 (widescreen)"),
                    ("4-3", "4:3 (standard)"),
                    ("1-1", "1:1 (square)"),
                    ("3-2", "3:2 (classic photo)"),
                    ("21-9", "21:9 (cinematic)"),
                ],
                default="4-3",
                help_text="Aspect ratio for the main carousel area.",
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name="lightbox2gallery",
            name="carousel_background_color",
            field=models.CharField(
                default="#F8F8F8",
                help_text="Background color applied to the main carousel area.",
                max_length=7,
                validators=[
                    validators.RegexValidator(
                        '^#(?:[0-9a-fA-F]{3}){1,2}$',
                        'Enter a valid hex color in the format #RRGGBB.',
                    )
                ],
            ),
        ),
        migrations.AddField(
            model_name="lightbox2gallery",
            name="carousel_object_fit",
            field=models.CharField(
                choices=[
                    ("cover", "cover"),
                    ("contain", "contain"),
                    ("fill", "fill"),
                    ("none", "none"),
                    ("scale-down", "scale-down"),
                ],
                default="cover",
                help_text="CSS object-fit value used for images in the carousel.",
                max_length=10,
            ),
        ),
    ]

