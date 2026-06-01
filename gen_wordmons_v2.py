#!/usr/bin/env python3
"""5 new Wordmons with a cooler/edgier aesthetic for the redesign."""
import base64, pathlib, sys, warnings
warnings.filterwarnings("ignore")
from google import genai

ROOT = pathlib.Path(__file__).parent
client = genai.Client(api_key=(ROOT / ".api_key").read_text().strip())
SPRITES = ROOT / "sprites"

STYLE = (
    "chunky 16-bit pixel-art sprite, cute Pokemon-style monster, "
    "transparent background, centered, full body facing forward, "
    "soft outline, vibrant saturated colors, crisp pixels, "
    "square 1:1 aspect, sleek/cool aesthetic — slightly edgier than "
    "baby cute, more like a teen-friendly battle creature"
)

WORDMONS = {
    "goopling": [
        "a tiny cute green minecraft-style cube slime with big anime eyes and a happy face, glowing translucent green body, single antenna",
        "a medium green slime monster with multiple cubes stuck together, sharp eyes, drippy gooey body, slimy texture, dripping trails",
        "a massive slime king with a golden crown of cubes, glowing emerald body, fanged grin, smaller slime minions clinging to it",
    ],
    "roboraptor": [
        "a tiny robot velociraptor with chrome silver body, glowing blue eyes, cute small head, robotic legs, sleek metallic design",
        "a medium-sized robot raptor with armor plates, red glowing chest core, sharp claws, dynamic pose, futuristic design",
        "a huge cybernetic T-Rex robot with massive armor, glowing red optic eyes, plasma cannons on shoulders, intimidating apex predator pose",
    ],
    "voltwing": [
        "a tiny lightning bird chick with yellow feathers, electric crackles around it, oversized wings, cute beak, sparkling tail",
        "a medium lightning eagle with spread wings of pure electricity, golden body, fierce yellow eyes, plasma talons",
        "a colossal thunder phoenix with massive electric storm wings, glowing white-hot body, golden crown of lightning, lightning bolts arcing around",
    ],
    "frostmaw": [
        "a tiny white furry ice cub with crystal blue eyes, tiny ice horns on head, fluffy snowflake patterns on fur, adorable predator look",
        "a medium ice wolf with thick frost-white fur, sharp ice fangs, glowing cyan eyes, frost mist around paws",
        "a massive arctic beast with thick fur covered in ice crystals, huge curved ice tusks, glowing pale-blue eyes, blizzard aura, intimidating but majestic",
    ],
    "phazoroid": [
        "a tiny floating purple orb UFO with a single cute eye in the center, antenna on top, soft glowing aura, alien-style",
        "a medium UFO disc with three glowing eyes, neon underside lights, metallic body, beam coming from below",
        "a colossal alien mothership orb with many glowing eyes, complex futuristic mechanical body, beams of cosmic light radiating out, otherworldly menacing presence",
    ],
}


def gen(prompt, out):
    print(f"  → {out.name}")
    resp = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=f"{STYLE}. Subject: {prompt}.",
    )
    for p in resp.candidates[0].content.parts:
        if getattr(p, "inline_data", None) and p.inline_data.data:
            d = p.inline_data.data
            if isinstance(d, str): d = base64.b64decode(d)
            out.write_bytes(d)
            return
    raise RuntimeError(f"no image for {out.name}")


def main():
    only = set(sys.argv[1:])
    for mon, prompts in WORDMONS.items():
        if only and mon not in only:
            continue
        print(mon)
        for i, p in enumerate(prompts, 1):
            out = SPRITES / f"{mon}_{i}.png"
            if out.exists():
                print(f"  ✓ exists, skip {out.name}")
                continue
            gen(p, out)


if __name__ == "__main__":
    main()
