### v0.6.9-beta
""  
Month Day, Year

1. **New experience system**:
   1. feat: change how exp is computed in fights
   2. feat: static accomplishment experience
   3. feat: modify exp per level (static) and school training exp
   4. feat: constants package, experience module inside it
   5. feat: misc exp-related tweaks for the new exp system
   6. feat: home training is only allowed when have a wooden mannequin
   7. feat: base and derived experience constants
2. feat: biography generation for winning players
   1. feat: describe strengths
3. refactor:
   1. refactor: __init_subclass__ in base encounter for automatic class registration
   2. refactor: BaseEncounter is an ABC
   3. refactor: type annotations for BaseEncounter methods
   4. refactor: BookSeller to a separate module

### Coming soon:
* make sure that new moves to automatically created fighters are assigned fairly (without premature bonuses)
* rethink loser exp? no need to reward losses so much
* Fat Girl, Thief, and other strong opponents - encounters can happen at any level, but the enemies are persistent
* biographies:
  * favorite strike: most feared move, preferred
* tests of strength / speed / health / agility in various encounters and stories = new mechanics
* Drunken has improved ground defense (there is a multiplier for this)
* ability to upgrade moves (from pathetic to ultimate)
* yell (as move_fun?)
* in-fight nunchacku tech (like impro weapons)
* refactor accomplishemnts as dict {accompl: date}, otherwise inefficient
* reduce dist3 and dist2 bonuses
* ABC for Fighter
* refactor, refactor, refactor
* fight AI rule to hurry and finish off knocked down opponent 
* learn weak / pathetic moves in books
* nerf guard while atk
* donate to friends, to charity 
* buff att-based damage for strikes
* add societies (bandits, sect: Righteous, White Lotus)
* toughness: level-dependent dam reduction for all
* strong against stronger, strong against weaker - techs (intimidating, fearless) Giant Killer
* continue refactoring encounters while adding lucky/unlucky developments
* more strike types (see strike notes)
* momentum style / techs, use own and opponent's - like Judo
* grabs
* look at fighter atts for unused ideas
* look at todos

---

### v0.6.8-beta
"Drunken Boxing"  
August 13, 2022  

1. fixes: game loading, SpectateFight, qi-based damage, feel too scared
2. feat: add quotes from Dark
3. feat: add Weak and Pathetic moves (3313 -> 3795 moves)
4. feat: ~8 more new quotes (various sources)
5. fix: bug in 'unlucky' craftsman encounter
6. **feat: Bandit Fiance story**
7. feat: test story in debug menu
8. refactor: ratio -> opp_to_self_pwr_ratio
9. feat: move fail chance multiplier and fall damage multiplier
10. feat: add descriptors for value validation
11. feat: exception handling when applying techs
12. refactor: major refactor of stories
13. feat: 3 new style words: Drunken, Acrobatic, Squirrel
14. feat: 2 new techs: Drunken Moves and Drunken Acrobat
15. feat: better move learning through debug menu
16. fix: double knockback (at last!)
17. fix: easy knockback when rushing forward
18. feat: improved handling of knockback
19. feat: new ASCII arts (drunken, acrobatic) (total 198 arts)
20. feat: redraw a few old ASCII arts
21. feat: detect duplicates in ASCII arts
22. feat: remove backflip strikes
23. **feat: combinations of move functions for generation are now described in a table ("move_word_combinations.csv"), not in the code** 
24. feat: new "Drunken" moves, revamp move word combinations (generated 3095 -> 3768 moves)
25. refactor: strike multipliers
26. feat: common logger
27. refactor: Fighter.techs now consists of Tech objects, rather than strings
28. feat: acrobatic styles, techs and buffs
29. feat: reduce folk hero reputation
30. feat: boost_combos.py as SSOT for technique effects
31. feat: improve new move selection

---

### v.0.6.7-beta
"Blood Sport"  
March 29, 2022  

