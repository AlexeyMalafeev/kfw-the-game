"""The punching bag: a training target for the Punching Bag mini-game and the
main game's practice (State > Moves > Punching Bag). Fights against it live in
kf_lib/fighting/fight/_bag_fights.py."""
from kf_lib.kung_fu import styles
from .fighter import Fighter

BAG_NAME = 'Punching Bag'
BAG_HP = 9999  # far more than a round can take: the bag is never knocked out
# ASCII art (moves/ascii_mapping.txt): hanging still / swinging after a hit
ART_STILL = 'Punching Bag'
ART_HIT = 'Punching Bag Hit'
HIT_ARTS = {'Hit', 'Hit Effect', 'Knockback'}


class PunchingBag(Fighter):
    """Takes every hit: no turns (bag fights never queue it), no dodging or
    blocking, no statuses, no bleeding or gasping, no knock-out."""

    is_living = False

    def __init__(self):
        super().__init__(
            BAG_NAME, styles.NO_STYLE.name, 1, atts_tuple=(1, 1, 1, 1),
            tech_names=[], move_names=[],
        )

    def prepare_for_fight(self):
        super().prepare_for_fight()
        self.hp_max = self.hp = BAG_HP
        self.toughness = 0
        self.dam_reduc = 0.0

    def set_ascii(self, ascii_name):
        """The fighter pictures a strike would set become the bag's own."""
        super().set_ascii(ART_HIT if ascii_name in HIT_ARTS else ART_STILL)

    def calc_dfs(self):
        self.to_dodge = self.to_block = 0
        self.dfs_pwr = 0

    def take_damage(self, dam):
        # only an instant knock-out takes all of a bag's HP; a bag just swings
        super().take_damage(min(dam, self.hp - 1))

    # a bag doesn't fall, lose balance, get stunned, shocked or slowed down
    def cause_fall(self):
        pass

    def cause_off_balance(self, brief=False):
        pass

    def cause_shock(self):
        pass

    def cause_slow_down(self):
        pass

    def cause_stun(self):
        pass

    def try_counter(self):
        pass

    def say_prefight_quote(self):
        return False

    def say_win_quote(self):
        pass
