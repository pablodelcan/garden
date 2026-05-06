#!/usr/bin/env python3
"""Generate 4 new illustrated books for Río — harder/longer stories."""
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
    "attached reference sprites precisely. Keep Río's curly brown hair, "
    "green hoodie with red stripe, and red sneakers consistent. Keep "
    "each Wordmon's exact body shape, colors, tail, and facial features "
    "identical to its reference. Full scene illustration in chunky 16-"
    "bit pixel-art style, 1:1 square aspect, vibrant saturated colors, "
    "crisp pixels, detailed pixel environment"
)

BOOKS = {
    "book_pikachu_ketchup": {
        "refs": ["rio_trainer_idle.png"],
        "cover": "book cover: a cute yellow Pokemon-style Pikachu with red cheeks holding a giant red ketchup bottle, Río standing next to him laughing, bright sunny park, title area blank top",
        "1": "a cute yellow Pikachu with red cheeks looking sad and panicked, his ketchup bottle is missing from the kitchen counter, lots of empty plates around",
        "2": "Río and Pikachu searching together: looking under the bed, behind the couch, inside a closet, with confused faces, comedy detective vibe",
        "3": "Río and Pikachu in the backyard, splitting open a giant green watermelon and seeing the red ketchup bottle hidden inside, surprised expressions",
        "4": "Pikachu hugging his ketchup bottle with cheeks glowing red with happiness, Río laughing, both sitting on the grass eating sandwiches with ketchup",
    },
    "book_missing_cake": {
        "refs": ["rio_trainer_idle.png"],
        "cover": "book cover: Río wearing a tiny detective hat and holding a magnifying glass, looking at the camera, cake crumbs and footprints around an empty cake plate, mystery vibe, title area blank",
        "1": "a kitchen with a beautiful frosted birthday cake on the counter, sunlight streaming in, peaceful before the chaos",
        "2": "Río wearing a small detective hat with a magnifying glass, kneeling next to an empty cake plate with crumbs scattered, his Mom in the background looking shocked",
        "3": "Río pointing at three suspects lined up like a police lineup: a guilty-looking dog, a sneaky cat, and his confused brother, all standing in the kitchen",
        "4": "the cat in front, paws covered in pink frosting and a smug grin, Río pointing dramatically while everyone else looks surprised, mystery solved",
    },
    "book_drakle_school": {
        "refs": ["rio_trainer_idle.png", "drakle_1.png"],
        "cover": "book cover: baby Drakle the green dragon wearing a tiny backpack, Río waving goodbye, a school building full of dragon kids in the background, sunny morning, title area blank",
        "1": "Drakle the baby green dragon at home wearing a tiny red backpack and clutching a lunchbox, looking nervous on his first day of school, Río giving him an encouraging thumbs up",
        "2": "Drakle standing alone at the entrance to a colorful pixelated school building shaped like a castle, other dragon kids running past him, looking shy",
        "3": "inside a classroom with cube-style desks, Drakle sitting next to a friendly red dragon kid sharing crayons, both smiling, blackboard behind them",
        "4": "Drakle and three new dragon friends laughing together at a cafeteria lunch table, sharing snacks and stickers, very happy bright scene",
    },
    "book_sparky_race": {
        "refs": ["rio_trainer_idle.png", "sparky_1.png", "flamepup_1.png"],
        "cover": "book cover: Sparky the yellow Pokemon-style Wordmon with lightning tail at a starting line, ready to race, Flamepup beside him, Río holding a checkered flag, title area blank",
        "1": "a big race track in a sunny field, a starting line with Sparky, Flamepup, and other small Wordmons stretching and warming up, banners and flags",
        "2": "the race begins! all Wordmons sprinting forward, Sparky in front leaving a trail of electric sparks, Flamepup right behind with flame trails, motion lines",
        "3": "near the finish, Sparky tripping on a banana peel and tumbling, Flamepup zooming past, Río in the crowd looking shocked but cheering",
        "4": "Sparky getting up dirty but smiling, Flamepup at the finish line wearing a gold medal, both hugging in friendship, Río holding two trophies, sportsmanship",
    },
}


def load_ref(name):
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