1. fix: nerf default block power, agility goes down in significance, balance improves
2. fix: remove depth-3 move generation for cleaner moves with shorter names (17699 -> 3095 moves)
3. fix: using @property, fix the upper bound of chance to resist KO to avoid endless / very long fights
4. fix: separate bonuses for Guard (as a move) and "guard while attacking"
5. fix: increase guard bonus for all
6. refactor: factor folder name constants and ensuring folders exist to a separate module
7. feat: also save moves as a Pandas DataFrame (for development purposes only)
8. refactor: separate fight into submodules
9. **feat: bleeding mechanic**
10. feat: techniques (and styles) related to bleeding
11. feat: "Slashing" moves (3095 -> 3313) and Claw is slashing by default
12. refactor: game.py is now a package
13. feat: school students are now levels 1-10, masters levels 11-14
14. fix: bug in saving game (duplicated players)
15. feat: change tournament levels: 1-3 "beginner", 4-6 "intermediate", 7-10 "advanced", 11-14 "master"
16. feat: hp gain is relative to max hp
17. feat: dam reduc is relative to damage
18. feat[dev]: basic move analysis (with pandas)
19. feat: overhaul move tiers

---

### v.0.6.6-beta
"Rebalance, Fixes and Fun"  
February 24, 2022    
1. feat: start using rich module for colorful text 
2. refactor: significant overhaul of utils, ui and testing tools
3. refactor: remove unnecessary tech classes, reimplement their functionality as attributes
4. feat: preemptive strikes are tech-only
5. feat: fury is tech-only
6. feat: new flexible profiling script
7. **feat: new fight AI that is more fun (rushes in from distance 4 when hp and stamina are full)**
8. fix: ASCII art errors in weapon strikes
9. fix: old bug with umbrella turning into a pole
10. fix: old bug with standard moves
11. feat: confirm randomly generated styles with the player, regenerate if not ok
12. fix: guard and guard while attacking now work properly
13. fix: qi gain techs now work properly
14. fix: stamina and qp are now properly spent when missing
15. fix: counters and preemptives can now miss, too
16. fix: criticals are now working properly
17. fix: blocks are now working properly
18. fix: counter techniques
19. **feat: complete rebalance of techniques, boosts and strikes**
20. fix: moves with distance bonus are now properly suggested on level up

---

### v.0.6.5-beta
"Fist of Fury"  
February 12, 2022  

1. feat: luck (extremely good/bad, corresponding stats and accomplishments)
2. feat: learn other fighters' moves
3. refactor: encounters.py
4. feat: lucky and unlucky scenarios in Challenger encounter
5. feat: counters, preemptive strikes and criticals are now agility-based
6. fix: test fight balance
7. feat: improved fight balance (agility is no longer weak)
8. feat: quotes from Chinese classic "The Outlaws of the Marsh"
9. feat: lucky and unlucky scenarios in Craftsman encounter
10. feat: use completely new randomly generated styles in many encounters
11. refactor: use type hints in Fighter, accept both strings and objects as style
12. feat: reimplement takedown generation, hence more moves: 15805 -> 17699
13. fix: bug in prefight quotes not being said by second participant
14. feat: fury, another (hopefully) fun game mechanic
15. feat: fury-related techniques and styles
16. feat: new fight AI that rushes when fights against 4-distance moves or when has a bigger crowd
17. feat: improved testing of fight balance and AI
18. feat: lucky and unlucky scenarios in strong Beggar encounter
19. refactor: genetic algorithm for fight AI training
20. feat: remove help in Fat Girl encounter
21. feat: in genetic algo, mutation only applies to children
22. refactor: player as a package
23. feat: train a new powerful genetic fight AI (pop=32 fights=160 n_gen=128 gen=84)

---

### v.0.6.4-beta
"Flashy Fights"  
December 25, 2021  

