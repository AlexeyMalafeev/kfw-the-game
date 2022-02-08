### v.0.6.5-beta
"Lucky Furious AI Mutants"  
date  

* feat: luck (extremely good/bad, corresponding stats and accomplishments)
* feat: learn other fighters' moves
* refactor: encounters.py
* feat: lucky and unlucky scenarios in Challenger encounter
* feat: counters, preemptive strikes and criticals are now agility-based
* fix: test fight balance
* feat: improved fight balance (agility is no longer weak)
* feat: quotes from Chinese classic "The Outlaws of the Marsh"
* feat: lucky and unlucky scenarios in Craftsman encounter
* feat: use completely new randomly generated styles in many encounters
* refactor: use type hints in Fighter, accept both strings and objects as style
* feat: reimplement takedown generation, hence more moves: 15805 -> 17699
* fix: bug in prefight quotes not being said by second participant
* feat: fury, another (hopefully) fun game mechanic
* feat: fury-related techniques and styles
* feat: new fight AI that rushes when fights against 4-distance moves or when has a bigger crowd
* feat: improved testing of fight balance and AI
* feat: lucky and unlucky scenarios in strong Beggar encounter
* refactor: genetic algorithm for fight AI training
* feat: remove help in Fat Girl encounter
* feat: in genetic algo, mutation only applies to children


### v.0.6.4-beta
"Flashy Fights"  
December 25, 2021  

* docs: add a (more or less) proper README
* feat: PvP in debug menu  
* fix: turn off items in ninja turtles fight  
* feat: momentum!  
* feat: ability to learn any existing tech via the debug menu  
* feat: ability to inspect current player's attributes in the debug menu  
* feat: ability to set any player attribute in the debug menu   
* feat: faster strike / maneuver mechanics (28594 possible unique styles)  
* feat: utility for counting the number of possible generated styles  
* feat: new styles for generation (including preemptive strikes)  
* feat: preemptive strikes!  
* feat: ASCII additions and improvements  
* fix: bug in debug menu (current player was assigned only once)  
* feat: new formula for knockback caused by damage  
* feat: visualize knockback  
* feat: criticals are level-dependent  
* feat: "~*~*~EPIC!!!~*~*~"  
* refactor: basic and fight attributes  
* feat: a few new hero quotes  
* feat: 3x3 co-op mode  

---

### v.0.6.3-beta  
"Bet on Tournaments"  
October 31, 2021  

feat: ability to bet on tournament outcome  
feat: ability to start a tournament via the debug menu  
feat: knockdown and off-balance are relative to current hp, not max hp 
      (knockback and stun remain relative to max hp)  
feat: probability of feeling too scared to fight is now proportional to risk  
feat: debug mode in user input (get_key)  
feat: a few new quotes, inspired by Lady Bloodfight  
feat: one of the rewards for protecting street performer from thugs is new move  
feat: new "Super" fight items  
refactor: Tournament  
refactor: major refactor of Fighter (split into submodules) as well as some other modules  
refactor: put docs to separate folder, add some todos  
fix: bug in tournaments with odd numbers of fighters  
fix: small import bug in encounters  
fix: bug when fights didn't happen because fighters started with 0 hp  
fix: import bug in turtles reward  
fix: fight items have relative effect  
fix: qp-related custom styles  
fix: qi cost rebalance  

---

### v.0.6.2  
"Debug Menu"  
June 17, 2021  

feat: add debug menu to status screen  
fix: proper input validation in get_int_from_user  
feat: ability to get money via debug menu  
feat: ability to get items via debug menu  
feat: ability to level up via debug menu  
feat: first custom exception - MoveNotFoundError  
feat: randomly choosing weapons in school challenges  
feat: ability to learn moves (by name or tier) via debug menu  
feat: ability to fight thugs via debug menu  

---

### v.0.6.1  
"Fist of Vengeance"  
June 16, 2021  

feat: if lose to strong Beggar/Drunkard/Performer, learn a move  
feat: books sometimes give moves  
feat: more flexible tournaments (variable number of participants)  
feat: new default move: Weak Short Punch  
refactor: flynt (convert to f-strings)  
feat: max stamina is relative to level and stamina gain is relative to max stamina  
feat: stamina boosts in techs are relative (and a bit nerfed?)  
feat: stamina damage is relative  
balance: Guard doesn't gain additional stamina, but also doesn't reduce qi  
feat: add Do Nothing move  
feat: qp max / gain increases with level  
balance: leaps, sweeps and other basic moves don't expend qp  
balance: reduce qi cost for moves  
feat: qi-related boosts are multipliers, like with stamina  
feat: COUNTERS!  
feat: crash report generation  
feat: counter chance increases with level  
feat: boosts / techniques / styles related to counters  
fix: adjust qi-based damage  
fix: 20 options on screen by default  
fix: counter chance increases by 0.02, not by 2  
fix: game loading didn't work after refactoring  
fix: "Ox Herb" and "Dragon Herb" now work properly  
feat: add version history  
