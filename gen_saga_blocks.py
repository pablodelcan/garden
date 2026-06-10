#!/usr/bin/env python3
"""Generate Minecraft-style block textures for Wordmon Saga's 3D voxel world.

Each texture is a single seamless block face in chunky 16x16-style pixel art.
Post-processed: downscaled to 128px (nearest) for crisp GPU textures; the
"tuft" sprites get white flood-filled to alpha so they work as cross-planes.
"""
import base64, pathlib, sys, warnings
warnings.filterwarnings("ignore")
from google import genai
from PIL import Image
import numpy as np
from collections import deque

ROOT = pathlib.Path(__file__).parent
client = genai.Client(api_key=(ROOT / ".api_key").read_text().strip())
OUT = ROOT / "sprites"

STYLE = (
    "a single Minecraft-style voxel game BLOCK TEXTURE, true 16x16 pixel art "
    "aesthetic with chunky visible square pixels, NO anti-aliasing, NO gradients, "
    "NO border NO frame NO vignette, the texture fills the ENTIRE square frame "
    "edge-to-edge and tiles seamlessly with copies of itself, flat orthographic "
    "straight-on view of one block face, vibrant kid-friendly colors"
)

BLOCKS = {
    "mc_grass_top":  "bright green grass block top face, small darker green pixel speckles",
    "mc_grass_side": "grass block SIDE face: top 25% bright green grass lip with a jagged pixel edge, bottom 75% warm brown dirt with small darker speck pixels",
    "mc_dirt":       "plain warm brown dirt block face with scattered darker and lighter brown speck pixels",
    "mc_path_top":   "trodden dirt path block top face, light tan-khaki packed earth with subtle darker pixel specks",
    "mc_stone":      "gray cobblestone-like stone block face with lighter and darker gray pixel patches",
    "mc_ore":        "stone block face embedded with glowing cyan-blue crystal letter shapes, like alphabet rune ore, dark gray stone with 4 bright glowing blue letter-crystals",
    "mc_log_side":   "tree log block side face, vertical brown bark stripes with darker grooves",
    "mc_log_top":    "tree log block top face, concentric tan growth rings on cut wood",
    "mc_leaves":     "dense leafy foliage block face, layered bright and dark green leaf pixels",
    "mc_sand":       "pale yellow-tan sand block face with subtle speck pixels",
    "mc_snow":       "white snow block face with very subtle pale blue pixel sparkles",
    "mc_ice":        "translucent-looking pale blue ice block face with lighter diagonal crack lines",
    "mc_water":      "deep blue water block face with lighter blue wave ripple pixel lines",
    "mc_obsidian":   "very dark purple-black obsidian block face with thin violet glints",
    "mc_void":       "dark indigo void block face with glowing purple rune pixels and tiny white star specks",
    "mc_cosmic":     "deep space block face, dark blue-purple with small pink and cyan nebula pixel swirls and star specks",
    "mc_lava":       "glowing orange-red molten lava block face with bright yellow cracks",
    "mc_plank":      "warm light-brown wooden plank block face, horizontal planks with nail pixel dots",
    "mc_bookshelf":  "bookshelf block face like Minecraft: wooden frame with two shelf rows of colorful pixel book spines (red, blue, green, yellow books)",
}
# Cross-plane tufts: drawn on a PLAIN WHITE background, white becomes alpha
TUFTS = {
    "mc_tuft_grass":   "a clump of tall green grass blades, pixel art, on a PLAIN PURE WHITE background, the tuft occupies the lower 80% of the frame",
    "mc_tuft_flower_red": "a small red pixel-art flower with green stem and leaves, on a PLAIN PURE WHITE background",
    "mc_tuft_flower_yellow": "a small yellow pixel-art flower with green stem and leaves, on a PLAIN PURE WHITE background",
}


def gen(prompt, path):
    print("  ->", path.name)
    resp = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=STYLE + ". Subject: " + prompt + ".",
    )
    for p in resp.candidates[0].content.parts:
        if getattr(p, "inline_data", None) and p.inline_data.data:
            d = p.inline_data.data
            if isinstance(d, str):
                d = base64.b64decode(d)
            path.write_bytes(d)
            return True
    return False


def downscale(path, size=128):
    img = Image.open(path).convert("RGBA")
    img = img.resize((size, size), Image.NEAREST)
    img.save(path)


def white_to_alpha(path):
    img = Image.open(path).convert("RGBA")
    arr = np.array(img)
    r, g, b = arr[..., 0].astype(int), arr[..., 1].astype(int), arr[..., 2].astype(int)
    nearwhite = (r >= 215) & (g >= 215) & (b >= 215)
    H, W = nearwhite.shape
    visited = np.zeros_like(nearwhite, dtype=bool)
    q = deque()
    for x in range(W):
        if nearwhite[0, x]: q.append((0, x))
        if nearwhite[H - 1, x]: q.append((H - 1, x))
    for y in range(H):
        if nearwhite[y, 0]: q.append((y, 0))
        if nearwhite[y, W - 1]: q.append((y, W - 1))
    while q:
        y, x = q.popleft()
        if visited[y, x] or not nearwhite[y, x]:
            continue
        visited[y, x] = True
        if y > 0: q.append((y - 1, x))
        if y < H - 1: q.append((y + 1, x))
        if x > 0: q.append((y, x - 1))
        if x < W - 1: q.append((y, x + 1))
    arr[visited, 3] = 0
    Image.fromarray(arr).save(path)


def main():
    print("=== MINECRAFT BLOCK TEXTURES ===")
    for name, prompt in BLOCKS.items():
        path = OUT / (name + ".png")
        if path.exists():
            print("  skip", path.name)
            continue
        try:
            if gen(prompt, path):
                downscale(path)
        except Exception as e:
            print("  !!", name, e)
    print("=== TUFT SPRITES (white->alpha) ===")
    for name, prompt in TUFTS.items():
        path = OUT / (name + ".png")
        if path.exists():
            print("  skip", path.name)
            continue
        try:
            if gen(prompt, path):
                white_to_alpha(path)
                downscale(path, 256)
        except Exception as e:
            print("  !!", name, e)
    print("done")


if __name__ == "__main__":
    main()
