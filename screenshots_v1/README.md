# Screenshots — Version 1 (May 8, 2026)

Snapshot of the games before the next round of major updates.

Captured with headless Chrome at iPhone-size viewport (390 × 844, 2× DPI).
Save state was seeded with realistic-looking progress (coins, level, caught
Wordmons) so the HUD shows real values, not zeros.

## WordQuest (Río — age 7, 1st-grade reading)

| File | What it shows |
|---|---|
| `01_wordquest_main_top.jpg` | Header logo, HUD pills (score/streak/lives/level/coins), XP bar, streak dots, top of battle scene |
| `02_wordquest_main_middle.jpg` | Battle scene with Sparky vs Muddle, mode tab, game card |
| `03_wordquest_my_wordmons.jpg` | "My Wordmons" roster grid + stats below |
| `04_bookshelf_grid_top.jpg` | Bookshelf overlay with **Today's Challenge** banner + first 4 books |
| `05_bookshelf_grid_more.jpg` | Bookshelf scrolled, more book covers |
| `06_bookshelf_grid_bottom.jpg` | Bookshelf scrolled to bottom, the Minecraft + extra books |
| `07_book_cover.jpg` | Sparky and the Big Storm — cover page with 3-read dots, "+15 coins" callout |
| `08_book_page1.jpg` | Page 1, gated words (dashed boxes, "I" highlighted in yellow) |
| `09_book_page1_read.jpg` | Page 1 after all words tapped, "Next Page" unlocked |
| `10_book_page2.jpg` | Page 2 of the same book |
| `11_book_quiz_question.jpg` | Comprehension question, "Question 1 of 3" with progress dots |
| `12_book_quiz_result.jpg` | Final result screen with coins earned + perfect bonus |
| `13_mode_1_storybook.jpg` | 📖 Storybook mode |
| `13_mode_2_comicchat.jpg` | 💬 Comic Chat mode (3-panel dialogue reader) |
| `13_mode_3_readfind.jpg` | 🔎 Read & Find mode (n/u, b/d distractors) |
| `13_mode_4_finisher.jpg` | 📚 What Comes Next mode |
| `13_mode_5_writing.jpg` | ✍️ Be a Writer mode (dragon prompt, type-your-own-story) |
| `13_mode_6_speakback.jpg` | 🎤 Speak It mode (mic + word) |
| `20_shop_view.jpg` | Shop with Pokémon stickers, cards, figures |
| `21_shop_view_more.jpg` | Shop scrolled, more rewards including Hot Wheels + Minecoins |
| `22_house_view.jpg` | "Río's House" — caught Wordmons positioned in bedroom |
| `23_parent_dashboard_top.jpg` | Parent Dashboard top — stats, untouched teacher words |
| `24_parent_dashboard_words.jpg` | Dashboard middle — word-by-word accuracy table |
| `25_parent_dashboard_writing.jpg` | Dashboard bottom — Río's Writing log + 7-day reading chart |

## Rosalearns (Rosa — age 3, text-free / icons + audio)

| File | What it shows |
|---|---|
| `30_rosa_1_letters_top.jpg` | 🔤 Letters mode, with buddy area + sticker collection |
| `30_rosa_1_letters_full.jpg` | Same scrolled to game area |
| `30_rosa_2_numbers_*.jpg` | 🔢 Numbers — count the dots |
| `30_rosa_3_colors_*.jpg` | 🎨 Colors — colored buttons with colored emoji |
| `30_rosa_4_shapes_*.jpg` | 🔷 Shapes — emoji-only choices |
| `30_rosa_5_matching_*.jpg` | 🃏 Match — flip-and-pair card game |
| `30_rosa_6_spanish_*.jpg` | 🇪🇸 Español — hear Spanish word, pick matching emoji |
| `30_rosa_7_smemory_*.jpg` | 🧠🇪🇸 Spanish Memory — bilingual card match |
| `30_rosa_8_maze_*.jpg` | 🌀 Maze — navigate Rosa with arrow buttons |
| `40_rosa_shop.jpg` | Toy shop where Rosa can earn real Bluey / Spidey toys |

## How these were generated

```bash
node /tmp/capture_screenshots.mjs
```

(See `/tmp/capture_screenshots.mjs` for the CDP-driven Chrome script.)
