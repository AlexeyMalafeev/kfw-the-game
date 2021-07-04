class FighterBase:
    level: int = 0
    name: str = ''
    style = None  # object

    def log(self, text):
        """Empty method for convenience."""
        pass

    def msg(self, *args, **kwargs):
        pass

    def pak(self):
        pass

    def show(self, text, align=False):
        pass
