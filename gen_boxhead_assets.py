#!/usr/bin/env python3
"""Generate diorama-style assets for the Boxhead game using Nano Banana.

Writes PNGs to ./boxhead_assets/. Re-running skips files that already exist
unless FORCE=1 is set.
"""
import base64
import os
import pathlib
import sys
import warnings
warnings.filterwarnings("ignore")

from google import genai

ROOT = pathlib.Path(__file__).parent
API_KEY = (ROOT / ".api_key").read_text().strip()
OUT = ROOT / "boxhead_assets"
OUT.mkdir(exist_ok=True)

client = genai.Client(api_key=API_KEY)

STYLE = (
    "wide horizontal landscape illustration"
)

BG_STYLE = (
    "low-fidelity dithered illustration with a retro-futurist mood, "
    "layered cardstock-style shapes against atmospheric sky gradients, "
    "limited palette of about 6 colors, visible Floyd-Steinberg dithering "
    "in the gradients, slight CRT scanline feel, evocative and quiet, "
    "like a screenshot from Hyper Light Drifter or Sword & Sworcery or a "
    "PS1-era adventure game, no text, no watermark, no people, no detailed "
    "architecture, simple silhouettes plus a few small evocative details"
)

LOCATIONS = {
    "tokyo": {
        "bg": (
            "Tokyo at dusk: layered silhouette buildings receding in three "
            "depths with a few warm glowing rectangle windows scattered "
            "across them, a single soft moon disc, one or two paper-lantern "
            "round shapes hanging high, dusk gradient sky from deep indigo "
            "at top through magenta to peach at the horizon, dithered "
            "pixel transitions between sky bands, evocative and quiet, "
            "empty bottom third"
        ),
        "ground": (
            "an even seamless dark plum-violet pixel-art texture, slight "
            "noise, like dusk-lit asphalt at low resolution, fills the "
            "entire image edge to edge with no features, no shapes, no "
            "lines, no objects, no border, just an even noisy color field"
        ),
        "grass": (
            "an even seamless deep-plum pixel-art texture with a few "
            "scattered neon-pink and amber dither dots, slight noise, "
            "fills the entire image edge to edge with no shapes, no border"
        ),
    },
    "sahara": {
        "bg": (
            "Saharan dunes at golden hour: three layered dune silhouettes "
            "in warm tan, apricot, and rust receding into the distance, a "
            "single small circular sun low on the horizon, a small palm "
            "silhouette tucked in mid-distance, dusk gradient sky from "
            "peach at top through cream to soft yellow at the horizon, "
            "dithered pixel transitions in the gradients, calm and "
            "evocative, empty foreground"
        ),
        "ground": (
            "an even seamless warm tan pixel-art sand texture, slight "
            "noise dither, fills the entire image edge to edge with no "
            "shapes, no ripples, no objects, no border, just an even color "
            "field"
        ),
        "grass": (
            "an even seamless slightly-darker apricot pixel-art sand crust "
            "texture, slight dither dots, fills the entire image edge to "
            "edge with no shapes, no border"
        ),
    },
    "patagonia": {
        "bg": (
            "Patagonian steppe: three layers of jagged snow-capped mountain "
            "silhouettes in slate-blue, teal, and pale gray receding into "
            "haze, a hint of teal glacial water in the mid-distance, "
            "overcast pearl sky with gradient from cool gray-blue at top "
            "through pale lilac to cream at the horizon, dithered pixel "
            "transitions in the sky, cool atmospheric mood, empty foreground"
        ),
        "ground": (
            "an even seamless cool slate-gray pixel-art rocky-soil "
            "texture, slight dither noise, fills the entire image edge to "
            "edge with no shapes, no rocks, no border, just an even color "
            "field"
        ),
        "grass": (
            "an even seamless muted olive pixel-art texture with a few "
            "scattered cream and amber dither dots, fills the entire image "
            "edge to edge with no shapes, no border"
        ),
    },
    "marrakech": {
        "bg": (
            "Marrakech medina at dusk: layered terracotta clay rooftops "
            "with a few simple silhouettes of minarets and arched windows "
            "receding into haze, a few small lantern-orange rectangles "
            "glowing in distant walls, sky as gradient from deep lavender "
            "at top through warm amber to peach at the horizon, dithered "
            "pixel transitions in the sky, evocative and quiet, empty "
            "foreground"
        ),
        "ground": "",  # procedural
        "grass":  "",  # procedural
    },
    "iceland": {
        "bg": (
            "Iceland volcanic landscape at dusk: layered black volcanic "
            "mountain silhouettes with one small glowing orange lava "
            "crack high in the distance, a faint plume of pale steam, "
            "sky as gradient from deep teal at top through indigo to a "
            "wash of dim aurora green at the horizon, dithered pixel "
            "transitions, atmospheric and cold, empty foreground"
        ),
        "ground": "",
        "grass":  "",
    },
    "metro": {
        "bg": (
            "underground metro tunnel: layered rectangular concrete "
            "columns and tiled wall silhouettes receding into a dark "
            "tunnel, a few warm yellow rectangle lights glowing on "
            "distant ceiling, a faint train-headlight glow far in the "
            "tunnel mouth, palette of slate, dim teal, and warm amber, "
            "dithered pixel gradients, empty foreground"
        ),
        "ground": "",
        "grass":  "",
    },
    "amazon": {
        "bg": (
            "Amazon rainforest at dawn: three layers of jungle tree "
            "silhouettes in deep emerald, teal, and misty sage receding "
            "into fog, a few simple round canopy shapes, a single hanging "
            "vine silhouette, dawn sky as gradient from misty pale green "
            "at top through cream to peach at the horizon, dithered pixel "
            "transitions in the sky, atmospheric and quiet, empty foreground"
        ),
        "ground": (
            "an even seamless deep umber-brown pixel-art soil texture, "
            "slight dither noise, fills the entire image edge to edge "
            "with no shapes, no leaves, no twigs, no border, just an even "
            "color field"
        ),
        "grass": (
            "an even seamless rich emerald pixel-art texture with a few "
            "scattered teal dither dots, fills the entire image edge to "
            "edge with no shapes, no border"
        ),
    },
}

