#!/usr/bin/env python3
"""Generate v4 visuals — authentic GBA-era Pokemon Ruby/Sapphire/Emerald
   battle backgrounds + town backdrop, Nintendo early-2000s style.

   This generation enforces TRUE 16-bit pixel art aesthetics:
   - Limited palette (~32 colors per scene)
   - No anti-aliasing, no gradients, chunky pixels
   - Authentic GBA layered platform composition
   - Bottom third = ground/platform where fighters stand
"""
import base64, pathlib, sys, warnings
warnings.filterwarnings("ignore")
from google import genai

ROOT = pathlib.Path(__file__).parent
client = genai.Client(api_key=(ROOT / ".api_key").read_text().strip())
SPRITES = ROOT / "sprites"

# ===== BATTLE BACKGROUNDS V3 — authentic GBA Pokemon =====
# Pokemon Ruby/Sapphire/Emerald (2002-2004) / FireRed-LeafGreen (2004)
# / Diamond-Pearl/Platinum (2006-2008) style. Wide 16:9 framing with a
# distinct bottom platform/ground tier where the fighters stand.
BG_STYLE = (
    "AUTHENTIC POKEMON GAME BOY ADVANCE pixel art battle background, "
    "in the exact style of Pokemon Ruby Sapphire Emerald FireRed (2002-2004), "
    "true 16-bit pixel art aesthetic, chunky visible pixels NO anti-aliasing "
    "NO gradient smoothing, limited palette of about 24 colors, "
    "wide 16:9 horizontal composition divided into 3 clear horizontal tiers: "
    "(1) upper sky/canopy tier, (2) middle horizon/midground tier, "
    "(3) lower foreground PLATFORM tier where fighters will stand — "
    "this lower platform must be visually distinct (solid color or "
    "tiled pattern) and roughly 30% of frame height, "
    "the platform's CENTER must be empty of any creatures or characters, "
    "decorative pixel-art props framing the edges (rocks, plants, props) "
    "but center clear, "
    "saturated cheerful Nintendo color palette, "
    "the look of a child-friendly 2003 handheld Pokemon game battle scene"
)
BACKGROUNDS_V3 = {
    "bg_forest": "Hoenn-region forest battle background, tall pixel-art conifer trees as silhouettes against a green canopy sky, a flat grassy meadow platform in the foreground tier with scattered pixel grass tufts and small mushroom props at the edges, two distant trees framing left and right, warm afternoon green palette",
    "bg_volcano": "Mt Chimney-style volcano battle background, dark obsidian rocky slopes with bright orange-red lava cracks zigzagging through, ember pixels floating in the sky, a flat dark obsidian rock platform foreground with glowing red veins, distant lava-mountain silhouette in the back, fiery red-orange-black palette",
    "bg_ocean": "tropical seaside battle background, pixel-art turquoise ocean waves with white foam tiles in the midground, a sandy beach platform foreground with seashell and starfish pixel props at edges, palm tree silhouettes framing left and right, bright cyan-blue sky, sunny tropical palette",
    "bg_cave": "underground crystal cave battle background, dark cave ceiling with stalactite pixels at top, glowing cyan and purple crystal cluster props at the sides, a flat rocky stone platform in the foreground with small pebble pixels, dim purple-blue cave lighting, mysterious cave palette",
    "bg_sky": "Sky Pillar style battle background high in the clouds, fluffy pixel-art cumulus cloud platforms with hard pixel edges in the midground and background, a circular cloud platform foreground tier with rainbow pixel edge highlights, distant pixel-art mountain peaks below, bright airy blue-white sky palette",
    "bg_snow": "Snowpoint-style snowy mountain battle background, snow-covered pixel pine trees framing the edges, blue mountain silhouettes in the background, flat snow platform foreground with pixel snowflake props and small icicle clumps, light snowfall pixels in the air, crisp icy blue-white palette",
    "bg_castle": "Pokemon-Castle battle background interior, gray stone brick wall pattern in the background tier, ornate pillars framing left and right with banner pixels, flat cobblestone tile platform foreground with a polished marble pattern, torch flame pixel props at the edges, regal red-gold-gray palette",
    "bg_space": "cosmic space battle background, deep purple-black pixel starfield with bright star pixels scattered, distant ringed planet pixel sprite in the upper background, a metallic crystalline space platform foreground tier with cyan glow edge pixels, scattered tiny meteor pixels at the edges, cosmic purple-cyan-magenta palette",
    "bg_mushroom": "whimsical giant mushroom forest battle background, tall pink and red pixel-art mushroom silhouettes framing both sides, sparkle spore pixels floating in the air, a flat moss-grass platform foreground with tiny pixel mushroom props at edges, dreamy soft-pink purple-pink palette",
    "bg_lavapit": "lava chamber battle background, jagged dark obsidian cliff walls framing left and right, glowing orange lava lakes in the midground tier with bubble pixel sprites, a small dark obsidian rock platform in the foreground center surrounded by lava edges, ember spark pixels in the air, intense red-orange-black palette",
    "bg_frozen": "frozen tundra battle background, towering ice pillar pixel-art silhouettes framing left and right, frozen waterfall pixel art in the background, a smooth ice platform foreground tier with reflective light-blue tile pattern, snowflake spark pixels in the air, crisp pale-blue white palette",
    "bg_shadow": "haunted shadow realm battle background, twisted dark pixel-art tree silhouettes framing left and right with bare branches, eerie purple mist pixel sprites rising from ground, a cracked stone platform foreground tier with faint glowing rune pixels, full moon pixel sprite in upper background, indigo-purple-black palette",
    "bg_cosmic": "ultimate cosmic vortex battle background, swirling spiral galaxy pixel art in the upper sky tier with pink violet blue and gold spiral arms, a hexagonal crystalline platform foreground tier with rainbow pixel glow edges, scattered shooting-star pixels in the air, epic rainbow cosmic palette",
}

