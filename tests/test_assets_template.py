from django.template import engines
from django.test import RequestFactory
from sekizai.context import SekizaiContext


def render_assets(use_bundled_jquery=True, lb_options=None, include_count=1):
    includes = (
        "{% include 'djangocms_lightbox2/includes/assets.html' %}" * include_count
    )
    tpl_src = (
        "{% load sekizai_tags static %}" + includes + "{% render_block 'js' %}"
        "{% render_block 'css' %}"
    )
    django_engine = engines["django"]
    template = django_engine.from_string(tpl_src)
    request = RequestFactory().get("/")
    context_data = {
        "use_bundled_jquery": use_bundled_jquery,
        "lb_options": lb_options,
        "lb_options_id": "dclb2-options-test",
    }
    ctx = SekizaiContext(context_data)
    ctx["request"] = request
    if hasattr(template, "template"):
        return template.template.render(ctx)
    return template.render(ctx, request=request)


def test_assets_include_bundled_jquery_and_options():
    out = render_assets(True, {"resizeDuration": 123})
    assert "lightbox-plus-jquery.min.js" in out
    assert '"resizeDuration": 123' in out
    assert "window.lightbox && window.lightbox.option(options)" not in out


def test_assets_include_standalone_and_options_with_jquery_check():
    out = render_assets(False, {"fadeDuration": 321})
    assert "lightbox.min.js" in out
    assert "window.jQuery" in out
    assert '"fadeDuration": 321' in out
    assert "window.lightbox && window.lightbox.option(options)" not in out


def test_assets_escape_script_content_in_lightbox_options():
    payload = "</script><script>window.pwned = true</script>"

    out = render_assets(True, {"albumLabel": payload})

    assert payload not in out
    assert r"\u003C/script\u003E" in out
    assert "window.pwned = true" in out


def test_assets_multiple_includes_are_guarded_against_duplicate_loads():
    out = render_assets(include_count=2)

    assert out.count("dclb2LightboxAssetsLoaded") == 4
    assert out.count("dclb2LightboxOverridesLoaded") == 4
    assert out.count("dclb2LightboxApiLoaded") == 4
    assert out.count("lightbox-plus-jquery.min.js") == 2
    assert out.count("lightbox-overrides.js") == 2
    assert out.count("lightbox-api.js") == 2
