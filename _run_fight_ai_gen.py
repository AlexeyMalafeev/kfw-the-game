from kf_lib.ai import fight_ai, fight_ai_gen

try:
    ga = fight_ai_gen.GeneticAlgorithm(
        pop_size=64,
        gene_names=fight_ai.GENETIC_AI_PARAM_NAMES,
        mut_prob=0.1,
        infighting=True,
        comment='',
    )
    ga.run(100)
    input('Press Enter to exit')


except Exception: # noqa
    import traceback
    traceback.print_exc()
    input('Press Enter to exit')
