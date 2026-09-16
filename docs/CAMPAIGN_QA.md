# Native SNES campaign validation

Tested ROM SHA-256: `cc4aed7fbadcf86426d81bafc3bb8dc9a67199bf2badad0f6e65a8b60be6b5a4`

Emulator: Snes9x 1.63, libretro commit `890b5d445538fe790aa3add3d5702c80f551e0ae`, compiled on Linux x86-64. Frontend: original `headless.py`, Python ctypes. No commercial ROM or firmware used.

## Result

- 60 of 60 rooms visited through their actual doors.
- All 60 item types acquired through gameplay.
- All 10 bosses defeated, including both optional encounters and the final boss.
- Zero deaths during the automated run.
- Final ending displayed, with `finished=1` and `mode=3`.
- Native framebuffer: 256×224, RGB565.
- Native sound output: stereo PCM, 32,040 Hz, nonzero musical samples.
- Battery SRAM exposed by emulator: 8,192 bytes.

The complete run used only emulated SNES controller input. The adaptive runner reads WRAM to decide where to move and to report state, but never writes WRAM, SRAM, save states, cheats or patches. `inputs.json` contains the exact recorded button sequence; `replay.py` plays it back with no gameplay memory reads until the final assertions.

The route crossed gates using the corresponding earned wolf, bat and mist transformations, attacked suspicious walls to reveal secrets, healed at sanctuaries, acquired equipment, equipped it through the actual inventory menu, and fought with sword, magic and potions. It deliberately deferred the last boss until every other accessible room was explored.

## Reproduction

```sh
python campaign.py
python replay.py
```

`campaign.py` needs `headless.py` in its parent directory, the matching ROM, labels and content tables beside it. `replay.py` only needs the ROM, labels and recorded inputs.

## Evidence and limits

The run took 43,400 emulated frames, approximately 12 minutes 2 seconds of simulated time; this is an automated route with knowledge of the map, not a human completion-time estimate. It does not establish a four-to-six-hour campaign.

`events.json` records equipment, health, visits, items and boss flags throughout. `inputs.json` records all physical controller commands. Screenshots include every room, each boss's start and victory, and the final ending. The full PCM capture is `campaign.wav`; `final.srm` and `final.wram` are diagnostic dumps.

This is an emulator test. It does not establish behavior on an original console, a flash cartridge, every emulator, or every possible input sequence. It establishes that the entire tested ROM's progression is reachable without cheats, including all content and the ending.

An earlier smoke run also verified that a locked shortcut refuses passage before obtaining its key, active boss arenas refuse exit, the first boss's rewards unlock the next region, double jump operates after its relic is acquired, and 600 continuous emulated frames advance the game by exactly 600 ticks.
