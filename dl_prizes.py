#!/usr/bin/env python3
"""Download REAL product photos for the WordQuest shop, square them onto
white, and save to sprites/prizes/<source>.jpg. A separate MAP (printed at
the end) tells which shop item id should point at which downloaded photo.

Sources are official/retailer CDNs that serve images directly:
  - images.mattel.net  (Mattel official Hot Wheels photos)
  - m.media-amazon.com/images/P/<ASIN>...  (Amazon by-ASIN image endpoint)
Both confirmed downloadable via curl/urllib (unlike the product PAGES,
which are bot-blocked).
"""
import sys, pathlib, urllib.request, ssl, io
from PIL import Image

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "sprites" / "prizes"
OUT.mkdir(parents=True, exist_ok=True)
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
HDRS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"}

M = "https://images.mattel.net/image/upload/w_646,f_auto,c_scale/shop-us-prod/files/"
MC = "https://images.mattel.net/image/upload/c_scale,w_600/creations-us-prod/files/"
def AZ(asin): return f"https://m.media-amazon.com/images/P/{asin}.01._SCLZZZZZZZ_.jpg"

# source-name -> URL
SOURCES = {
  # Hot Wheels — Mattel official
  "hw_multipack":   M + "twxdqskd9tm2a93pgyik.jpg",     # 10-car pack
  "hw_garage":      M + "ya5sfisiogld3z36obsn.jpg",     # City Ultimate Garage
  "hw_track_fuelcan": M + "xi5c0envm86lo6siinyt.jpg",   # Fuel Can stunt box (track parts)
  "hw_track_booster": M + "1049b887d309469f7da5d6139e173f8d554b4628.jpg",  # boosted jump
  "hw_marvel":      MC + "esh1pxg6j6q1mgnk1gms.jpg",    # Spider-Man character car 5-pack
  "hw_mariokart":   M + "fg0kdlzgssrjpf6piadi_a59b099c-4a43-4def-9130-850fb458de66.jpg",  # Mario Kart 4-pack
  # Amazon by-ASIN
  "hw_single":      AZ("B0DB417945"),  # premium single 1:64 car (true single)
  "hw_8pack":       AZ("B0CD86BG67"),  # 8 basic cars
  "hw_racecars":    AZ("B0CNJFV6KH"),  # 10 race cars (singles look)
  "hw_track_loop":  AZ("B07RMCGP21"),  # triple loop kit
  "hw_track_loopkick": AZ("B07XD6F53G"),  # loop kicker pack
  "hw_track_raceway": AZ("B08WKH1XDC"),   # roll-out raceway (big set)
  "hw_track_foldup": AZ("B07XB3JFYZ"),    # fold-up track pack
  "pokemon_figs":   AZ("B0B32365PH"),  # Paldea battle figure 4-pack (Fuecoco/Quaxly/Sprigatito/Pikachu)
  # Minecraft translucent green slime cube (the "jelly cube") — Mattel slime cube minifigure
  "mc_slime_cube":  "https://cdn11.bigcommerce.com/s-0kvv9/products/371827/images/569539/mincraft24slimecube__91137.1629933741.500.750.jpg?c=2",
}

# shop-item-id -> source-name
MAP = {
  # Pokemon
  "fuecoco_fig": "pokemon_figs", "fuecoco_cards": "pokemon_figs",
  "quaxly_fig": "pokemon_figs", "quaxly_cards": "pokemon_figs",
  "paldea_starters_3pack": "pokemon_figs",
  # Hot Wheels older sets
  "hw_10pack": "hw_multipack", "hw_loop": "hw_track_loop", "hw_garage": "hw_garage",
  "hw_monster": "hw_8pack", "hw_shark": "hw_track_raceway", "hw_mario": "hw_mariokart",
  "hw_launcher": "hw_track_loopkick", "hw_criss": "hw_track_raceway",
  "hw_volcano": "hw_track_raceway", "hw_spiral": "hw_track_loop",
  # Hot Wheels single cars
  "hw_car_redmuscle": "hw_single", "hw_car_bluerace": "hw_single",
  "hw_car_greentruck": "hw_single", "hw_car_yellow_sports": "hw_single",
  "hw_car_police": "hw_single", "hw_car_firetruck": "hw_single",
  "hw_car_ambulance": "hw_single", "hw_car_pinkflash": "hw_single",
  "hw_car_monster_purple": "hw_8pack", "hw_car_taxi": "hw_single",
  "hw_car_5pack_classic": "hw_8pack",
  # Hot Wheels track parts
  "hw_part_connector": "hw_track_foldup", "hw_part_jumpramp": "hw_track_loopkick",
  "hw_part_splitter": "hw_track_foldup", "hw_part_loopkit": "hw_track_loop",
  "hw_part_corkscrew": "hw_track_loop", "hw_part_360": "hw_track_foldup",
  "hw_part_clamp_wall": "hw_track_fuelcan", "hw_part_crash_cone": "hw_track_fuelcan",
  "hw_part_finishline": "hw_track_fuelcan", "hw_part_booster_single": "hw_track_booster",
  "hw_part_supercharger": "hw_track_booster", "hw_part_bridge": "hw_track_foldup",
  "hw_part_funnel": "hw_track_loopkick",
  # Themed cars
  "hw_marvel_spider": "hw_marvel", "hw_marvel_iron": "hw_marvel",
  "hw_marvel_hulk": "hw_marvel", "hw_marvel_5pack": "hw_marvel",
  "hw_mario_kart_single": "hw_mariokart", "hw_mario_kart_yoshi": "hw_mariokart",
  "hw_mario_kart_peach": "hw_mariokart", "hw_mario_kart_bowser": "hw_mariokart",
  # NEW: Minecraft jelly/slime cube
  "mc_jelly_cube": "mc_slime_cube",
}


def fetch(url):
    req = urllib.request.Request(url, headers=HDRS)
    with urllib.request.urlopen(req, context=ctx, timeout=30) as r:
        return r.read()


def square(data, size=320):
    im = Image.open(io.BytesIO(data)).convert("RGBA")
    w, h = im.size
    side = int(max(w, h) * 1.04)
    bg = Image.new("RGBA", (side, side), (255, 255, 255, 255))
    bg.paste(im, ((side - w) // 2, (side - h) // 2), im)
    return bg.convert("RGB").resize((size, size), Image.LANCZOS)


def main():
    only = set(sys.argv[1:])
    ok = fail = 0
    for name, url in SOURCES.items():
        if only and name not in only:
            continue
        out = OUT / (name + ".jpg")
        try:
            data = fetch(url)
            if len(data) < 2000:
                raise RuntimeError(f"placeholder ({len(data)}b)")
            square(data).save(out, quality=88)
            print(f"  ok  {name}  ({out.stat().st_size//1024}kb)")
            ok += 1
        except Exception as e:
            print(f"  !!  {name}  {e}")
            fail += 1
    print(f"\ndone: {ok} ok, {fail} failed")
    print("\n# item -> file map (for HTML patch):")
    for item, src in MAP.items():
        print(f"  {item}  ->  sprites/prizes/{src}.jpg")


if __name__ == "__main__":
    main()
