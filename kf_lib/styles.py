from . import boosts as b
from .techniques import StyleTech
from .utilities import *

# the following dicts will be filled when styles are instantiated
all_styles = {}
all_tech_styles = {}
all_no_tech_styles = {}

DEFAULT_STYLE_MOVE_DICT = {2: '1', 4: '2', 6: '3', 8: '4'}


class BaseStyle(object):
    is_style = True

    def __init__(self, name):
        self.name = name
        self.descr = ''
        self.descr_short = ''
        # b.set_descr(self)
        all_styles[self.name] = self

    def __str__(self):
        return '{} ({})'.format(self.name, self.descr)


class TechStyle(BaseStyle):
    is_tech_style = True

    def __init__(self, name, techs_dict, move_str_dict):
        BaseStyle.__init__(self, name)
        self.techs = techs_dict if techs_dict is not None else {}
        self.move_strings = (move_str_dict if move_str_dict is not None
                             else DEFAULT_STYLE_MOVE_DICT.copy())
        features = []
        for lv, t in self.techs.items():
            if t.descr_short not in features:
                features.append(t.descr_short)
        self.descr_short = '({})'.format(', '.join(features))
        all_tech_styles[self.name] = self


class NoTechStyle(BaseStyle):
    is_tech_style = False

    def __init__(self, name, move_str_dict=None):
        BaseStyle.__init__(self, name)
        # todo move next line to BaseStyle? TechStyle does the same
        self.move_strings = (move_str_dict if move_str_dict is not None
                             else DEFAULT_STYLE_MOVE_DICT.copy())
        all_no_tech_styles[self.name] = self


