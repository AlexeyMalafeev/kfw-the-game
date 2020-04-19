from . import boosts as b
from .styles import TechStyle
from .techniques import StyleTech
from .utilities import *

W1 = {  # add dfs_penalty_step=b.DFS_PEN1, but 1 or 2 words, not 3
        # + distance
        # + stats
    "Mystic": StyleTech('Mystic Power', qp_gain=b.QP_GAIN1),
    "Vigorous": StyleTech('Vigor', hp_gain=b.HP_GAIN1),
    "Attacking": StyleTech('Attack after Attack', atk_mult=b.ATTACK1),
    "Defending": StyleTech('Defense Stance', dfs_mult=b.DEFENSE1),
    "Invulnerable": StyleTech('Invulnerable', dam_reduc=b.DAM_REDUC1),
    "Rising": StyleTech('Rising from the Ashes', resist_ko=b.RESIST_KO1),
    "Guarding": StyleTech('Guard Form', guard_dfs_bonus=b.GUARD_DFS1),
    "Persevering": StyleTech('Perseverance', stamina_gain=b.STAM_RESTORE1),
    "Shattering": StyleTech('Shattering Strikes', critical_chance=b.CRIT_CH1, critical_mult=b.CRIT_M1),
    "Elusive": StyleTech('Elusive Form', dodge_mult=b.EVADE1),
    "Indestructible": StyleTech('Indestructible Body', block_mult=b.BLOCK1),
    "": StyleTech('', punch_strike_mult=b.STRIKE_MULT1),
    "": StyleTech('', palm_strike_mult=b.STRIKE_MULT_HALF),
    "": StyleTech('', kick_strike_mult=b.STRIKE_MULT1),
    "": StyleTech('', exotic_strike_mult=b.RARE_STRIKE_MULT1),
    "": StyleTech('', flying_strike_mult=b.RARE_STRIKE_MULT1),
    "": StyleTech('', guard_while_attacking=b.GUARD_WHILE_ATTACKING1),
    "": StyleTech('', dist1_bonus=b.STRIKE_MULT1),
    "": StyleTech('', dist2_bonus=b.STRIKE_MULT1),
    "": StyleTech('', dist3_bonus=b.STRIKE_MULT1),
    "": StyleTech('', agility_mult=b.AGILITY1),
    "": StyleTech('', speed_mult=b.SPEED1),
    "": StyleTech('', strength_mult=b.STRENGTH1),
    "": StyleTech('', health_mult=b.HEALTH1),
    "": StyleTech('', unblock_chance=b.UNBLOCK_CHANCE1),
    "": StyleTech('', stun_chance=b.STUN_CH1),

    
}

# exclude resist_ko=b.RESIST_KO1
W2 = {
    "Emerald": StyleTech('Emerald Flow', qp_gain=b.QP_GAIN1),
    "Water": StyleTech('Healing Water', hp_gain=b.HP_GAIN1),
    "Fire": StyleTech('Inferno', atk_mult=b.ATTACK1),
    "Ice": StyleTech('Hard like Ice', dfs_mult=b.DEFENSE1),
    "Iron": StyleTech('Iron Skin', dam_reduc=b.DAM_REDUC1),
    "Wooden": StyleTech('Wooden Limbs', guard_dfs_bonus=b.GUARD_DFS1),
    "Storm": StyleTech('Relentless Storm', stamina_gain=b.STAM_RESTORE1),
    "Razor": StyleTech('Razor-Sharp Strikes', critical_chance=b.CRIT_CH1, critical_mult=b.CRIT_M1),
    "Misty": StyleTech('Misty Steps', dodge_mult=b.EVADE1),
    "Stone": StyleTech('Stone Forearms', block_mult=b.BLOCK1),
    "": StyleTech('', punch_strike_mult=b.STRIKE_MULT1),
    "": StyleTech('', palm_strike_mult=b.STRIKE_MULT_HALF),
    "": StyleTech('', kick_strike_mult=b.STRIKE_MULT1),
    "": StyleTech('', exotic_strike_mult=b.RARE_STRIKE_MULT1),
    "": StyleTech('', flying_strike_mult=b.RARE_STRIKE_MULT1),
    "": StyleTech('', guard_while_attacking=b.GUARD_WHILE_ATTACKING1),
    "": StyleTech('', dist1_bonus=b.STRIKE_MULT1),
    "": StyleTech('', dist2_bonus=b.STRIKE_MULT1),
    "": StyleTech('', dist3_bonus=b.STRIKE_MULT1),
    "": StyleTech('', agility_mult=b.AGILITY1),
    "": StyleTech('', speed_mult=b.SPEED1),
    "": StyleTech('', strength_mult=b.STRENGTH1),
    "": StyleTech('', health_mult=b.HEALTH1),
    "": StyleTech('', unblock_chance=b.UNBLOCK_CHANCE1),
    "": StyleTech('', stun_chance=b.STUN_CH1),

    # obsidian, wind, crystal

}

