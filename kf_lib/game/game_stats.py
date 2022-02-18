COLUMN_INTERVAL = 2

# order doesn't matter
# it is safe to add new stats - that won't break the saved games

DEFAULT_STATS = (
    ('aston_victory', None),  # tuple: (date, p.level, [enemies], big ratio)
    ('bad_luck', 0),
    ('became_master', '--'),
    ('became_master_at_lv', 0),
    ('days_inactive', 0),
    ('donated', 0),
    ('exp_bonuses', 0),
    ('fight_items_used', 0),
    ('fights_won', 0),
    ('gamb_lost', 0),
    ('gamb_won', 0),
    ('good_luck', 0),
    ('got_drunk', 0),
    ('healers_used', 0),
    ('humil_defeat', None),  # tuple: (date, p.level, [enemies], small ratio)
    ('items_bought', 0),
    ('items_found', 0),
    ('items_lost', 0),
    ('items_obtained', 0),
    ('items_stolen_from', 0),
    ('mock_items_bought', 0),
    ('money_earned', 0),
    ('money_robbed', 0),
    ('num_fights', 0),
    ('num_kos', 0),
    ('num_stories', 0),
    ('num_tourn', 0),
    ('prize_money_earned', 0),
    ('rew_money_earned', 0),
    ('spent_on_training', 0),
    ('stolen_from', 0),
    ('super_herbs_obtained', 0),
    ('times_koed', 0),
    ('tourn_won', 0),
)


def get_blank_stats_dict():
    return dict(DEFAULT_STATS)


# todo refactor game_stats.get_player_data
def get_player_data(p, labels_only=False, data_only=False):
    gs = p.get_stat
    ft = p.game.fights_total
    nf = gs('num_fights')
    fpcnt = round(nf / ft * 100) if ft > 0 else '-'
    full = [
        ('\n*GENERAL*', ''),
        ('Name', p.name),
        ('Style', p.get_style_string()),
        ('Level (Exp.)', f'{p.level} ({p.exp})'),
        ('Strength', f"{p.get_att_str('strength')}"),
        ('Agility', f"{p.get_att_str('agility')}"),
        ('Speed', f"{p.get_att_str('speed')}"),
        ('Health', f"{p.get_att_str('health')}"),
        ('Techs', len(p.techs)),
        ('Moves', len(p.moves)),
        ('\n*FIGHTING*', ''),
        (f'Fights ({ft})', f'{nf} ({fpcnt}%)'),
        ('Wins,KOs', '{},{}'.format(gs('fights_won'), gs('num_kos'))),
        ('Exp bonuses', gs('exp_bonuses')),
        ('KOed,days inac.', '{},{}'.format(gs('times_koed'), gs('days_inactive'))),
        ('Tourn.won', '{}/{}'.format(gs('tourn_won'), gs('num_tourn'))),
        ('\n*LIFE*', ''),
        ('Became master', gs('became_master')),
        ('...at lv.', gs('became_master_at_lv')),
        ('Friends', str(len(p.friends))),
        ('Enemies', str(len(p.enemies))),
        ('Students', str(p.students)),
        ('Accomp,stories', '{},{}'.format(len(p.accompl), gs('num_stories'))),
        ('Got drunk', gs('got_drunk')),
        ('Reputation', p.reputation),
        ('\n*MONEY*', ''),
        ('Money', p.money),
        ('Money earned', gs('money_earned')),
        ('Rewards,prizes', '{},{}'.format(gs('rew_money_earned'), gs('prize_money_earned'))),
        ('Spent on train.', gs('spent_on_training')),
        ('Donated', gs('donated')),
        ('Gamb.won,lost', '{},{}'.format(gs('gamb_won'), gs('gamb_lost'))),
        ('Robbed,stolen', '{},{}'.format(gs('money_robbed'), gs('stolen_from'))),
        ('\n*ITEMS*', ''),
        ('Bought/total', '{}/{}'.format(gs('items_bought'), gs('items_obtained'))),
        ('Found,lost', '{},{}'.format(gs('items_found'), gs('items_lost'))),
        ('Used:ft,med', '{},{}'.format(gs('fight_items_used'), gs('healers_used'))),
        ('Stolen by th.', gs('items_stolen_from')),
        ('Junk items b.', gs('mock_items_bought')),
        ('S.herbs obt.', gs('super_herbs_obtained')),
    ]
    if labels_only:
        return [a for a, b in full]
    elif data_only:
        return [b for a, b in full]
    else:
        return full


class StatGen(object):
    def __init__(self, game):
        self.game = game

    def get_full_report(self):
        g = self.game
        labels = get_player_data(g.current_player, labels_only=True)
        report = [[lab] for lab in labels]
        for p in g.players:
            data = get_player_data(p, data_only=True)
            for i, d in enumerate(data):
                report[i].append(d)
        return report

    def get_full_report_string(self):
        g = self.game
        report = self.get_full_report()
        num_columns = len(report[0])
        lines = [[] for _ in report]
        for ncol in range(num_columns):
            width = max((len(str(x[ncol])) for x in report)) + COLUMN_INTERVAL
            for k, line in enumerate(report):
                lines[k].append('{:<{}}'.format(line[ncol], width))

        lines = [''.join(line) for line in lines]
        lines = [g.get_date()] + lines
        return '\n'.join(lines)