# todo to txt file, then load? less syntax?
default_styles = [TechStyle('Bagua Zhang',
                            {3: StyleTech('Bagua Zhang I', dodge_mult=b.EVADE1),
                             5: StyleTech('Bagua Zhang II', qp_gain=b.QP_GAIN1),  # todo replace this
                             7: StyleTech('Bagua Zhang III', in_fight_impro_wp_chance=b.IN_FIGHT_IMPRO_WP_CH1)},
                            {1: 'Throw',
                             2: '1,palm',
                             4: '2,punch',
                             6: '3,kick',
                             8: '4,palm'}
                            ),
                  TechStyle('Balanced Fist',
                            {3: StyleTech('Balanced Fist I', dist2_bonus=b.STRIKE_MULT1),
                             5: StyleTech('Balanced Fist II', atk_mult=b.ATTACK_HALF, dfs_mult=b.DEFENSE_HALF),
                             7: StyleTech('Balanced Fist III', atk_mult=b.ATTACK1, dfs_mult=b.DEFENSE1)},
                            {1: 'Sweep',  # deprives opponent of balance
                             2: '1,mid-range',
                             4: '2,mid-range',
                             6: '3,long-range,charging',
                             8: '4,mid-range'}
                            ),
                  TechStyle('Centipede',
                            {3: StyleTech('Centipede I', agility_mult=b.AGILITY1),
                             5: StyleTech('Centipede II', speed_mult=b.SPEED1),
                             7: StyleTech('A Hundred Arms', punch_strike_mult=b.STRIKE_MULT_HALF,
                                          palm_strike_mult=b.STRIKE_MULT_HALF)},
                            {1: 'Short Palm',
                             2: '1,punch',
                             4: '2,palm',
                             6: '3,punch',
                             8: '4,palm'}
                            ),
                  TechStyle('Choy Li Fut',
                            {3: StyleTech('Choy Li Fut I', atk_mult=b.ATTACK1),
                             5: StyleTech('Choy Li Fut II', block_mult=b.BLOCK1),
                             7: StyleTech('Choy Li Fut III', dfs_penalty_step=b.DFS_PEN2)},
                            {1: 'Short Punch',
                             2: '1,grappling',
                             4: '2,kick',
                             6: '3,punch',
                             8: '4,kick'}
                            ),
                  TechStyle('Dragon',
                            {3: StyleTech('Dragon I', unblock_chance=b.UNBLOCK_CHANCE1),
                             5: StyleTech('Dragon II', dodge_mult=b.EVADE1),
                             7: StyleTech('Dragon III', qp_max=b.QP_MAX1, qp_start=b.QP_START1)},
                            {2: 'Dragon Claw',
                             4: '2,kick',
                             6: '3,punch',
                             8: '4,energy,kick'}
                            ),
                  TechStyle('Drunken Boxing',
                            # todo for drunken: no fall damage, falling restores qp, off-balance gives bonus to atk&dfs
                            {3: StyleTech('Drunken Boxing I', agility_mult=b.AGILITY1),
                             5: StyleTech('Drunken Boxing II', exotic_strike_mult=b.RARE_STRIKE_MULT1),
                             7: StyleTech('Drunken Boxing III', flying_strike_mult=b.RARE_STRIKE_MULT1)},
                            {2: '1,grappling',
                             4: 'Trick Punch',  # todo 'Drunken Punch'
                             6: '3,trick',
                             8: '4,trick'}
                            ),
                  TechStyle('Eagle Claw',
                            # todo jumps cost less stamina; jumps restore qp?; reduced complexity for jumps
                            # todo jump feature is called flying and it's hard to change
                            {3: StyleTech('Eagle Claw I', dist3_bonus=b.STRIKE_MULT1),
                             5: StyleTech('Eagle Claw II', stun_chance=b.STUN_CH1),
                             7: StyleTech('Eagle Claw III', critical_chance=b.CRIT_CH1, critical_mult=b.CRIT_M1)},
                            {1: ('Leap Forward', 'Leap Back'),
                             2: '1,grappling',
                             4: '2,charging,punch',
                             6: '3,flying',
                             8: '4,flying'}
                            ),
                  TechStyle('Eight Extremities Fist',
                            # todo opens the opponent's arms forcibly? fast movement?
                            {3: StyleTech('Eight Extremities Fist I', dist1_bonus=b.STRIKE_MULT1),
                             5: StyleTech('Eight Extremities Fist II', elbow_strike_mult=b.RARE_STRIKE_MULT1),
                             7: StyleTech('Eight Extremities Fist III', speed_mult=b.SPEED1)},
                            {1: ('Elbow', 'Charging Step'),
                             2: '1,knee',
                             4: '2,punch',
                             6: '3,elbow',
                             8: '4,close-range'}
                            ),
                  TechStyle('Gecko',
                            # todo an emphasis on speed and gravity? walls? implement 'cornered' status?
                            {3: StyleTech('Gecko I', dist3_bonus=b.STRIKE_MULT1),
                             5: StyleTech('Gecko II', environment_chance=b.ENVIRONMENT_CH1),
                             7: StyleTech('Gecko III', flying_strike_mult=b.STRIKE_MULT1)},
                            {1: 'Retreat',  # todo more suitable moves for Gecko
                             2: '1,long-range',
                             4: '2,long-range',
                             6: '3,extra long-range',
                             8: '4,long-range'}
                            ),
                  TechStyle('Hung Ga',
                            {3: StyleTech('Hung Ga I', punch_strike_mult=b.STRIKE_MULT1),
                             5: StyleTech('Hung Ga II', stamina_gain=b.STAM_RESTORE1, stamina_max=b.STAM_MAX1),
                             7: StyleTech('Hung Ga III', strength_mult=b.STRENGTH1)},
                            {1: 'Short Punch',
                             2: '1,punch',
                             4: '2,punch',
                             6: '3,punch',
                             8: 'No-Shadow Kick'}
                            ),
                  TechStyle('Leopard',
                            # todo counters
                            {3: StyleTech('Leopard I', speed_mult=b.SPEED1),
                             5: StyleTech('Leopard II', agility_mult=b.AGILITY1),
                             7: StyleTech('Leopard III', guard_while_attacking=b.GUARD_WHILE_ATTACKING1)},
                            {1: ('Rush Forward', 'Retreat'),
                             2: 'Leopard Punch',
                             4: '2,elbow',
                             6: '3,knee',
                             8: '4,shocking'}
                            ),
                  TechStyle('Long Fist',
                            # todo acrobatics bonus - more damage with complexity and no penalty
                            {3: StyleTech('Long Fist I', dist3_bonus=b.STRIKE_MULT1),
                             5: StyleTech('Whirlwind Kicks', kick_strike_mult=b.STRIKE_MULT1),
                             7: StyleTech('Long Fist III', atk_mult=b.ATTACK1)},
                            {1: 'Retreat',
                             2: 'Long Punch',
                             4: '2,long,kick',
                             6: '3,acrobatic',
                             8: '4,acrobatic'}
                            ),
                  TechStyle('Monkey',
                            # todo reduce 'flying' stam_cost and complexity; can also give acrobatics bonus
                            # todo very good ground defense
                            {3: StyleTech('Monkey I', dodge_mult=b.EVADE1),
                             5: StyleTech('Monkey II', agility_mult=b.AGILITY1),
                             7: StyleTech('Monkey III', flying_strike_mult=b.STRIKE_MULT1)},
                            {1: ('Leap Forward', 'Leap Back'),
                             2: '1,palm',
                             4: '2,claw',
                             6: '3,flying,punch',
                             8: '4,flying'}
                            ),
                  TechStyle('Poking Foot',
                            # todo a tech: if a strike connects, give a speed boost (combo)
                            {3: StyleTech('Poking Foot I', kick_strike_mult=b.STRIKE_MULT1),
                             5: StyleTech('Poking Foot II', punch_strike_mult=b.STRIKE_MULT1),
                             7: StyleTech('Falling Meteorites', speed_mult=b.SPEED1)},
                            {1: 'Short Punch',
                             2: '1,fast,kick',
                             4: '2,lightning,kick',
                             6: '3,lightning,punch',
                             8: '4,shocking,kick'}
                            ),
                  TechStyle('Praying Mantis',
                            # todo claw mult instead of atk?
                            {3: StyleTech('Praying Mantis I', block_mult=b.BLOCK1),
                             5: StyleTech('Praying Mantis II', stun_chance=b.STUN_CH1),
                             7: StyleTech('Praying Mantis III', atk_mult=b.ATTACK1)},
                            {1: 'Claw',
                             2: '1,claw',
                             4: 'Mantis Hook',
                             6: '3,fast,kick',
                             8: '4,shocking,claw'}
                            ),

                  TechStyle('Scorpion',
                            {3: StyleTech('Scorpion I', kick_strike_mult=b.STRIKE_MULT1),
                             5: StyleTech('Scorpion II', kick_strike_mult=b.STRIKE_MULT1),
                             7: StyleTech('Scorpion III', kick_strike_mult=b.STRIKE_MULT1)},
                            {2: '1,kick',
                             4: '2,kick',
                             6: '3,kick,shocking',
                             8: '4,kick'}
                            ),
                  TechStyle('Shaolin Fist',
                            {3: StyleTech('Shaolin Fist I', hp_gain=b.HP_GAIN1),
                             5: StyleTech('Shaolin Fist II', palm_strike_mult=b.STRIKE_MULT1),
                             7: StyleTech('Shaolin Fist III', palm_strike_mult=b.STRIKE_MULT1)},
                            {2: '1,palm',
                             4: '2,palm',
                             6: '3,palm,surprise',
                             8: '4,palm'}  # todo 'Buddha Palm'
                            ),
                  TechStyle('Snake',
                            {3: StyleTech('Snake I', dodge_mult=b.EVADE1),
                             5: StyleTech('Snake II', critical_chance=b.CRIT_CH1, critical_mult=b.CRIT_M1),
                             7: StyleTech('Snake III', qp_max=b.QP_MAX1, qp_start=b.QP_START1)},
                            {2: '1,claw',
                             4: 'Trick Claw',  # todo 'Snake Strike'
                             6: '3,shocking,claw',
                             8: '4,claw'}  # todo 'Poisonous Snake'
                            ),
                  TechStyle('Taiji',
                            {3: StyleTech('Taiji I', guard_dfs_bonus=b.GUARD_DFS1),
                             5: StyleTech('Taiji II', qp_gain=b.QP_GAIN1),
                             7: StyleTech('Taiji III', health_mult=b.HEALTH1)},
                            {2: '1,palm',
                             4: '2,palm',
                             6: '3,energy',
                             8: '4,energy'}
                            ),
                  TechStyle('Tiger',
                            {3: StyleTech('Tiger I', atk_mult=b.ATTACK1),
                             5: StyleTech('Tiger II', strength_mult=b.STRENGTH1),
                             7: StyleTech('Tiger III', stamina_gain=b.STAM_RESTORE1, stamina_max=b.STAM_MAX1)},
                            {2: '1,claw',  # todo 'Tiger Claw' causes bleeding and not at lv2
                             4: '2,power,palm',
                             6: '3,power',
                             8: '4,kick'}  # todo "Tiger's Tail"
                            ),
                  TechStyle('Toad',
                            {3: StyleTech('Toad I', strength_mult=b.STRENGTH1),
                             5: StyleTech('Toad II', dam_reduc=b.DAM_REDUC1),
                             7: StyleTech('Toad III', dam_reduc=b.DAM_REDUC1)},
                            {2: '1,palm',
                             4: '2,heavy,punch',
                             6: '3,power,palm',
                             8: '4,punch'}
                            ),
                  TechStyle('White Crane',
                            {3: StyleTech('White Crane I', dfs_mult=b.DEFENSE1),
                             5: StyleTech('White Crane II', dist1_bonus=b.STRIKE_MULT1),
                             7: StyleTech('White Crane III', block_mult=b.BLOCK1)},
                            {2: '1,claw',  # todo "Crane's Beak"
                             4: '2,claw',
                             6: '3,close-range',
                             8: '4,kick'}
                            ),
                  TechStyle('Wing Chun',
                            {3: StyleTech('Wing Chun I', punch_strike_mult=b.STRIKE_MULT1),
                             5: StyleTech('Wing Chun II', dist1_bonus=b.STRIKE_MULT1),
                             7: StyleTech('Wing Chun III', speed_mult=b.SPEED1)},
                            {1: 'Charging Step',
                             2: 'Short Fast Punch',  # todo Wing Chun Punch
                             4: '2,elbow',
                             6: '3,short',
                             8: '4,short,punch'}  # todo Chain of Punches
                            ),
                  TechStyle('Xing Yi',
                            {3: StyleTech('Xing Yi I', speed_mult=b.SPEED1),
                             5: StyleTech('Xing Yi II', critical_chance=b.CRIT_CH1, critical_mult=b.CRIT_M1),
                             7: StyleTech('Xing Yi III', qp_gain=b.QP_GAIN1)},
                            {2: '1,fast,mid-range',
                             4: '2,shocking,close-range',
                             6: '3,lightning,punch',
                             8: '4,lightning,mid-range'}
                            )]

