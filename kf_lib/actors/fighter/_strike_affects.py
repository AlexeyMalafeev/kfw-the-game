


class StrikeAffectVictim:
    took_damage = False

    def take_damage(self, dam):
        self.change_hp(-dam)
        self.took_damage = True
