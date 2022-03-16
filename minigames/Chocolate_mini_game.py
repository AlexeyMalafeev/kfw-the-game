import os
import sys
from pathlib import Path
# this has to be before imports from kf_lib
lib_path = Path('..').resolve()
os.chdir(lib_path)
if lib_path not in sys.path:
    sys.path.append(str(lib_path))


# todo fix Chocolate mini-game, it's not working now


from kf_lib import game
from kf_lib.actors import fighter_factory as ff
from kf_lib import human_player
from kf_lib.kung_fu import styles, moves
from kf_lib.ui import pak


class Zen(human_player.HumanPlayer):
    def can_learn_new_tech(self):
        pass

    def choose_new_move(self):
        pass

    def choose_new_tech(self):
        pass

    def choose_tech_to_upgrade(self):
        pass

    def gain_exp(self, amount, silent=False):
        pass

    def log(self, text):
        pass

    def set_rand_moves(self):
        for m in moves.BASIC_MOVES:
            self.learn_move(m.name, silent=True)  # 'silent' is not to write in the log about learning basic moves

    def set_rand_techs(self):
        pass


def main():
    print(' ***Welcome to Chocolate***')
    pak()
    g = game.Game()
    p = Zen(name="Zen", style=styles.ZENS_STYLE, level=12, atts_tuple=(5, 10, 7, 5))
    # Scene 1 Teen Gang - 4 opp, kicks and evade
    # Scene 2 Ice - Bruce Lee 'Explosive Strikes', 'Hurricane Legs', boss armed with an axe, roundhouse and spin
    # Scene 3 Warehouse - Jackie Chan 'Behind You', environment, some enemies with sticks
    # Scene 4 Meat - cleavers, wield pole
    # Scene 5 Tension - tough opponents * 3, Tony Jaa 'Mighty Elbows', 'Mighty Knees'
    # Scene 6 Katana - 'Flying Strikes', bare-handed first, epileptic fighter more elbows and knees, weild katana; 
    # father, mother? mafia boss, twin sheath
    # Scene 7 Anger - boss and henchmen, tough thug
    p.game = g
    # play = True
    # attempts = 3
    # score = 0
    # difficulty = menu([('easy', 0.8), ('normal', 1.0), ('hard', 1.2), ('extreme', 1.5)], "Choose the difficulty:")

    # s_name, allies, opponents, techs, moves
    scenes = (('Scene 1 - Teen Gang', [],
               ff.new_f('Teen Thug', 'Dirty Fighting', 1, n=4),
               ['Shadow of a Shadow', 'Strong as an Ox'],
               ['Jumping Kick']),

              ('Scene 2 - Ice', [],
               [ff.new_f('Boss', 'Dirty Fighting', 3, weapon='axe')] + ff.new_f('Worker', 'Dirty Fighting', 1, n=5),
               ['Hurricane Legs', 'Explosive Strikes'],
               ['Roundhouse Kick', 'Spin Kick']),

              ('Scene 3 - Factory', [],
               [ff.new_f('Boss', 'Dirty Fighting', 3)] + ff.new_f('Worker', 'Dirty Fighting', 1, n=3) +
               ff.new_f('Armed Worker', 'Dirty Fighting', 1, n=4, weapon='stick'),
               ['Behind You All', 'Environment Domination'],
               ['Dragon Block', 'Dragon Evasion']),

              ('Scene 4 - Meat', [],
               [ff.new_f('Boss', 'Dirty Fighting', 4, weapon='knife')] +
               ff.new_f('Butcher', 'Dirty Fighting', 1, n=5) +
               ff.new_f('Armed Butcher', 'Dirty Fighting', 1, n=4, weapon='knife'),
               ['Flying Monkey and Golden Fox', 'Anything Is a Weapon'],
               ['Energy Kick']),

              ('Scene 5 - Tension', [],
               ff.new_f('Tough Thug', 'Muai Thai', 10, n=3),
               ['Mighty Elbows', 'Mighty Knees'],
               ['Dragon Elbow', 'Jumping Knee', 'Volcano Knee']),
              )
    for s_name, s_allies, s_opps, s_techs, s_moves in scenes:
        p.cls()
        p.show(s_name)
        p.pak()
        p.learn_tech(*s_techs)
        for m in s_moves:
            p.learn_move(m)
        print('Zen:', p.get_exp_worth(), 'opponents:', sum((op.get_exp_worth() for op in s_opps)))
        p.pak()
        while True:  # but enemies that lost their weapons will not have them again, even if you lose
            if p.fight(s_opps[0], allies=s_allies, en_allies=s_opps[1:], hide_stats=False):
                break
    print(' ***Game over***')
    pak()


try:
    main()

except Exception:
    import traceback
    traceback.print_exc()
    input('Press Enter to exit')
