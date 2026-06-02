#!/usr/bin/env python3
"""Generate battle backgrounds v2, new wordmarks, and GBC town backdrop."""
import base64, pathlib, sys, warnings
warnings.filterwarnings("ignore")
from google import genai

ROOT = pathlib.Path(__file__).parent
client = genai.Client(api_key=(ROOT / ".api_key").read_text().strip())
SPRITES = ROOT / "sprites"

# ===== BATTLE BACKGROUNDS V2 =====
# Same 13 zones but more cinematic, dramatic compositions. Center is kept
# relatively empty so the big sprite fighters can be overlaid on top.
BG_STYLE = (
    "cinematic 16-bit pixel-art game battle scene background, "
    "dramatic Pokemon-game-boy-advance / Pokemon-platinum quality, "
    "wide 16:9 aspect ratio, deeply detailed atmospheric scene, "
    "vibrant rich colors with strong contrast, an empty arena platform "
    "in the center middle where two fighting creatures will be placed, "
    "the rest of the frame full of theme-appropriate dramatic detail, "
    "no characters or creatures, just the environment"
)
BACKGROUNDS = {
    "bg_forest": "an ancient enchanted forest at golden hour, towering moss-covered trees forming a canopy, beams of warm light piercing through, a flat grassy circular battle arena at center, glowing fireflies, deep emerald and gold tones",
    "bg_volcano": "a volcanic eruption arena, glowing lava rivers carving down obsidian cliffs, ash and embers swirling in the air, dark rocky battle platform in the middle, red and orange sunset sky with smoke columns",
    "bg_ocean": "a tropical coral reef shallows at sunset, crystal-clear turquoise water with light caustics, a sandy island arena platform in the center, palm trees framing the edges, pink and orange sky reflected in the water, dramatic clouds",
    "bg_cave": "a mystical underground crystal cathedral, walls embedded with massive glowing amethyst and cyan crystals, an arena of polished obsidian stone in the center, dripping stalactites above, deep purple and electric blue lighting",
    "bg_sky": "a floating cloud arena high above the world, fluffy cumulus clouds in every direction, golden sunlight streaming through, a smooth rainbow cloud platform in the center, distant mountains on the horizon, magical and airy",
    "bg_snow": "a snowy mountaintop battlefield under aurora borealis, pine trees laden with snow, an ice-glazed arena in the center, dramatic green and pink northern lights swirling overhead, falling snowflakes",
    "bg_castle": "a grand medieval castle courtyard at dusk, towering stone walls and banners, an ornate cobblestone battle arena at center, torch flames flickering, deep blue twilight sky, regal and dramatic",
    "bg_space": "deep space battle arena floating in a colorful nebula, swirling clouds of magenta and cyan cosmic gas, distant glowing planets, scattered stars everywhere, a crystalline arena platform in the center, epic cosmic atmosphere",
    "bg_mushroom": "a giant whimsical mushroom forest grove, towering red-capped and pink-stemmed mushrooms, sparkling spores in the air, a soft moss arena in the center, dreamy pink and purple lighting, fairy-tale magical",
    "bg_lavapit": "a fiery infernal lava pit arena, surrounded by molten orange lava on all sides, jagged obsidian rocks, a small dark obsidian platform in the center, flame geysers erupting from the edges, intense red and black",
    "bg_frozen": "a frozen tundra cathedral, towering blue ice formations and frozen waterfalls, a smooth ice arena in the center, dramatic icy blue and white palette with hints of pink sunrise, crisp and majestic",
    "bg_shadow": "a haunted shadow realm at midnight, twisted dark purple silhouette trees, eerie violet mist rising from ground, a cracked stone arena in the center with faint glowing runes, indigo and purple atmosphere, mysterious",
    "bg_cosmic": "a final-boss cosmic vortex, swirling rainbow galaxies of pink violet blue green and gold spinning around a central crystalline platform, shooting stars, epic and overwhelming intensity",
}

