# Audio: music and sound effects

The Android app plays a chiptune soundtrack (22 tunes) and fight sound effects
(27 effects, 3 jingles). The desktop terminal game stays silent: the game code
names tunes and effects everywhere, but only a frontend that installs a player
makes them audible, and only Android does.

## Pipeline

1. **Scores as code.** `dev_scripts/audio/` (see `docs/dev_scripts.md`)
   synthesizes everything: `tunes.py` holds the scores, `sfx.py` the effects,
   `chipsynth.py` the NES-style synth.
2. **Game files.** `cd dev_scripts/audio && ../../.venv/bin/python render.py
   --game` (about 20 s; needs numpy, scipy and soundfile from the dev venv)
   writes OGG Vorbis files, mono, 44.1 kHz, about 64–70 kbit/s, to the
   committed `audio/` folder at the repo root: `audio/music/<tune>_intro.ogg`
   and `<tune>_loop.ogg` per tune, `audio/sfx/<effect>.ogg` per effect or
   jingle. About 9 MB in all. Re-run it after changing a score and commit the
   new files.
3. **APK.** Gradle's `syncAssetsMain` copies `audio/` into the APK's assets.
   The APK build needs no Python audio tooling. Sound added about 9 MB to the
   debug APK (37 → 46 MB).

### Intro and loop files

The app plays a tune's intro file once, then repeats its loop file. A loop
pass does not end in silence: notes released near its end ring on (releases,
the echo on lead voices, gongs and crashes), and in the steady state that tail
sounds over the start of the next pass. A loop file cut at the bar line would
lose that tail, and the jump at the loop point would click or go dry.

`render.py` therefore renders intro + three loop passes and measures the
longest tail `x` (the time until the intro alone, or one loop pass alone, goes
silent; at most about 8 s). The intro file runs from the start to `x` seconds
into the first pass, so the intro's own tail is over before the hand-over. The
loop file is one exact loop period cut from the second pass onward, starting
`x` seconds into a pass: its end flows into its start just as one pass flows
into the next, tail included. Tunes without an intro get a short intro file
too (the first `x` seconds), so the very first pass does not start with the
tail of a pass that never played. Both files get the same mastering gain,
measured on the loop.

## Python side

- `kf_lib/ui/_frontend.py`: `install_frontend(music_player=..., sound_player=...)`
  next to the other optional hooks. `music_player(tune)` gets a tune file stem
  or None (stop); a repeated tune is not sent again. `sound_player(effect)` gets
  an effect file stem.
- `kf_lib/ui/_sound.py` (star-exported by `kf_lib.ui`): `play_music`,
  `play_sound`, the `music(tune, enabled=...)` block that plays a tune and then
  returns to the previous one, `fight_music(tune)` that sets the tune of fights
  started inside it, and the tune table `MUSIC` plus the two rotation pools.
- **Who hears it.** Music changes only for scenes someone watches: players have
  `shows_output` (True for `HumanPlayer` and `SmartAIPVisible`), so an
  invisible AI player's turn never switches the music. Fight effects come only
  from fights shown blow by blow (`NormalFight.plays_sound`); a fight resolved
  with "Auto fight?" plays only the end jingle. None of the hooks draws random
  numbers, so seeded fights end the same with or without sound
  (`test/test_sound.py`).

### Where each tune plays

