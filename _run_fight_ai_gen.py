from kf_lib import fight_ai
from kf_lib import fight_ai_gen

try:
    # ga = fight_ai_gen.GeneticAlgorithm(pop_size=20, n_genes=5, gene_names=fight_ai.GENETIC_AI_PARAM_NAMES,
    #                                    n_top=10, mut_prob=0.1)
    ga = fight_ai_gen.GeneticAlgorithm(pop_size=32, n_genes=5, gene_names=fight_ai.GENETIC_AI_PARAM_NAMES,
                                       n_top=16, mut_prob=0.1, comment='infighting fixed')
    ga.run(30)
    input('Press Enter to exit')

except Exception:
    import traceback
    traceback.print_exc()
    input('Press Enter to exit')
