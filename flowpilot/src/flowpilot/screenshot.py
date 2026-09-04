import base64
import io
from PIL import Image


def resize_screenshot(png_bytes: bytes, max_edge: int = 2576) -> tuple[bytes, float]:
    img = Image.open(io.BytesIO(png_bytes))
    w, h = img.size
    long_edge = max(w, h)
    if long_edge <= max_edge:
        return png_bytes, 1.0
    scale = max_edge / long_edge
    new_w = int(w * scale)
    new_h = int(h * scale)
    resized = img.resize((new_w, new_h), Image.LANCZOS)
    buf = io.BytesIO()
    resized.save(buf, format="PNG")
    return buf.getvalue(), scale


def encode_screenshot(png_bytes: bytes) -> str:
    return base64.b64encode(png_bytes).decode("ascii")


def scale_coordinates(coord: list[int], scale_factor: float) -> list[int]:
    return [int(c / scale_factor) for c in coord]
