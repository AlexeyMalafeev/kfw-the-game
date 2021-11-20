from . import boosts as b
from .styles import Style
from .techniques import StyleTech
from kf_lib.utils.utilities import *

W1 = {  # add dfs_penalty_step=b.DFS_PEN1, but 1 or 2 words, not 3
    # + stats
    "Attacking": StyleTech('Attack Method', atk_mult=b.ATTACK1),
    'Averting': StyleTech('Avert Attacks', preemptive_chance_mult=b.PREEMPTIVE_CH1),
    "Balanced": StyleTech('Mid-Range Strikes', dist2_bonus=b.STRIKE_MULT1),
    "Cautious": StyleTech('Cautious Attacks', guard_while_attacking=b.GUARD_WHILE_ATTACKING1),
    "Clinging": StyleTech('Short Strikes', dist1_bonus=b.STRIKE_MULT1),
    "Close-Range": StyleTech('Close-Range Fighting', dist1_bonus=b.STRIKE_MULT1),
    "Dancing": StyleTech('Dance-Like Form', agility_mult=b.AGILITY1),
    "Defending": StyleTech('Defense Stance', dfs_mult=b.DEFENSE1),
    "Elusive": StyleTech('Elusive Moves', dodge_mult=b.EVADE1),
    "Exotic": StyleTech(
        'Exotic Strikes Training',
        knee_strike_mult=b.STRIKE_MULT1,
        elbow_strike_mult=b.STRIKE_MULT1,
        head_strike_mult=b.STRIKE_MULT1,),
    "Flying": StyleTech('Jump Technique', flying_strike_mult=b.STRIKE_MULT1),
    "Grappling": StyleTech('Grappling Training', grappling_strike_mult=b.STRIKE_MULT1),
    "Guarding": StyleTech('Guard Form', guard_dfs_bonus=b.GUARD_DFS1),
    "Indestructible": StyleTech(
        'Indestructible Body',
        block_mult=b.BLOCK1,
        block_disarm=b.BLOCK_DISARM1
    ),
    "Invulnerable": StyleTech('Invulnerable', dam_reduc=b.DAM_REDUC1),
    "Kicking": StyleTech('Kick Training', kick_strike_mult=b.STRIKE_MULT1),
    "Long-Range": StyleTech('Long-Range Fighting', dist3_bonus=b.STRIKE_MULT1),
    "Mid-Range": StyleTech('Mid-Range Fighting', dist2_bonus=b.STRIKE_MULT1),
    "Mystic": StyleTech('Mystic Power', qp_gain_mult=b.QP_GAIN1, qp_max_mult=b.QP_MAX1),
    "Open-Handed": StyleTech(
        'Palm and Claw Training', palm_strike_mult=b.STRIKE_MULT1, claw_strike_mult=b.STRIKE_MULT1
    ),
    "Paralyzing": StyleTech('Paralyzing Strikes', stun_chance=b.STUN_CH1),
    "Persevering": StyleTech(
        'Perseverance', stamina_max_mult=b.STAM_MAX1, stamina_gain_mult=b.STAM_RESTORE1
    ),
    "Powerful": StyleTech('Strength Training', strength_mult=b.STRENGTH1),
    "Punching": StyleTech('Fist Training', punch_strike_mult=b.STRIKE_MULT1),
    "Quick": StyleTech('Emphasis on Speed', speed_mult=b.SPEED1),
    "Retaliating": StyleTech('Retaliation', counter_chance_mult=b.COUNTER_CH_MULT1),
    "Rising": StyleTech('Rising from the Ashes', resist_ko=b.RESIST_KO1),
    "Sharp": StyleTech('Long-Range Strikes', dist3_bonus=b.STRIKE_MULT1),
    "Shattering": StyleTech(
        'Shattering Strikes', critical_chance_mult=b.CRIT_CH1, critical_mult=b.CRIT_M1
    ),
    "Tough": StyleTech('Toughness', health_mult=b.HEALTH1),
    "Unstoppable": StyleTech('Unstoppable Attacks', unblock_chance=b.UNBLOCK_CHANCE1),
    "Vigorous": StyleTech('Vigor', hp_gain=b.HP_GAIN1),
}  # drunken, light-footed

