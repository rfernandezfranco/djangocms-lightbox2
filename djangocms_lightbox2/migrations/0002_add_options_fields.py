from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("djangocms_lightbox2", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="lightbox2gallery",
            name="album_label",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AddField(
            model_name="lightbox2gallery",
            name="always_show_nav_on_touch_devices",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="lightbox2gallery",
            name="fade_duration",
            field=models.PositiveIntegerField(default=600),
        ),
        migrations.AddField(
            model_name="lightbox2gallery",
            name="fit_images_in_viewport",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="lightbox2gallery",
            name="image_fade_duration",
            field=models.PositiveIntegerField(default=600),
        ),
        migrations.AddField(
            model_name="lightbox2gallery",
            name="position_from_top",
            field=models.PositiveIntegerField(default=50),
        ),
        migrations.AddField(
            model_name="lightbox2gallery",
            name="resize_duration",
            field=models.PositiveIntegerField(default=700),
        ),
        migrations.AddField(
            model_name="lightbox2gallery",
            name="show_image_number_label",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="lightbox2gallery",
            name="wrap_around",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="lightbox2gallery",
            name="disable_scrolling",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="lightbox2gallery",
            name="max_width",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="lightbox2gallery",
            name="max_height",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
