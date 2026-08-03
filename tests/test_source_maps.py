import json
import re
from pathlib import Path

import pytest

LIGHTBOX_JS = Path("djangocms_lightbox2/static/djangocms_lightbox2/lightbox2/js")


@pytest.mark.parametrize(
    ("bundle_name", "map_name"),
    [
        ("lightbox.min.js", "lightbox.min.map"),
        ("lightbox-plus-jquery.min.js", "lightbox-plus-jquery.min.map"),
    ],
)
def test_lightbox_bundle_references_matching_source_map(bundle_name, map_name):
    bundle = (LIGHTBOX_JS / bundle_name).read_text()
    source_mapping = re.search(r"//# sourceMappingURL=(\S+)", bundle)
    source_map = json.loads((LIGHTBOX_JS / map_name).read_text())

    assert source_mapping
    assert source_mapping.group(1) == map_name
    assert source_map["version"] == 3
    assert source_map["file"] == bundle_name