# exclude resist_ko=b.RESIST_KO1
W2 = {
    'Adamant': StyleTech('Adamant Strikes', unblock_chance=b.UNBLOCK_CHANCE1),
    "Air": StyleTech('Air Attacks', flying_strike_mult=b.STRIKE_MULT1),
    "Astral": StyleTech('Astral Footwork', kick_strike_mult=b.STRIKE_MULT1),
    "Bizarre": StyleTech(
        'Bizarre Forms',
        knee_strike_mult=b.STRIKE_MULT1,
        elbow_strike_mult=b.STRIKE_MULT1,
        head_strike_mult=b.STRIKE_MULT1,),
    "Earth": StyleTech('Earth\'s Orbit', dist1_bonus=b.STRIKE_MULT1),
    "Emerald": StyleTech('Emerald Flow', qp_gain_mult=b.QP_GAIN1, qp_max_mult=b.QP_MAX1),
    "Fire": StyleTech('Inferno', atk_mult=b.ATTACK1),
    "Formless": StyleTech('Formless Form', agility_mult=b.AGILITY1),
    'Heavenly': StyleTech(
        'Heavenly Hands', palm_strike_mult=b.STRIKE_MULT1, claw_strike_mult=b.STRIKE_MULT1
    ),
    "Ice": StyleTech('Hard like Ice', dfs_mult=b.DEFENSE1),
    "Iron": StyleTech('Iron Skin', dam_reduc=b.DAM_REDUC1),
    'Meteor': StyleTech('Meteor Punches', punch_strike_mult=b.STRIKE_MULT1),
    "Misty": StyleTech('Misty Steps', dodge_mult=b.EVADE1),
    'Moon': StyleTech('Moon\'s Orbit', dist2_bonus=b.STRIKE_MULT1),
    'Northern': StyleTech('Northern Style Kung-fu', strength_mult=b.STRENGTH1),
    'Obsidian': StyleTech('Obsidian Guard', guard_while_attacking=b.GUARD_WHILE_ATTACKING1),
    "Razor": StyleTech(
        'Razor-Sharp Strikes', critical_chance_mult=b.CRIT_CH1, critical_mult=b.CRIT_M1
    ),
    'Red': StyleTech('Red Energy', preemptive_chance_mult=b.PREEMPTIVE_CH1),
    "Stone": StyleTech('Stone Forearms', block_mult=b.BLOCK1, block_disarm=b.BLOCK_DISARM1),
    "Storm": StyleTech(
        'Relentless Storm', stamina_max_mult=b.STAM_MAX1, stamina_gain_mult=b.STAM_RESTORE1
    ),
    'Sun': StyleTech('Sun\'s Orbit', dist3_bonus=b.STRIKE_MULT1),
    "Vengeful": StyleTech('Strikes of Vengeance', counter_chance_mult=b.COUNTER_CH_MULT1),
    'Venom': StyleTech('Deadly Venom', stun_chance=b.STUN_CH1),
    "Water": StyleTech('Healing Water', hp_gain=b.HP_GAIN1),
    'White': StyleTech('White Energy', health_mult=b.HEALTH1),
    "Wind": StyleTech('Wind Form', speed_mult=b.SPEED1),
    "Wooden": StyleTech('Wooden Limbs', guard_dfs_bonus=b.GUARD_DFS1),
    # crystal, colors, colorless, snow, mountain, river, rainbow
    # imperial, golden, southern, northern, silver, bronze, lotus, avalanche, sky,
    # diamond, pearl, hellish, hard, soft, deadly
}

