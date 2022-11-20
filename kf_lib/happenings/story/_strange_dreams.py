from ._base_story import BaseStory
from kf_lib.actors import fighter_factory
from kf_lib.constants.experience import DREAM1_EXP, DREAM2_EXP, DREAM3_EXP


class StrangeDreamsStory(BaseStory):
    min_level = 6
    max_level = 8

    def intro(self):
        g = self.game
        g.cls()
        g.show('Every so often one has some really unusual dreams...')
        g.pak()

    def reward(self):
        p = self.player
        p.add_accompl('Beat Self')
        p.gain_exp(DREAM3_EXP)
        p.pak()

    def scene1(self):
        p = self.player
        p.write(f'{p.name} has a strange dream...')
        p.choose_best_norm_wp()
        ens = fighter_factory.new_opponent(n=4, rand_atts_mode=0)
        for en in ens:
            en.arm('chopsticks')
        if p.spar(ens[0], en_allies=ens[1:]):
            p.gain_exp(DREAM1_EXP)
            p.pak()

    def scene2(self):
        p = self.player
        p.write(f'{p.name} has a strange dream...')
        p.pak()
        en = fighter_factory.new_monster(lv=p.level)
        en.name = 'Weird ' + en.name
        if p.spar(en):
            p.gain_exp(DREAM2_EXP)
            p.pak()

    def scene3(self):
        p = self.player
        p.write(f'{p.name} has a strange dream...')
        p.pak()
        en = fighter_factory.copy_fighter(p)
        en.__class__ = fighter_factory.Fighter
        if p.spar(en):
            self.reward()

        # end of the story
        self.end()
