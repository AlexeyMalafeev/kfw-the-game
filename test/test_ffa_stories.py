"""End-to-end runs of the free-for-all story lines with AI players."""
import random

from kf_lib import game  # import first: avoids circular import via kf_lib.actors.player
from kf_lib.actors.player import SmartAIP


def make_game_and_player(seed=0, level=1):
    random.seed(seed)
    g = game.Game()
    g.new_game(
        num_players=2,
        coop=False,
        ai_only=True,
        auto_save_on=False,
        generated_styles=True,
        silent_ending=True,
        forced_aip_class=SmartAIP,
    )
    p = g.players[0]
    if level > 1:
        p.level_up(level - 1)
    return g, p


def run_story(g, p, story_name, max_advances=6):
    """Force-start a story and advance it to the end; return the story object."""
    s = g.stories[story_name]
    assert s.test(p), f'{story_name} should be available to {p.name} (lv {p.level})'
    s.start(p)
    for _ in range(max_advances):
        if p.current_story is None:
            break
        p.hp = p.hp_max
        p.inactive = 0
        s.advance()
    assert p.current_story is None, f'{story_name} stuck at state {s.state}'
    return s


class TestGrandMeleeStory:
    def test_completes_when_broke(self):
        g, p = make_game_and_player(seed=1, level=5)
        p.money = 0
        s = run_story(g, p, 'GrandMeleeStory')
        assert s.state == -1

    def test_participation_paths(self):
        seen_night_melee = False
        for seed in range(12):
            g, p = make_game_and_player(seed=seed, level=6)
            p.money = 500
            s = g.stories['GrandMeleeStory']
            s.start(p)
            scenes = []
            for _ in range(5):
                if p.current_story is None:
                    break
                p.hp = p.hp_max
                p.inactive = 0
                scenes.append(s.state + 1)
                s.advance()
            assert p.current_story is None
            assert scenes[-1] == 4  # the reprimand always comes last
            if 3 in scenes:
                seen_night_melee = True
        assert seen_night_melee  # at least one run won the day melee


class TestSchoolBan:
    def test_ban_blocks_training_and_can_be_lifted(self):
        from kf_lib.actors.player import _base_player

        g, p = make_game_and_player(seed=2, level=5)
        p.banned_from_school = True
        old_exp = p.exp
        old_money = p.money
        _base_player.CH_MASTER_FORGIVES = 0.0
        _base_player.CH_BEG_BULLIED = 0.0
        try:
            p.practice_school()
            assert p.banned_from_school
            assert p.exp == old_exp and p.money == old_money  # no training, no tuition
            _base_player.CH_MASTER_FORGIVES = 1.0
            p.practice_school()
            assert not p.banned_from_school
        finally:
            _base_player.CH_MASTER_FORGIVES = 0.25
            _base_player.CH_BEG_BULLIED = 0.2

    def test_ban_is_saved(self):
        g, p = make_game_and_player(seed=3, level=5)
        p.banned_from_school = True
        from kf_lib.game._save_game import SaveGame
        data = SaveGame._player_to_data(g, p)
        assert data['atts']['banned_from_school'] is True


class TestSaintsDayRiotStory:
    def test_completes(self):
        for seed in range(6):
            g, p = make_game_and_player(seed=seed, level=7)
            run_story(g, p, 'SaintsDayRiotStory')


class TestJadeTableStory:
    def test_completes_and_lose_branch_makes_enemy(self):
        saw_win = saw_loss = False
        for seed in range(16):
            g, p = make_game_and_player(seed=seed, level=11)
            s = run_story(g, p, 'JadeTableStory')
            if 'Jade Table' in p.accompl:
                saw_win = True
            else:
                saw_loss = True
                assert s.boss is None  # kept registered as a persistent enemy
                assert p.enemies and p.enemies[-1].name in g.fighters_dict
        assert saw_win and saw_loss


class TestEightGatesStory:
    def test_gated_on_battle_royale_title(self):
        g, p = make_game_and_player(seed=4, level=12)
        s = g.stories['EightGatesStory']
        assert not s.test(p)
        p.accompl.append('Battle Royale Champion')
        assert s.test(p)

    def test_completes(self):
        for seed in range(6):
            g, p = make_game_and_player(seed=seed, level=12)
            p.accompl.append('Battle Royale Champion')
            run_story(g, p, 'EightGatesStory')


class TestWrongPouchStory:
    def test_completes_and_returns_money_on_win(self):
        saw_win = False
        for seed in range(12):
            g, p = make_game_and_player(seed=seed, level=6)
            p.money = 100
            s = g.stories['WrongPouchStory']
            s.start(p)
            stolen = s.stolen
            for _ in range(3):
                if p.current_story is None:
                    break
                p.hp = p.hp_max
                p.inactive = 0
                s.advance()
            assert p.current_story is None
            if 'Pouch Justice' in p.accompl:
                saw_win = True
                assert p.money >= stolen
        assert saw_win
