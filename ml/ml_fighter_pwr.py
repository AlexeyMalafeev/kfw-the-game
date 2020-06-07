import numpy as np
import pandas as pd


from kf_lib.experience import extract_features
from kf_lib.fighter_factory import new_fighter, new_prize_fighter
from kf_lib.fight import AutoFight
from kf_lib.utilities import *
#from .experience import extract_features
# from .fighter_factory import new_fighter, new_prize_fighter
# from .fight import AutoFight
# from .utilities import *


np.random.seed(0)

feature_labels_str = 'lv1,lv2,lvrel,att1,att2,attrel,tech1,tech2,techrel,n1,n2,nrel,y'
feature_labels = feature_labels_str.split(',')


def generate_data(examples=1000, min_lv=1, max_lv=20, max_n=8, group_fight_chance=0.5,
                  one_vs_many_subchance=0.5, tech_style_chance=0.75):
    data_file = open(os.path.join('ml', f'ML_fight_data m={examples}, lv={min_lv}-{max_lv}, max_crowd={max_n}.csv'),
                     'a', encoding='utf-8')
    data_file.write(feature_labels_str)
    for i in range(examples):
        if not i % 100:
            print(f'{i}/{examples}')
        if rnd() <= group_fight_chance:
            # group fight
            if rnd() <= one_vs_many_subchance:
                n_a = 1
            else:
                n_a = rndint(1, max_n)
            if rnd() <= tech_style_chance:
                fs1 = [new_fighter(lv=rndint(min_lv, max_lv)) for _ in range(n_a)]
            else:
                fs1 = [new_prize_fighter(lv=rndint(min_lv, max_lv)) for _ in range(n_a)]
            n_b = rndint(1, max_n)
            if rnd() <= tech_style_chance:
                fs2 = [new_fighter(lv=rndint(min_lv, max_lv)) for _ in range(n_b)]
            else:
                fs2 = [new_prize_fighter(lv=rndint(min_lv, max_lv)) for _ in range(n_b)]
            side_a = fs1
            side_b = fs2
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
        f = AutoFight(side_a=side_a, side_b=side_b)
        feat_vals.append(float(f.win))
        data_file.write('\n' + ','.join([str(val) for val in feat_vals]))
    print(f'Successfully generated {examples} examples.')
    data_file.close()


def learn_LR(data_file, feature_list=None):
    from sklearn.linear_model import LogisticRegression
    if feature_list is None:
        features = feature_labels[:-1]
    else:
        features = feature_list
    df = pd.read_csv(data_file)
    X = df[features]
    y = df[feature_labels[-1]]

    from sklearn.model_selection import train_test_split
    train_X, test_X, train_y, test_y = train_test_split(X, y, random_state=1)

    print('initializing the model')
    model = LogisticRegression(solver='lbfgs', random_state=0)
    print(f'training on {len(train_X)} samples')
    model.fit(train_X, train_y)

    print('predicting')
    h = model.predict(test_X)

    from sklearn.metrics import classification_report
    print(classification_report(test_y, h))
    clf = 'LR'
    n = len(df)
    feats = len(features)
    report_file = open(os.path.join('ml', f'ML report {clf} m={m} n={feats}.txt'), 'w', encoding='utf-8')
    print(classification_report(test_y, h), file=report_file)

    # REFERENCE, DO NOT DELETE!
    # print('coefficients =', model.coef_)
    # print('intercept =', model.intercept_)
    # # new = np.array([[0.94, 0.8, 4, 0.17]])
    # new = np.array([[0.94, 0.8, 4, 2.17]])
    # my_new = [1, 0.94, 0.8, 4, 2.17]  # first is for intercept
    # my_coef = [-8.85045241, 2.42517891, 0.23488417, 0.28182145, 5.22587173,]  # 0=intercept
    # my_neg_coef = [-x for x in my_coef]
    #
    # print('positive outcome:')
    # z = sum([my_new[j] * my_coef[j] for j in range(len(my_new))])
    # print('z =', z)
    # pos = sigmoid(z)
    # print('sigmoid =', pos)
    #
    # print('negative outcome:')
    # z = sum([my_new[j] * -my_coef[j] for j in range(len(my_new))])
    # print('z =', z)
    # neg = sigmoid(z)
    # print('sigmoid =', neg)
    #
    # tot = pos + neg
    # print('my probs:', pos/tot, neg/tot)
    #
    # print('predict =', model.predict(new))
    # print('predict_proba =', model.predict_proba(new))
    # print('y =', 1)
    # REFERENCE, DO NOT DELETE!

    coef_file = open(os.path.join('ml', f'ML LR coef m={m} n={feats}.txt'), 'w', encoding='utf-8')
    print('intercept:', model.intercept_, 'coefficients:', model.coef_, file=coef_file)


def learn_RFC(data_file, feature_list=None):
    from sklearn.ensemble import RandomForestClassifier
    if feature_list is None:
        features = feature_labels[:-1]
    else:
        features = feature_list
    df = pd.read_csv(data_file)
    X = df[features]
    y = df[feature_labels[-1]]

    from sklearn.model_selection import train_test_split
    train_X, test_X, train_y, test_y = train_test_split(X, y, random_state=1)

    print('initializing the model')
    model = RandomForestClassifier(n_jobs=2, random_state=0)
    print(f'training on {len(train_X)} samples')
    model.fit(train_X, train_y)

    print('predicting')
    h = model.predict(test_X)

    # View a list of the features and their importance scores
    print('feature importance scores:')
    print(list(zip(train_X, model.feature_importances_)))

    from sklearn.metrics import classification_report
    print(classification_report(test_y, h))
    clf = 'RFC'
    m = len(df)
    feats = len(features)
    report_file = open(os.path.join('ml', f'ML report {clf} m={m} n={feats}.txt'), 'w', encoding='utf-8')
    print(classification_report(test_y, h), file=report_file)

    #print(model.coef_)
