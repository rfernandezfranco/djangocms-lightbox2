from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("djangocms_lightbox2", "0002_add_options_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="lightbox2gallery",
            name="layout",
            field=models.CharField(
                choices=[("grid", "Grid"), ("masonry", "Masonry"), ("justified", "Justified")],
                default="grid",
                help_text="Disposición de la galería en la página.",
                max_length=12,
            ),
        ),
        migrations.AddField(
            model_name="lightbox2gallery",
            name="columns_desktop",
            field=models.PositiveIntegerField(default=4, help_text="Columnas en desktop (Grid)."),
        ),
        migrations.AddField(
            model_name="lightbox2gallery",
            name="columns_tablet",
            field=models.PositiveIntegerField(default=2, help_text="Columnas en tablet (Grid)."),
        ),
        migrations.AddField(
            model_name="lightbox2gallery",
            name="columns_mobile",
            field=models.PositiveIntegerField(default=1, help_text="Columnas en móvil (Grid)."),
        ),
        migrations.AddField(
            model_name="lightbox2gallery",
            name="gutter",
            field=models.PositiveIntegerField(default=8, help_text="Espacio entre elementos (px)."),
        ),
        migrations.AddField(
            model_name="lightbox2gallery",
            name="show_captions",
            field=models.BooleanField(default=False, help_text="Mostrar captions bajo miniaturas."),
        ),
        migrations.AddField(
            model_name="lightbox2gallery",
            name="justified_row_height",
            field=models.PositiveIntegerField(default=220, help_text="Altura objetivo por fila (Justified, px)."),
        ),
        migrations.AddField(
            model_name="lightbox2gallery",
            name="justified_tolerance",
            field=models.FloatField(default=0.25, help_text="Tolerancia de ajuste de fila (0-1)."),
        ),
        migrations.AddField(
            model_name="lightbox2gallery",
            name="limit_items",
            field=models.PositiveIntegerField(blank=True, help_text="Límite de imágenes a mostrar (opcional).", null=True),
        ),
    ]

