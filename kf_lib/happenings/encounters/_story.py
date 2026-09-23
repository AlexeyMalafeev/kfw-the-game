from kf_lib.utils import rnd
from ._base_encounter import BaseEncounter


# misc chances
CH_STORY_DEVELOPS = 0.07


class ContinueStory(BaseEncounter):
    def check_if_happens(self):
        p = self.player
        s = p.current_story
        # never advance a story while the player is KO'd/inactive; the story
        # just waits (random_encounters also skips inactive players outright)
        return s and not p.inactive and rnd() <= CH_STORY_DEVELOPS

    def run(self):
        s = self.player.current_story
        s.advance()