ASSETS = {

    # Character (idle) — SIDE PROFILE facing right, isolated on pure white.
    # Outfit: kraft box head with gray dots + rectangle mouth, fitted black
    # V-neck tee, dark charcoal slim pants, salmon-pink shoes, bare arms.
    "boxhead_idle": (
        "product render of a stylized 3D character in a strict SIDE-VIEW "
        "PROFILE (the character is facing right, body in pure profile so we "
        "see the side of the cardboard box head, the side of one shoulder, "
        "and both legs in profile lined up): athletic lean human body with "
        "bare arms, wearing a fitted black short-sleeve T-shirt, dark "
        "charcoal slim-fit jeans, and bright salmon-pink ankle shoes. The "
        "head is a kraft-brown corrugated-cardboard box; from this side "
        "view we see ONE round dark-gray dot eye and a small horizontal "
        "rectangular gray mouth on the visible side panel, plus a strip of "
        "masking tape across the top. Pose: STANDING STILL, both feet "
        "together planted side by side, arms relaxed straight down at "
        "sides. Full body visible from feet to head, centered with even "
        "padding. Isolated against a PURE WHITE seamless studio "
        "background, no shadow, no scenery, no other objects. CRITICAL: "
        "side profile, NOT facing the camera, NOT three-quarter — pure "
        "side view"
    ),
    # Character walking — SIDE PROFILE facing right, mid-stride
    "boxhead_walk_a": (
        "product render of the SAME stylized 3D character in strict "
        "SIDE-VIEW PROFILE (facing right, body in pure profile): athletic "
        "lean human body with bare arms, kraft-brown cardboard box head "
        "with one round gray dot eye and a rectangular gray mouth visible "
        "on the side, fitted black T-shirt, dark charcoal slim jeans, "
        "salmon-pink ankle shoes. Pose: WALKING right, mid-stride, with "
        "the FRONT foot lifted forward off the ground (knee bent), back "
        "foot planted, arms swinging in opposition (front arm back, back "
        "arm forward). Full body visible centered. Isolated against a "
        "PURE WHITE seamless studio background, no shadow, no scenery, no "
        "other objects. CRITICAL: side profile, facing right, NOT facing "
        "the camera"
    ),

    # Exit door prop — isolated on pure white
    "prop_exit_door": (
        "product photograph of a small handmade cardboard door prop "
        "standing upright on the ground: kraft-brown corrugated cardboard "
        "frame, the door slightly ajar with warm yellow light glowing from "
        "inside, a hand-cut paper sign stuck above the door that reads "
        "'OUT' in black marker (just the word OUT, nothing else), full "
        "object visible, isolated against a PURE WHITE seamless studio "
        "background, no shadow, no scenery, no other objects, like a clean "
        "ecommerce cutout"
    ),

    # Spawner hatch prop — isolated on pure white
    "prop_spawner": (
        "product photograph of a small handmade cardboard trapdoor hatch "
        "hanging from a piece of brown twine: kraft-brown corrugated "
        "cardboard cube with masking-tape hinges on one side, a hand-cut "
        "paper label stuck on the front that reads 'IN' in black marker "
        "(just the word IN, nothing else), the hatch open showing dark "
        "interior, isolated against a PURE WHITE seamless studio "
        "background, no shadow, no scenery, no other objects, like a clean "
        "ecommerce cutout"
    ),
}


def generate(key: str, prompt: str, subdir: str = "", style: str = STYLE) -> None:
    base = OUT / subdir if subdir else OUT
    base.mkdir(exist_ok=True, parents=True)
    out = base / f"{key}.png"
    if out.exists() and not os.environ.get("FORCE"):
        print(f"  skip (exists): {out.relative_to(OUT)}")
        return
    full = f"{style}. {prompt}."
    print(f"  → {out.relative_to(OUT)}")
    try:
        resp = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=full,
        )
    except Exception as e:
        print(f"    !! error: {e}")
        return
    cand = resp.candidates[0] if resp.candidates else None
    if not cand or not cand.content or not cand.content.parts:
        finish = getattr(cand, "finish_reason", "?") if cand else "?"
        print(f"    !! empty response (finish={finish})")
        return
    for part in cand.content.parts:
        if getattr(part, "inline_data", None) and part.inline_data.data:
            data = part.inline_data.data
            if isinstance(data, str):
                data = base64.b64decode(data)
            out.write_bytes(data)
            print(f"    wrote {len(data)} bytes")
            return
    print("    !! no image in response")


def main() -> None:
    only = sys.argv[1:]
    # Universal assets
    for key, prompt in ASSETS.items():
        if only and key not in only:
            continue
        generate(key, prompt)
    # Per-location assets
    for loc, prompts in LOCATIONS.items():
        for kind, prompt in prompts.items():
            if not prompt:
                continue
            full_key = f"{loc}_{kind}"
            if only and full_key not in only and loc not in only:
                continue
            style = BG_STYLE if kind == "bg" else STYLE
            generate(kind, prompt, subdir=loc, style=style)


if __name__ == "__main__":
    main()
