import os
import sys
from pathlib import Path
# this has to be before imports from kf_lib
lib_path = Path('..', '..').resolve()
os.chdir(lib_path)
if lib_path not in sys.path:
    sys.path.append(str(lib_path))


from ml import ml_fighter_pwr


try:
    file_name = os.path.join('../../ml', 'ML_fight_data m=10000, lv=1-20, max_crowd=8.csv')
    feature_lists = [None,  # default, all available features
                     ['lvrel', 'attrel', 'techrel', 'nrel', 'wprel'],
                     ['lv1', 'lv2', 'att1', 'att2', 'tech1', 'tech2', 'n1', 'n2', 'wp1', 'wp2']
                     ]
    for method in (ml_fighter_pwr.learn_rfc, ml_fighter_pwr.learn_logreg):
        for feat_list in feature_lists:
            method(file_name, feat_list)
    input('Press Enter to exit')


except Exception:
    import traceback
    traceback.print_exc()
    input('Press Enter to exit')