W3 = {
    "Dragon": StyleTech('Dragon\'s Energy', qp_gain=b.QP_GAIN1),
    "Monk": StyleTech('Monk\'s Life Force', hp_gain=b.HP_GAIN1),
    "Tiger": StyleTech('Tiger\'s Rage', atk_mult=b.ATTACK1),
    "Crane": StyleTech('Crane Flapping Wings', dfs_mult=b.DEFENSE1),
    "Bear": StyleTech('Bear\'s Toughness', dam_reduc=b.DAM_REDUC1),
    "Phoenix": StyleTech('Rising Phoenix', resist_ko=b.RESIST_KO1),
    "Wolf": StyleTech('Cornered Wolf', guard_dfs_bonus=b.GUARD_DFS1),
    "Boar": StyleTech('Rushing Boar', stamina_gain=b.STAM_RESTORE1),
    "Viper": StyleTech('Stinging Viper', critical_chance=b.CRIT_CH1, critical_mult=b.CRIT_M1),
    "Snake": StyleTech('Dodging Snake', dodge_mult=b.EVADE1),
    "Mantis": StyleTech('', block_mult=b.BLOCK1),
    "": StyleTech('', punch_strike_mult=b.STRIKE_MULT1),
    "": StyleTech('', palm_strike_mult=b.STRIKE_MULT_HALF),
    "": StyleTech('', kick_strike_mult=b.STRIKE_MULT1),
    "": StyleTech('', exotic_strike_mult=b.RARE_STRIKE_MULT1),
    "": StyleTech('', flying_strike_mult=b.RARE_STRIKE_MULT1),
    "": StyleTech('', guard_while_attacking=b.GUARD_WHILE_ATTACKING1),
    "": StyleTech('', dist1_bonus=b.STRIKE_MULT1),
    "": StyleTech('', dist2_bonus=b.STRIKE_MULT1),
    "": StyleTech('', dist3_bonus=b.STRIKE_MULT1),
    "": StyleTech('', agility_mult=b.AGILITY1),
    "": StyleTech('', speed_mult=b.SPEED1),
    "": StyleTech('', strength_mult=b.STRENGTH1),
    "": StyleTech('', health_mult=b.HEALTH1),
    "": StyleTech('', unblock_chance=b.UNBLOCK_CHANCE1),
    "": StyleTech('', stun_chance=b.STUN_CH1),
    
}
'''


                (Tech('Elbow Boxing', elbow_strike_mult=b.RARE_STRIKE_MULT1),
                 Tech('Mighty Elbows', elbow_strike_mult=b.RARE_STRIKE_MULT2)),

                (Tech('Knee Boxing', knee_strike_mult=b.RARE_STRIKE_MULT1),
                 Tech('Mighty Knees', knee_strike_mult=b.RARE_STRIKE_MULT2)),

                (Tech('Flying Strikes', flying_strike_mult=b.RARE_STRIKE_MULT1),
                 Tech('Sky Dragon', flying_strike_mult=b.RARE_STRIKE_MULT2)),

                (Tech('Hardened Palms', palm_strike_mult=b.RARE_STRIKE_MULT1),
                 Tech('Palms of Justice', palm_strike_mult=b.RARE_STRIKE_MULT2)),

                (Tech('Uncanny Strikes', exotic_strike_mult=b.RARE_STRIKE_MULT1),
                 Tech('Whole Body Weapon', exotic_strike_mult=b.RARE_STRIKE_MULT2)),

                (Tech('Weapon Competence', weapon_strike_mult=b.WP_STRIKE_MULT1),
                 Tech('Weapon Mastery', weapon_strike_mult=b.WP_STRIKE_MULT2)),

                (Tech('Environment Fighting', environment_chance=b.ENVIRONMENT_CH1),
                 Tech('Environment Domination', environment_chance=b.ENVIRONMENT_CH2)),

                (Tech('Unlikely Weapons', in_fight_impro_wp_chance=b.IN_FIGHT_IMPRO_WP_CH1),
                 Tech('Anything Is a Weapon', in_fight_impro_wp_chance=b.IN_FIGHT_IMPRO_WP_CH2)),

                (Tech('Debilitating Strikes', stun_chance=b.STUN_CH1),
                 Tech('Crippling Strikes', stun_chance=b.STUN_CH2)),'''

# todo strikes for new styles


def generate_new_styles(n, overlap=True):
    generated = []
    if overlap:
        words1 = random.choices(list(W1), k=n)
        words2 = random.choices(list(W2), k=n)
        words3 = random.choices(list(W3), k=n)
    else:
        words1 = list(W1)[:n]
        random.shuffle(words1)
        words2 = list(W2)[:n]
        random.shuffle(words2)
        words3 = list(W3)[:n]
        random.shuffle(words3)
    results = [' '.join(triple) for triple in zip(words1, words2, words3)]
    if overlap:
        results = list(set(results))  # remove possible duplicates
    return get_styles_from_list(results)


def get_style_from_str(s):
    w1, w2, w3 = s.split()
    t1 = W1[w1]
    t2 = W2[w2]
    t3 = W3[w3]
    return TechStyle(s, {3: t1, 5: t2, 7: t3}, None)  # todo 3, 5, 7 are magic numbers


def get_styles_from_list(style_list):
    return [get_style_from_str(s) for s in style_list]
