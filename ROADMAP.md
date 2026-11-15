# Contra recomp: roadmap

Checked 2026-11-15 (Phase 1): `contra.nes` is **mapper 2 (UxROM)**, 128 KB PRG,
**CHR RAM**, vertical mirroring, same board as Blades of Steel. SHA-1 in `notes.txt`.

Template: **Ninja Gaiden II** (`src/contra_extras.c` is `ng2_extras.c` renamed, with
bands, eased glide, second core, shake, no flicker, crop and the measurement logs).
Engine `nesrecomp` branch `dd2-240hz` @ `1f57896`, recomp-ui `c099b88`.

**Goal:** 120-180 pictures a second (try 240 like NG2), smooth camera and characters,
no flicker, eye-friendly, two players.

## Ground rules (playbook + RecompLab)

1. Plain playable 100% native port first. Every feature after that has an Off.
2. Measure before building. Everything Contra-specific below is a guess until the logs
   show it.
3. One feature at a time, play-tested against the last good build (two players too).
4. A stutter that's the same at 120, 180 and 240 is a logic bug, not the CPU.
5. Ask before softening any flash.

## Milestone 1: boots and runs native (Phases 2-4)

- Git, submodules, headless build, first boot, probe screenshots (STEPS.txt).
- **Route with the Konami code** at the title (Up Up Down Down Left Right Left Right
  B A Start = 30 lives) so the random-play tail survives deep into Stage 1 and further.
  A second route with **2 players** (B A Select Start) so the 2P code paths get harvested.
- Harvest from real play (diagnostics replay): every stage, bosses, the ending,
  continues, game over, 2-player.
- Done when: `native ... (100.0%)` and it plays at 60 like the original.

## Milestone 2: measure (Phase 5), the whole game

Play through once with the window build (it records), then `tools/segment_logs.py`
replays every piece with `--scroll-log --oam-log --ppu-log`. Claude reads them.

- **Emulation cost per frame** (pacing log): BOS, the same board, was 7.5-8.5 ms, so
  expect the second core to be needed.
- **Slowdown (lag frames).** Contra is known for slowing down when the screen is busy:
  the game skips a logic update and nothing moves that frame. Count them per stage.
  The 4-step easing should hide most of it; the logs show whether it needs more.
- **Camera:** Stage 1/5/6/7 horizontal (player-pushed, right only?), step rhythm, wrap
  at 512. **Stage 3 waterfall scrolls up**: Y steps, rhythm, and where it wraps (240,
  not 256), plus which rows the game rewrites at the edge (junk rows = crop).
- **Base stages (2 and 4):** pseudo-3D rooms. How the screen changes between rooms,
  whether anything scrolls, how the rolling grenades / enemies grow (tile swaps).
- **HUD / splits:** lives medals are probably sprites; check for any scroll split or
  sprite-0 split (the base stages may have one).
- **Sprites:** busiest line (bullets + enemies + 2 players), does OAM rotate, the
  respawn blink (invincible player).
- **Bullets:** size in pixels, speed per frame (spread gun, machine gun, laser, fire),
  max on screen.
- **Flashes:** boss deaths, explosions, any whole-screen palette flash; Stage 6
  (Energy Zone) fire beams. List them with frame numbers before deciding anything.
- **CHR RAM writes during play** (`--ppu-log` CHR checksums): animated tiles
  (waterfall?) are fine for the snapshot as long as CHR is copied at frame end.

## Milestone 3: the basics

- Edge crop (8 px; more top/bottom on the waterfall if junk rows show).
- No sprite flicker, stable overlap order (lower on screen in front, ties by X/tile).
- Sprite mask from OAM, never from colours.

## Milestone 4: eye-friendly

- Flash softening only where a flash carries no information (ask first).
- Respawn blink -> steady (semi-transparent?) player instead of blinking.
- Boss hit flashes softened, keeping their meaning.

## Milestone 5: smooth motion

- 120/180/240 pictures a second with the second core (decide from the pacing log).
- Eased camera X (NG2 code as-is).
- **Eased camera Y: new work** for the waterfall. NG2 never needed it
  ("Vertical scrolling is not glided yet" in the extras). Same rules as X: limited
  acceleration, never past the real camera, rows drawn from the nametables, trail at
  most 8 px so it stays under the crop.
- Character glide, **two players**: palette-aware grouping should keep Bill (blue) and
  Lance (red) apart even when they overlap.
- **Bullets: new work.** They're particles (< 20 px) so they never join a character,
  but they're the fastest things on screen; glide each one alone (single-sprite match,
  straight-line motion, steps > 8 px still not glided), or they'll look choppy next to
  a smooth camera.
- Base stages: room changes are > 8 px jumps, so no glide across them; check that
  enemies "growing" toward the screen are followed by position.

## Milestone 5b (optional, needs an engine change): no slowdown

The engine has an **extra CPU time** option (`cyc_set_extra_scanlines`, `--extra-scanlines
128`) that gives the game more time per frame so it stops slowing down, at normal
speed. Today it only allows MMC1/MMC3 (`hw_machine.c`: `cyc_extra_scanlines_supported`).
UxROM has no IRQ, so allowing mapper 2 is probably a small change on `dd2-240hz`, but
it needs its parity test and a play-test. Costs ~50% more emulation per frame (second
core). Offer it as a menu option ("Slowdown: Original / Removed"); it changes how the
game feels, so you decide the default.

## Milestone 6: release

Phase 8 (defaults: Pictures per second 60, rewind off; fresh-config test) and Phase 9
(release files from NG2, README, stranger test, workflow, `v1.0.0`).

## What I expect to be hard

1. The waterfall's vertical eased camera (new code, the 240-line wrap).
2. Bullets gliding cleanly in a crowded 2-player screen.
3. Slowdown making motion uneven (and the optional removal).
4. Base stages' room changes and pseudo-3D enemies.
