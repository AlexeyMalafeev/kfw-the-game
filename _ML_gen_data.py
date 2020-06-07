from ml import ml_fighter_pwr


try:
    examples = 10000
    ml_fighter_pwr.generate_data(examples=examples)


except Exception:
    import traceback
    traceback.print_exc()
    input('Press Enter to exit')