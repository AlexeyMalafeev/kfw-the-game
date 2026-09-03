from kf_lib.utils import rnd
from ._base_encounter import BaseEncounter


# misc chances
CH_STORY_DEVELOPS = 0.07


class ContinueStory(BaseEncounter):
    def check_if_happens(self):
        p = self.player
        s = p.current_story
        return s and rnd() <= CH_STORY_DEVELOPS

    def run(self):
        s = self.player.current_story
        s.advance()



