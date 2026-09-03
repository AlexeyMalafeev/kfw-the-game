import random

from ._ambush import Ambush
from ._base_encounter import BaseEncounter, Guaranteed, all_random_encounter_classes
from ._beggar import BEGGAR_LOSE_MOVE_TIERS, Beggar, GBeggar
from ._book_seller import BookSeller
from ._challenger import Challenger, GChallenger
from ._craftsman import Craftsman
from ._crime import *
from ._gambling import *
from ._items import *
from ._people import *
from ._performer import *
from ._school import *
from ._story import *
from ._utils import FAILED_ESCAPE_BEATING, check_feeling_greedy, check_scary_fight, \
    get_escape_chance, set_up_weapon_fight, try_enemy, try_escape


# todo f-strings in encounters


# todo reimplement enc extra chances with random.choices
# extra chance of getting these encounters when choosing the corresponding day actions
BUY_ITEMS_ENCS = (
        [Craftsman] * 2 + [BookSeller] * 2 + [GMerchant] * 5 + [Merchant] * 3
        + [StreetPerformer] * 2
)
FIGHT_CRIME_ENCS = (
    [GRobbers] + [Criminal] * 4 + [Extorters] * 7 + [HelpPolice] * 7 + [RobbingSomeone] * 7
)
HELP_POOR_ENCS = [GBeggar] * 3 + [Beggar] * 10 + [WiseMan] * 5
PICK_FIGHTS_ENCS = (
        [Brawler] * 3 + [GChallenger] + [Challenger] * 3 + [FriendMatch] * 3 + [PlayerMatch] * 3
)
PRACTICE_SCHOOL_ENCS = [MasterTrial] * 3 + [SchoolChallenge] * 3 + [SchoolBullying]
SEEDY_PLACES_ENCS = (
    [GGambler] * 1
    + [GDrunkard] * 1
    + [Gambler] * 3
    + [Drunkard] * 3
    + [OverhearConversation] * 3
    + [PrizeFighting] * 3
)
WALK_ENCS = (
    [ContinueStory] * 3
    + [OverhearConversation] * 3
    + [StreetPerformer] * 3
    + [Merchant] * 3
    + [Gossip] * 3
    + [Weirdo] * 3
)
WORK_ENCS = []


def random_encounters(p, encs=None):
    if encs is None:
        encs = all_random_encounter_classes[:]
    random.shuffle(encs)

    for e in encs:
        if p.inactive:
            return
        e(p)


class EncControl:
    def __init__(self, game):
        self.g = self.game = game

    def rand_enc(self, encs=None):
        p = self.g.current_player
        random_encounters(p, encs)

    def run_enc(self, enc_name_string, test=False):
        # todo properly run encounters without execs
        p = self.g.current_player
        exec(f"{enc_name_string}(p, test={test})")
