"""To add a story, implement it as a subclass of BaseStory in a separate module using one of the
existing stories as a reference.
After this, it is sufficient to import the new story here like others below."""

from typing import List, Type

from ._base_story import BaseStory, _all_stories
from ._bandit_fiance import BanditFianceStory
from ._eight_gates import EightGatesStory
from ._foreigner import ForeignerStory
from ._grand_melee import GrandMeleeStory
from ._jade_table import JadeTableStory
from ._ninja_turtles import NinjaTurtlesStory
from ._renowned_master import RenownedMasterStory
from ._saints_day_riot import SaintsDayRiotStory
from ._school_attack import SchoolAttackStory
from ._stolen_treasures import StolenTreasuresStory
from ._strange_dreams import StrangeDreamsStory
from ._student_rivalry import StudentRivalryStory
from ._wrong_pouch import WrongPouchStory


def get_all_stories() -> List[Type[BaseStory]]:
    return _all_stories
