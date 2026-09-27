"""Russian rendering of generated kung-fu style names.

Generated English style names are 'W1 W2 W3' (kf_lib/kung_fu/style_gen.py) with
W3 an animal noun; Russian adjectives must agree with the noun's gender, so the
word translations live here as data instead of the gettext catalog. Adjectives
are (masculine, feminine, neuter) forms; nouns are (nominative, gender index).
"""

W1_RU = {
    'Acrobatic': ('Акробатический', 'Акробатическая', 'Акробатическое'),
    'Attacking': ('Атакующий', 'Атакующая', 'Атакующее'),
    'Averting': ('Уклончивый', 'Уклончивая', 'Уклончивое'),
    'Balanced': ('Уравновешенный', 'Уравновешенная', 'Уравновешенное'),
    'Cautious': ('Осторожный', 'Осторожная', 'Осторожное'),
    'Clinging': ('Цепкий', 'Цепкая', 'Цепкое'),
    'Dancing': ('Танцующий', 'Танцующая', 'Танцующее'),
    'Defending': ('Защитный', 'Защитная', 'Защитное'),
    'Drunken': ('Пьяный', 'Пьяная', 'Пьяное'),
    'Elusive': ('Неуловимый', 'Неуловимая', 'Неуловимое'),
    'Exotic': ('Экзотический', 'Экзотическая', 'Экзотическое'),
    'Flying': ('Летающий', 'Летающая', 'Летающее'),
    'Furious': ('Яростный', 'Яростная', 'Яростное'),
    'Grappling': ('Борцовский', 'Борцовская', 'Борцовское'),
    'Guarding': ('Сторожевой', 'Сторожевая', 'Сторожевое'),
    'Indestructible': ('Несокрушимый', 'Несокрушимая', 'Несокрушимое'),
    'Invulnerable': ('Неуязвимый', 'Неуязвимая', 'Неуязвимое'),
    'Kicking': ('Ножной', 'Ножная', 'Ножное'),
    'Light-Footed': ('Легконогий', 'Легконогая', 'Легконогое'),
    'Long-Range': ('Дальнобойный', 'Дальнобойная', 'Дальнобойное'),
    'Mid-Range': ('Среднедистанционный', 'Среднедистанционная', 'Среднедистанционное'),
    'Mystic': ('Мистический', 'Мистическая', 'Мистическое'),
    'Open-Handed': ('Ладонный', 'Ладонная', 'Ладонное'),
    'Paralyzing': ('Парализующий', 'Парализующая', 'Парализующее'),
    'Persevering': ('Упорный', 'Упорная', 'Упорное'),
    'Powerful': ('Мощный', 'Мощная', 'Мощное'),
    'Punching': ('Кулачный', 'Кулачная', 'Кулачное'),
    'Quick': ('Быстрый', 'Быстрая', 'Быстрое'),
    'Retaliating': ('Ответный', 'Ответная', 'Ответное'),
    'Rising': ('Восходящий', 'Восходящая', 'Восходящее'),
    'Sharp': ('Острый', 'Острая', 'Острое'),
    'Shattering': ('Сокрушительный', 'Сокрушительная', 'Сокрушительное'),
    'Slashing': ('Рубящий', 'Рубящая', 'Рубящее'),
    'Swift-Striking': ('Молниеносный', 'Молниеносная', 'Молниеносное'),
    'Tough': ('Крепкий', 'Крепкая', 'Крепкое'),
    'Unstoppable': ('Неостановимый', 'Неостановимая', 'Неостановимое'),
    'Vigorous': ('Энергичный', 'Энергичная', 'Энергичное'),
}

