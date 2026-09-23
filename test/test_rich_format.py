import pytest

from kf_lib.ui import _rich_format as rf
from kf_lib.ui import align_text, pretty_table


@pytest.fixture(autouse=True)
def restore_colors_state():
    was_enabled = rf.colors_enabled()
    yield
    rf.set_colors_enabled(was_enabled)


class TestRender:
    def test_simple_tag(self):
        rf.set_colors_enabled(True)
        assert rf.render('[red]hi[/red]') == '\x1b[31mhi\x1b[0m'

    def test_compound_tag(self):
        rf.set_colors_enabled(True)
        assert rf.render('[bold red]hi[/]') == '\x1b[1;31mhi\x1b[0m'

    def test_nested_tags_reopen_outer(self):
        rf.set_colors_enabled(True)
        out = rf.render('[cyan]a[red]b[/red]c[/cyan]')
        assert out == '\x1b[36ma\x1b[31mb\x1b[0m\x1b[36mc\x1b[0m'

    def test_literal_brackets_untouched(self):
        rf.set_colors_enabled(True)
        assert rf.render('Press [Enter] now') == 'Press [Enter] now'

    def test_colors_off_strips_tags(self):
        rf.set_colors_enabled(False)
        assert rf.render('[red]hi[/red] [Enter]') == 'hi [Enter]'

    def test_no_brackets_fast_path(self):
        rf.set_colors_enabled(True)
        assert rf.render('plain text') == 'plain text'


class TestAutoColor:
    def test_coins(self):
        rf.set_colors_enabled(True)
        assert rf.render('pays 100 coins') == 'pays \x1b[33m100 coins\x1b[0m'

    def test_hyphenated_coin(self):
        rf.set_colors_enabled(True)
        assert rf.render('a 50-coin prize') == 'a \x1b[33m50-coin\x1b[0m prize'

    def test_signed_amount(self):
        rf.set_colors_enabled(True)
        assert rf.render('(-30 coins)') == '(\x1b[33m-30 coins\x1b[0m)'

    def test_exp(self):
        rf.set_colors_enabled(True)
        assert rf.render('gains 10 exp.') == 'gains \x1b[32m10 exp\x1b[0m.'

    def test_bare_words_not_colored(self):
        rf.set_colors_enabled(True)
        assert rf.render('fights for coins, no exp') == 'fights for coins, no exp'

    def test_colors_off_no_tags_left(self):
        rf.set_colors_enabled(False)
        assert rf.render('pays 100 coins, gains 10 exp') == 'pays 100 coins, gains 10 exp'


class TestStripAndMeasure:
    def test_strip_tags(self):
        assert rf.strip_tags('[red]a[bold]b[/bold]c[/]') == 'abc'

    def test_strip_keeps_literal_brackets(self):
        assert rf.strip_tags('[1] [Enter] ok') == '[1] [Enter] ok'

    def test_visible_len(self):
        assert rf.visible_len('[bold]Name[/bold]: [red]5[/red]') == len('Name: 5')

    def test_style_helper(self):
        assert rf.style('x', 'bold red') == '[bold red]x[/bold red]'
        assert rf.red('x') == '[red]x[/red]'


class TestWidthAwareFormatting:
    def test_align_text_ignores_tags(self):
        text = 'word ' + rf.red('colored') + ' word'
        aligned = align_text(text, 0, 60)
        for line in aligned.split('\n'):
            assert rf.visible_len(line) <= 60

    def test_align_text_same_layout_as_plain(self):
        plain = 'alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi'
        colored = f'alpha {rf.red("beta gamma")} delta {rf.bold("epsilon")} zeta eta theta iota kappa lambda mu nu xi'
        assert align_text(colored, 0, 40) == align_text(plain, 0, 40).replace(
            'beta gamma', rf.red('beta gamma')
        ).replace('epsilon', rf.bold('epsilon'))

    def test_pretty_table_pads_by_visible_width(self):
        table = [(rf.red('abc'), 'x'), ('de', 'y')]
        out = pretty_table(table)
        lines = out.split('\n')
        assert rf.visible_len(lines[0]) == rf.visible_len(lines[1])
