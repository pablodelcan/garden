#!/usr/bin/env python3
"""Generate the bedroom art + illustrated storybook pages."""
import base64, pathlib, sys, warnings
warnings.filterwarnings("ignore")

from google import genai

ROOT = pathlib.Path(__file__).parent
API_KEY = (ROOT / ".api_key").read_text().strip()
SPRITES = ROOT / "sprites"

client = genai.Client(api_key=API_KEY)

# ------ Bedroom ------
BEDROOM_STYLE = (
    "cozy kid's bedroom scene, cinematic top-down-ish three-quarter view, "
    "bright colorful vector-painted game art like Pokemon Unite, "
    "warm inviting colors, 1:1 aspect, detailed furniture, "
    "empty spaces on bed/couch/shelf/rug for small cute creatures to sit in"
)
BEDROOM_PROMPT = (
    "a 7-year-old boy's dream bedroom with a blue twin bed on left, "
    "an orange and yellow couch in center, tall white bookshelf on right "
    "full of books, a big round striped rug on floor, window with blue "
    "sky, toys scattered around, magical warm lighting, Pokemon posters "
    "on wall, a skylight showing stars"
)

# ------ Illustrated storybook pages ------
# Each book has 1 cover + 4 page scenes. All pixel-art / kid book illustration style.
BOOK_STYLE = (
    "bright colorful children's book illustration, kawaii cute style, "
    "1:1 aspect square, vector-painted with soft shading, cinematic "
    "composition, 1st grade reading book cover or page scene, "
    "friendly characters with big expressive eyes, vibrant saturated colors"
)

BOOKS = {
    "book_rio_dragon": {
        "cover": "storybook cover showing a brown-haired 7-year-old boy in a red shirt named Rio kneeling and smiling at a tiny bright green baby dragon in his hands, magical sparkles, title area left blank at top",
        "1": "a brown-haired boy in a red shirt named Rio in a sunny green park kneeling down, a tiny emerald baby dragon no bigger than his hand sitting in grass looking up at him cutely",
        "2": "close-up of the tiny green baby dragon with big eyes looking up at Rio with a sad face, a little speech bubble shape, park grass background",
        "3": "Rio and the tiny dragon walking up a grassy hill together, a small stream with a wooden bridge, bright blue sky with clouds, the dragon puffing a tiny cloud of smoke",
        "4": "top of a grassy hill at sunset, a huge friendly green mother dragon hugging Rio and the tiny baby dragon, warm golden light, magical happy ending scene",
    },
    "book_dog_cake": {
        "cover": "storybook cover showing a fluffy brown-and-white puppy named Bubble with frosting on his face next to a giant red birthday cake with sprinkles, boy Rio laughing in background, title area left blank",
        "1": "a warm kitchen scene with a huge three-tier red frosted cake with rainbow sprinkles on a wooden table, Mom icing the top, sunlight through window, cozy",
        "2": "a fluffy brown-and-white puppy named Bubble staring up at the red cake with wide eyes and his tail blurred from wagging super fast, tongue sticking out",
        "3": "chaotic funny scene of Bubble the dog jumping up onto the table with frosting smeared on his face, pieces of red cake flying everywhere, crumbs on floor",
        "4": "Rio a brown-haired 7-year-old boy laughing his head off, Mom with hands on hips smiling, Bubble the puppy sitting with a guilty grin and frosting on his nose, a new smaller cake on a high shelf",
    },
    "book_space_picnic": {
        "cover": "storybook cover showing a brown-haired boy Rio and his fluffy brown puppy Bubble inside a cardboard rocket ship flying through a star-filled sky, planets in background, title area blank",
        "1": "a sunny backyard with a tall cardboard rocket ship painted with stars and moons, a 7-year-old brown-haired boy in red shirt named Rio and his fluffy brown puppy Bubble holding a picnic basket",
        "2": "interior of outer space with colorful planets, shooting stars, a cardboard rocket zooming past the moon, the puppy Bubble barking at a shooting star through the window",
        "3": "a fantastical pink planet surface with cotton-candy-colored clouds, Rio and Bubble sitting on a blanket eating sandwiches, purple and pink sky, stars visible even in daytime",
        "4": "Rio happily hugging Mom in the backyard at sunset, the rocket ship behind them, Bubble wagging his tail, warm fuzzy family scene, Mom laughing",
    },
    "book_ghost_friend": {
        "cover": "storybook cover showing a brown-haired boy Rio smiling at a small cute blue translucent ghost floating out of a closet at night, soft moonlight, friendly not scary, title area blank",
        "1": "a kid's bedroom at night with a scared 7-year-old brown-haired boy Rio hiding under a blue blanket on his bed, moonlight through window, a slightly open closet door with shadows inside, cozy kids room",
        "2": "the closet door slowly opening on its own with a tiny soft glow inside, Rio peeking over his blanket looking curious but nervous, gentle blue light spilling out",
        "3": "a small cute translucent blue ghost with big friendly eyes floating out of the closet, smiling sweetly, Rio smiling back with his blanket pulled down, surprised but happy",
        "4": "Rio and the blue ghost sitting on his bed together reading a book with a flashlight, both smiling, stars on the bedroom ceiling, a warm glow, friendship vibes",
    },
}


def generate(prompt: str, out: pathlib.Path, style: str) -> None:
    full = f"{style}. Subject: {prompt}."
    print(f"  → {out.name}")
    resp = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=full,
    )
    for part in resp.candidates[0].content.parts:
        if getattr(part, "inline_data", None) and part.inline_data.data:
            data = part.inline_data.data
            if isinstance(data, str):
                data = base64.b64decode(data)
            out.write_bytes(data)
            return
    raise RuntimeError(f"no image returned for {out.name}")


def main() -> None:
    # Bedroom
    print("bedroom")
    out = SPRITES / "house_empty.png"
    backup = SPRITES / "house_empty_old.png"
    if out.exists() and not backup.exists():
        out.rename(backup)
    generate(BEDROOM_PROMPT, out, BEDROOM_STYLE)

    # Books
    for book_id, pages in BOOKS.items():
        print(book_id)
        for key, prompt in pages.items():
            suffix = "_cover" if key == "cover" else f"_{key}"
            out = SPRITES / f"{book_id}{suffix}.png"
            if out.exists():
                print(f"  ✓ {out.name} exists, skipping")
                continue
            generate(prompt, out, BOOK_STYLE)


if __name__ == "__main__":
    main()
