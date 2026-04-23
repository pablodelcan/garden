#!/usr/bin/env python3
"""Generate illustrated book pages in the pixel-art style matching Wordmons."""
import base64, pathlib, sys, warnings
warnings.filterwarnings("ignore")

from google import genai

ROOT = pathlib.Path(__file__).parent
API_KEY = (ROOT / ".api_key").read_text().strip()
SPRITES = ROOT / "sprites"
client = genai.Client(api_key=API_KEY)

STYLE = (
    "chunky 16-bit pixel-art scene for a children's reading videogame, "
    "cute Pokemon-style characters, vibrant saturated colors, crisp pixels, "
    "detailed pixel environment, 1:1 square aspect, clean shading, "
    "kid-friendly adventure vibe, bold colorful palette"
)

# Reused character descriptions (so they look consistent across pages)
RIO = "a 7-year-old brown-haired boy named Rio with big eyes, wearing a red t-shirt and blue shorts, smiling"
SPARKY = "Sparky, a tiny cute yellow pokemon-style creature with lightning bolt tail, chubby body, big eyes, rabbit-like ears"
FLAMEPUP = "Flamepup, a tiny fire puppy with red fur, flame tufts on head, cute big eyes"
BUBBLEFIN = "Bubblefin, a tiny cute blue fish-like pokemon with big eyes and a spout on her head"
DRAKLE = "Drakle, a tiny emerald-green baby dragon with oversized head, big eyes, small wings, chubby"
SNOWPUFF = "Snowpuff, a tiny round white snowball creature with pale cyan blush, big eyes, twig arms, icy crystal on top"

BOOKS = {
    "book_sparky": {
        "cover": f"pixel-art book cover scene with {RIO} kneeling next to {SPARKY} inside a cozy bedroom during a rainstorm, lightning flashing in window, title area left blank at top, cute style",
        "1": f"pixel-art scene: a kid's bedroom at night during a thunderstorm, rain hitting the window, lightning flashing outside, {SPARKY} hiding and shaking under the bed",
        "2": f"pixel-art scene: {RIO} kneeling down on the bedroom floor looking at {SPARKY} who is shaking with wide worried eyes under the bed, comforting expression",
        "3": f"pixel-art scene: {RIO} smiling and pointing at the window where lightning sparkles, {SPARKY} next to him looking up curious, bedroom at night",
        "4": f"pixel-art scene: {SPARKY} happily zapping electricity toward the stormy sky from the bedroom window, {RIO} laughing in the background, lightning everywhere, joyful mood",
    },
    "book_flamepup": {
        "cover": f"pixel-art book cover scene with {FLAMEPUP} and {BUBBLEFIN} sitting by a sparkling pond, {RIO} smiling in background, sunny day, title area left blank",
        "1": f"pixel-art scene: {FLAMEPUP} running super fast across a grassy field with flame trails behind him, alone, other creatures far in the distance",
        "2": f"pixel-art scene: {FLAMEPUP} standing at the edge of a blue pond, {BUBBLEFIN} visible in the water looking scared and swimming away",
        "3": f"pixel-art scene: {FLAMEPUP} sitting sadly on the grass, {RIO} crouching next to him with a kind smile, patting his head, pond in background",
        "4": f"pixel-art scene: {FLAMEPUP} sitting by the pond with no fire, {BUBBLEFIN} happily blowing bubbles at him above the water, both smiling, sunny",
    },
    "book_drakle": {
        "cover": f"pixel-art book cover scene with {DRAKLE} flapping his tiny wings trying to fly, {RIO} cheering on the ground, grassy hill, title area left blank",
        "1": f"pixel-art scene: {DRAKLE} standing on green grass looking up longingly at big dragons flying in the sky above, wistful mood",
        "2": f"pixel-art scene: {DRAKLE} jumping off a small rock and flapping wings hard, but falling to the ground with a funny face, grass below",
        "3": f"pixel-art scene: {RIO} jumping and cheering excitedly, {DRAKLE} running on the grass next to him about to jump, motion lines, energetic",
        "4": f"pixel-art scene: {DRAKLE} flying joyfully up in the blue sky with tiny clouds around, {RIO} on the ground below pumping his fist in celebration, sunny",
    },
    "book_snowpuff": {
        "cover": f"pixel-art book cover scene with {SNOWPUFF} under a big colorful umbrella held by {RIO} on a sunny day, title area left blank",
        "1": f"pixel-art scene: {SNOWPUFF} rolling happily in a snowy winter field, snowflakes falling, cozy cold atmosphere",
        "2": f"pixel-art scene: {SNOWPUFF} on green summer grass looking worried, drops of water dripping off her body, bright sun shining down, heat waves",
        "3": f"pixel-art scene: {RIO} running fast with a big rainbow-striped umbrella toward {SNOWPUFF}, action pose, grassy sunny field",
        "4": f"pixel-art scene: {SNOWPUFF} safely under the big umbrella in cool shade, smiling happily, {RIO} standing proudly beside her, sunny day",
    },
}


def generate(prompt: str, out: pathlib.Path) -> None:
    full = f"{STYLE}. Subject: {prompt}."
    print(f"  → {out.name}")
    resp = client.models.generate_content(model="gemini-2.5-flash-image", contents=full)
    for part in resp.candidates[0].content.parts:
        if getattr(part, "inline_data", None) and part.inline_data.data:
            d = part.inline_data.data
            if isinstance(d, str):
                d = base64.b64decode(d)
            out.write_bytes(d)
            return
    raise RuntimeError(f"no image for {out.name}")


def main():
    for book_id, prompts in BOOKS.items():
        print(book_id)
        for key, p in prompts.items():
            suffix = "_cover" if key == "cover" else f"_{key}"
            out = SPRITES / f"{book_id}{suffix}.png"
            if out.exists():
                print(f"  ✓ exists, skipping {out.name}")
                continue
            generate(p, out)


if __name__ == "__main__":
    main()
