import random
from typing import List

from kf_lib.kung_fu import boosts as b
from kf_lib.kung_fu import boost_combos as bc
from kf_lib.kung_fu.styles import Style
from kf_lib.kung_fu.techniques import Tech


# todo consider adding move strings to each word below
W1 = {  # add dfs_penalty_step=b.DFS_PEN1, but 1 or 2 words, not 3
    # + stats
    'Acrobatic': Tech('Acrobatics', **bc.ACROBATIC1),
    'Attacking': Tech('Attack Method', atk_mult=b.ATTACK1),
    'Averting': Tech('Avert Attacks', preemptive_chance=b.PREEMPTIVE_CH1),
    'Balanced': Tech('Mid-Range Strikes', dist2_strike_mult=b.DIST2_MULT1),
    'Cautious': Tech('Cautious Attacks', guard_while_attacking=b.GUARD_WHILE_ATTACKING1),
    'Clinging': Tech('Short Strikes', dist1_strike_mult=b.DIST1_MULT1),
    'Dancing': Tech('Dance-Like Form', agility_mult=b.AGILITY1),
    'Defending': Tech('Defense Stance', dfs_mult=b.DEFENSE1),
    'Drunken': Tech('Drunken Form', **bc.DRUNKEN1),
    'Elusive': Tech('Elusive Moves', dodge_mult=b.EVADE1),
    'Exotic': Tech('Exotic Strikes Training', **bc.EXOTIC1),
    'Flying': Tech('Jump Technique', flying_strike_mult=b.STRIKE_MULT1),
    'Furious': Tech('Kung-Fu Fury', fury_chance=b.FURY_CH1),
    'Grappling': Tech('Grappling Training', grappling_strike_mult=b.STRIKE_MULT1),
    'Guarding': Tech('Guard Form', guard_dfs_bonus=b.GUARD_DFS1),
    'Indestructible': Tech('Indestructible Body', **bc.BLOCKS1),
    'Invulnerable': Tech('Invulnerable', dam_reduc=b.DAM_REDUC1),
    'Kicking': Tech('Kick Training', kick_strike_mult=b.STRIKE_MULT1),
    'Light-Footed': Tech('Light Feet', maneuver_time_cost_mult=b.MANEUVER_TIME_COST_MULT1),
    'Long-Range': Tech('Long-Range Fighting', dist3_strike_mult=b.DIST3_MULT1),
    'Mid-Range': Tech('Mid-Range Fighting', dist2_strike_mult=b.DIST2_MULT1),
    'Mystic': Tech('Mystic Power', **bc.QI1),
    'Open-Handed': Tech('Palm and Claw Training', **bc.PALM_AND_CLAW1),
    'Paralyzing': Tech('Paralyzing Strikes', stun_chance=b.STUN_CH1),
    'Persevering': Tech('Perseverance', **bc.STAMINA1),
    'Powerful': Tech('Strength Training', strength_mult=b.STRENGTH1),
    'Punching': Tech('Fist Training', punch_strike_mult=b.STRIKE_MULT1),
    'Quick': Tech('Emphasis on Speed', speed_mult=b.SPEED1),
    'Retaliating': Tech('Retaliation', counter_chance_mult=b.COUNTER_CH_MULT1),
    'Rising': Tech('Rising from the Ashes', resist_ko=b.RESIST_KO1),
    'Sharp': Tech('Long-Range Strikes', dist3_strike_mult=b.DIST3_MULT1),
    'Shattering': Tech('Shattering Strikes', **bc.CRITICAL1),
    'Slashing': Tech('Slashing Strikes', chance_cause_bleeding=b.BLEEDING_CH1),
    'Swift-Striking': Tech(
        'Swift Strikes', strike_time_cost_mult=b.STRIKE_TIME_COST_MULT1
    ),
    'Tough': Tech('Toughness', health_mult=b.HEALTH1),
    'Unstoppable': Tech('Unstoppable Attacks', unblock_chance=b.UNBLOCK_CHANCE1),
    'Vigorous': Tech('Vigor', hp_gain_mult=b.HP_GAIN1),
}  # light-footed, furious, enraged

