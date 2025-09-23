SECRET_KEY = "tests-secret-key"
DEBUG = True
USE_TZ = True

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "django.contrib.messages",
    # django CMS stack
    "cms",
    "menus",
    "treebeard",
    "sekizai",
    # filer stack
    "easy_thumbnails",
    "mptt",
    "filer",
    # our app
    "djangocms_lightbox2",
]

MIDDLEWARE = []

ROOT_URLCONF = __name__

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.template.context_processors.static",
            ]
        },
    }
]

STATIC_URL = "/static/"
SITE_ID = 1

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# CMS minimal templates (not used directly but required by cms)
CMS_TEMPLATES = (("base.html", "Base"),)

CMS_CONFIRM_VERSION4 = True
