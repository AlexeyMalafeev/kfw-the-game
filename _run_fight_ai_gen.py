from kf_lib.ai import fight_ai, fight_ai_gen

try:
    # ga = fight_ai_gen.GeneticAlgorithm(
    #     pop_size=16,
    #     # n_fights_per_setting=16,
    #     n_fights_per_setting=1,
    #     gene_names=fight_ai.GENETIC_AI_PARAM_NAMES,
    #     mutation_prob=0.1,
    #     infighting=True,
    # )
    # ga.run(3)

    ga = fight_ai_gen.GeneticAlgorithm(
        pop_size=64,
        # n_fights_per_setting=64,
        n_fights_1on1=8,
        n_fights_crowd=2,
        gene_names=fight_ai.GENETIC_AI_PARAM_NAMES,
        mutation_prob=0.1,
        infighting=False,
    )
    ga.run(3)

    input('Press Enter to exit')


except Exception: # noqa
    import traceback
    traceback.print_exc()
    input('Press Enter to exit')
