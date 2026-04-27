#!/usr/bin/env python3
"""Post-process raw Nano Banana outputs into game-ready PNGs.

- Sprites (boxhead, props): chroma-key the near-white background → transparent
- Backgrounds: trim the bottom, then dither + low-res pixelize
- Tiles: generated procedurally (the API blocks plain-texture prompts).

Outputs go to boxhead_assets/processed/.
"""
import pathlib
import random
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "boxhead_assets"
DST = SRC / "processed"
DST.mkdir(exist_ok=True)


def chroma_key(im: Image.Image, tol: int = 30, soft: int = 18) -> Image.Image:
    """Auto-detect corner background color and make matching pixels transparent.

    Samples 4 corners; if they agree (low chroma neutral color), keys that
    color out within `tol` distance, with `soft` band of partial transparency.
    """
    im = im.convert("RGBA")
    w, h = im.size
    corners = [im.getpixel((1, 1)),
               im.getpixel((w - 2, 1)),
               im.getpixel((1, h - 2)),
               im.getpixel((w - 2, h - 2))]
    # Use mean of 4 corners as the bg key
    br = sum(c[0] for c in corners) / 4
    bg = sum(c[1] for c in corners) / 4
    bb = sum(c[2] for c in corners) / 4
    px = im.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            d = max(abs(r - br), abs(g - bg), abs(b - bb))
            if d <= tol:
                px[x, y] = (r, g, b, 0)
            elif d <= tol + soft:
                t = (d - tol) / soft
                a2 = int(a * t)
                px[x, y] = (r, g, b, max(0, min(255, a2)))
    return im


def trim_bbox(im: Image.Image, pad: int = 6) -> Image.Image:
    """Crop to the non-transparent bbox + a little padding."""
    bbox = im.getbbox()
    if not bbox:
        return im
    x0, y0, x1, y1 = bbox
    w, h = im.size
    x0 = max(0, x0 - pad)
    y0 = max(0, y0 - pad)
    x1 = min(w, x1 + pad)
    y1 = min(h, y1 + pad)
    return im.crop((x0, y0, x1, y1))


