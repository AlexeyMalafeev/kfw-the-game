class FightAttributes:
    act_allies = []
    act_targets = []
    action = None
    atk_bonus = 0
    atk_pwr = 0
    av_moves = []
    current_fight = None  # ...Fight object
    dam = 0
    defended = False
    dfs_bonus = 1.0  # for moves like Guard
    dfs_penalty_mult = 1.0
    dfs_pwr = 0
    distances = {}  # fighter_obj: int
    is_auto_fighting = True
    previous_actions = ['', '', '']
    qp_start = 0.0  # portion of total
    stamina_factor = 1.0
    status = {}  # {'status_name': status_dur}
    target = None  # used both for attacker and defender
    to_block = 0
    to_dodge = 0
    to_hit = 0

    def add_status(self, status, dur):
        if status not in self.status:
            self.status[status] = 0
        self.status[status] += dur

    def check_status(self, status):
        return self.status.get(status, False)

    def get_status_marks(self):
        slowed_down = ',' if self.check_status('slowed down') else ''
        off_bal = '\'' if self.check_status('off-balance') else ''
        lying = '...' if self.check_status('lying') else ''
        excl = 0
        if self.check_status('shocked'):
            excl = 2
        elif self.check_status('stunned'):
            excl = 1
        inact = '!' * excl
        padding = ' ' if lying or inact else ''
        return f'{padding}{slowed_down}{off_bal}{lying}{inact}'
