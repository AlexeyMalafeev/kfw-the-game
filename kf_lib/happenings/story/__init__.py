"""To add a story, implement it as a subclass of BaseStory in a separate module using one of the
existing stories as a reference.
After this, it is sufficient to import the new story here like others below."""

from typing import List, Type

from ._base_story import BaseStory, _all_stories
from ._bandit_fiance import BanditFianceStory
from ._foreigner import ForeignerStory
from ._ninja_turtles import NinjaTurtlesStory
from ._renowned_master import RenownedMasterStory
from ._stolen_treasures import StolenTreasuresStory
from ._strange_dreams import StrangeDreamsStory


def get_all_stories() -> List[Type[BaseStory]]:
    return _all_stories