W3 = {
    "Bear": StyleTech('Bear\'s Strength', strength_mult=b.STRENGTH1),
    "Boar": StyleTech('Rusher Boar', dist1_bonus=b.STRIKE_MULT1),
    "Centipede": StyleTech(
        'Countless Palms', palm_strike_mult=b.STRIKE_MULT1, claw_strike_mult=b.STRIKE_MULT1
    ),
    "Cobra": StyleTech('Attacking Cobra', critical_chance_mult=b.CRIT_CH1, critical_mult=b.CRIT_M1),
    "Crab": StyleTech('Defending Crab', guard_dfs_bonus=b.GUARD_DFS1),
    "Crane": StyleTech('Crane Flapping Wings', dfs_mult=b.DEFENSE1),
    "Dragon": StyleTech('Dragon\'s Energy', qp_gain_mult=b.QP_GAIN1, qp_max_mult=b.QP_MAX1),
    "Eagle": StyleTech('Flying Eagle', flying_strike_mult=b.STRIKE_MULT1),
    "Elephant": StyleTech('Elephant\'s Health', health_mult=b.HEALTH1),
    "Falcon": StyleTech('Hunting Falcon', speed_mult=b.SPEED1),
    "Fox": StyleTech('Fox Strikes Back', counter_chance_mult=b.COUNTER_CH_MULT1),
    "Hawk": StyleTech('Hunting Hawk', dist3_bonus=b.STRIKE_MULT1),
    "Leopard": StyleTech('Hunting Leopard', guard_while_attacking=b.GUARD_WHILE_ATTACKING1),
    "Lion": StyleTech('Lion\'s Paws', punch_strike_mult=b.STRIKE_MULT1),
    "Lizard": StyleTech('Regenerating Lizard', hp_gain=b.HP_GAIN1),
    "Mantis": StyleTech('Praying Mantis', preemptive_chance_mult=b.PREEMPTIVE_CH1),
    "Monkey": StyleTech('Playing Monkey', agility_mult=b.AGILITY1),
    "Ox": StyleTech(
        'Ox\'s Stamina', stamina_max_mult=b.STAM_MAX1, stamina_gain_mult=b.STAM_RESTORE1
    ),
    "Panther": StyleTech('Panther Attacks', unblock_chance=b.UNBLOCK_CHANCE1),
    "Phoenix": StyleTech('Rising Phoenix', resist_ko=b.RESIST_KO1),
    "Scorpion": StyleTech('Stinging Scorpion', kick_strike_mult=b.STRIKE_MULT1),
    "Snake": StyleTech('Twisting Snake', dodge_mult=b.EVADE1),
    "Tiger": StyleTech('Tiger\'s Rage', atk_mult=b.ATTACK1),
    "Toad": StyleTech('Toad\'s Toughness', dam_reduc=b.DAM_REDUC1),
    'Turtle': StyleTech(
        'Turtle\'s Shell', block_mult=b.BLOCK1, block_disarm=b.BLOCK_DISARM1
    ),
    "Viper": StyleTech('Stinging Viper', stun_chance=b.STUN_CH1),
    "Wolf": StyleTech('Wolf\'s Attacking Distance', dist2_bonus=b.STRIKE_MULT1),
    # "Rat": StyleTech('Cornered Rat', gain bonus when low on hp)
    # crow, horse, spider - grabs?, shark, dog, bull
    # see https://imperialcombatarts.com/rare-kung-fu-styles--animal-substyles.html
}

# todo strikes for new styles


def generate_new_styles(n, overlap=False):
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


def get_n_possible_styles():
    return len(W1) * len(W2) * len(W3)


def get_style_from_str(s):
    w1, w2, w3 = s.split()
    t1 = W1[w1]
    t2 = W2[w2]
    t3 = W3[w3]
    return Style(s, {3: t1, 5: t2, 7: t3}, None)  # todo 3, 5, 7 are magic numbers


def get_styles_from_list(style_list):
    return [get_style_from_str(s) for s in style_list]
