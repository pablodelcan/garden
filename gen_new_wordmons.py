#!/usr/bin/env python3
"""Generate AI sprites for the 8 newest Wordmons (June 2026 batch)."""
import base64, pathlib, warnings
warnings.filterwarnings("ignore")
from google import genai

ROOT = pathlib.Path(__file__).parent
client = genai.Client(api_key=(ROOT / ".api_key").read_text().strip())
SPRITES = ROOT / "sprites"

SPRITE_STYLE = (
    "AUTHENTIC POKEMON GAME BOY ADVANCE creature sprite, "
    "front-facing isolated on a TRANSPARENT background, "
    "Pokemon FireRed/LeafGreen/Emerald creature-design style, "
    "true 16-bit pixel art aesthetic, chunky visible pixels, NO anti-aliasing, "
    "limited Nintendo color palette, the creature is centered in the frame "
    "with a slight bouncy expressive pose, big cute Pokemon-style eyes, "
    "looking at the viewer, friendly child-game design, "
    "no background, no platform shadow, just the creature"
)

WORDMONS = {
    # baby / mid / final tier per id
    "leafkin":    ["a tiny leaf sprite, sage-green body with two big leaf-ears, smiling sweetly", "Bramblepaw — a slightly larger leafy creature with thorny vines on its shoulders", "Ancientoak — an enormous leafy beast with a crown of leaves and vines wrapping its arms"],
    "pebblet":    ["Pebblet — a small smiling pebble with rosy cheeks and tiny stubby arms", "Boulderbro — a medium boulder humanoid with friendly eyes and arm-rocks", "Mountainfist — a massive mountain creature with stone fists and a crown peak"],
    "puddlepuff": ["Puddlepuff — a tiny round water puddle creature with eyes and a smile", "Streamglop — a flowing water spirit with arms of streaming water", "Oceanqueen — a regal water creature with a coral crown and ocean cape"],
    "shroomy":    ["Shroomy — a small red mushroom creature with white spots on its cap and little kid-arms and legs", "Sporebobble — a medium giggling red mushroom with bigger cap and spores floating around", "Toadstoolord — a tall majestic mushroom king with cloak of spores"],
    "duskling":   ["Duskling — a tiny twilight kitten with violet fur and glowing purple eyes, fluffy tail", "Twilightprowl — a medium dark cat with bigger glowing slit eyes, shadowy purple fur", "Nightmaul — a fierce shadow panther with razor fangs, glowing violet eyes, three swishing tails"],
    "glowfly":    ["Glowfly — a tiny firefly creature with a glowing yellow lantern-belly", "Lanternmoth — a medium moth with four lantern-glow wings", "Stellabug — a majestic large bug with star-bright wings glowing gold"],
    "spritefox":  ["Spritefox — a tiny pink fox with a forehead star, fluffy tail, glittery fur", "Wishweaver — a medium pink/lavender fox with a bigger star, magic sparkles on tail", "Stardancer — a tall regal fox with 9 swishing starlit tails and a crown of stars"],
    "ironcrab":   ["Ironcrab — a small armored crab with red glowing eyes, polished iron shell, two big claws", "Steelcrust — a medium armored crab with rivets and bolts, fiercer red eyes", "Titanclamp — a massive metal crab fortress with huge claws like cannons"],
    "breezling":  ["Breezling — a tiny baby sky-blue bird Pokemon with a fluffy white cloud-puff for a tail, holding a green leaf in its beak, big sparkly eyes, very cute and friendly", "Skywhirl — a medium sky-blue bird with bigger cloud-tail swirl and confident grin", "Stormgale — a majestic large storm bird with electric crackles in its feathers and a huge cloud-storm tail"],
}


def gen(prompt, out):
    print(f"  -> {out.name}")
    resp = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=SPRITE_STYLE + ". Subject: " + prompt + ".",
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
    for wm_id, stages in WORDMONS.items():
        print(wm_id)
        for i, prompt in enumerate(stages):
            out = SPRITES / f"{wm_id}_{i+1}.png"
            if out.exists():
                print(f"  exists, skip {out.name}")
                continue
            try:
                gen(prompt, out)
            except Exception as e:
                print(f"  ⚠️  {e}")


if __name__ == "__main__":
    main()
