import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier


from .fighter_factory import new_fighter, new_prize_fighter
from .fight import AutoFight
from .utilities import *


np.random.seed(0)





def generate_data(examples=1000, min_lv=1, max_lv=20, max_n=8, group_fight_chance=0.5,
                  tech_style_chance=0.75):
    for i in range(examples):
        if rnd() <= group_fight_chance:
            # group fight
            pass
        else:
            # mano a mano
            if rnd() <= tech_style_chance:
                f1 = new_fighter(lv=rndint(min_lv, max_lv))
            else:
                f1 = new_prize_fighter(lv=rndint(min_lv, max_lv))
            if rnd() <= tech_style_chance:
                f2 = new_fighter(lv=rndint(min_lv, max_lv))
            else:
                f2 = new_prize_fighter(lv=rndint(min_lv, max_lv))
            side_a = [f1]
            side_b = [f2]
        feat_vals = extract_features(side_a, side_b)
        AutoFight(side_a=side_a, side_b=side_b)
        f.win