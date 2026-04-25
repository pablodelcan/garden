#!/usr/bin/env python3
"""Generate 5 NEW illustrated book pages using in-game sprites as refs."""
import base64, pathlib, sys, warnings
warnings.filterwarnings("ignore")
from google import genai
from google.genai import types

ROOT = pathlib.Path(__file__).parent
API_KEY = (ROOT / ".api_key").read_text().strip()
SPRITES = ROOT / "sprites"
client = genai.Client(api_key=API_KEY)

STYLE_NOTE = (
    "Match the pixel-art style, colors, proportions, and exact character "
    "features of the attached reference sprites precisely. Keep Río's "
    "curly brown hair, green hoodie with red stripe, and red sneakers "
    "consistent. Keep each Wordmon's exact body shape, colors, tail, and "
    "facial features identical to its reference. Full scene illustration "
    "in the same chunky 16-bit pixel-art style, 1:1 square aspect, "
    "vibrant saturated colors, crisp pixels, detailed pixel environment"
)

BOOKS = {
    "book_spookle": {
        "refs": ["rio_trainer_idle.png", "spookle_1.png"],
        "cover": "book cover: Río standing next to Spookle the friendly purple ghost wearing a tiny party hat, balloons and birthday banners around them, cozy bedroom, title area blank top",
        "1": "kid's bedroom, Spookle the purple ghost floating sadly alone with no decorations, looking lonely on his birthday",
        "2": "Río walking up to Spookle with a kind smile, holding a small wrapped present and a balloon, friendly approach",
        "3": "lots of Wordmons (Sparky, Flamepup, Bubblefin, Drakle) and Río all gathered around Spookle in a colorful birthday party scene with cake and balloons, party hats on everyone",
        "4": "Spookle smiling huge with happy tears, surrounded by all his new Wordmon friends, confetti falling, Río in the middle hugging Spookle, joyful",
    },
    "book_crunchstone_swim": {
        "refs": ["rio_trainer_idle.png", "crunchstone_1.png", "bubblefin_1.png"],
        "cover": "book cover: Crunchstone the gray rock Wordmon standing nervously at the edge of a sparkling blue pond, Río next to him pointing toward the water encouragingly, Bubblefin in the water waving, sunny day",
        "1": "Crunchstone the gray rock Wordmon sitting on dry grass watching other Wordmons happily splashing in a pond, looking shy and uncertain",
        "2": "Río gently holding Crunchstone's hand at the edge of the pond, Crunchstone looking scared with big worried eyes, Bubblefin in the water encouraging from below",
        "3": "Crunchstone closing his eyes and jumping with all his might into the pond, water splashing up dramatically, action shot",
        "4": "Crunchstone happily floating in the pond with a huge smile, Bubblefin swimming next to him, Río cheering from the shore, sunshine and sparkles on water",
    },
    "book_leafwhisk_garden": {
        "refs": ["rio_trainer_idle.png", "leafwhisk_1.png"],
        "cover": "book cover: Leafwhisk the green plant Wordmon and Río holding watering cans together in a beautiful garden full of colorful flowers, butterflies fluttering, sunny day",
        "1": "an empty patch of brown soil in a backyard, Leafwhisk the green plant Wordmon holding four tiny seeds in her hands looking hopeful, Río beside her with a small shovel",
        "2": "close-up of small green sprouts just popping out of the dirt, Río and Leafwhisk crouching down looking at them excitedly with watering cans",
        "3": "the garden is now full of colorful pink, yellow, and red flowers everywhere, Leafwhisk happily dancing among them, Río smiling, butterflies and bees flying around",
        "4": "Río's family (mom, dad, little sister) all in the garden picking flowers together, Leafwhisk in the middle proudly showing off her garden, warm afternoon light",
    },
    "book_buzzlet_honey": {
        "refs": ["rio_trainer_idle.png", "buzzlet_1.png"],
        "cover": "book cover: Buzzlet the small yellow bee Wordmon flying alongside Río who carries a glowing jar of golden honey, dark cave entrance with sparkles in background, adventure mood",
        "1": "Buzzlet the yellow bee Wordmon looking sad and worried in a hive, the honey jars all empty, dust on the shelves, somber lighting",
        "2": "Buzzlet and Río standing at the entrance of a dark mossy cave, both holding small flashlights, looking determined to find the honey",
        "3": "inside the cave, Río and Buzzlet discovering a hidden pile of glowing golden honeycombs nestled in a magical underground chamber, eyes wide with wonder",
        "4": "Buzzlet and her whole bee family hugging Río in the hive, all the honey jars now full and glowing, everyone smiling and celebrating",
    },
    "book_drakle_snow": {
        "refs": ["rio_trainer_idle.png", "drakle_1.png", "snowpuff_1.png"],
        "cover": "book cover: Drakle the baby green dragon and Río standing in deep snow with snowflakes falling, Drakle looking up at the sky with wonder, Snowpuff next to them, winter wonderland",
        "1": "Drakle the baby green dragon staring out a frosty bedroom window in awe at snow falling outside for the first time, big curious eyes",
        "2": "Drakle stepping cautiously onto fresh snow with one tiny foot, surprised expression at the cold sensation, Río laughing kindly behind him",
        "3": "Drakle, Río, and Snowpuff playing in the snow together, building a snowman, snowballs flying, joyful action scene with snow flakes everywhere",
        "4": "Drakle, Río, and a whole family of dragons (mom and dad dragon) sliding down a snowy hill on a wooden sled, all laughing, blue sky",
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
        print(book_id, "with refs:", cfg["refs"])
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
