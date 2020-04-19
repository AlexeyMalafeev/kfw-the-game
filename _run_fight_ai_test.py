#! python3

from kf_lib import fight_ai
from kf_lib import fight_ai_test
from kf_lib.utilities import *

try:
    write_log = True
    same_class_fights = False
    # AIs = (fight_ai.BaseAI, fight_ai.WeightedActionsAI, fight_ai.CarefulManeuvers5, fight_ai.NewSystemAI)
    # AIs = (fight_ai.BaseAI, fight_ai.WeightedActionsAI, fight_ai.CarefulManeuvers5)
    AIs = (fight_ai.BaseAI, fight_ai.WeightedActionsAI, fight_ai.GeneticAITrainedParams8,
           fight_ai.GeneticAIExtraRules4, fight_ai.GeneticAIExtraRules7, fight_ai.GeneticAIExtraRules9,
           fight_ai.GeneticAIAggro)
    if write_log:
        for AI in AIs:
            with open('{}.txt'.format(AI.__name__), 'w') as f:
                f.write('')
    # tests = (fight_ai_test.FightAITest, fight_ai_test.CrowdVsCrowd)
    # tests = (fight_ai_test.CrowdVsCrowd, fight_ai_test.CrowdVsCrowdFair)
    tests = (fight_ai_test.CrowdVsCrowdFair, fight_ai_test.FightAITest)
    scores = {test: {ai: 0 for ai in AIs} for test in tests}
    for i, AI1 in enumerate(AIs):
        for AI2 in AIs[i:]:
            if AI1 is AI2 and not same_class_fights:
                continue
            for test in tests:
                t = test(AI1, AI2, rep=500, write_log=write_log)
                scores[test][AI1] += t.wins[0]
                scores[test][AI2] += t.wins[1]
    # fight_ai_test.CrowdVsCrowd(fight_ai.BaseAI, fight_ai.WeightedActionsAI)
    # fight_ai_test.CrowdVsCrowdFair(fight_ai.BaseAI, fight_ai.WeightedActionsAI)
    # fight_ai_test.OneVsCrowd(fight_ai.BaseAI, fight_ai.WeightedActionsAI)
    total = {ai: 0 for ai in AIs}
    for test in tests:
        for ai, score in scores[test].items():
            total[ai] += score
    list_of_scores = [scores[test] for test in tests]
    legend = [test.__name__ for test in tests]
    list_of_scores.append(total)
    legend.append('Total')
    for i, scores in enumerate(list_of_scores):
        tups = []
        for ai in scores:
            tups.append((ai.__name__, scores[ai]))
        # print(scores)
        tups.sort(key=lambda x: x[1], reverse=True)
        print('-' * 80)
        print(legend[i])
        print(pretty_table(tups))
        print('{}\n\n{}'.format(get_time(), pretty_table(tups)), file=open('fight AI comparison.txt', 'w'))
    input('Press Enter to exit')

except Exception:
    import traceback
    traceback.print_exc()
    input('Press Enter to exit')
