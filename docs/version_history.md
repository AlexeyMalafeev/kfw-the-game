

fix: bug when fights didn't happen because fighters started with 0 hp
feat: debug mode in user input (get_key)
refactor: tech-based weapon choosing
feat: a few new quotes, inspired by Lady Bloodfight
refactor: fighter._constants  
refactor: fighter module becomes a package  
refactor: put docs to separate folder, add some todos  
fix: import bug in turtles reward  
feat: one of the rewards for protecting street performer from thugs is new move  
feat: new "Super" fight items  
fix: fight items have relative effect  
fix: qp-related custom styles  
fix: qi cost rebalance  

---

v.0.6.2  
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

v.0.6.1  
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
