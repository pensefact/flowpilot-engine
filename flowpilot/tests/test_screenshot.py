import io
from PIL import Image
from flowpilot.screenshot import resize_screenshot, encode_screenshot, scale_coordinates


def _make_png(width: int, height: int) -> bytes:
    img = Image.new("RGB", (width, height), color="red")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_resize_no_change_when_within_limit():
    png = _make_png(1280, 720)
    resized, scale = resize_screenshot(png, max_edge=2576)
    img = Image.open(io.BytesIO(resized))
    assert img.size == (1280, 720)
    assert scale == 1.0


def test_resize_scales_down_large_image():
    png = _make_png(3840, 2160)
    resized, scale = resize_screenshot(png, max_edge=2576)
    img = Image.open(io.BytesIO(resized))
    assert img.size[0] <= 2576
    assert img.size[1] <= 2576
    assert scale < 1.0


def test_encode_returns_base64_string():
    png = _make_png(100, 100)
    encoded = encode_screenshot(png)
    assert isinstance(encoded, str)
    import base64
    decoded = base64.b64decode(encoded)
    assert decoded[:4] == b"\x89PNG"


def test_scale_coordinates_identity():
    assert scale_coordinates([500, 300], 1.0) == [500, 300]


def test_scale_coordinates_scales_up():
    result = scale_coordinates([500, 300], 0.5)
    assert result == [1000, 600]
