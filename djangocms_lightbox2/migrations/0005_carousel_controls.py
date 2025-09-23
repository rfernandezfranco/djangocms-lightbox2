from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("djangocms_lightbox2", "0004_carousel_customization"),
    ]

    operations = [
        migrations.AddField(
            model_name="lightbox2gallery",
            name="show_download_button",
            field=models.BooleanField(
                default=True,
                help_text="Display the download control in the carousel overlay.",
                verbose_name="Show download button",
            ),
        ),
        migrations.AddField(
            model_name="lightbox2gallery",
            name="show_fullscreen_button",
            field=models.BooleanField(
                default=True,
                help_text="Display the fullscreen control in the carousel overlay.",
                verbose_name="Show fullscreen button",
            ),
        ),
    ]
