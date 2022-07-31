from . import BaseStory
from kf_lib.actors import fighter_factory
from kf_lib.kung_fu.styles import TURTLE_NUNJUTSU


class NinjaTurtlesStory(BaseStory):
    min_level = 12
    max_level = 15

    def intro(self):
        g = self.game
        g.cls()
        t = (
            'A sudden flash pierces the deep darkness of the night... Four figures appear, '
            'muscular and not quite human. They are wielding traditional Japanese weapons. '
            'Looking around in confusion, they speak in hushed tones, clearly deciding what to do '
            'next...'
        )
        g.show(t)
        g.pak()

    def reward(self):
        p = self.player
        p.add_accompl('TMNT')
        p.learn_tech(*list(TURTLE_NUNJUTSU.techs.values()))  # todo refactor this; make a helper?

    def scene1(self):
        p = self.player
        p.write(
            f'{p.name} encounters the four teenage mutant ninja turtles travelling in time.'
        )
        p.pak()
        opponents = fighter_factory.new_ninja_turtles()
        if p.fight(opponents[0], en_allies=opponents[1:], items_allowed=False):
            self.reward()

        # end of the story
        self.end()
