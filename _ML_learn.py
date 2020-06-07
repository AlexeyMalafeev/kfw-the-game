import os


from ml import ml_fighter_pwr


try:
    # ml_fighter_pwr.learn_LR('ML_fight_data_1K.csv')
    # ml_fighter_pwr.learn_LR('ML_fight_data_1K.csv',
    #                      feature_list=['lvrel', 'attrel', 'techrel', 'nrel'])
    # ml_fighter_pwr.learn_LR('ML_fight_data_10K.csv')
    # ml_fighter_pwr.learn_LR('ML_fight_data_10K.csv',
    #                         feature_list=['lvrel', 'attrel', 'techrel', 'nrel'])
    ml_fighter_pwr.learn_LR(os.path.join('ml', 'ML_fight_data_1K.csv'))
    ml_fighter_pwr.learn_LR(os.path.join('ml', 'ML_fight_data_1K.csv'),
                             feature_list=['lvrel', 'attrel', 'techrel', 'nrel'])
    ml_fighter_pwr.learn_LR(os.path.join('ml', 'ML_fight_data_1K.csv'),
                             feature_list=['lv1', 'lv2', 'att1', 'att2', 'tech1', 'tech2', 'n1', 'n2'])
    # 'lv1,lv2,lvrel,att1,att2,attrel,tech1,tech2,techrel,n1,n2,nrel,y'

    input('Press Enter to exit')


except Exception:
    import traceback
    traceback.print_exc()
    input('Press Enter to exit')
