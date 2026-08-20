#!/usr/bin/env python3
"""Generate sprites for the 8 new 2nd-grade Wordmons (Aug 2026 batch).
Includes the white->alpha flood-fill post-processing this time."""
import base64, pathlib, warnings
warnings.filterwarnings("ignore")
from google import genai
from PIL import Image
import numpy as np
from collections import deque

ROOT = pathlib.Path(__file__).parent
client = genai.Client(api_key=(ROOT / ".api_key").read_text().strip())
SPRITES = ROOT / "sprites"

STYLE = (
    "AUTHENTIC POKEMON GAME BOY ADVANCE creature sprite, front-facing, "
    "isolated on a PLAIN PURE WHITE background, Pokemon FireRed/Emerald "
    "creature-design style, true 16-bit pixel art aesthetic, chunky visible "
    "pixels, NO anti-aliasing, limited Nintendo palette, creature centered, "
    "bouncy expressive pose, big cool Pokemon-style eyes, looking at viewer, "
    "kid-friendly but slightly fierce design for an 8 year old, "
    "no background scenery, no platform, no shadow"
)

MONS = {
    "drakelet":  ["Drakelet — a small green baby dragon with tiny wings and one puff of smoke from its nose",
                  "Wyvernix — a medium green dragon with proper spread wings and amber chest scales",
                  "Dracolord — a mighty emerald dragon with huge wings, golden horns and a small flame crown"],
    "shadowpaw": ["Shadowpaw — a small dark-blue ninja cat with a red headband mask and one paw raised",
                  "Ninjaclaw — a sleek dark ninja cat with twin silver claw blades and a flowing red scarf",
                  "Phantomstrike — a large shadow ninja panther mid-strike with smoke wisps and glowing red eyes"],
    "gearbot":   ["Gearbot — a cute small boxy robot with one big round blue eye and visible gears on its chest",
                  "Mechatron — a medium humanoid robot with twin blue eyes, piston arms and a chest gear turning",
                  "Titancore — a huge armored mech robot with a glowing orange core and massive shoulder plates"],
    "finfang":   ["Finfang — a small cheeky blue shark pup with a big grin and one shiny tooth",
                  "Jawtide — a medium blue shark with a scarred fin and rows of white teeth, riding a wave",
                  "Megajaw — a massive dark blue shark with a huge open jaw, glowing eyes and battle scars"],
    "rexling":   ["Rexling — a tiny lime-green T-rex hatchling with big eyes and tiny arms",
                  "Raptorix — a fast lean green raptor with a striped tail and sharp claws mid-run",
                  "Tyrannoking — a giant green T-rex with a golden crown, roaring with tiny arms flexed"],
    "emberhawk": ["Emberhawk — a small orange hawk chick with flame-tipped wing feathers",
                  "Flarewing — a medium fiery hawk with blazing spread wings and ember trail",
                  "Solarphoenix — a majestic phoenix with sun-gold and crimson flame wings and a radiant tail"],
    "knightpup": ["Knightpup — a golden puppy wearing a tiny silver knight helmet with the visor up",
                  "Squirehound — a sturdy golden dog in chest armor holding a small blue shield",
                  "Paladinwolf — a noble armored wolf with a glowing sword strapped on and a royal blue cape"],
    "viperling": ["Viperling — a small emerald snake with big friendly eyes and a curled tail",
                  "Cobracoil — a medium emerald cobra with flared hood and diamond pattern",
                  "Basilisk — a great emerald serpent king with a golden crest and hypnotic purple eyes"],
}


def white_to_alpha(path):
    img = Image.open(path).convert("RGBA")
    arr = np.array(img)
    r, g, b = arr[..., 0].astype(int), arr[..., 1].astype(int), arr[..., 2].astype(int)
    nearwhite = (r >= 215) & (g >= 215) & (b >= 215)
    H, W = nearwhite.shape
    visited = np.zeros_like(nearwhite, dtype=bool)
    q = deque()
    for x in range(W):
        if nearwhite[0, x]: q.append((0, x))
        if nearwhite[H-1, x]: q.append((H-1, x))
    for y in range(H):
        if nearwhite[y, 0]: q.append((y, 0))
        if nearwhite[y, W-1]: q.append((y, W-1))
    while q:
        y, x = q.popleft()
        if visited[y, x] or not nearwhite[y, x]:
            continue
        visited[y, x] = True
        if y > 0: q.append((y-1, x))
        if y < H-1: q.append((y+1, x))
        if x > 0: q.append((y, x-1))
        if x < W-1: q.append((y, x+1))
    arr[visited, 3] = 0
    Image.fromarray(arr).save(path)


def gen(prompt, out):
    print("  ->", out.name, flush=True)
    resp = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=STYLE + ". Subject: " + prompt + ".",
    )
    for p in resp.candidates[0].content.parts:
        if getattr(p, "inline_data", None) and p.inline_data.data:
            d = p.inline_data.data
            if isinstance(d, str):
                d = base64.b64decode(d)
            out.write_bytes(d)
            white_to_alpha(out)
            return True
    return False


def main():
    for mid, stages in MONS.items():
        print(mid, flush=True)
        for i, prompt in enumerate(stages):
            out = SPRITES / f"{mid}_{i+1}.png"
            if out.exists():
                print("  skip", out.name)
                continue
            try:
                gen(prompt, out)
            except Exception as e:
                print("  !!", out.name, e)
    print("done")


if __name__ == "__main__":
    main()
