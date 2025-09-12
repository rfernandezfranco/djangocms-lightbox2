from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("cms", "0001_initial"),
        ("filer", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Lightbox2Gallery",
            fields=[
                ("cmsplugin_ptr", models.OneToOneField(
                    auto_created=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    parent_link=True,
                    primary_key=True,
                    related_name="djangocms_lightbox2_lightbox2gallery",
                    serialize=False,
                    to="cms.cmsplugin",
                )),
                ("title", models.CharField(blank=True, default="", max_length=150)),
                (
                    "group_name",
                    models.CharField(
                        blank=True,
                        help_text=(
                            "Nombre de grupo para 'data-lightbox'. Si está vacío, se usará 'gallery-<id>'."
                        ),
                        max_length=100,
                    ),
                ),
            ],
            bases=("cms.cmsplugin",),
        ),
        migrations.CreateModel(
            name="Lightbox2Image",
            fields=[
                ("cmsplugin_ptr", models.OneToOneField(
                    auto_created=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    parent_link=True,
                    primary_key=True,
                    related_name="djangocms_lightbox2_lightbox2image",
                    serialize=False,
                    to="cms.cmsplugin",
                )),
                ("caption", models.CharField(blank=True, default="", max_length=255)),
                ("alt_text", models.CharField(blank=True, default="", max_length=255)),
                ("thumbnail_width", models.PositiveIntegerField(default=400)),
                ("thumbnail_height", models.PositiveIntegerField(default=300)),
                (
                    "image",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="filer.image",
                    ),
                ),
            ],
            bases=("cms.cmsplugin",),
        ),
    ]
