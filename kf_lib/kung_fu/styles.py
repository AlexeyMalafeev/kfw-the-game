from . import boosts as b
from .techniques import StyleTech


all_styles = {}


DEFAULT_STYLE_MOVE_DICT = {2: '1', 4: '2', 6: '3', 8: '4'}


class Style(object):
    def __init__(self, name, techs_dict, move_str_dict):
        self.name = name
        self.techs = techs_dict
        if self.techs:
            self.is_tech_style = True
        else:
            self.is_tech_style = False
        features = []
        self.features = features
        for lv, t in self.techs.items():
            if t.descr_short not in features:
                features.append(t.descr_short)
        self.descr = ''
        self.descr_short = f"({', '.join(features)})"
        all_styles[self.name] = self
        self.move_strings = (
            move_str_dict if move_str_dict is not None else DEFAULT_STYLE_MOVE_DICT.copy()
        )

    def __str__(self):
        return f'{self.name} ({self.descr})'

    def __repr__(self):
        return f'{self.__class__.__name__}({self.name}, {self.techs}, {self.move_strings})'


# todo to txt file, then load? less syntax?
default_styles = [
    Style(
        'Bagua Zhang',
        {
            3: StyleTech('Bagua Zhang I', dodge_mult=b.EVADE1),
            5: StyleTech('Bagua Zhang II', qp_gain=b.QP_GAIN1),  # todo replace this
            7: StyleTech('Bagua Zhang III', in_fight_impro_wp_chance=b.IN_FIGHT_IMPRO_WP_CH1),
        },
        {1: 'Throw', 2: '1,palm', 4: '2,punch', 6: '3,kick', 8: '4,palm'},
    ),
    Style(
        'Balanced Fist',
        {
            3: StyleTech('Balanced Fist I', dist2_bonus=b.STRIKE_MULT1),
            5: StyleTech('Balanced Fist II', atk_mult=b.ATTACK_HALF, dfs_mult=b.DEFENSE_HALF),
            7: StyleTech('Balanced Fist III', atk_mult=b.ATTACK1, dfs_mult=b.DEFENSE1),
        },
        {
            1: 'Sweep',  # deprives opponent of balance
            2: '1,mid-range',
            4: '2,mid-range',
            6: '3,long-range,charging',
            8: '4,mid-range',
        },
    ),
    Style(
        'Centipede',
        {
            3: StyleTech('Centipede I', agility_mult=b.AGILITY1),
            5: StyleTech('Centipede II', speed_mult=b.SPEED1),
            7: StyleTech(
                'A Hundred Arms',
                punch_strike_mult=b.STRIKE_MULT_HALF,
                palm_strike_mult=b.STRIKE_MULT_HALF,
            ),
        },
        {1: 'Short Palm', 2: '1,punch', 4: '2,palm', 6: '3,punch', 8: '4,palm'},
    ),
    Style(
        'Choy Li Fut',
        {
            3: StyleTech('Choy Li Fut I', atk_mult=b.ATTACK1),
            5: StyleTech('Choy Li Fut II', block_mult=b.BLOCK1),
            7: StyleTech('Choy Li Fut III', dfs_penalty_step=b.DFS_PEN2),
        },
        {1: 'Short Punch', 2: '1,grappling', 4: '2,kick', 6: '3,punch', 8: '4,kick'},
    ),
    Style(
        'Dragon',
        {
            3: StyleTech('Dragon I', unblock_chance=b.UNBLOCK_CHANCE1),
            5: StyleTech('Dragon II', dodge_mult=b.EVADE1),
            7: StyleTech('Dragon III', qp_max=b.QP_MAX1, qp_start=b.QP_START1),
        },
        {2: 'Dragon Claw', 4: '2,kick', 6: '3,punch', 8: '4,energy,kick'},
    ),
    Style(
        'Drunken Boxing',
        # todo for drunken: no fall damage, falling restores qp, off-balance gives bonus to atk&dfs
        {
            3: StyleTech('Drunken Boxing I', agility_mult=b.AGILITY1),
            5: StyleTech('Drunken Boxing II', exotic_strike_mult=b.RARE_STRIKE_MULT1),
            7: StyleTech('Drunken Boxing III', flying_strike_mult=b.RARE_STRIKE_MULT1),
        },
        {2: '1,grappling', 4: 'Trick Punch', 6: '3,trick', 8: '4,trick'},  # todo 'Drunken Punch'
    ),
    Style(
        'Eagle Claw',
        # todo jumps cost less stamina; jumps restore qp?; reduced complexity for jumps
        # todo jump feature is called flying and it's hard to change
        {
            3: StyleTech('Eagle Claw I', dist3_bonus=b.STRIKE_MULT1),
            5: StyleTech('Eagle Claw II', stun_chance=b.STUN_CH1),
            7: StyleTech('Eagle Claw III', critical_chance_mult=b.CRIT_CH1,
                         critical_mult=b.CRIT_M1),
        },
        {
            1: ('Leap Forward', 'Leap Back'),
            2: '1,grappling',
            4: '2,charging,punch',
            6: '3,flying',
            8: '4,flying',
        },
    ),
    Style(
        'Eight Extremities Fist',
        # todo opens the opponent's arms forcibly? fast movement?
        {
            3: StyleTech('Eight Extremities Fist I', dist1_bonus=b.STRIKE_MULT1),
            5: StyleTech('Eight Extremities Fist II', elbow_strike_mult=b.RARE_STRIKE_MULT1),
            7: StyleTech('Eight Extremities Fist III', speed_mult=b.SPEED1),
        },
        {
            1: ('Elbow', 'Charging Step'),
            2: '1,knee',
            4: '2,punch',
            6: '3,elbow',
            8: '4,close-range',
        },
    ),
    Style(
        'Gecko',
        # todo an emphasis on speed and gravity? walls? implement 'cornered' status?
        {
            3: StyleTech('Gecko I', dist3_bonus=b.STRIKE_MULT1),
            5: StyleTech('Gecko II', environment_chance=b.ENVIRONMENT_CH1),
            7: StyleTech('Gecko III', flying_strike_mult=b.STRIKE_MULT1),
        },
        {
            1: 'Leap Back',
            2: '1,long-range',
            4: '2,long-range',
            6: '3,extra long-range',
            8: '4,long-range',
        },
    ),
    Style(
        'Hung Ga',
        {
            3: StyleTech('Hung Ga I', punch_strike_mult=b.STRIKE_MULT1),
            5: StyleTech(
                'Hung Ga II', stamina_max_mult=b.STAM_MAX1, stamina_gain_mult=b.STAM_RESTORE1
            ),
            7: StyleTech('Hung Ga III', strength_mult=b.STRENGTH1),
        },
        {1: 'Short Punch', 2: '1,punch', 4: '2,punch', 6: '3,punch', 8: 'No-Shadow Kick'},
    ),
    Style(
        'Leopard',
        # todo counters
        {
            3: StyleTech('Leopard I', speed_mult=b.SPEED1),
            5: StyleTech('Leopard II', agility_mult=b.AGILITY1),
            7: StyleTech('Leopard III', guard_while_attacking=b.GUARD_WHILE_ATTACKING1),
        },
        {
            1: ('Leap Forward', 'Leap Back'),
            2: 'Leopard Punch',
            4: '2,elbow',
            6: '3,knee',
            8: '4,shocking',
        },
    ),
    Style(
        'Long Fist',
        # todo acrobatics bonus - more damage with complexity and no penalty
        {
            3: StyleTech('Long Fist I', dist3_bonus=b.STRIKE_MULT1),
            5: StyleTech('Whirlwind Kicks', kick_strike_mult=b.STRIKE_MULT1),
            7: StyleTech('Long Fist III', atk_mult=b.ATTACK1),
        },
        {1: 'Leap Back', 2: 'Long Punch', 4: '2,long,kick', 6: '3,acrobatic', 8: '4,acrobatic'},
    ),
    Style(
        'Monkey',
        # todo reduce 'flying' stam_cost and complexity; can also give acrobatics bonus
        # todo very good ground defense
        {
            3: StyleTech('Monkey I', dodge_mult=b.EVADE1),
            5: StyleTech('Monkey II', agility_mult=b.AGILITY1),
            7: StyleTech('Monkey III', flying_strike_mult=b.STRIKE_MULT1),
        },
        {
            1: ('Leap Forward', 'Leap Back'),
            2: '1,palm',
            4: '2,claw',
            6: '3,flying,punch',
            8: '4,flying',
        },
    ),
    Style(
        'Poking Foot',
        # todo a tech: if a strike connects, give a speed boost (combo)
        {
            3: StyleTech('Poking Foot I', kick_strike_mult=b.STRIKE_MULT1),
            5: StyleTech('Poking Foot II', punch_strike_mult=b.STRIKE_MULT1),
            7: StyleTech('Falling Meteorites', speed_mult=b.SPEED1),
        },
        {
            1: 'Short Punch',
            2: '1,fast,kick',
            4: '2,lightning,kick',
            6: '3,lightning,punch',
            8: '4,shocking,kick',
        },
    ),
    Style(
        'Praying Mantis',
        # todo claw mult instead of atk?
        {
            3: StyleTech('Praying Mantis I', block_mult=b.BLOCK1),
            5: StyleTech('Praying Mantis II', stun_chance=b.STUN_CH1),
            7: StyleTech('Praying Mantis III', atk_mult=b.ATTACK1),
        },
        {1: 'Claw', 2: '1,claw', 4: 'Mantis Hook', 6: '3,fast,kick', 8: '4,shocking,claw'},
    ),
    Style(
        'Scorpion',
        {
            3: StyleTech('Scorpion I', kick_strike_mult=b.STRIKE_MULT1),
            5: StyleTech('Scorpion II', kick_strike_mult=b.STRIKE_MULT1),
            7: StyleTech('Scorpion III', kick_strike_mult=b.STRIKE_MULT1),
        },
        {2: '1,kick', 4: '2,kick', 6: '3,kick,shocking', 8: '4,kick'},
    ),
    Style(
        'Shaolin Fist',
        {
            3: StyleTech('Shaolin Fist I', hp_gain=b.HP_GAIN1),
            5: StyleTech('Shaolin Fist II', palm_strike_mult=b.STRIKE_MULT1),
            7: StyleTech('Shaolin Fist III', palm_strike_mult=b.STRIKE_MULT1),
        },
        {2: '1,palm', 4: '2,palm', 6: '3,palm,surprise', 8: '4,palm'},  # todo 'Buddha Palm'
    ),
    Style(
        'Snake',
        {
            3: StyleTech('Snake I', dodge_mult=b.EVADE1),
            5: StyleTech('Snake II', critical_chance_mult=b.CRIT_CH1, critical_mult=b.CRIT_M1),
            7: StyleTech('Snake III', qp_max=b.QP_MAX1, qp_start=b.QP_START1),
        },
        {
            2: '1,claw',
            4: 'Trick Claw',  # todo 'Snake Strike'
            6: '3,shocking,claw',
            8: '4,claw',
        },  # todo 'Poisonous Snake'
    ),
    Style(
        'Taiji',
        {
            3: StyleTech('Taiji I', guard_dfs_bonus=b.GUARD_DFS1),
            5: StyleTech('Taiji II', qp_gain=b.QP_GAIN1),
            7: StyleTech('Taiji III', health_mult=b.HEALTH1),
        },
        {2: '1,palm', 4: '2,palm', 6: '3,energy', 8: '4,energy'},
    ),
    Style(
        'Tiger',
        {
            3: StyleTech('Tiger I', atk_mult=b.ATTACK1),
            5: StyleTech('Tiger II', strength_mult=b.STRENGTH1),
            7: StyleTech(
                'Tiger III', stamina_max_mult=b.STAM_MAX1, stamina_gain_mult=b.STAM_RESTORE1
            ),
        },
        {
            2: '1,claw',  # todo 'Tiger Claw' causes bleeding and not at lv2
            4: '2,power,palm',
            6: '3,power',
            8: '4,kick',
        },  # todo "Tiger's Tail"
    ),
    Style(
        'Toad',
        {
            3: StyleTech('Toad I', strength_mult=b.STRENGTH1),
            5: StyleTech('Toad II', dam_reduc=b.DAM_REDUC1),
            7: StyleTech('Toad III', dam_reduc=b.DAM_REDUC1),
        },
        {2: '1,palm', 4: '2,heavy,punch', 6: '3,power,palm', 8: '4,punch'},
    ),
    Style(
        'White Crane',
        {
            3: StyleTech('White Crane I', dfs_mult=b.DEFENSE1),
            5: StyleTech('White Crane II', dist1_bonus=b.STRIKE_MULT1),
            7: StyleTech('White Crane III', block_mult=b.BLOCK1),
        },
        {2: '1,claw', 4: '2,claw', 6: '3,close-range', 8: '4,kick'},  # todo "Crane's Beak"
    ),
    Style(
        'Wing Chun',
        {
            3: StyleTech('Wing Chun I', punch_strike_mult=b.STRIKE_MULT1),
            5: StyleTech('Wing Chun II', dist1_bonus=b.STRIKE_MULT1),
            7: StyleTech('Wing Chun III', speed_mult=b.SPEED1),
        },
        {
            1: 'Charging Step',
            2: 'Short Fast Punch',  # todo Wing Chun Punch
            4: '2,elbow',
            6: '3,short',
            8: '4,short,punch',
        },  # todo Chain of Punches
    ),
    Style(
        'Xing Yi',
        {
            3: StyleTech('Xing Yi I', speed_mult=b.SPEED1),
            5: StyleTech('Xing Yi II', critical_chance_mult=b.CRIT_CH1, critical_mult=b.CRIT_M1),
            7: StyleTech('Xing Yi III', qp_gain=b.QP_GAIN1),
        },
        {
            2: '1,fast,mid-range',
            4: '2,shocking,close-range',
            6: '3,lightning,punch',
            8: '4,lightning,mid-range',
        },
    ),
]

