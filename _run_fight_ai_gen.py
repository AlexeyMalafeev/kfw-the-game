from kf_lib.ai import fight_ai, fight_ai_gen

try:
    # ga = fight_ai_gen.GeneticAlgorithm(pop_size=20, n_genes=5, gene_names=fight_ai.GENETIC_AI_PARAM_NAMES,
    #                                    n_top=10, mut_prob=0.1)
    ga = fight_ai_gen.GeneticAlgorithm(
        pop_size=32,
        n_genes=5,
        gene_names=fight_ai.GENETIC_AI_PARAM_NAMES,
        n_top=16,
        mut_prob=0.1,
        comment='',
    )
    ga.run(30)
    input('Press Enter to exit')


except Exception:
    import traceback
    traceback.print_exc()
    input('Press Enter to exit')