1. docs: add a (more or less) proper README
2. feat: PvP in debug menu  
3. fix: turn off items in ninja turtles fight  
4. feat: momentum!  
5. feat: ability to learn any existing tech via the debug menu  
6. feat: ability to inspect current player's attributes in the debug menu  
7. feat: ability to set any player attribute in the debug menu   
8. feat: faster strike / maneuver mechanics (28594 possible unique styles)  
9. feat: utility for counting the number of possible generated styles  
10. feat: new styles for generation (including preemptive strikes)  
11. feat: preemptive strikes!  
12. feat: ASCII additions and improvements  
13. fix: bug in debug menu (current player was assigned only once)  
14. feat: new formula for knockback caused by damage  
15. feat: visualize knockback  
16. feat: criticals are level-dependent  
17. feat: "~*~*~EPIC!!!~*~*~"  
18. refactor: basic and fight attributes  
19. feat: a few new hero quotes  
20. feat: 3x3 co-op mode  

---

### v.0.6.3-beta  
"Bet on Tournaments"  
October 31, 2021  

1. feat: ability to bet on tournament outcome  
2. feat: ability to start a tournament via the debug menu  
3. feat: knockdown and off-balance are relative to current hp, not max hp (knockback and stun remain relative to max hp)  
4. feat: probability of feeling too scared to fight is now proportional to risk  
5. feat: debug mode in user input (get_key)  
6. feat: a few new quotes, inspired by Lady Bloodfight  
7. feat: one of the rewards for protecting street performer from thugs is new move  
8. feat: new "Super" fight items  
9.  refactor: Tournament  
10.  refactor: major refactor of Fighter (split into submodules) as well as some other modules  
11.  refactor: put docs to separate folder, add some todos  
12.  fix: bug in tournaments with odd numbers of fighters  
13.  fix: small import bug in encounters  
14.  fix: bug when fights didn't happen because fighters started with 0 hp  
15.  fix: import bug in turtles reward  
16.  fix: fight items have relative effect  
17.  fix: qp-related custom styles  
18.  fix: qi cost rebalance  

---

### v.0.6.2  
"Debug Menu"  
June 17, 2021  

1. feat: add debug menu to status screen  
2. fix: proper input validation in get_int_from_user  
3. feat: ability to get money via debug menu  
4. feat: ability to get items via debug menu  
5. feat: ability to level up via debug menu  
6. feat: first custom exception - MoveNotFoundError  
7. feat: randomly choosing weapons in school challenges  
8. feat: ability to learn moves (by name or tier) via debug menu  
9. feat: ability to fight thugs via debug menu  

---

### v.0.6.1  
"Fist of Vengeance"  
June 16, 2021  

1. feat: if lose to strong Beggar/Drunkard/Performer, learn a move  
2. feat: books sometimes give moves  
3. feat: more flexible tournaments (variable number of participants)  
4. feat: new default move: Weak Short Punch  
5. refactor: flynt (convert to f-strings)  
6. feat: max stamina is relative to level and stamina gain is relative to max stamina  
7. feat: stamina boosts in techs are relative (and a bit nerfed?)  
8. feat: stamina damage is relative  
9. balance: Guard doesn't gain additional stamina, but also doesn't reduce qi  
10. feat: add Do Nothing move  
11. feat: qp max / gain increases with level  
12. balance: leaps, sweeps and other basic moves don't expend qp  
13. balance: reduce qi cost for moves  
14. feat: qi-related boosts are multipliers, like with stamina  
15. feat: COUNTERS!  
16. feat: crash report generation  
17. feat: counter chance increases with level  
18. feat: boosts / techniques / styles related to counters  
19. fix: adjust qi-based damage  
20. fix: 20 options on screen by default  
21. fix: counter chance increases by 0.02, not by 2  
22. fix: game loading didn't work after refactoring  
23. fix: "Ox Herb" and "Dragon Herb" now work properly  
24. feat: add version history  