# exclude resist_ko=b.RESIST_KO1
W2 = {
    'Air': Tech('Air Attacks', flying_strike_mult=b.STRIKE_MULT1),
    'Astral': Tech('Astral Footwork', kick_strike_mult=b.STRIKE_MULT1),
    'Avalanche': Tech('Avalanche Strikes', unblock_chance=b.UNBLOCK_CHANCE1),
    'Bizarre': Tech('Bizarre Forms', **bc.EXOTIC1),
    'Burning': Tech('Burning Fury', fury_chance=b.FURY_CH1),
    'Earth': Tech('Earth\'s Orbit', dist1_strike_mult=b.DIST1_MULT1),
    'Emerald': Tech('Emerald Flow', **bc.QI1),
    'Fire': Tech('Inferno', atk_mult=b.ATTACK1),
    'Formless': Tech('Formless Form', agility_mult=b.AGILITY1),
    'Heavenly': Tech('Heavenly Hands', **bc.PALM_AND_CLAW1),
    'Ice': Tech('Hard like Ice', dfs_mult=b.DEFENSE1),
    'Iron': Tech('Iron Skin', dam_reduc=b.DAM_REDUC1),
    'Meteor': Tech('Meteor Punches', punch_strike_mult=b.STRIKE_MULT1),
    'Misty': Tech('Misty Steps', dodge_mult=b.EVADE1),
    'Moon': Tech('Moon\'s Orbit', dist2_strike_mult=b.DIST2_MULT1),
    'Nimble': Tech('Nimble Movements', **bc.ACROBATIC1),
    'Northern': Tech('Northern Style Kung-fu', strength_mult=b.STRENGTH1),
    'Obsidian': Tech('Obsidian Guard', guard_while_attacking=b.GUARD_WHILE_ATTACKING1),
    'Rainbow': Tech('Rainbow Steps', maneuver_time_cost_mult=b.MANEUVER_TIME_COST_MULT1),
    'Razor': Tech('Razor-Sharp Strikes', **bc.CRITICAL1),
    'Red': Tech('Red Energy', preemptive_chance=b.PREEMPTIVE_CH1),
    'Snow': Tech(
        'Snowfall', strike_time_cost_mult=b.STRIKE_TIME_COST_MULT1
    ),
    'Spiky': Tech('Spiky Attacks', chance_cause_bleeding=b.BLEEDING_CH1),
    'Stone': Tech('Stone Forearms', **bc.BLOCKS1),
    'Storm': Tech('Relentless Storm', **bc.STAMINA1),
    'Sun': Tech('Sun\'s Orbit', dist3_strike_mult=b.DIST3_MULT1),
    'Tipsy': Tech('Tipsy Form', **bc.DRUNKEN1),
    'Vengeful': Tech('Strikes of Vengeance', counter_chance_mult=b.COUNTER_CH_MULT1),
    'Venom': Tech('Deadly Venom', stun_chance=b.STUN_CH1),
    'Water': Tech('Healing Water', hp_gain_mult=b.HP_GAIN1),
    'White': Tech('White Energy', health_mult=b.HEALTH1),
    'Wind': Tech('Wind Form', speed_mult=b.SPEED1),
    'Wooden': Tech('Wooden Limbs', guard_dfs_bonus=b.GUARD_DFS1),
    # crystal, colors, colorless, snow, mountain, river,
    # imperial, golden, southern, silver, bronze, lotus, sky,
    # diamond, pearl, hellish, hard, soft, deadly, lightning
    # adamantine
}

