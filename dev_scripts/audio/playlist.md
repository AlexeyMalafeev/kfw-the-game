# KFW soundtrack plan

Wired into the Android app; `docs/audio.md` has the exact game events and
code behind each row.

Chiptune in the NES style: two pulse voices, a stepped triangle bass, a noise
drum channel. Kung-fu flavour comes from pentatonic melodies, parallel
fourths, erhu-like slides and vibrato, pipa-like tremolo, woodblocks and gongs.

To keep the music from wearing thin, the contexts that come up every day get a
small pool to rotate through (town days: 3, street fights: 3), while rare
moments get one tune each. All 22 are composed (scores in `tunes.py`;
`python render.py` writes previews to `out/`, `python render.py --game` the
game's files to `audio/`).

## Tunes

| # | Working title | Where it plays | Mood, tempo |
|---|---|---|---|
| 1 | The Path of the Fist | Title / main menu | heroic anthem, 120 bpm, G pentatonic |
| 2 | Choosing a Style | New game, character creation | curious, light, 110 bpm |
| 3 | Morning Market | Town day, pool 1 of 3 | calm, bright, 100 bpm, D pentatonic |
| 4 | Teahouse Afternoon | Town day, pool 2 of 3 | relaxed, lilting, 3/4 feel |
| 5 | Lanterns at Dusk | Town day, pool 3 of 3 | warm, slightly wistful |
| 6 | Bamboo Courtyard | Practice at school / own practice | rhythmic, disciplined, drill-like |
| 7 | Words of the Master | Master's teachings | slow, contemplative, guqin-like plucks |
| 8 | Fists Like Rain | Street fight, pool 1 of 3 | fast, driving, 152 bpm, E minor pentatonic |
| 9 | Alley Cats | Street fight, pool 2 of 3 | scrappy, swung, playful menace |
| 10 | Thugs at the Bridge | Street fight, pool 3 of 3 | heavy, stomping |
| 11 | Outnumbered | Fights against a group / ambushes by enemies | frantic, rising tension |
| 12 | Every Fist for Itself | Free-for-all and group free-for-all | chaotic, odd accents |
| 13 | Tournament Day | Tournament rounds | ceremonial drums, then fast |
| 14 | The Final Platform | Tournament final | epic, highest stakes |
| 15 | Shadow of the Boss | Story boss fights | dark, minor, relentless |
| 16 | Strange Dreams | Stories (quest scenes) | mysterious, dreamy |
| 17 | Dice in the Back Room | Seedy places, gambling | sleazy, swaggering |
| 18 | Footsteps Behind You | Crime, thieves, tense encounters | suspense, sparse |
| 19 | Plum Blossom | Romance encounters | tender, slow |
| 20 | Healing Herbs | Injured / resting days | slow, gentle, sad |
| 21 | Master of the House | Own school (master mode) | proud, steady |
| 22 | A Legend Is Born | Victory, biography, end of game | grand finale |

## Jingles (short, non-looping)

Victory (fight won), defeat (fight lost), level up — made with the sound
effects. Candidates for later: new day, story begins, accomplishment earned,
tournament won.

## In-fight sound effects (all made, see `out/sfx/`)

| File | When |
|---|---|
| fight_start | Fight begins (gong and drums) |
| gong_clash | Tournament fight begins (one big gong, no drums) |
| whiff | "Miss!": the attacker's move fails |
| dodge | "dodges!": the defender evades |
| hit | Clean hit |
| hit_weapon | Clean hit with a bladed weapon |
| critical | Critical hit: the old-movie echoing punch, CHA-cha-cha |
| epic | EPIC hit: a bigger CHAAA-CHAAA-CHAAA-chaa-cha |
| block | Partial block (some damage gets through) |
| block_full | Full block (no damage) |
| qi_shield | Qi shield absorbs damage |
| counter | Counterattack |
| knockback | Knocked back (a short sweep) |
| knockdown | Fighter falls |
| stun | Fighter stunned |
| shock | Fighter shocked (a stronger stun: a zap, then longer birdies) |
| ko | Knock-out |
| resist_ko | "resists being knocked out!" |
| fury | "is in FURY!": a kung-fu yell |
| guard | Guard move |
| step | Footwork (step in / step back) |
| rush | Rush forward |
| retreat | Retreat |
| focus | Focus (qi) |
| catch_breath | Catch Breath (stamina) |
| bleeding | A wound starts bleeding |
| disarm | Weapon knocked away |
| item_use | Item used in a fight (potion etc.) |
| victory | Jingle: fight won |
| defeat | Jingle: fight lost |
| level_up | Jingle: level up |

Candidates for later, outside fights: menu cursor, menu confirm, coins
(money gained/spent), new day.
