make tournaments with various non-kung-fu styles and bet (as a separate mini-game)

spectate tournaments option

boost reducing move complexity (add to 'Air' style tech etc.)

boost reduce fall damage

master day action: do street performance to earn money, unique encounters (challenges, robbers)

qi shouldn't increase by default? Maybe it should even decrease unless you focus. It could increase when you successfully defend or attack.

momentum style / techs

On dodge / block / hit / fall - techniques

fury (when low on hp, increase atk or str or crit)

Some opponents enter fury spontaneously

item bundles

Observe opponent: see atts and moves, but selectively, with ??

refactor: 
* @property

story:
* righteous sect, evil sect, triads?

encounters:
* enc: sect members, atk or ignore, sects fighting each other

wtf is STAMINA_FACTOR_BIAS in fighter.py?  

modify qi_when_atk

repair tests; make balance and test suites

y no close-range @ lv up ?  

evil weapons  

remove wp atk bonus

fight players from past games (legendary, story?)

generate new maneuvers (fast charging step etc.), a fixed chance at getting maneuvers when choosing new move

more complex genetic fight AI that learns not only probabilies to execute moves, but also some thresholds (e.g. do focus when qp < threshold etc.; also consider group advantage

specific encs: test of strength, speed, agility, health

! use | in style move_s (e.g. short-range,punch|kick)

weapons are OP?

free-for-all fights

grab enemy's weapon

now we can actually create own styles (with 27 boosts -> 2925 combinations without repetition [n! / (r!(n-r)!)]

Iron Gauntlet/Fist weapon; Iron Claws

add timer to fight screens?

better defense move that requires qi

Light Body Tech - bonus to jumps (use less stamina) and reduce fall damage

AI: compute distance change differently (efficiency of strikes rather than the sheer number)

all levels are 100 exp, calc win exp relative to winner's level (how difficult was the fight? + bonuses)

tavern trouble, losers pay for the breakages

more ASCII and a better matching function for name of move and art

refactor main modules

change function fighter to exp; multiple fighters to exp; calc amount of exp, make it more of a relationship

tech that gives you a powerful attack when you have < 10% hp

tech that makes your attacks more powerful if you are low on hp (Sekibayashi Jun)

fix style moves

save winner fighters at the end of the game

tech: analyze - attack and defense against the same opponent get more effective

tech: predict opponent's actions

move: Rakshasa Palm

series of strikes as one move?

berserk-like state (gradually decrease HP, get attack bonus); different from rage and fury  

preset fighters in development in text file, which move/tech at which level

new game settings in separate text file

mine more quotes

collect 'most damage dealt in one blow' stat

different stance ASCII (depending on style; this can help implement punching bag)

punching bag mini-game: how much damage can you deal in a limited amount of time?

other fight-based mini-games: evade/block as many attacks as you can, etc.

impro weapon break chance on each hit! (techs that reduce it)); may be implemented via move functions

turn numbers - another tactical dimension
(wtf is this??)

rich boy - monthly allowance; prodigy - starting level?

day action: go to tavern

more life sim

add persuade/talk into checks, dependent on trait (add new trait?)

temp traits after talking to wise man?

debt collectors

"I don't know, maybe a year, maybe ten"

martial ars spirit / world

seven Japanese masters

advanced martial arts tournament, super advanced fighters

off-balance when dodge

Focus (with dfs penalty?)

. align ascii in the middle

foreign styles

always get reward for helping people?

enc: market troublemakers, items as reward (as many as the troublemakers)

foreign devils, moral standards

penalize repeated actions more for more interesting fights

waves (ASCII)

generic AI player decision funciton: money, rep, risk, exp (=stakes dict), sum of feature-weight products

a tech that negates fall damage, improves ground dfs, reduces knockback ('will to fight' or sth)

more impro weapons

in-fight stats (strikes thrown/landed etc.)

sometimes, both opponents strike each other at the same time, so double KOs (and draws) are possible

knockback resistance tech; stun/shock resistance tech

use a custom console (for colors at least)

moves like 'overdrives' that require lots of qp to execute; advanced moves or special style moves?

coach mode

add trait-based quotes?

handle grappling differently from strikes?

coordinated attacks tech: bonus when have allies

Deep Focus

add straight/circular/shocking/stam_dam/mob_dam to boosts and techniques

more sophisticated chat system (hero to challenger, hero to villain, master to student, etc.)

fight without being able to attack (subclass Fight)

redo names (Chen Kuo-Wei, Su Hua-Chi)?

Iron Bullet (iron head fighter), Bamboo King (and other weapon masters), Thunderleg

Shadowless Hand, Putting On Her Makeup, Pretty Girl Looks In Her Glass

Bite

no blocks in Long Fist? (0.0 multiplier? -1.0?)

chain hammer weapon

crazy moves: no-shadow headbutt

arm the turtles

reintroduce weapon techs (they don't do anything right now)

knockback against a wall (connected with environment use?)

accum wisdom instead of random chance for personality change

disarm opponent is a Move?

test exp bonuses, reweigh them accordingly?

fight stats (accuracy, moves used, damage dealt)

get verbose f info

kumite/ba?? (tournament) mini-game

tournament winners become selected fighters, another way to generate strong fighters; large tournaments, e.g. 128
participants

enemy becomes friend (story?) - changed my ways

masters sometimes have discipline rod

Style has optional lines (list) spoken when attacking

"ездящая подсечка" (sliding ...?); more trips/sweeps that result in enemy falling down

add more throws (close range, of course); defensive throws too!

nerve blocking

different fight ai behaviors: aggressive, defensive, cautious, sneaky, erratic

use PyGame?

impro weapons: grab a weapon (Move)

add more moves (higher tiers, handle tiers)

styles: add Hapkido

Location class: street, mall, home, etc. Affect improv. weapons and the such

rain -> slip

fighting game mod

fighting game generator: make roster

Intelligent move and tech selection, but non-deterministic

SSS, Tekken, Streets of Rage mods

merge with School World! fight your classmates and develop relationships; or just relationships without all this
studying thing

a miss results in being off-balance (status) for a time

more defense (grabs, counters, side-steps?, acrobatics?)

run-up (status?)

body parts, stances?

Jeet Kune Do: wuuooooooooo

flying forehead?

weight (not easy to change; has pros and cons)

change style in-fight?

new system:
    style moves for non-playable styles (Muai Thai etc.)
    non-playable style emphases
    fight AI: stamina weight, consider enemy dfs, cons criticals and other stuff
    counters
    acrobatics
    grab
	other ways to obtain moves
	reward for beating school challenges? a style move, unavailable otherwise?

AI Players should buy Magic Healers more

players can learn moves used against them (traits affect this too) a special attribute that allows learning other
fighters' moves and techs (a small chance by default, but add traits)?

on defeating your master, become head of your school instead of opening a new one? a choice?

ambush - never feel too scared? run away on feel too scared?

stolen mannequin story?

different fight ais for different enemies? subclass Fighter?

no Tech fighter (override some methods) rather than no Tech style (the same with moves?)?

work encounters

a simple utility to collect total number of moves, styles, techs, etc.

add Thai names

rep -> good deeds, affect traits, more good deed encs, like help and become exhausted, pay lots of money etc.

increase Wiseman trait chance

took hostage bring money to the fish market

subclass Fighter (Robber, Thug etc.; collective names, styles - instead of the ugly style.name

more intelligent att selection depending on the style perks

compare styles in 1on1 and 1 vs 3 fights

AI players don't use fight items much, yet buy them; use more

new AI players

three days before the tournament (upcoming event, store the Tournament instance; add method Tournament.start)

summarize the player's 'career', highlight interesting things

exponential exp?

split the prize if draw at the tournament

new AI testing routine: one vs big crowd

accompl: Crime Fighter

other interesting ways to lose items

grab improvised weapons during fights (secret technique) (automatic)

interact with environment (esp. doing unblockables) (automatic)

Jackie Chan mod?

out-of-towners

custom player creation option

actually join a school early in the game? spend time begging the master?

secret tech: Invisible Armor (dam reduc)

enc: school rivals attack you

traits: gullible (easy to fool - but already have careless; and what would the opposite trait be?); add more life
simulation to the game, different plot twists and interesting encounters; e.g. bad guys luring the gullible hero into
 a trap, etc.

days -> weeks; encounters, work and training are automatic? or choose what to spend more time on (two actions/week)

which traits result in winning more often?

common log for all players

trait-related stats

reduce and rewrite trait exp bonuses?

arguments between students

run away (in some fights) (secret tech or not?)?

(earn) nicknames

add_numbers utility function (set numbers from... to...)

collective_name attribute in fighters, filled in fighter_factory.py

simulating AI (when choosing upgrades/techs)

collect interesting stats (biggest gambling loss/win, most drinking player)

choice: make extra money and get tired

masters have an argument (students fight)

reduce enc chances?

school challenges take place only when go to school?

fight master when disobeying him

increase chance of friendship

show accomplishments in options (already have dates and types)

clear town of crime

TBD:

accomplishments:

    3 exp bonuses at a time -> accomplishment?

    create a kung-fu association

AI:

    implement online learning?

    choose techniques to match your style

    target enemies wisely

    difficulty levels can be implemented by using different AIs

    different AIs for common fighters and masters/bosses?

code:

    fight approximation formula?

    subclass Fight more (components: spectator/no spectator; exp/no exp; stats/no stats)

    normalize values in uneven prob distribution: a1, b1, c1 = tuple([n / sum((a, b, c)) * 100 for n in (a, b, c)])

    generate important fighters: consider style emphases

    Player.get_name_as_master

    time AI play (when there are no human players)?

    stats class / component?

    clear personal log method

    look for bottlenecks

    generic Saver component saving relevant atts?

    rewrite the ugly get_prefight_info Fighter method (possibly as a HumanPlayer method)

    auto fight? option for each player

    subclass Weapon (RobberWeapon etc.)? do I really need to?

    Event class

    test module and cases?

    .__repr__ or .__str__ in all classes (instead of .get_init_string())

events:

    kung-fu festival

encounters:

    help other people more

    protect townspeople

    daughter of tavern owner

    troublemaker (flower kung-fu but can be strong)

    wandering master, sometimes a fraud: pay for an exp reward, sometimes a tech

    old man?

gameplay:

    RING: score (for exp bonuses)

    really teach students; reduce their numbers; simulate school structure

    when a friend challenges you, he becomes stronger

    special enemy (story?) that can only be defeated with counters

    other special fighters (e.g. very high attack but very low health etc.)

    disarm and snatch weapon - separate tech or add to existing

    get help: check impro weapon and walk-ins separately

    unique encounters for school, walk etc.

    new actions like 'do charity' or something like that (late game)

    strong robber + accomplishment

    criminal protected by thugs

    fight with a normal weapon against a crowd, or school vs school fights

    promotion at work, run your business?

    spectate tournament fights?

    more rare things (e.g. in encounters, a very strong robber all of a sudden)

    drunk effects?

    money victory: become governor?

    luck: increase evasion and critical chances?

    better rewards for stories: lots of rep, lots of exp, special techs, lots of money, special items, remove character
    flaw, special friend, move, 100 magic healers

    sequential school challenges?

    training: bullied by senior student(s) - school encounter

    your master retires after you defeat him? or you create a new style? (this will affect creating kung-fu association)

    choose between good things; choose between bad things; choose between MANY things at once

    all fighters of appropriate levels in g.fighters can take part in tournaments (even enemies!)

    lose qi when defend?

    ���������� (a large gang of robbers attacked Foshan!)

    learn medicine, help the sick (another action)

    challengers become friends more often?

    different rewards for tough fights (items?)

    display hp as percentage? or string?

    face

    different AIs for different fighters

    another advanced tech at lv 15?

    always get help in fights against crowds?

    underground tournaments

    remove tedious routines - work and training are resources, not events?

    gangs (join gang?)

    make it possible to change names

    secrets of kung-fu book

    make school training more interesting and interactive (disobey master; practice aspects; risk of injuries - school encounters)

    more cool stuff to do in late game

    when a player is a master, he has a best student who can be trained

    tavern (get quests?)

    depression (e.g. when beaten in an important fight), or small chance after every fight

    values / tenets

reputation:

    top reputation could lead to unique encounters, etc.

    reputation could influence creating an association

    rep levels?

    rep-based: people ask you to help (money, fight sb, etc.)

story:

    thugs burn down school

    arrest gang leader to prove innocence

    school attacked

    10 masters from the North

    story with a powerful item

    style stories (drunken, Wong Fei-Hung - master of fan)

    school bullying (is a story?)

    do master a favour

    lose fight on purpose

    'begging' master to teach you kung-fu

    strong old man (lots of techs) protects you from a gang of robbers

    challenge REALLY strong opponent (like 'god of Wushu' from film) who later teaches you kung-fu (and you are injured)

    all weapons test

    wins out of three matches (different opponents?), different rewards depending on the winning rate

    underground tournament

    dirty money

    showdown with robbers: all masters and players vs huge crowd (epic fight)

    evil sect

    Master Disappears

    ginseng

    major international fighting tournament

    girl kidnapped by bandits

    criminal syndicate

    lost manuscript

    rival schools (new powerful school)

    trouble with family members

    master that turns evil

    betrayal

    archenemy

    Shaolin wooden fighters

    Shaolin gets destroyed?

styles:

    create new style with an extra style bonus on reaching level 20 (or 15?)

    ? learn several styles, choose styles before fights

techniques:

    style weapon techs

    carry a weapon around

    Eight methods, Eight Trigrams Palm, Ultimate Supreme Fist, five fists of sth, eight drunken fairies, Five Explosive Fists

    unique techs named after player

    damage opponent's qi

    weapon: sacrifice defense for attack; all weapons attack; all weapons defense

    breathe: sacrifice health for qi; qi for health

    supreme (sublime?) control - against disarming

    special techniques that are not normally available! (e.g. recovery of hp, qi fountain etc.)

    multishadow kick (attack several enemies at the same time)

traits:

    prone to depression?

    observant: see fighters' atk/dfs/fcs

    honest / unscrupulous

    knowledge of medicine - recovery time is decreased by 1 day, to the minimum of 1 day

    fast / slow recovery (when injured) - tech?

UI:

    display player's all fighter atts in state menu (suboption?)

    generate player description in text (style, strong points, everything)

    game beginning text

virtues:

    humility sincerity courtesy morality trust courage patience endurance perseverance will

weapons:

    meat weapon

    hidden weapon 'flying guillotine'