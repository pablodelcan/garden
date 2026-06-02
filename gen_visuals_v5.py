#!/usr/bin/env python3
"""v5 — Authentic GBA Pokemon tileset for the walkable Adventure Mode.

   Generates EDGE-TO-EDGE seamlessly tiling 16x16 / 32x32 style tiles
   (no inset borders, no frames) plus 2x2 building sprites.

   Backs up the existing tile_*.png to *_v4.png first.
"""
import base64, pathlib, sys, warnings
warnings.filterwarnings("ignore")
from google import genai

ROOT = pathlib.Path(__file__).parent
client = genai.Client(api_key=(ROOT / ".api_key").read_text().strip())
SPRITES = ROOT / "sprites"

# ===== EDGE-TO-EDGE TILES (square 1:1) =====
TILE_STYLE = (
    "AUTHENTIC POKEMON GAME BOY ADVANCE seamless top-down map tile, "
    "Pokemon FireRed LeafGreen Emerald style (2003-2004 Nintendo Game Freak), "
    "true 16-bit pixel art aesthetic, chunky 16x16 pixel cells, "
    "NO anti-aliasing NO gradient smoothing NO outlines NO frame NO border, "
    "the tile MUST fill the entire frame edge-to-edge with NO inset margin and NO background frame — "
    "it must seamlessly tile when placed next to copies of itself, "
    "limited 8-12 color authentic GBA Pokemon palette, "
    "square 1:1 framing showing one single tile texture only, "
    "viewed from directly above (top-down)"
)
TILES = {
    "tile_grass":     "lush green grass terrain tile with subtle tiny darker grass tuft pixel details scattered, the green base color fills every edge so it tiles seamlessly, NO border, NO inset margin",
    "tile_path":      "tan/beige dirt road tile, flat slightly textured tan-brown ground, small pebble pixels scattered, the tan base color fills every edge so it tiles seamlessly into adjacent path tiles, NO border, NO inset margin",
    "tile_tallgrass": "tall dark green grass tile with vertical blade pixels poking up, slightly darker than regular grass, signals wild encounter zone, base color fills every edge for seamless tiling",
    "tile_water":     "shallow turquoise water tile with subtle pixel ripple lines, gentle wave pixel highlights, tiles seamlessly, NO border NO inset margin",
    "tile_sand":      "sandy beach tile, pale yellow-tan sand with tiny darker speck pixels, tiles seamlessly",
    "tile_flower_red":   "grass tile with one small red flower pixel cluster in the center, otherwise same lush green grass base as tile_grass, base color fills every edge for seamless tiling",
    "tile_flower_yellow":"grass tile with one small yellow flower pixel cluster in the center, otherwise same lush green grass base, base fills every edge for seamless tiling",
}

# ===== TREES & PROPS (single-tile but with transparent grass under is OK) =====
TILE_PROPS = {
    "tile_tree":     "a single chunky round pixel-art tree centered on a grass tile, dark-green canopy circle with darker shadow side, small brown trunk peeking under, AUTHENTIC POKEMON-CRYSTAL-STYLE pixel tree, grass color fills around the tree to the edges of the frame so it sits naturally on a grass background",
    "tile_fence":    "a wooden picket fence segment running horizontally, two-rail design, tan wood color, viewed top-down on grass, the grass surrounds the fence and fills to the edges",
    "tile_sign":     "a small wooden sign post with a square sign board attached, brown wood post, beige sign face, viewed top-down on grass, grass surrounds the sign and fills to the edges",
    "tile_rock":     "a single small gray pixel-art rock boulder sitting on grass, viewed top-down, grass surrounds and fills to the edges of the frame",
}

# ===== BUILDINGS (these are 1.5x1.5 footprint — generated as square sprites
#       but the canvas will render them spanning 2x2 tiles) =====
BUILDING_STYLE = (
    "AUTHENTIC POKEMON GAME BOY ADVANCE 3/4-top-down pixel-art building sprite, "
    "Pokemon FireRed LeafGreen Emerald style, true 16-bit pixel art, chunky pixels, "
    "NO anti-aliasing, limited GBA palette, "
    "the building sits centered on a square tile of GRASS, "
    "grass color fills the area around the building all the way to the frame edges, "
    "so the sprite can be overlaid on a grass map and look natural, "
    "viewed slightly from above with the roof visible and the front facade visible, "
    "small front door, small windows, classic Pokemon-game building proportions"
)
BUILDINGS = {
    "tile_house":      "small cottage-style residential house, beige/tan stucco walls, red-tile pitched roof, brown front door, two small square windows, small chimney with smoke wisp pixels, classic FireRed-style Pallet Town house",
    "tile_pokecenter": "Pokemon Center building, larger than houses, white walls, big red pitched roof with a white medical CROSS sign on the front face, blue automatic glass doors, small POKEMON CENTER sign banner above the door",
    "tile_shop":       "Poke Mart shop building, larger than houses, beige walls, blue pitched roof, yellow MART sign banner on the front face, blue automatic glass door, classic Pokemon-mart proportions",
    "tile_library":    "small library/lab building, brown wooden walls, dark-brown pitched roof, small READ sign banner above door, wooden front door, two front windows with warm yellow light",
}


def gen(prompt, out, full_style=None):
    print(f"  -> {out.name}")
    full = (full_style + ". Subject: " + prompt + ".") if full_style else prompt
    resp = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=full,
    )
    for p in resp.candidates[0].content.parts:
        if getattr(p, "inline_data", None) and p.inline_data.data:
            d = p.inline_data.data
            if isinstance(d, str):
                d = base64.b64decode(d)
            out.write_bytes(d)
            return
    raise RuntimeError(f"no image for {out.name}")


def main():
    args = set(sys.argv[1:])  # 'tile' | 'prop' | 'building'

    if not args or "tile" in args:
        print("\n=== EDGE-TO-EDGE TERRAIN TILES ===")
        for name, prompt in TILES.items():
            out = SPRITES / f"{name}.png"
            backup = SPRITES / f"{name}_v4.png"
            if out.exists() and not backup.exists():
                out.rename(backup)
                print(f"  backed up {out.name} -> {backup.name}")
            print(name)
            try:
                gen(prompt, out, TILE_STYLE)
            except Exception as e:
                print(f"  ⚠️  {e}")

    if not args or "prop" in args:
        print("\n=== PROP TILES ===")
        for name, prompt in TILE_PROPS.items():
            out = SPRITES / f"{name}.png"
            backup = SPRITES / f"{name}_v4.png"
            if out.exists() and not backup.exists():
                out.rename(backup)
                print(f"  backed up {out.name} -> {backup.name}")
            print(name)
            try:
                gen(prompt, out, TILE_STYLE)
            except Exception as e:
                print(f"  ⚠️  {e}")

    if not args or "building" in args:
        print("\n=== BUILDINGS (2x2 sprites) ===")
        for name, prompt in BUILDINGS.items():
            out = SPRITES / f"{name}.png"
            backup = SPRITES / f"{name}_v4.png"
            if out.exists() and not backup.exists():
                out.rename(backup)
                print(f"  backed up {out.name} -> {backup.name}")
            print(name)
            try:
                gen(prompt, out, BUILDING_STYLE)
            except Exception as e:
                print(f"  ⚠️  {e}")


if __name__ == "__main__":
    main()
