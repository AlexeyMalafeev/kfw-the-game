"""Distance column formatting in the learn-move menu."""
from kf_lib.actors.human_controlled_fighter import format_move_distance
from kf_lib.kung_fu.moves import Move


def make_move(distance, dist_change):
    return Move(name='Test Move', distance=distance, dist_change=dist_change)


class TestFormatMoveDistance:
    def test_no_dist_change(self):
        assert format_move_distance(make_move(2, 0)) == '2'

    def test_retreating_strike(self):
        assert format_move_distance(make_move(1, 1)) == '1->2'

    def test_charging_strike(self):
        assert format_move_distance(make_move(3, -1)) == '3->2'