MAX_LEN_STYLE_NAME = max((len(s.name) for s in default_styles))

BEGGAR_STYLE = TechStyle('Beggar\'s Fist',
                         {3: StyleTech('Beggar\'s Fist I', dfs_mult=b.DEFENSE1),
                          5: StyleTech('Beggar\'s Fist II', palm_strike_mult=b.RARE_STRIKE_MULT1),
                          7: StyleTech('Beggar\'s Fist III', qp_gain=b.QP_GAIN1, hp_gain=b.HP_GAIN1)},
                         {2: '1,palm',
                          4: '2,palm',
                          6: '3,energy',
                          8: '4,energy'}
                         )
THIEF_STYLE = TechStyle('Thief\'s Shadow',
                        {3: StyleTech('Thief\'s Shadow I', speed_mult=b.SPEED1),
                         5: StyleTech('Thief\'s Shadow II', dodge_mult=b.EVADE1),
                         7: StyleTech('Thief\'s Shadow III', atk_mult=b.ATTACK1)},
                        {2: '1,fast',
                         4: '2,surprise',
                         6: '3,shocking',
                         8: '4,trick'}
                        )
DRUNKARD_STYLE = TechStyle('Drunken Dragon',
                           {3: StyleTech('Drunken Dragon I', agility_mult=b.AGILITY1),
                            5: StyleTech('Drunken Dragon II', exotic_strike_mult=b.RARE_STRIKE_MULT1),
                            7: StyleTech('Drunken Dragon III', unblock_chance=b.UNBLOCK_CHANCE1)},
                           {2: '1,punch',  # 'Drunken Punch'?
                            4: '2,energy',
                            6: '5,trick',
                            8: '6,trick'}
                           )