# ===== WORDMARK / LOGO VARIATIONS =====
LOGO_STYLE = (
    "wide horizontal banner wordmark logo for a children's reading "
    "videogame called 'RÍO READS'. 4:1 banner aspect ratio. "
    "Solid dark navy background (#1a1a2e) filling entire canvas. "
    "Bold blocky uppercase pixel-art letters. Letters POP brightly "
    "against the dark background. No characters or scenes — just "
    "the wordmark"
)
LOGOS = {
    "logo_v12_arcade": "the words 'RÍO READS' in chunky 16-bit pixel-art letters using a hot pink and gold gradient fill with thick golden outline, small pixel star sparkles scattered around, retro arcade game cartridge feel",
    "logo_v13_pokemon": "the words 'RÍO READS' in classic Pokemon-game-style chunky cartoon letters, deep blue letters with thick yellow outline and red drop shadow, blocky 90s gameboy logo aesthetic, tiny pokeball motif as the dot on the 'i' of RÍO",
    "logo_v14_nintendo": "the words 'RÍO READS' in nostalgic Super Mario / Nintendo Entertainment System style block letters, primary red letters with bold white inner stroke and thick black outline, slightly tilted angle, dynamic feel",
    "logo_v15_modern": "the words 'RÍO READS' in modern bubbly chunky pixel letters with a magenta-to-cyan gradient fill, sharp white inner highlight on each letter, soft glowing aura, vibrant and playful but premium-feeling",
}

# ===== GBC TOWN BACKDROP =====
TOWN_PROMPT = (
    "a top-down tile-based pixel art town backdrop in authentic "
    "Gameboy Color era Pokemon Gold/Silver/Crystal art style. "
    "Square 1:1 aspect ratio. Limited 4-color palette per tile region. "
    "Crisp chunky 16x16 pixel tiles, no anti-aliasing. "
    "Features: a central cobblestone path running through the middle, "
    "a Pokemon-Center-style red-roofed clinic building on the left, "
    "a blue-roofed Mart shop building on the right, a tan/brown wooden "
    "library building with a sign, a couple of small houses with chimneys, "
    "a few trees with classic pixel tree shapes, a wooden fence around "
    "the edges, patches of grass, a small pond with sparkles. "
    "No NPCs or characters — just the town itself. "
    "Nostalgic, warm, cozy small-town feel. Empty walking spaces "
    "between buildings where Wordmon NPCs will be overlaid later."
)


def gen(prompt, out, full_style=None):
    print(f"  → {out.name}")
    full = (full_style + ". Subject: " + prompt + ".") if full_style else prompt
    resp = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=full,
    )
    for p in resp.candidates[0].content.parts:
        if getattr(p, "inline_data", None) and p.inline_data.data:
            d = p.inline_data.data
            if isinstance(d, str): d = base64.b64decode(d)
            out.write_bytes(d)
            return
    raise RuntimeError(f"no image for {out.name}")


def main():
    args = set(sys.argv[1:])  # subset by category: 'bg', 'logo', 'town'

    if not args or "bg" in args:
        # Back up existing v2 backgrounds before overwriting
        print("\n=== BATTLE BACKGROUNDS V2 ===")
        for name, prompt in BACKGROUNDS.items():
            out = SPRITES / f"{name}.png"
            backup = SPRITES / f"{name}_v2.png"
            if out.exists() and not backup.exists():
                out.rename(backup)
                print(f"  backed up {name}.png → {name}_v2.png")
            print(name)
            try:
                gen(prompt, out, BG_STYLE)
            except Exception as e:
                print(f"  ⚠️  {e}")

    if not args or "logo" in args:
        print("\n=== LOGO WORDMARK VARIATIONS ===")
        for name, prompt in LOGOS.items():
            out = SPRITES / f"{name}.png"
            if out.exists():
                print(f"  ✓ exists, skip {out.name}")
                continue
            try:
                gen(prompt, out, LOGO_STYLE)
            except Exception as e:
                print(f"  ⚠️  {e}")

    if not args or "town" in args:
        print("\n=== GBC TOWN ===")
        out = SPRITES / "gbc_town.png"
        if not out.exists():
            try:
                gen(TOWN_PROMPT, out)
            except Exception as e:
                print(f"  ⚠️  {e}")
        else:
            print("  ✓ gbc_town.png exists, skip")


if __name__ == "__main__":
    main()
