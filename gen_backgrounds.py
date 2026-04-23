#!/usr/bin/env python3
"""Generate fresh battle zone backgrounds for Río Reads using Nano Banana.

Each background is a cinematic kid-friendly scene in a pixel-art / modern
vector-painted style, 16:9 aspect, designed to feel like a new exciting
location.
"""
import base64
import pathlib
import sys
import warnings
warnings.filterwarnings("ignore")

from google import genai

ROOT = pathlib.Path(__file__).parent
API_KEY = (ROOT / ".api_key").read_text().strip()
SPRITES = ROOT / "sprites"

client = genai.Client(api_key=API_KEY)

STYLE = (
    "cinematic kid-friendly game battle scene background, 16:9 aspect ratio, "
    "vibrant saturated colors, vector-painted art style like Pokemon Unite or "
    "Monument Valley, clean flat design with soft gradients, empty center "
    "stage for two characters to battle, no people or creatures, "
    "immersive atmospheric landscape"
)

BACKGROUNDS = {
    "bg_forest": "lush magical forest clearing with tall glowing mushrooms, bright green canopy above, sun rays piercing through leaves, soft moss-covered ground in center, mystical fireflies",
    "bg_volcano": "dramatic volcanic crater with flowing orange lava rivers on sides, dark rocky ground in middle, ash clouds above, glowing embers floating in air, red sunset sky",
    "bg_ocean": "shallow tropical ocean battlefield with crystal clear turquoise water, sandy island platform in middle, palm trees on sides, bright blue sky with fluffy clouds, sparkling waves",
    "bg_cave": "mysterious crystal cave with glowing purple and cyan gems embedded in rock walls, smooth stone floor, soft blue luminescent pools, stalactites above",
    "bg_sky": "floating cloud kingdom platform with fluffy white clouds below and around, bright blue sky, golden sun in corner, small flying birds in distance, airy and magical",
    "bg_snow": "snowy winter tundra clearing with pine trees covered in snow on edges, soft snowfall, aurora borealis in sky, icy ground glinting, cozy warm lighting",
    "bg_castle": "grand stone castle courtyard with tall towers and flags on sides, stone pathway in middle, golden sunlight, banners waving, medieval fantasy style",
    "bg_space": "outer space battleground with colorful nebula swirls, distant glowing planets, star field everywhere, floating rocky platform in center, cosmic atmosphere",
    "bg_mushroom": "giant whimsical mushroom forest with oversized red and pink mushrooms on sides, tiny glowing spores in air, soft pink and purple lighting, fairy tale style",
    "bg_lavapit": "infernal lava pit arena with glowing orange lava pools around the edges, obsidian rock platform in center, flame geysers on sides, dark red sky, intense atmosphere",
    "bg_frozen": "frozen tundra with huge ice crystal formations on sides, glassy blue ice floor, snowy mountains in background, northern lights in sky, magical and crisp",
    "bg_shadow": "dark shadow realm with twisted purple shadow wisps rising from ground, eerie dim purple and blue lighting, ghostly atmosphere, slight mist, cracked dark stone floor",
    "bg_cosmic": "cosmic rainbow vortex with swirling galaxies of pink, purple, blue, green, and gold, floating crystal platform in middle, shooting stars, epic final-battle atmosphere",
}


def generate(prompt: str, out: pathlib.Path) -> None:
    full = f"{STYLE}. Scene: {prompt}."
    print(f"  → {out.name}")
    resp = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=full,
    )
    for part in resp.candidates[0].content.parts:
        if getattr(part, "inline_data", None) and part.inline_data.data:
            data = part.inline_data.data
            if isinstance(data, str):
                data = base64.b64decode(data)
            out.write_bytes(data)
            return
    raise RuntimeError(f"no image returned for {out.name}")


def main() -> None:
    only = set(sys.argv[1:])
    for name, prompt in BACKGROUNDS.items():
        if only and name not in only:
            continue
        out = SPRITES / f"{name}.png"
        backup = SPRITES / f"{name}_old.png"
        # Back up the old one (first time only)
        if out.exists() and not backup.exists():
            out.rename(backup)
        print(name)
        generate(prompt, out)


if __name__ == "__main__":
    main()