MAX_LEN_STYLE_NAME = max((len(s.name) for s in default_styles))

BEGGAR_STYLE = Style(
    'Beggar\'s Fist',
    {
        3: StyleTech('Beggar\'s Fist I', dfs_mult=b.DEFENSE1),
        5: StyleTech('Beggar\'s Fist II', palm_strike_mult=b.RARE_STRIKE_MULT1),
        7: StyleTech('Beggar\'s Fist III', qp_gain=b.QP_GAIN1, hp_gain=b.HP_GAIN1),
    },
    {2: '1,palm', 4: '2,palm', 6: '3,energy', 8: '4,energy'},
)
THIEF_STYLE = Style(
    'Thief\'s Shadow',
    {
        3: StyleTech('Thief\'s Shadow I', speed_mult=b.SPEED1),
        5: StyleTech('Thief\'s Shadow II', dodge_mult=b.EVADE1),
        7: StyleTech('Thief\'s Shadow III', atk_mult=b.ATTACK1),
    },
    {2: '1,fast', 4: '2,surprise', 6: '3,shocking', 8: '4,trick'},
)
DRUNKARD_STYLE = Style(
    'Drunken Dragon',
    {
        3: StyleTech('Drunken Dragon I', agility_mult=b.AGILITY1),
        5: StyleTech('Drunken Dragon II', exotic_strike_mult=b.RARE_STRIKE_MULT1),
        7: StyleTech('Drunken Dragon III', unblock_chance=b.UNBLOCK_CHANCE1),
    },
    {2: '1,punch', 4: '2,energy', 6: '5,trick', 8: '6,trick'},  # 'Drunken Punch'?
)
TURTLE_NUNJUTSU = Style(
    'Turtle Ninjutsu',
    {
        3: StyleTech('Cowabunga I', agility_mult=b.AGILITY1),
        5: StyleTech('Cowabunga II', flying_strike_mult=b.RARE_STRIKE_MULT1),
        7: StyleTech('Cowabunga III', weapon_strike_mult=b.WP_STRIKE_MULT1),
    },
    {2: '1,punch', 4: '2,kick', 6: '3,flying', 8: '4,flying'},
)

