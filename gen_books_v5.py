#!/usr/bin/env python3
"""Generate 2 Minecraft-themed illustrated books for Río."""
import base64, pathlib, sys, warnings
warnings.filterwarnings("ignore")
from google import genai
from google.genai import types

ROOT = pathlib.Path(__file__).parent
API_KEY = (ROOT / ".api_key").read_text().strip()
SPRITES = ROOT / "sprites"
client = genai.Client(api_key=API_KEY)

STYLE_NOTE = (
    "Match the pixel-art style and exact character features of the "
    "attached reference sprite of Río precisely. Keep Río's curly brown "
    "hair, green hoodie with red stripe, and red sneakers consistent. "
    "Full scene illustration in chunky 16-bit pixel-art style mixed "
    "with Minecraft cube-style blocks for the world (grass blocks, dirt, "
    "stone, trees made of cubes). 1:1 square aspect, vibrant saturated "
    "colors, crisp pixels, blocky Minecraft world combined with pixel-"
    "art character style"
)

BOOKS = {
    "book_minecraft_creeper": {
        "refs": ["rio_trainer_idle.png"],
        "cover": "book cover: Río standing in a Minecraft world hugging a small lonely-looking green creeper, blocky Minecraft trees and grass blocks around them, sunny sky, friendship vibe, title area blank top",
        "1": "Río spawning into a Minecraft world standing on a green grass block, blocky trees and dirt blocks around him, looking around curiously",
        "2": "Río spotting a small sad green creeper sitting alone behind a blocky tree, other creepers in the distance laughing meanly, lonely mood",
        "3": "Río walking up to the creeper and gently giving him a friendly hug, the creeper's eyes wide with happy surprise, blocky meadow",
        "4": "Río and the friendly creeper building a small wooden cube house together in Minecraft, both smiling, plank blocks stacked, cozy scene",
    },
    "book_minecraft_diamond": {
        "refs": ["rio_trainer_idle.png"],
        "cover": "book cover: Río holding a giant glowing diamond inside a Minecraft cave, glowing torches on stone walls, blocky pixel style, hero pose, title area blank",
        "1": "Río digging into a hillside in a Minecraft world with a wooden pickaxe, dirt blocks flying, determined face, sunny day",
        "2": "Río deep in a dark Minecraft cave with a torch, a zombie peeking around a corner with green skin and torn clothes, scary but cute",
        "3": "Río running fast away from the zombie, then spotting bright sparkly diamond ore embedded in the cave wall ahead, excited expression",
        "4": "Río holding a shiny blue diamond sword high in triumph, the zombie defeated in the background, Río standing on a stack of diamond blocks like a hero",
    },
}


def load_ref(name: str):
    return types.Part.from_bytes(data=(SPRITES / name).read_bytes(), mime_type="image/png")


def generate(prompt, out, refs):
    print(f"  → {out.name}")
    parts = [load_ref(r) for r in refs]
    parts.append(f"{STYLE_NOTE}. Scene: {prompt}.")
    resp = client.models.generate_content(model="gemini-2.5-flash-image", contents=parts)
    for part in resp.candidates[0].content.parts:
        if getattr(part, "inline_data", None) and part.inline_data.data:
            d = part.inline_data.data
            if isinstance(d, str):
                d = base64.b64decode(d)
            out.write_bytes(d)
            return
    raise RuntimeError(f"no image for {out.name}")


def main():
    only = set(sys.argv[1:])
    for book_id, cfg in BOOKS.items():
        if only and book_id not in only:
            continue
        print(book_id)
        refs = cfg["refs"]
        for key, prompt in cfg.items():
            if key == "refs":
                continue
            suffix = "_cover" if key == "cover" else f"_{key}"
            out = SPRITES / f"{book_id}{suffix}.png"
            if out.exists():
                print(f"  ✓ {out.name} exists, skipping")
                continue
            generate(prompt, out, refs)


if __name__ == "__main__":
    main()