# ===== GBC TOWN BACKDROP V2 — even more Pokemon-authentic =====
TOWN_V2_PROMPT = (
    "AUTHENTIC POKEMON GOLD SILVER CRYSTAL Game Boy Color top-down town map, "
    "exact pixel-art style of Pokemon Crystal / FireRed Pallet Town / "
    "Littleroot Town (2000-2004 Nintendo Game Freak), square 1:1 framing, "
    "true 16-bit pixel art with chunky 16x16 visible tile boundaries, "
    "NO anti-aliasing, NO gradient smoothing, limited 24-color palette per scene, "
    "top-down birds-eye view. "
    "Layout: a wide vertical cobblestone path running down the center of the frame, "
    "a Pokemon Center building on the upper-left (red roof with white cross sign, "
    "tan stone walls, blue glass automatic door), "
    "a Poke Mart building on the upper-right (blue tile roof, tan walls, "
    "yellow MART sign), "
    "a small wooden house with brown shingle roof and chimney in the lower-left "
    "(this is the player's house), "
    "a tall brown library building with READ sign in the lower-right, "
    "patches of tall pixel grass tiles between buildings, "
    "round green pixel-art trees framing the edges (top-down circular tree shapes), "
    "a small blue pond with light-blue ripple pixels in the bottom-right corner, "
    "a wooden fence around the outer edges, "
    "wide open walkable grass areas where the player and Wordmons can stand, "
    "warm sunny cheerful Pokemon Crystal palette of greens, browns, reds, blues, "
    "NO characters or NPCs visible — empty town ready for sprites to be overlaid"
)


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
    args = set(sys.argv[1:])

    if not args or "bg" in args:
        print("\n=== BATTLE BACKGROUNDS V3 (authentic GBA Pokemon) ===")
        for name, prompt in BACKGROUNDS_V3.items():
            out = SPRITES / f"{name}.png"
            backup = SPRITES / f"{name}_v3.png"
            if out.exists() and not backup.exists():
                # current is v3-cinematic — back it up
                out.rename(backup)
                print(f"  backed up {name}.png -> {name}_v3.png")
            print(name)
            try:
                gen(prompt, out, BG_STYLE)
            except Exception as e:
                print(f"  ⚠️  {e}")

    if not args or "town" in args:
        print("\n=== GBC TOWN V2 (more authentic) ===")
        out = SPRITES / "gbc_town.png"
        backup = SPRITES / "gbc_town_v3.png"
        if out.exists() and not backup.exists():
            out.rename(backup)
            print(f"  backed up gbc_town.png -> gbc_town_v3.png")
        try:
            gen(TOWN_V2_PROMPT, out)
        except Exception as e:
            print(f"  ⚠️  {e}")


if __name__ == "__main__":
    main()