| Tune | Where |
|---|---|
| 1 The Path of the Fist | Android title screen (played by the app itself) |
| 2 Choosing a Style | New game setup (`Game.new_game`) |
| 3–5 Morning Market, Teahouse Afternoon, Lanterns at Dusk | Town days, by date: day 1 plays 3, day 2 plays 4, day 3 plays 5, day 4 plays 3 again (`Playing.play_day_music`) |
| 6 Bamboo Courtyard | School encounters during practice: master's trial, school challenge, bullying |
| 7 Words of the Master | The master's teachings |
| 8–10 Fists Like Rain, Alley Cats, Thugs at the Bridge | Ordinary fights, taking turns in that order |
| 11 Outnumbered | Fights where the enemy side has more fighters than yours |
| 12 Every Fist for Itself | Free-for-all and group free-for-all |
| 13 Tournament Day | Tournaments and the All-Schools Tournament, scenes and fights |
| 14 The Final Platform | A tournament's final bout (not the All-Schools Tournament's) |
| 15 Shadow of the Boss | Fights that include the player's current story boss |
| 16 Strange Dreams | Story scenes (start and every later scene) |
| 17 Dice in the Back Room | Gambling, prize fighting, drunkards |
| 18 Footsteps Behind You | Crime encounters, thieves, ambushes |
| 19 Plum Blossom | Romance encounters, visiting the sweetheart or spouse |
| 20 Healing Herbs | Days the player is injured or sick |
| 21 Master of the House | Master mode: teaching students, visiting other masters, new students arriving |
| 22 A Legend Is Born | The victory screen, stats and biography |

Encounters pick their tune with a `music` class attribute (a `MUSIC` key),
applied around `run()` in `BaseEncounter`; day actions use the
`scene_music` decorator in `_base_player.py`. A fight's tune is chosen in
`BaseFight.choose_music`, first match wins: a `fight_music` block
(tournaments), the story boss, free-for-all, outnumbered, then the street
pool. After a scene or fight the previous tune comes back, from its intro.

### Fight effects

| Effect | Fired by |
|---|---|
| fight_start | Start of a shown fight, after the prefight quotes |
| whiff | "Miss!": the attacker's own move fails (`check_move_failed`) |
| dodge | The defender dodges (`defend`) |
| block / block_full | A block that lets some damage through / none (after the qi shield) |
| qi_shield | The qi shield absorbs damage |
| hit / hit_weapon / critical / epic | An undefended strike that does damage: epic beats critical beats a bladed move (slash, stab, chop, sword, saber, spear, knife, axe) beats a plain hit. A partial block plays only `block` |
| counter | "+COUNTER!+" |
| knockback, knockdown, stun, shock | `cause_knockback`, `cause_fall` (also falls after a failed maneuver), `cause_stun`, `cause_shock` |
| ko / resist_ko | A knock-out (also passing out from bleeding) / "resists being knocked out!" |
| fury | "is in FURY!" |
| guard, focus, catch_breath | The Guard, Focus and Catch Breath moves |
| step / rush / retreat | Maneuvers: one step either way / two or more steps forward / two or more back |
| bleeding | A wound starts bleeding, and each turn's bleeding damage |
| disarm | Disarming while blocking or attacking |
| item_use | A human player uses an item before a fight |
| victory / defeat | End of a fight watched by a human: the fight music stops, then the jingle for the watching player (a draw counts as defeat) |
| level_up | A human player levels up |

## Android side

- `android/python/kfw_android.py` installs `music_player` and `sound_player`,
  which call `GameHost.playMusic` / `playSound` (they never raise; a closing
  session just goes quiet). `MainActivity` hands them to `GameAudio` on the UI
  thread, ignoring calls from an old session.
- `GameAudio.java`: music through two `MediaPlayer`s, the intro handing over
  to the looping loop file with `setNextMediaPlayer` (gapless); effects through
  a `SoundPool` loaded at start-up. The effects of one blow arrive together;
  they start 110 ms apart so they stay distinguishable, and an effect that
  would start more than 1.2 s late is dropped. Music plays at 80% volume, under
  the effects.
- The title screen plays tune 1; returning to the title switches back to it.
  Moving the app to the background pauses the music (and drops effects); coming
  back resumes it where it was.
- **Volume.** The phone's media volume keys control everything. The game
  toolbar has two toggles next to A− / A+: ♪ (music) and FX (effects), dimmed
  when off, remembered between runs. Music muted at the title stays muted in
  the game.

## Tests

`test/test_sound.py` (the hooks, the silence without a frontend, that every
tune and fired effect has its file, unchanged seeded fights) and the Android
runtime tests (`test_android_fight.py`: a shown fight plays a street tune,
effects and the victory jingle, then restores the music;
`test_android_runtime.py`: new-game and first-day music).
