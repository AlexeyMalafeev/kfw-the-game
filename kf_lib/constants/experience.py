# base constants
DEFAULT_BASE_EXP = 20
DRAW_EXP_DIVISOR = 2
EXP_PER_LEVEL = 100


def set_base_exp(value):
    """Set the base exp value and recompute all derived exp constants.

    Read the constants as module attributes (experience.SCHOOL_TRAINING_EXP etc.),
    not via from-imports, so that a tweaked base takes effect at runtime."""
    global BASE_FIGHT_EXP, _BASE, ACCOMPL_EXP, BOOK_EXP, DREAM1_EXP, DREAM2_EXP, \
        DREAM3_EXP, HOME_TRAINING_EXP, LOSER_EXP, MASTER_TRAINING_EXP, \
        SCHOOL_TRAINING_EXP, SPECTATE_FOREIGNER_EXP
    BASE_FIGHT_EXP = _BASE = value
    # derived
    ACCOMPL_EXP = round(_BASE * 2.5)
    BOOK_EXP = (round(_BASE * 0.25), _BASE)
    DREAM1_EXP = round(_BASE * 0.5)
    DREAM2_EXP = _BASE
    DREAM3_EXP = round(_BASE * 1.5)
    HOME_TRAINING_EXP = round(_BASE * 0.15)
    LOSER_EXP = round(_BASE * 0.1)
    MASTER_TRAINING_EXP = round(_BASE * 0.4)
    SCHOOL_TRAINING_EXP = round(_BASE * 0.4)
    SPECTATE_FOREIGNER_EXP = (round(_BASE * 0.25), round(_BASE * 0.75))


set_base_exp(DEFAULT_BASE_EXP)