TURTLE_NUNJUTSU = TechStyle('Turtle Ninjutsu',
                            {3: StyleTech('Cowabunga I', agility_mult=b.AGILITY1),
                             5: StyleTech('Cowabunga II', flying_strike_mult=b.RARE_STRIKE_MULT1),
                             7: StyleTech('Cowabunga III', weapon_strike_mult=b.WP_STRIKE_MULT1)},
                            {2: '1,punch',
                             4: '2,kick',
                             6: '3,flying',
                             8: '4,flying'}
                            )

FLOWER_KUNGFU = NoTechStyle('Flower Kung-fu')
DIRTY_FIGHTING = NoTechStyle('Dirty Fighting',
                             {2: '1,heavy',
                              4: '2,power',
                              6: '3,shocking',
                              8: '4,surprise'}
                             )
POLICE_KUNGFU = NoTechStyle('Police Kung-fu')
MONSTER_KUNGFU = NoTechStyle('Monster Kung-fu')
ZENS_STYLE = NoTechStyle('Savant')
NO_STYLE = NoTechStyle('No Style')

# todo add more foreign styles
# NB! when adding new foreign style, add names to names.py as well!
FOREIGN_STYLES = {
    'England': TechStyle('English Boxing',
                         {3: StyleTech('English Boxing I', punch_strike_mult=b.STRIKE_MULT1),
                          5: StyleTech('English Boxing II', block_mult=b.BLOCK1),
                          7: StyleTech('English Boxing III', punch_strike_mult=b.STRIKE_MULT1)},
                         {1: ('Long Punch', 'Short Punch'),
                          2: '1,punch',
                          4: '2,punch',
                          6: '3,punch',
                          8: '4,punch'}
                         ),
    'Germany': TechStyle('Wrestling',
                         # todo add grabbing to wreslers (a defense move)
                         {3: StyleTech('Wrestling I', grappling_strike_mult=b.STRIKE_MULT1),
                          5: StyleTech('Wrestling II', strength_mult=b.STRENGTH1),
                          7: StyleTech('Wrestling III', hp_gain=b.HP_GAIN1)},
                         {1: ('Rush Forward', 'Throw'),
                          2: '1,grappling',
                          4: '2,grappling',
                          6: '3,grappling',
                          8: '4,grappling'}
                         ),
    'Japan': TechStyle('Karate',
                       {3: StyleTech('Karate I', punch_strike_mult=b.STRIKE_MULT1),
                        5: StyleTech('Karate II', kick_strike_mult=b.STRIKE_MULT1),
                        7: StyleTech('Karate III', block_mult=b.BLOCK1)},
                       {2: '1,punch',
                        4: '2,kick',
                        6: '3,shocking,palm',
                        8: '4,kick'}
                       ),
    'Korea': TechStyle('Taekwondo',
                       {3: StyleTech('Taekwondo I', kick_strike_mult=b.STRIKE_MULT1),
                        5: StyleTech('Taekwondo II', block_mult=b.BLOCK1),
                        7: StyleTech('Taekwondo III', kick_strike_mult=b.STRIKE_MULT1)},
                       {1: 'Short Kick',
                        2: '1,kick',
                        4: '2,kick',
                        6: '3,kick',
                        8: '4,kick'}
                       ),
    'Thailand': TechStyle('Muai Thai',
                          {3: StyleTech('Muai Thai I', atk_mult=b.ATTACK1),
                           5: StyleTech('Muai Thai II', elbow_strike_mult=b.STRIKE_MULT1,
                                        knee_strike_mult=b.STRIKE_MULT1),
                           7: StyleTech('Muai Thai III', kick_strike_mult=b.STRIKE_MULT1)},
                          {1: ('Knee', 'Elbow'),
                           2: '1,kick',
                           4: '2,elbow',
                           6: '3,knee',
                           8: '4,flying,kick'}
                          ),
    'Brazil': TechStyle('Capoeira',
                        {3: StyleTech('Capoeira I', agility_mult=b.AGILITY1),
                         5: StyleTech('Capoeira II', strength_mult=b.STRENGTH1),
                         7: StyleTech('Capoeira III', stamina_gain=b.STAM_RESTORE1,
                                      stamina_max=b.STAM_MAX1)},
                        {2: '1,kick',
                         4: 'Acrobatic Kick',
                         6: '3,acrobatic,kick',
                         8: '4,acrobatic,flying,kick'}
                        )
}


def get_rand_std_style():
    return random.choice(default_styles)


def get_style_obj(sname):
    if sname not in all_styles:
        from .style_gen import get_style_from_str
        get_style_from_str(sname)  # this should register the style in all_styles
    return all_styles[sname]