W3 = {  # todo add grappling stike multiplier
    'Bear': Tech('Bear\'s Strength', strength_mult=b.STRENGTH1),
    'Boar': Tech('Rusher Boar', dist1_strike_mult=b.DIST1_MULT1),
    'Butterfly': Tech(
        'Fluttering Butterfly', maneuver_time_cost_mult=b.MANEUVER_TIME_COST_MULT1
    ),
    'Cat': Tech('Cat\'s Attacking Distance', dist2_strike_mult=b.DIST2_MULT1),
    'Centipede': Tech('Countless Palms', **bc.PALM_AND_CLAW1),
    'Cobra': Tech('Attacking Cobra', **bc.CRITICAL1),
    'Crab': Tech('Defending Crab', guard_dfs_bonus=b.GUARD_DFS1),
    'Crane': Tech('Crane Flapping Wings', dfs_mult=b.DEFENSE1),
    'Dragon': Tech('Dragon\'s Energy', **bc.QI1),
    'Eagle': Tech('Flying Eagle', flying_strike_mult=b.STRIKE_MULT1),
    'Elephant': Tech('Elephant\'s Health', health_mult=b.HEALTH1),
    'Falcon': Tech('Hunting Falcon', speed_mult=b.SPEED1),
    'Fox': Tech('Fox Strikes Back', counter_chance_mult=b.COUNTER_CH_MULT1),
    'Hawk': Tech('Hunting Hawk', dist3_strike_mult=b.DIST3_MULT1),
    'Leopard': Tech('Hunting Leopard', guard_while_attacking=b.GUARD_WHILE_ATTACKING1),
    'Lion': Tech('Lion\'s Paws', punch_strike_mult=b.STRIKE_MULT1),
    'Lizard': Tech('Regenerating Lizard', hp_gain_mult=b.HP_GAIN1),
    'Mantis': Tech('Praying Mantis', preemptive_chance=b.PREEMPTIVE_CH1),
    'Monkey': Tech('Playing Monkey', agility_mult=b.AGILITY1),
    'Ox': Tech('Ox\'s Stamina', **bc.STAMINA1),
    'Panther': Tech('Panther Attacks', unblock_chance=b.UNBLOCK_CHANCE1),
    'Phoenix': Tech('Rising Phoenix', resist_ko=b.RESIST_KO1),
    'Rat': Tech('Cornered Rat', fury_chance=b.FURY_CH1),
    'Shark': Tech('Shark Pursues Its Prey', chance_cause_bleeding=b.BLEEDING_CH1),
    'Scorpion': Tech('Stinging Scorpion', kick_strike_mult=b.STRIKE_MULT1),
    'Snake': Tech('Twisting Snake', dodge_mult=b.EVADE1),
    'Squirrel': Tech('Squirrel\'s Agility', **bc.ACROBATIC1),
    'Tiger': Tech('Tiger\'s Rage', atk_mult=b.ATTACK1),
    'Toad': Tech('Toad\'s Toughness', dam_reduc=b.DAM_REDUC1),
    'Turtle': Tech('Turtle\'s Shell', **bc.BLOCKS1),
    'Viper': Tech('Stinging Viper', stun_chance=b.STUN_CH1),
    'Wino': Tech('Wino Form', **bc.DRUNKEN1),
    'Wolf': Tech('Attacking Wolf', strike_time_cost_mult=b.STRIKE_TIME_COST_MULT1),
    # crow, horse, spider - grabs?, dog, bull
    # see https://imperialcombatarts.com/rare-kung-fu-styles--animal-substyles.html
}

# todo strikes for new styles


def generate_new_styles(n, overlap=False) -> List[Style]:
    if overlap:
        words1 = random.choices(list(W1), k=n)
        words2 = random.choices(list(W2), k=n)
        words3 = random.choices(list(W3), k=n)
    else:
        words1 = list(W1)
        random.shuffle(words1)
        words1 = words1[:n]
        words2 = list(W2)
        random.shuffle(words2)
        words2 = words2[:n]
        words3 = list(W3)
        random.shuffle(words3)
        words3 = words3[:n]
    results = [' '.join(triple) for triple in zip(words1, words2, words3)]
    if overlap:
        results = list(set(results))  # remove possible duplicates
    return get_styles_from_list(results)


def get_new_randomly_generated_style() -> Style:
    words = []
    for w_list in (
        list(W1),
        list(W2),
        list(W3)
    ):
        words.append(random.choice(w_list))
    return get_style_from_words(*words)


def get_n_possible_styles() -> int:
    return len(W1) * len(W2) * len(W3)


def get_style_from_str(s) -> Style:
    w1, w2, w3 = s.split()
    return get_style_from_words(w1, w2, w3, s)


def get_style_from_words(w1, w2, w3, style_name='') -> Style:
    t1 = W1[w1]
    t2 = W2[w2]
    t3 = W3[w3]
    if not style_name:
        style_name = ' '.join((w1, w2, w3))
    return Style(style_name, {3: t1, 5: t2, 7: t3}, None)  # todo 3, 5, 7 are magic numbers


def get_styles_from_list(style_list: List[str]) -> List[Style]:
    return [get_style_from_str(s) for s in style_list]
