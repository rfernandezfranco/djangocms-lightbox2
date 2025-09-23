from django.template import engines
from django.test import RequestFactory
from sekizai.context import SekizaiContext


def render_assets(use_bundled_jquery=True, lb_options=None):
    tpl_src = (
        "{% load sekizai_tags static %}"
        "{% include 'djangocms_lightbox2/includes/assets.html' %}"
        "{% render_block 'js' %}"
        "{% render_block 'css' %}"
    )
    django_engine = engines["django"]
    template = django_engine.from_string(tpl_src)
    request = RequestFactory().get("/")
    context_data = {
        "use_bundled_jquery": use_bundled_jquery,
        "lb_options_json": lb_options,
    }
    ctx = SekizaiContext(context_data)
    ctx["request"] = request
    if hasattr(template, "template"):
        return template.template.render(ctx)
    return template.render(ctx, request=request)


def test_assets_include_bundled_jquery_and_options():
    out = render_assets(True, '{"resizeDuration": 123}')
    assert "lightbox-plus-jquery.min.js" in out
    assert 'window.lightbox && window.lightbox.option({"resizeDuration": 123})' in out


def test_assets_include_standalone_and_options_with_jquery_check():
    out = render_assets(False, '{"fadeDuration": 321}')
    assert "lightbox.min.js" in out
    assert "window.jQuery" in out
    assert 'window.lightbox && window.lightbox.option({"fadeDuration": 321})' in out
