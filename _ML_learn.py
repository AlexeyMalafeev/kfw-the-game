from kf_lib import ml_fighter_pwr


try:
    # ml_fighter_pwr.learn_LR('ML_fight_data_1K.csv')
    # ml_fighter_pwr.learn_LR('ML_fight_data_1K.csv',
    #                      feature_list=['lvrel', 'attrel', 'techrel', 'nrel'])
    # ml_fighter_pwr.learn_LR('ML_fight_data_10K.csv')
    # ml_fighter_pwr.learn_LR('ML_fight_data_10K.csv',
    #                         feature_list=['lvrel', 'attrel', 'techrel', 'nrel'])
    ml_fighter_pwr.learn_RFC('ML_fight_data_10K.csv')
    ml_fighter_pwr.learn_RFC('ML_fight_data_10K.csv',
                             feature_list=['lvrel', 'attrel', 'techrel', 'nrel'])

    input('Press Enter to exit')

except Exception:
    import traceback
    traceback.print_exc()
    input('Press Enter to exit')