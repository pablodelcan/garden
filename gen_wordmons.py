#!/usr/bin/env python3
"""Generate Wordmon sprites with Gemini 2.5 Flash Image (Nano Banana).

Reads the API key from .api_key and writes sprites/{id}_{1,2,3}.png
for each new Wordmon.
"""
import base64
import pathlib
import sys
import warnings
warnings.filterwarnings("ignore")

from google import genai
from google.genai import types

ROOT = pathlib.Path(__file__).parent
API_KEY = (ROOT / ".api_key").read_text().strip()
SPRITES = ROOT / "sprites"

client = genai.Client(api_key=API_KEY)

STYLE = (
    "chunky 16-bit pixel-art sprite, cute Pokémon-style monster, "
    "transparent background, centered, full body facing forward, "
    "soft outline, vibrant saturated colors, crisp pixels, "
    "square 1:1 aspect, simple clean design suitable for a kids' game"
)

WORDMONS = {
    "snowpuff": [
        "a tiny round white snowball creature with big sparkling eyes, two small twig arms, a happy smile, tiny icy crystal antenna on top, pale cyan blush",
        "a fluffy snow cub with soft white fur and icy blue paws, big eyes, small ice crystal horns on forehead, light blue frost patterns on body, standing on hind legs",
        "a majestic ice beast with thick snowy white fur, large icicle fangs, glowing cyan eyes, a jagged crown of ice shards, huge clawed paws, aura of frost around body",
    ],
    "buzzlet": [
        "a tiny round yellow bee creature with oversized translucent wings, huge cute eyes, small black stripes, two tiny antennae, friendly smile",
        "a medium yellow and black striped bee monster with sharp stinger, two pairs of shimmering wings, determined expression, small spike on head",
        "a regal queen bee monster with golden honey crown, four large iridescent wings, glowing amber eyes, black and gold armored body, long elegant stinger",
    ],
    "drakle": [
        "a tiny emerald green baby dragon with oversized head, big round eyes, tiny stubby wings, small tail, a single tiny puff of smoke from nostril, chubby and cute",
        "a medium green dragon with sleek scales, spread leather wings, sharp little claws, two small horns, smoke curling from jaws, confident stance",
        "a mighty ancient emerald dragon with huge spread wings, long spiked tail, glowing green eyes, crown of horns, armored scales, flames flickering from mouth",
    ],
    "shadopup": [
        "a tiny shadowy black puppy with glowing golden yellow eyes, wispy dark mist trailing off its body, floppy pointed ears, cute friendly smile",
        "a medium black wolf-like creature made of swirling shadows, glowing amber eyes, sharp ears, spectral mist flowing from body, alert pose",
        "a massive dark beast made of living shadow and starlight, glowing yellow eyes full of tiny stars, long spectral mane, mist swirling around, powerful stance",
    ],
    "boltbit": [
        "a tiny boxy silver robot with a small round head, cyan LED eyes, a tiny red antenna with bulb, short metal arms and legs, adorable",
        "a medium mecha warrior with armored silver plates, glowing cyan visor eyes, shoulder pads, red chest light, sturdy metallic legs, heroic pose",
        "a huge chrome battle mech with massive armor, piercing cyan optic eyes, glowing red core, rocket boosters on shoulders, powerful titan-class pose",
    ],
    "turboroar": [
        "a tiny cute race car monster with big googly eyes on the windshield, chunky rubber wheels, orange paint, a small spoiler, friendly smile",
        "a sleek orange and red race car creature with flame decals, aggressive headlight eyes, big rear spoiler, exhaust flames, dynamic pose",
        "a futuristic gold and orange hypercar monster with jet engines, glowing blue headlight eyes, massive tires, huge rear wing, flame trail behind",
    ],
    # ===== 20 NEW WORDMONS =====
    "sproutkin": [
        "a tiny round green seedling creature with two baby leaves on its head, big happy eyes, tiny arms, pale green skin, cute",
        "a small grass monster with a glowing pink flower blooming on its head, green skin with petal patterns, leaf hands, wide smile",
        "a majestic forest guardian covered in vines and flowers, glowing green eyes, crown of golden petals, tall regal pose, butterflies around it",
    ],
    "pebblet": [
        "a tiny round gray rock creature with big round eyes, tiny rock feet, small smile, a little patch of moss on top, chunky pixel style",
        "a boulder monster with thick stone body, patches of green moss on back, small sturdy arms, determined eyes, grounded pose",
        "a giant mountain guardian titan made of stone with crystal spikes on back, glowing yellow eyes, massive stone fists, moss and small flowers growing on shoulders",
    ],
    "chirpy": [
        "a tiny round fluffy yellow bird chick with huge eyes, orange beak, tiny wings sticking out, cute and adorable",
        "a medium yellow bird with spread feathered wings, blue highlights on wings, sharp determined eyes, standing proudly",
        "a majestic phoenix-like raptor with golden feathers, huge spread wings glowing with fire, fierce red eyes, crown of feathers, regal stance",
    ],
    "munchy": [
        "a chubby round orange blob monster with a huge mouth full of tiny teeth, tiny hands, googly eyes, always looking hungry, cute",
        "a bigger orange monster with massive teeth, drool, two clawed hands, excited eyes, ready to chomp, round body",
        "a gigantic orange and red food king monster with golden spiked crown, massive tooth-filled mouth, two big clawed arms, throne-like pose",
    ],
    "fluffle": [
        "a tiny round pink fluffball creature with soft white cheeks, two tiny bunny-like ears, sparkly black eyes, super soft cotton candy fur",
        "a fluffy pink bunny-cloud creature with long bunny ears, rosy cheeks, fluffy tail, kind eyes, standing on two feet",
        "a majestic pink cloud queen with golden tiara, fluffy bunny ears with ribbons, long flowing fur, rainbow trail behind her, pastel pink and white",
    ],
    "zappit": [
        "a tiny yellow lightning bolt creature with cute eyes, small zigzag body, tiny arms and legs, sparks around it, smiling",
        "a bigger electric creature shaped like a lightning bolt with thunder-cloud belly, angry eyes, sparking tail, dynamic zigzag pose",
        "a towering electric thunder titan with massive lightning body, glowing red eyes, crackling electricity around it, two huge bolt arms, lightning storm background feel",
    ],
    "blubber": [
        "a tiny cute light blue baby whale creature with tiny fins, big sparkling eyes, little water spout on top, chubby round body",
        "a medium blue whale monster with spread fins, cute tail, spouting a rainbow of water from blowhole, adventurous eyes",
        "a massive dark blue ocean god whale with coral crown, bioluminescent markings, glowing white eyes, huge fins, regal underwater king pose",
    ],
    "mudkin": [
        "a tiny brown round muddy creature with big innocent eyes, mud dripping off its body, tiny legs, dirty paws, cute baby style",
        "a medium sized muddy monster with thick arms, moss and rocks stuck in fur, determined eyes, stance like a digger",
        "a giant earth titan made of packed earth and stone fists, glowing amber eyes, huge crystal shards on shoulders, powerful stance, ground cracking under feet",
    ],
    "pyrofly": [
        "a tiny red ladybug creature with glowing ember belly, small fire wings, tiny antennae, cute black eyes with reflection",
        "a bigger flaming bug with larger yellow and red wings, flame trails coming off wings, orange body, fiery eyes, dynamic pose",
        "a colossal fire moth with four massive spread wings of flame, glowing amber eyes, molten red and gold body, embers swirling around it",
    ],
    "glimmer": [
        "a tiny glowing yellow sphere creature with cute eyes, soft radiant aura, sparkles around it, magical little being",
        "a star-shaped yellow creature with cute face in middle of star, glowing points, little sparkles, confident smile",
        "a radiant rainbow light goddess being with golden star-shaped body, long iridescent wings, glowing face, crown of tiny stars, rainbow aura",
    ],
    "bramblepup": [
        "a tiny green puppy creature made of grass and leaves, big floppy leaf ears, cute nose, wagging leaf tail, adorable",
        "a medium wolf pup with moss-green fur and thorny spikes on back, leaf ears, sharp eyes, protective stance",
        "a huge noble forest wolf with deep emerald fur, massive thorny mane of leaves and flowers, glowing yellow eyes, majestic predator pose",
    ],
    "squibble": [
        "a tiny purple baby octopus creature with four wiggly tentacles, big cute eyes, tiny mouth, soft round head, bubbly",
        "a bigger purple octopus with six tentacles, sharper eyes, ink dripping from one tentacle, dynamic swirling pose",
        "a massive regal kraken queen with golden crown, eight enormous tentacles, glowing amber eyes, bioluminescent spots, dark purple and gold",
    ],
    "moonmoth": [
        "a tiny indigo moth creature with two star-patterned wings, big sparkly eyes, tiny fluffy body, floating serenely",
        "a medium purple moth with four wings covered in constellations, glowing yellow spots, dreamy eyes, magical atmosphere",
        "a cosmic celestial moth with massive galaxy-patterned wings, glowing purple body, nebulas within wings, crown of stars, ethereal majestic pose",
    ],
    "pizzarone": [
        "a cute triangular slice of pizza character with pepperoni eyes, melted cheese smile, tiny stick arms and legs, running",
        "a bigger pizza slice monster with multiple pepperoni on body, mozzarella arms, little teeth, cheeky grin, two-footed stance",
        "a giant whole pizza king with golden crown of pepperoni, full circular body with toppings, kingly arms of breadsticks, regal pose on throne",
    ],
    "shadowkit": [
        "a tiny round black kitten with huge glowing yellow eyes, tiny pointy ears, fluffy fur, adorable shadowy aura",
        "a medium sleek black panther cub with yellow eyes, pointed ears, shadow mist around body, alert stance",
        "a massive black shadow panther with glowing yellow eyes like suns, smoky mist trailing behind, sharp white fangs, regal and intimidating pose",
    ],
    "crunchbite": [
        "a tiny orange baby T-Rex with big teeth, huge head, tiny arms, cute eyes, chubby baby dinosaur with round belly",
        "a medium orange dinosaur with sharp teeth, clawed feet, tiny arms, spiky head crest, roaring pose",
        "a mighty volcanic T-Rex with glowing cracks, massive fangs, spiked back, fiery yellow eyes, huge clawed feet, dominant roar pose",
    ],
    "frostfin": [
        "a tiny light blue fish creature with snowflake-patterned fins, big kawaii eyes, tiny tail, shimmering ice scales",
        "a medium elegant fish with long flowing ice fins, sharp fin spikes, crystal scales, wise calm eyes",
        "a regal ice queen fish with a crystal crown, long ornate fins with snowflake patterns, shimmering white and cyan body, aura of frost around her",
    ],
    "sparklebub": [
        "a tiny yellow fairy bug creature with pink translucent wings, little sparkles coming off, adorable antennae, tiny pink legs",
        "a medium butterfly-like creature with pink and yellow electric wings, star-patterned body, sparks flying from wingtips, dynamic pose",
        "a celestial star-bug queen shaped like a giant five-pointed star with fairy wings, glowing center face, electric sparkles all around, pink and gold",
    ],
    "doodledoo": [
        "a tiny chubby baby chicken with small red comb, big silly eyes, tiny yellow beak, orange fluffy body, cute clueless expression",
        "a medium fluffy rooster with colorful feathers, bigger red comb, dopey smile, googly eyes, silly stance",
        "a majestic rainbow-tailed rooster king with huge red crown comb, rainbow feathered tail, golden feathers, regal but still slightly silly expression",
    ],
}


def generate(prompt: str, out: pathlib.Path) -> None:
    full = f"{STYLE}. Subject: {prompt}."
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
    only = set(sys.argv[1:])
    for mon, prompts in WORDMONS.items():
        if only and mon not in only:
            continue
        print(mon)
        for i, p in enumerate(prompts, 1):
            out = SPRITES / f"{mon}_{i}.png"
            if out.exists():
                print(f"  ✓ {out.name} exists, skipping")
                continue
            generate(p, out)


if __name__ == "__main__":
    main()
