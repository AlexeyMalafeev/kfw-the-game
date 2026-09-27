"""Russian localization: catalogs, display-name layer, quotes, render patterns."""
import random

import pytest

from kf_lib import game  # import first: avoids circular import via kf_lib.actors.player
from kf_lib import i18n
from kf_lib.i18n import _, ngettext, tr_fighter_name, tr_name, tr_style_name
from kf_lib.actors import fighter_factory
from kf_lib.actors import quotes
from kf_lib.fighting.fight import AutoFight
from kf_lib.ui import _rich_format as rf
from kf_lib.utils import _lang_tools as lt


@pytest.fixture
def russian():
    i18n.set_language('ru')
    yield
    i18n.set_language('en')


class TestEnglishDefault:
    def test_passthrough(self):
        assert i18n.get_language() == 'en'
        assert _('Back') == 'Back'
        assert tr_name('Punch') == 'Punch'
        assert tr_style_name('Swift-Striking Snow Viper') == 'Swift-Striking Snow Viper'
        assert tr_fighter_name('Beggar Wang') == 'Beggar Wang'

    def test_unknown_language_falls_back_to_en(self):
        i18n.set_language('xx')
        try:
            assert i18n.get_language() == 'en'
            assert _('Back') == 'Back'
        finally:
            i18n.set_language('en')


@pytest.mark.usefixtures('russian')
class TestRussian:
    def test_prose_catalog(self):
        assert _('Back') == 'Назад'
        assert _('Miss!') == 'Промах!'
        assert _('Choose a style') == 'Выберите стиль'

    def test_plural_forms(self):
        s = ' knocked back {dist} step!'
        p = ' knocked back {dist} steps!'
        assert ngettext(s, p, 1).format(dist=1) == ' отлетает на 1 шаг назад!'
        assert ngettext(s, p, 3).format(dist=3) == ' отлетает на 3 шага назад!'
        assert ngettext(s, p, 5).format(dist=5) == ' отлетает на 5 шагов назад!'

    def test_names_catalog(self):
        assert tr_name('Punch') == 'Удар кулаком'
        assert tr_name('Acrobatic Charging Claw') == 'Акробатический Рвущийся коготь'
        assert tr_name('Ginseng Root') == 'Корень женьшеня'
        assert tr_name('Lone Warrior') == 'Одинокий воин'
        assert tr_name('narrow-minded') == 'недалёкий'
        assert tr_name('staff') == 'посох'
        assert 'продвинутый' in tr_name('Advanced Bagua Zhang I')

    def test_generated_style_gender_agreement(self):
        # W3 'Viper' is feminine in Russian, so the adjectives take feminine forms
        assert tr_style_name('Swift-Striking Snow Viper') == 'Молниеносная Снежная Гадюка'
        assert tr_style_name('Snow Viper') == 'Снежная Гадюка'
        # 'Dragon' is masculine
        assert tr_style_name('Drunken Fire Dragon') == 'Пьяный Огненный Дракон'
        # handcrafted styles go through the plain catalog
        assert tr_style_name('Bagua Zhang') == 'Багуа Чжан'

    def test_fighter_name_prefix(self):
        assert tr_fighter_name('Beggar Wang') == 'Нищий Wang'
        assert tr_fighter_name('Thug 1') == 'Головорез 1'
        assert tr_fighter_name('Liu Kang') == 'Liu Kang'

    def test_quotes_loaded_in_russian(self):
        assert len(quotes.HERO_PREFIGHT) > 100
        assert any('ы' in q or 'а' in q for q in quotes.HERO_PREFIGHT[:5])
        first = quotes.WISDOM[0]
        assert first.startswith('Птица поёт')

    def test_lang_tools_dispatch(self):
        assert lt.add_article('saber') == 'saber'  # no articles in Russian
        assert lt.enum_words(['а', 'б', 'в']) == 'а, б и в'
        assert lt.sg_or_pl(5) == ''

    def test_render_ru_auto_color(self):
        rf.set_colors_enabled(True)
        try:
            out = rf.render('День 12')
            assert '\x1b[1mДень 12\x1b[0m' in out
            out = rf.render('получено 100 монет')
            assert '\x1b[33m100 монет\x1b[0m' in out
            out = rf.render('ур.5')
            assert '\x1b[36mур.5\x1b[0m' in out
        finally:
            rf.set_colors_enabled(False)

    def test_autofight_smoke(self):
        random.seed(0)
        fa = fighter_factory.new_fighter(5)
        fb = fighter_factory.new_fighter(5)
        f = AutoFight([fa], [fb])
        assert f.winners is not None

    def test_move_display_name(self):
        from kf_lib.kung_fu import moves

        m = moves.ALL_MOVES_DICT['Punch']
        assert m.name == 'Punch'  # identifier unchanged
        assert m.display_name == 'Удар кулаком'