FLOWER_KUNGFU = Style('Flower Kung-fu', {}, {})
DIRTY_FIGHTING = Style(
    'Dirty Fighting',
    {},  # todo techs for dirty fighting?
    {2: '1,heavy', 4: '2,power', 6: '3,shocking', 8: '4,surprise'},
)
POLICE_KUNGFU = Style('Police Kung-fu', {}, {})
MONSTER_KUNGFU = Style('Monster Kung-fu', {}, {})
ZENS_STYLE = Style('Savant', {}, {})
NO_STYLE = Style('No Style', {}, {})

# todo add more foreign styles
# NB! when adding new foreign style, add names to names.py as well!
FOREIGN_STYLES = {
    'England': Style(
        'English Boxing',
        {
            3: StyleTech('English Boxing I', punch_strike_mult=b.STRIKE_MULT1),
            5: StyleTech('English Boxing II', block_mult=b.BLOCK1),
            7: StyleTech('English Boxing III', punch_strike_mult=b.STRIKE_MULT1),
        },
        {1: ('Long Punch', 'Short Punch'), 2: '1,punch', 4: '2,punch', 6: '3,punch', 8: '4,punch'},
    ),
    'Germany': Style(
        'Wrestling',
        # todo add grabbing to wreslers (a defense move)
        {
            3: StyleTech('Wrestling I', grappling_strike_mult=b.STRIKE_MULT1),
            5: StyleTech('Wrestling II', strength_mult=b.STRENGTH1),
            7: StyleTech('Wrestling III', hp_gain=b.HP_GAIN1),
        },
        {
            1: 'Throw',
            2: '1,grappling',
            4: '2,grappling',
            6: '3,grappling',
            8: '4,grappling',
        },
    ),
    'Japan': Style(
        'Karate',
        {
            3: StyleTech('Karate I', punch_strike_mult=b.STRIKE_MULT1),
            5: StyleTech('Karate II', kick_strike_mult=b.STRIKE_MULT1),
            7: StyleTech('Karate III', block_mult=b.BLOCK1),
        },
        {2: '1,punch', 4: '2,kick', 6: '3,shocking,palm', 8: '4,kick'},
    ),
    'Korea': Style(
        'Taekwondo',
        {
            3: StyleTech('Taekwondo I', kick_strike_mult=b.STRIKE_MULT1),
            5: StyleTech('Taekwondo II', block_mult=b.BLOCK1),
            7: StyleTech('Taekwondo III', kick_strike_mult=b.STRIKE_MULT1),
        },
        {1: 'Short Kick', 2: '1,kick', 4: '2,kick', 6: '3,kick', 8: '4,kick'},
    ),
    'Thailand': Style(
        'Muai Thai',
        {
            3: StyleTech('Muai Thai I', atk_mult=b.ATTACK1),
            5: StyleTech(
                'Muai Thai II', elbow_strike_mult=b.STRIKE_MULT1, knee_strike_mult=b.STRIKE_MULT1
            ),
            7: StyleTech('Muai Thai III', kick_strike_mult=b.STRIKE_MULT1),
        },
        {1: ('Knee', 'Elbow'), 2: '1,kick', 4: '2,elbow', 6: '3,knee', 8: '4,flying,kick'},
    ),
    'Brazil': Style(
        'Capoeira',
        {
            3: StyleTech('Capoeira I', agility_mult=b.AGILITY1),
            5: StyleTech('Capoeira II', strength_mult=b.STRENGTH1),
            7: StyleTech(
                'Capoeira III', stamina_max_mult=b.STAM_MAX1, stamina_gain_mult=b.STAM_RESTORE1
            ),
        },
        {2: '1,kick', 4: 'Acrobatic Kick', 6: '3,acrobatic,kick', 8: '4,acrobatic,flying,kick'},
    ),
}


def get_rand_std_style():
    return random.choice(default_styles)


def get_style_obj(sname):
    if sname not in all_styles:
        from .style_gen import get_style_from_str
        get_style_from_str(sname)  # this should register the style in all_styles
        # style = FLOWER_KUNGFU
        # print(f'warning: unknown style name {sname}, replacing with {style}')
        # return style
    return all_styles[sname]
