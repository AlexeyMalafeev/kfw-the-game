from ._load_game import LoadGame
from ._new_game import NewGame
from ._playing import Playing
from ._save_game import SaveGame
from ._state_menu import StateMenu


class Game(LoadGame, NewGame, Playing, SaveGame, StateMenu):
    pass
