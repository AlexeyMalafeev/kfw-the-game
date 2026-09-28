from kf_lib.i18n import _, tr_fighter_name, tr_name

COLUMN_INTERVAL = 2

# order doesn't matter
# it is safe to add new stats - that won't break the saved games

DEFAULT_STATS = (
    ('all_schools_tourn_won', 0),
    ('aston_victory', None),  # tuple: (date, p.level, [enemies], big opp_to_self_pwr_ratio)
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
    ('humil_defeat', None),  # tuple: (date, p.level, [enemies], small opp_to_self_pwr_ratio)
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
    ('strikes_landed', 0),
    ('strikes_thrown', 0),
    ('dam_dealt', 0),
    ('max_blow_dam', 0),
    ('max_blow_move', '--'),
    ('criticals', 0),
    ('epics', 0),
    ('super_herbs_obtained', 0),
    ('students_tourn_won', 0),
    ('times_koed', 0),
    ('tourn_won', 0),
)


def get_blank_stats_dict():
    return dict(DEFAULT_STATS)


def get_full_report(game_instance):
    g = game_instance
    labels = get_player_data(g.current_player, labels_only=True)
    report = [[lab] for lab in labels]
    for p in g.players:
        data = get_player_data(p, data_only=True)
        for i, d in enumerate(data):
            report[i].append(d)
    return report


def get_full_report_string(game_instance):
    g = game_instance
    report = get_full_report(g)
    num_columns = len(report[0])
    lines = [[] for _ in report]
    for ncol in range(num_columns):
        width = max((len(str(x[ncol])) for x in report)) + COLUMN_INTERVAL
        for k, line in enumerate(report):
            lines[k].append('{:<{}}'.format(line[ncol], width))
    lines = [''.join(line) for line in lines]
    lines = [g.get_date()] + lines
    return '\n'.join(lines)


# todo refactor game_stats.get_player_data
def get_player_data(p, labels_only=False, data_only=False):
    gs = p.get_stat
    ft = p.game.fights_total
    nf = gs('num_fights')
    fpcnt = round(nf / ft * 100) if ft > 0 else '-'
    sl = gs('strikes_landed')
    st = gs('strikes_thrown')
    slpcnt = round(sl / st * 100) if st else '-'
    fav_move = p.get_favorite_move(attack_only=True)
    feared_move = p.get_most_feared_move()
    max_blow_move = gs('max_blow_move')
    full = [
        (_('\n*GENERAL*'), ''),
        (_('Name'), tr_fighter_name(p.name)),
        (_('Style'), p.get_style_string()),
        (_('Level (Exp.)'), f'{p.level} ({p.exp})'),
        (_('Strength'), f"{p.get_att_str('strength')}"),
        (_('Agility'), f"{p.get_att_str('agility')}"),
        (_('Speed'), f"{p.get_att_str('speed')}"),
        (_('Health'), f"{p.get_att_str('health')}"),
        (_('Techs'), len(p.techs)),
        (_('Moves'), len(p.moves)),
        (_('\n*FIGHTING*'), ''),
        (_('Fights ({})').format(ft), f'{nf} ({fpcnt}%)'),
        (_('Wins,KOs'), '{},{}'.format(gs('fights_won'), gs('num_kos'))),
        (_('Strikes landed'), f'{sl}/{st} ({slpcnt}%)'),
        (_('Damage dealt'), gs('dam_dealt')),
        (_('Crits,EPICs'), '{},{}'.format(gs('criticals'), gs('epics'))),
        (_('Fav. move'), tr_name(fav_move) if fav_move else '-'),
        (_('Feared move'), tr_name(feared_move) if feared_move else '-'),
        (
            _('Max blow'),
            '{} ({})'.format(
                gs('max_blow_dam'),
                tr_name(max_blow_move) if max_blow_move != '--' else max_blow_move,
            ),
        ),
        (_('Exp bonuses'), gs('exp_bonuses')),
        (_('KOed,days inac.'), '{},{}'.format(gs('times_koed'), gs('days_inactive'))),
        (_('Tourn.won'), '{}/{}'.format(gs('tourn_won'), gs('num_tourn'))),
        (_('\n*LIFE*'), ''),
        (_('Became master'), gs('became_master')),
        (_('...at lv.'), gs('became_master_at_lv')),
        (_('Friends'), str(len(p.friends))),
        (_('Enemies'), str(len(p.enemies))),
        (_('Spouse'), tr_fighter_name(p.sweetheart.name) if p.is_married else '-'),
        (_('Children'), str(len(p.children_ages)) if p.children_ages else '-'),
        (_('Students'), str(p.students)),
        (_('Stud.tourn.won'), gs('students_tourn_won')),
        (_('A.-S.tourn.won'), gs('all_schools_tourn_won')),
        (_('Accomp,stories'), '{},{}'.format(len(p.accompl), gs('num_stories'))),
        (_('Got drunk'), gs('got_drunk')),
        (_('Reputation'), p.reputation),
        (_('Fame'), f'{p.get_fame():.0%}' if p.is_master else ''),
        (_('\n*MONEY*'), ''),
        (_('Money'), p.money),
        (_('Money earned'), gs('money_earned')),
        (_('Rewards,prizes'), '{},{}'.format(gs('rew_money_earned'), gs('prize_money_earned'))),
        (_('Spent on train.'), gs('spent_on_training')),
        (_('Donated'), gs('donated')),
        (_('Gamb.won,lost'), '{},{}'.format(gs('gamb_won'), gs('gamb_lost'))),
        (_('Robbed,stolen'), '{},{}'.format(gs('money_robbed'), gs('stolen_from'))),
        (_('\n*ITEMS*'), ''),
        (_('Bought/total'), '{}/{}'.format(gs('items_bought'), gs('items_obtained'))),
        (_('Found,lost'), '{},{}'.format(gs('items_found'), gs('items_lost'))),
        (_('Used:ft,med'), '{},{}'.format(gs('fight_items_used'), gs('healers_used'))),
        (_('Stolen by th.'), gs('items_stolen_from')),
        (_('Junk items b.'), gs('mock_items_bought')),
        (_('S.herbs obt.'), gs('super_herbs_obtained')),
    ]
    if labels_only:
        return [a for a, b in full]
    elif data_only:
        return [b for a, b in full]
    else:
        return full
