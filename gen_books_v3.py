#!/usr/bin/env python3
"""Generate book illustrations using the ACTUAL in-game sprites as reference
images, so characters look consistent across the whole game.

Nano Banana (gemini-2.5-flash-image) supports reference images via
multi-modal input — we pass the PNG bytes alongside the prompt.
"""
import base64, pathlib, sys, warnings, io
warnings.filterwarnings("ignore")

from google import genai
from google.genai import types
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

ROOT = pathlib.Path(__file__).parent
API_KEY = (ROOT / ".api_key").read_text().strip()
SPRITES = ROOT / "sprites"
client = genai.Client(api_key=API_KEY)

STYLE_NOTE = (
    "Match the pixel-art style, colors, proportions, and exact character "
    "features of the attached reference sprites precisely. Keep Río's "
    "curly brown hair, green hoodie, and red sneakers consistent. Keep "
    "each Wordmon's exact body shape, colors, tail, and facial features "
    "identical to its reference. Full scene illustration in the same "
    "chunky 16-bit pixel-art style, 1:1 square aspect, vibrant saturated "
    "colors, crisp pixels, detailed pixel environment"
)

# Reference sprites: which PNGs get attached for each book
BOOKS = {
    "book_sparky": {
        "refs": ["rio_trainer_idle.png", "sparky_1.png"],
        "cover": "book cover: Río kneeling next to Sparky inside a cozy bedroom during a rainstorm, lightning flashing in window, title area left blank at top",
        "1": "a kid's bedroom at night during a thunderstorm, rain hitting the window, lightning flashing outside, Sparky hiding and shaking under the bed, frightened expression",
        "2": "Río kneeling down on the bedroom floor with a kind face looking at Sparky who is shaking under the bed with wide worried eyes",
        "3": "Río smiling and pointing at the window where lightning flashes, Sparky standing next to him looking up curiously, bedroom at night",
        "4": "Sparky happily zapping blue electricity toward the stormy sky from an open bedroom window, Río laughing in the background, lightning everywhere, joyful mood",
    },
    "book_flamepup": {
        "refs": ["rio_trainer_idle.png", "flamepup_1.png", "bubblefin_1.png"],
        "cover": "book cover: Flamepup and Bubblefin sitting together by a sparkling pond, Río smiling in background, sunny day, title area left blank",
        "1": "Flamepup running super fast alone across a grassy field with orange flame trails behind him, motion lines, other tiny creatures in far distance",
        "2": "Flamepup standing at the edge of a blue pond looking sad, Bubblefin visible in the water looking scared and swimming away in the opposite direction",
        "3": "Flamepup sitting sadly on the grass with his head down, Río crouching next to him with a kind smile and a hand on his back, pond in background",
        "4": "Flamepup sitting peacefully by the pond with NO fire around him, Bubblefin happily blowing bubbles at him above the water surface, both characters smiling, sunny",
    },
    "book_drakle": {
        "refs": ["rio_trainer_idle.png", "drakle_1.png", "drakle_3.png"],
        "cover": "book cover: baby Drakle flapping his tiny wings trying to fly, Río cheering on the grassy ground below, sunny hill, title area left blank",
        "1": "baby Drakle standing on green grass looking up longingly at big adult dragons flying in the sky above, wistful yearning expression, sunny day",
        "2": "baby Drakle jumping off a small rock and flapping his tiny wings hard but falling down with an exaggerated funny face, grass patch below, comedic motion lines",
        "3": "Río jumping and cheering excitedly with arms raised, baby Drakle running determinedly on grass next to him about to jump, energetic motion, action scene",
        "4": "baby Drakle flying joyfully up in a bright blue sky with small fluffy clouds around him, wings fully spread, Río on the grass below pumping both fists celebrating, sunny",
    },
    "book_snowpuff": {
        "refs": ["rio_trainer_idle.png", "snowpuff_1.png"],
        "cover": "book cover: Snowpuff safely under a big colorful rainbow-striped umbrella held by Río on a sunny green field, title area left blank",
        "1": "Snowpuff rolling happily in a snowy winter field, white snowflakes falling, cold blue atmosphere, cozy winter scene",
        "2": "Snowpuff on bright green summer grass looking very worried, tiny water drops dripping off her body, bright yellow sun shining down, visible heat shimmer waves",
        "3": "Río running fast carrying a big rainbow-striped umbrella toward Snowpuff, dynamic action pose with motion lines, sunny grassy field",
        "4": "Snowpuff safely under the big rainbow-striped umbrella in cool shade, smiling happily, Río standing proudly beside her holding the umbrella up, sunny grass",
    },
}


def load_ref(name: str):
    path = SPRITES / name
    data = path.read_bytes()
    return types.Part.from_bytes(data=data, mime_type="image/png")


def generate(prompt: str, out: pathlib.Path, refs: list[str]) -> None:
    print(f"  → {out.name}")
    full_prompt = f"{STYLE_NOTE}. Scene: {prompt}."
    parts = [load_ref(r) for r in refs]
    parts.append(full_prompt)
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
        print(book_id, "with refs:", cfg["refs"])
        refs = cfg["refs"]
        for key, prompt in cfg.items():
            if key == "refs":
                continue
            suffix = "_cover" if key == "cover" else f"_{key}"
            out = SPRITES / f"{book_id}{suffix}.png"
            # Always regenerate (overwrite old inconsistent ones)
            generate(prompt, out, refs)


if __name__ == "__main__":
    main()
