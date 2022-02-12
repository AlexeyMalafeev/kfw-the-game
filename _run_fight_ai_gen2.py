from kf_lib.ai import fight_ai, fight_ai_gen

try:
    # ga = fight_ai_gen.GeneticAlgorithm(
    #     pop_size=16,
    #     n_fights_1on1=8,
    #     n_fights_crowd=2,
    #     mutation_prob=0.1,
    #     infighting=True,
    # )
    # ga.run(128)

    ga = fight_ai_gen.GeneticAlgorithm(
        pop_size=64,
        n_fights_1on1=0,
        n_fights_crowd=32,
        mutation_prob=0.1,
        infighting=False,
    )
    ga.run(128)

    input('Press Enter to exit')


except Exception: # noqa
    import traceback
    traceback.print_exc()
    input('Press Enter to exit')
