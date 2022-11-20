import random
import sys

from kf_lib.actors import fighter_factory, names
from kf_lib.happenings import encounters, events
from kf_lib.kung_fu import styles, style_gen
from kf_lib.utils import rndint
from .debug_menu import DebugMenu
from ._game_io import GameIO


NUM_CONVICTS = 5
NUM_STYLES = 10
TOWN_STAT_VALUES = (0.05, 0.1, 0.15, 0.2)


class BaseGame(GameIO):
    def __init__(self):
        super().__init__()
        # players
        self.players = []
        self.current_player = None
        # NPCs
        self.used_names = set()
        self.masters = {}
        self.schools = {}
        self.fighters_list = []  # need both list and dict
        self.fighters_dict = {}
        # special NPCs
        self.beggar = fighter_factory.new_beggar()
        self.beggar.name = self.get_new_name(prefix='Beggar')
        self.register_fighter(self.beggar)
        self.criminals = [fighter_factory.new_convict() for _ in range(NUM_CONVICTS)]
        for c in self.criminals:
            c.name = self.get_new_name(prefix=random.choice(names.ROBBER_NICKNAMES))
            self.register_fighter(c)
        self.drunkard = fighter_factory.new_drunkard(strong=True)
        self.drunkard.name = self.get_new_name(prefix='Drunkard')
        self.register_fighter(self.drunkard)
        self.thief = fighter_factory.new_thief(tough=True)
        self.thief.name = self.get_new_name(prefix='Thief')
        self.register_fighter(self.thief)
        self.fat_girl = fighter_factory.new_fat_girl()
        self.register_fighter(self.fat_girl)
        # misc
        self.auto_save_on = '?'
        self.style_list = styles.default_styles
        self.stories = {}
        self.day = 1
        self.month = 1
        self.year = 1
        self.town_name = 'Foshan'
        self.poverty = random.choice(TOWN_STAT_VALUES)
        self.crime = random.choice(TOWN_STAT_VALUES)
        self.kung_fu = random.choice(
            TOWN_STAT_VALUES
        )  # todo g.kung_fu is used only for tournaments
        self.fights_total = 0
        self.chosen_quit = False
        self.chosen_load = False
        self.n_days_to_win = None
        self.play_indefinitely = False
        self.silent_ending = False

        self.enc_count_dict = {}  # counter for how many times encounters happened
        for e in encounters.all_random_encounter_classes:
            self.enc_count_dict[e.__name__] = 0
        self.enc = encounters.EncControl(self)
        self.debug_menu = DebugMenu(self)

        self.savable_atts = '''town_name poverty crime kung_fu day month year auto_save_on 
            play_indefinitely fights_total enc_count_dict'''.split()

    def crime_down(self):
        events.crime_down(self)

    def get_act_players(self):
        return [p for p in self.players if not p.inactive]

    def get_date(self):
        return f'{self.day}/{self.month}/{self.year}'

    @staticmethod
    def get_fighter_ref(fighter):
        return f'g.fighters_dict[{fighter.name!r}]'

    def get_new_name(self, prefix=''):
        while True:
            for i in range(1000):
                sur = random.choice(names.SURNAME_PARTS)
                if not prefix:
                    nf = rndint(1, 2)
                    fir = ''.join(random.sample(names.FIRST_NAME_PARTS, nf))
                    name = f'{sur} {fir}'.title()
                else:
                    name = f'{prefix} {sur}'.title()
                if name not in self.used_names:
                    return name
            print('1000 names failed')
            print(prefix)

    @staticmethod
    def get_new_random_styles():
        return style_gen.generate_new_styles(NUM_STYLES)

    @staticmethod
    def quit():
        sys.exit()

    def register_fighter(self, f):
        if f.name in self.fighters_dict:
            raise Exception(
                f'Cannot register {f} because a fighter with this name is already registered.')
        self.fighters_list.append(f)
        self.fighters_dict[f.name] = f
        self.used_names.add(f.name)

    def rerank_schools(self):
        for school in self.schools.values():
            school.sort(key=lambda s: -s.get_exp_worth())
            for p in self.players:
                if p in school:
                    new_rank = school.index(p) + 1
                    if p.school_rank != new_rank:
                        p.msg(f'{p.name} is now number {new_rank} at his school.')
                        p.school_rank = new_rank

    def unregister_fighter(self, f):
        self.fighters_list.remove(f)
        del self.fighters_dict[f.name]
