#!/usr/bin/env python3
"""Generate authentic GBA Pokemon-style NPC sprites for the overworld."""
import base64, pathlib, warnings
warnings.filterwarnings("ignore")
from google import genai

ROOT = pathlib.Path(__file__).parent
client = genai.Client(api_key=(ROOT / ".api_key").read_text().strip())
SPRITES = ROOT / "sprites"

NPC_STYLE = (
    "AUTHENTIC POKEMON GAME BOY ADVANCE NPC overworld sprite, "
    "Pokemon FireRed/LeafGreen/Emerald style (2003-2004 Nintendo Game Freak), "
    "true 16-bit pixel art, chunky visible pixels, NO anti-aliasing, "
    "limited Nintendo GBA palette, full-body front-facing character standing pose, "
    "TRANSPARENT background (PNG alpha), the character is centered in the frame, "
    "small standing pose with feet visible and arms slightly out, "
    "small expressive face with big Pokemon-style eyes, "
    "the proportions match Pokemon Crystal/FireRed townspeople: head ~1/3 of body, "
    "no background, no shadow disc, just the character isolated"
)

NPCS = {
    "npc_prof":  "elderly friendly male Pokemon professor in a long white lab coat, balding gray hair, round glasses, blue undershirt, brown pants, brown shoes, kind smile, holding a notebook in one hand",
    "npc_kid":   "a cheerful young boy trainer with a blue baseball cap turned forward, red t-shirt, blue shorts, white sneakers, brown hair peeking out the cap, backpack on back, big smile",
    "npc_rosa":  "a cheerful young girl wearing a sunny yellow sundress with little flower print, brown braids tied with red ribbons, light brown skin, holding a small bouquet of red and yellow flowers, brown sandals, big bright smile",
    "npc_milo": "a friendly young boy reader with curly black hair, glasses, a green hoodie with white drawstrings, dark blue jeans, sneakers, holding a small open book in his hands, gentle smile",
}


def gen(prompt, out):
    print(f"  -> {out.name}")
    resp = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=NPC_STYLE + ". Subject: " + prompt + ".",
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
    for name, prompt in NPCS.items():
        out = SPRITES / f"{name}.png"
        backup = SPRITES / f"{name}_old.png"
        if out.exists() and not backup.exists():
            out.rename(backup)
            print(f"  backed up {out.name} -> {backup.name}")
        print(name)
        try:
            gen(prompt, out)
        except Exception as e:
            print(f"  ⚠️  {e}")


if __name__ == "__main__":
    main()
