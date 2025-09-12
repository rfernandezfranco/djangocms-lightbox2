from django.apps import AppConfig


class DjangoCMSLightbox2Config(AppConfig):
    name = "djangocms_lightbox2"
    verbose_name = "Django CMS Lightbox2"

    def ready(self):
        # No initialization required at import time.
        return None