W2_RU = {
    'Air': ('Воздушный', 'Воздушная', 'Воздушное'),
    'Astral': ('Астральный', 'Астральная', 'Астральное'),
    'Avalanche': ('Лавинный', 'Лавинная', 'Лавинное'),
    'Bizarre': ('Причудливый', 'Причудливая', 'Причудливое'),
    'Burning': ('Пылающий', 'Пылающая', 'Пылающее'),
    'Earth': ('Земляной', 'Земляная', 'Земляное'),
    'Emerald': ('Изумрудный', 'Изумрудная', 'Изумрудное'),
    'Fire': ('Огненный', 'Огненная', 'Огненное'),
    'Formless': ('Бесформенный', 'Бесформенная', 'Бесформенное'),
    'Heavenly': ('Небесный', 'Небесная', 'Небесное'),
    'Ice': ('Ледяной', 'Ледяная', 'Ледяное'),
    'Iron': ('Железный', 'Железная', 'Железное'),
    'Meteor': ('Метеорный', 'Метеорная', 'Метеорное'),
    'Misty': ('Туманный', 'Туманная', 'Туманное'),
    'Moon': ('Лунный', 'Лунная', 'Лунное'),
    'Nimble': ('Проворный', 'Проворная', 'Проворное'),
    'Northern': ('Северный', 'Северная', 'Северное'),
    'Obsidian': ('Обсидиановый', 'Обсидиановая', 'Обсидиановое'),
    'Rainbow': ('Радужный', 'Радужная', 'Радужное'),
    'Razor': ('Бритвенный', 'Бритвенная', 'Бритвенное'),
    'Red': ('Красный', 'Красная', 'Красное'),
    'Snow': ('Снежный', 'Снежная', 'Снежное'),
    'Spiky': ('Колючий', 'Колючая', 'Колючее'),
    'Stone': ('Каменный', 'Каменная', 'Каменное'),
    'Storm': ('Грозовой', 'Грозовая', 'Грозовое'),
    'Sun': ('Солнечный', 'Солнечная', 'Солнечное'),
    'Tipsy': ('Подвыпивший', 'Подвыпившая', 'Подвыпившее'),
    'Vengeful': ('Мстительный', 'Мстительная', 'Мстительное'),
    'Venom': ('Ядовитый', 'Ядовитая', 'Ядовитое'),
    'Water': ('Водяной', 'Водяная', 'Водяное'),
    'White': ('Белый', 'Белая', 'Белое'),
    'Wind': ('Ветреный', 'Ветреная', 'Ветреное'),
    'Wooden': ('Деревянный', 'Деревянная', 'Деревянное'),
}

_GENDER_M = 0
_GENDER_F = 1

W3_RU = {
    'Bear': ('Медведь', _GENDER_M),
    'Boar': ('Кабан', _GENDER_M),
    'Butterfly': ('Бабочка', _GENDER_F),
    'Cat': ('Кот', _GENDER_M),
    'Centipede': ('Многоножка', _GENDER_F),
    'Cobra': ('Кобра', _GENDER_F),
    'Crab': ('Краб', _GENDER_M),
    'Crane': ('Журавль', _GENDER_M),
    'Dragon': ('Дракон', _GENDER_M),
    'Eagle': ('Орёл', _GENDER_M),
    'Elephant': ('Слон', _GENDER_M),
    'Falcon': ('Сокол', _GENDER_M),
    'Fox': ('Лиса', _GENDER_F),
    'Hawk': ('Ястреб', _GENDER_M),
    'Leopard': ('Леопард', _GENDER_M),
    'Lion': ('Лев', _GENDER_M),
    'Lizard': ('Ящерица', _GENDER_F),
    'Mantis': ('Богомол', _GENDER_M),
    'Monkey': ('Обезьяна', _GENDER_F),
    'Ox': ('Бык', _GENDER_M),
    'Panther': ('Пантера', _GENDER_F),
    'Phoenix': ('Феникс', _GENDER_M),
    'Rat': ('Крыса', _GENDER_F),
    'Shark': ('Акула', _GENDER_F),
    'Scorpion': ('Скорпион', _GENDER_M),
    'Snake': ('Змея', _GENDER_F),
    'Squirrel': ('Белка', _GENDER_F),
    'Tiger': ('Тигр', _GENDER_M),
    'Toad': ('Жаба', _GENDER_F),
    'Turtle': ('Черепаха', _GENDER_F),
    'Viper': ('Гадюка', _GENDER_F),
    'Wino': ('Пьяница', _GENDER_M),
    'Wolf': ('Волк', _GENDER_M),
}


def render_style_name(name):
    """Render a generated style name ('W1 W2 W3' or the '{W2} {W3}' public
    form) in Russian with adjective-noun gender agreement.

    Returns None if the name is not a generated-style name (caller falls back
    to the gettext catalog). Note: the handcrafted style 'White Crane' also
    matches the W2+W3 shape and is rendered here — correctly, as it happens.
    """
    words = name.split()
    if len(words) == 3:
        w1, w2, w3 = words
        if w1 in W1_RU and w2 in W2_RU and w3 in W3_RU:
            noun, gender = W3_RU[w3]
            res = f'{W1_RU[w1][gender]} {W2_RU[w2][gender]} {noun}'
            return res[0].upper() + res[1:]
    elif len(words) == 2:
        w2, w3 = words
        if w2 in W2_RU and w3 in W3_RU:
            noun, gender = W3_RU[w3]
            res = f'{W2_RU[w2][gender]} {noun}'
            return res[0].upper() + res[1:]
    return None