def crop_center_square(im: Image.Image, frac: float = 0.55) -> Image.Image:
    """Crop a centered square that's `frac` of the smaller dimension. Used to
    remove the framing/perspective edges from tile textures."""
    w, h = im.size
    side = int(min(w, h) * frac)
    cx, cy = w // 2, h // 2
    return im.crop((cx - side // 2, cy - side // 2, cx + side // 2, cy + side // 2))


def crop_top(im: Image.Image, frac: float = 0.7) -> Image.Image:
    """Keep top `frac` of the image — strips the diorama stage floor."""
    w, h = im.size
    return im.crop((0, 0, w, int(h * frac)))


def dither_pixelize(im: Image.Image, target_w: int = 240, palette_n: int = 16) -> Image.Image:
    """Downsample, quantize+dither to a small palette, upscale with nearest
    neighbor. Forces a chunky retro-pixel look with visible Floyd-Steinberg
    dithering between palette colors."""
    im = im.convert("RGB")
    w, h = im.size
    target_h = max(1, int(h * target_w / w))
    small = im.resize((target_w, target_h), Image.LANCZOS)
    pal = small.convert(
        "P", palette=Image.Palette.ADAPTIVE, colors=palette_n,
        dither=Image.FLOYDSTEINBERG
    )
    quant = pal.convert("RGB")
    return quant.resize((w, h), Image.NEAREST)


def pixelize_sprite(im: Image.Image, target_h: int = 64, palette_n: int = 10) -> Image.Image:
    """Resize sprite to a target HEIGHT in pixels (preserving aspect),
    quantize colors with dither, then upscale 4x with NEAREST so it
    displays as chunky pixels but stays at a usable canvas size. Alpha
    is preserved separately."""
    w, h = im.size
    target_w = max(1, int(w * target_h / h))
    small = im.resize((target_w, target_h), Image.LANCZOS)
    # Split alpha so palette quantization doesn't trash it
    alpha = small.split()[-1]
    rgb = small.convert("RGB")
    pal = rgb.convert(
        "P", palette=Image.Palette.ADAPTIVE, colors=palette_n,
        dither=Image.FLOYDSTEINBERG
    )
    quant = pal.convert("RGB")
    out = Image.new("RGBA", small.size)
    out.paste(quant, (0, 0))
    # Threshold alpha hard so the silhouette is crisp at small size
    a = alpha.point(lambda v: 255 if v > 100 else 0)
    out.putalpha(a)
    return out


def process_sprite(name: str, pixelize: bool = False, target_h: int = 64) -> None:
    src = SRC / f"{name}.png"
    if not src.exists():
        print(f"  miss: {name}")
        return
    im = Image.open(src)
    im = chroma_key(im)
    im = trim_bbox(im, pad=4)
    if pixelize:
        im = pixelize_sprite(im, target_h=target_h, palette_n=12)
    out = DST / f"{name}.png"
    im.save(out)
    print(f"  → {out.relative_to(SRC)} ({im.size[0]}x{im.size[1]})")


def process_bg(loc: str) -> None:
    src = SRC / loc / "bg.png"
    if not src.exists():
        print(f"  miss: {loc}/bg")
        return
    im = Image.open(src).convert("RGB")
    im = crop_top(im, frac=0.78)
    im = dither_pixelize(im, target_w=128, palette_n=8)
    out = DST / f"{loc}_bg.png"
    im.save(out)
    print(f"  → {out.relative_to(SRC)} ({im.size[0]}x{im.size[1]})")


TILE_PALETTES = {
    "tokyo":     {"ground": ["#2a1d3a", "#3a2a4a", "#4a3a5a", "#523f63", "#1c1428"],
                  "grass":  ["#3a2a4a", "#4a3a5a", "#5a4570", "#a05a78", "#3a2a4a"]},
    "sahara":    {"ground": ["#c9966a", "#b8855a", "#d4a878", "#a87650", "#dab48a"],
                  "grass":  ["#a06f48", "#b07a55", "#bf8966", "#d49a72", "#996640"]},
    "patagonia": {"ground": ["#5a6470", "#4a5460", "#6a7480", "#3f4854", "#646e7a"],
                  "grass":  ["#6a7050", "#7a8058", "#5a6048", "#8a9068", "#606848"]},
    "amazon":    {"ground": ["#3a2618", "#4a3622", "#5a4232", "#2a1a10", "#403020"],
                  "grass":  ["#1f3f2a", "#2a5240", "#3f6850", "#1a3522", "#356548"]},
    # New worlds
    "marrakech": {"ground": ["#9c5a3c", "#b06a48", "#7a4030", "#bf7858", "#854424"],
                  "grass":  ["#c08858", "#a06640", "#b07a55", "#d49a72", "#9a6038"]},
    "iceland":   {"ground": ["#1a1a1f", "#2a2a31", "#3a3a42", "#0e0e10", "#252530"],
                  "grass":  ["#2a3a3f", "#1a2a30", "#3a4a50", "#445560", "#1a282e"]},
    "metro":     {"ground": ["#3a3838", "#2a2828", "#4a4848", "#1a1818", "#322f2f"],
                  "grass":  ["#5a5050", "#4a4040", "#6a5858", "#3a3232", "#5a4f48"]},
}


def make_tile(palette, size: int = 64, seed: int = 0) -> Image.Image:
    """Procedurally paint a chunky low-res tile from a small color palette."""
    rng = random.Random(seed)
    colors = [tuple(int(c[i:i+2], 16) for i in (1, 3, 5)) for c in palette]
    im = Image.new("RGB", (size, size), colors[0])
    px = im.load()
    # Two-pass dithered noise: a base layer + sparse highlights
    for y in range(size):
        for x in range(size):
            r = rng.random()
            if r < 0.55: c = colors[0]
            elif r < 0.78: c = colors[1]
            elif r < 0.92: c = colors[2]
            elif r < 0.98: c = colors[3]
            else: c = colors[4]
            px[x, y] = c
    return im


def process_tile(loc: str, kind: str) -> None:
    palette = TILE_PALETTES[loc][kind]
    seed = hash((loc, kind)) & 0xffff
    im = make_tile(palette, size=64, seed=seed)
    # Upscale 8x with nearest-neighbor for that chunky-pixel feel
    im = im.resize((512, 512), Image.NEAREST)
    out = DST / f"{loc}_{kind}.png"
    im.save(out)
    print(f"  → {out.relative_to(SRC)} ({im.size[0]}x{im.size[1]}) [procedural]")


def main() -> None:
    print("sprites:")
    for n in ("boxhead_idle", "boxhead_walk_a"):
        process_sprite(n, pixelize=True, target_h=64)
    for n in ("prop_exit_door", "prop_spawner"):
        process_sprite(n, pixelize=True, target_h=72)
    locs = ("tokyo", "sahara", "patagonia", "amazon",
            "marrakech", "iceland", "metro")
    print("backgrounds:")
    for loc in locs:
        process_bg(loc)
    print("tiles:")
    for loc in locs:
        process_tile(loc, "ground")
        process_tile(loc, "grass")


if __name__ == "__main__":
    main()
