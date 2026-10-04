"""Russian rendering of fighter proper names.

Proper names stay English internally (they are save-file cross-reference keys);
this module transliterates them for display only. The Chinese-ish syllables of
kf_lib/actors/names.py (SURNAME_PARTS / FIRST_NAME_PARTS /
FEMALE_FIRST_NAME_PARTS — closed lists, mirrored here as data because i18n is a
leaf package) are cyrillized with the Palladius system, the standard Russian
cyrillization of Chinese pinyin ('Qiu Qiufan' -> 'Цю Цюфань'). Given names are
1-2 syllables concatenated, so tokens that are not whole syllables are segmented
by backtracking search over the syllable set ('lin'+'gang' = 'lingang'
dead-ends on 'ling'+'ang' under plain greedy matching). Foreign-challenger
names and the turtle easter egg use conventional Russian spellings.
"""

# Palladius cyrillization for every syllable in the three name-part lists.
# 'jen' is Wade-Giles for pinyin 'ren'; 'hung'/'shing'/'ziu' are Cantonese-ish
# and get their conventional Russian spellings.
SYLLABLES_RU = {
    'bai': 'бай',
    'cai': 'цай',
    'cao': 'цао',
    'chang': 'чан',
    'chao': 'чао',
    'chen': 'чэнь',
    'cheng': 'чэн',
    'chu': 'чу',
    'chun': 'чунь',
    'cui': 'цуй',
    'dai': 'дай',
    'deng': 'дэн',
    'ding': 'дин',
    'dong': 'дун',
    'du': 'ду',
    'duan': 'дуань',
    'fan': 'фань',
    'fang': 'фан',
    'fei': 'фэй',
    'feng': 'фэн',
    'fu': 'фу',
    'gang': 'ган',
    'gao': 'гао',
    'gong': 'гун',
    'gu': 'гу',
    'gui': 'гуй',
    'guo': 'го',
    'han': 'хань',
    'hao': 'хао',
    'he': 'хэ',
    'hong': 'хун',
    'hou': 'хоу',
    'hu': 'ху',
    'hua': 'хуа',
    'huang': 'хуан',
    'hung': 'хун',
    'jen': 'жэнь',
    'jia': 'цзя',
    'jiang': 'цзян',
    'jiao': 'цзяо',
    'jie': 'цзе',
    'jin': 'цзинь',
    'jing': 'цзин',
    'jiu': 'цзю',
    'juan': 'цзюань',
    'jun': 'цзюнь',
    'kang': 'кан',
    'kong': 'кун',
    'lai': 'лай',
    'lan': 'лань',
    'lei': 'лэй',
    'li': 'ли',
    'lian': 'лянь',
    'liang': 'лян',
    'liao': 'ляо',
    'lin': 'линь',
    'ling': 'лин',
    'liu': 'лю',
    'long': 'лун',
    'lu': 'лу',
    'luo': 'ло',
    'ma': 'ма',
    'mao': 'мао',
    'mei': 'мэй',
    'meng': 'мэн',
    'min': 'минь',
    'ming': 'мин',
    'mo': 'мо',
    'na': 'на',
    'pan': 'пань',
    'peng': 'пэн',
    'ping': 'пин',
    'qian': 'цянь',
    'qiang': 'цян',
    'qiao': 'цяо',
    'qin': 'цинь',
    'qiu': 'цю',
    'shao': 'шао',
    'shen': 'шэнь',
    'sheng': 'шэн',
    'shi': 'ши',
    'shing': 'син',
    'shu': 'шу',
    'song': 'сун',
    'su': 'су',
    'sun': 'сунь',
    'tan': 'тань',
    'tang': 'тан',
    'tao': 'тао',
    'tian': 'тянь',
    'ting': 'тин',
    'to': 'то',
    'wan': 'вань',
    'wang': 'ван',
    'wei': 'вэй',
    'wen': 'вэнь',
    'wu': 'у',
    'xi': 'си',
    'xia': 'ся',
    'xiang': 'сян',
    'xiao': 'сяо',
    'xie': 'се',
    'xiong': 'сюн',
    'xiu': 'сю',
    'xu': 'сюй',
    'xue': 'сюэ',
    'yan': 'янь',
    'yang': 'ян',
    'yao': 'яо',
    'ye': 'е',
    'yi': 'и',
    'yin': 'инь',
    'ying': 'ин',
    'yong': 'юн',
    'yu': 'юй',
    'yuan': 'юань',
    'zeng': 'цзэн',
    'zhang': 'чжан',
    'zhao': 'чжао',
    'zheng': 'чжэн',
    'zhong': 'чжун',
    'zhou': 'чжоу',
    'zhu': 'чжу',
    'ziu': 'цзю',
    'zou': 'цзоу',
}

# foreign challengers, their countries and the turtle easter egg
# (kf_lib/actors/names.py FOREIGN_NAMES / FOREIGN_COUNTRIES / TURTLE_NAMES)
WHOLE_WORD_RU = {
    # England
    'Smith': 'Смит',
    'Jones': 'Джонс',
    'Taylor': 'Тейлор',
    'Brown': 'Браун',
    'Williams': 'Уильямс',
    'Wilson': 'Уилсон',
    'Johnson': 'Джонсон',
    'Walker': 'Уокер',
    'Robinson': 'Робинсон',
    'Green': 'Грин',
    'Roberts': 'Робертс',
    # Germany
    'Muller': 'Мюллер',
    'Schmidt': 'Шмидт',
    'Schneider': 'Шнайдер',
    'Fischer': 'Фишер',
    'Meyer': 'Майер',
    'Weber': 'Вебер',
    'Schulz': 'Шульц',
    'Becker': 'Беккер',
    'Hoffmann': 'Хоффман',
    # Japan
    'Satou': 'Сато',
    'Suzuki': 'Судзуки',
    'Takahashi': 'Такахаси',
    'Tanaka': 'Танака',
    'Watanabe': 'Ватанабэ',
    'Itou': 'Ито',
    'Nakamura': 'Накамура',
    'Yamamoto': 'Ямамото',
    'Kobayashi': 'Кобаяси',
    'Saitou': 'Сайто',
    # Korea
    'Kwan': 'Кван',
    'Kangjun': 'Канджун',
    'Kai': 'Кай',
    'Khong': 'Кхон',
    'Nham': 'Ням',
    'Thang': 'Тханг',
    'Pohng': 'Пхон',
    # Thailand
    'Awut': 'Авут',
    'Channarong': 'Чаннаронг',
    'Khemkhaeng': 'Кхемкхэнг',
    'Puenthai': 'Пынтхай',
    'Somchair': 'Сомчай',
    'Thuanthong': 'Тхуантхонг',
    # Brazil
    'Silva': 'Силва',
    'Santos': 'Сантос',
    'Oliveira': 'Оливейра',
    'Souza': 'Соуза',
    'Rodrigues': 'Родригес',
    # countries
    'England': 'Англия',
    'Germany': 'Германия',
    'Japan': 'Япония',
    'Korea': 'Корея',
    'Thailand': 'Таиланд',
    'Brazil': 'Бразилия',
    # turtles
    'Leonardo': 'Леонардо',
    'Raphael': 'Рафаэль',
    'Michelangelo': 'Микеланджело',
    'Donatello': 'Донателло',
}

_MAX_SYLL_LEN = max(len(s) for s in SYLLABLES_RU)


def _segment(s):
    """Split a concatenated-syllable string into known syllables; None if
    impossible. Greedy longest match with backtracking ('lin'+'gang' =
    'lingang' dead-ends on 'ling'+'ang', so plain greedy is not enough)."""
    parts = []

    def backtrack(rest):
        if not rest:
            return True
        for n in range(min(_MAX_SYLL_LEN, len(rest)), 0, -1):
            if rest[:n] in SYLLABLES_RU:
                parts.append(rest[:n])
                if backtrack(rest[n:]):
                    return True
                parts.pop()
        return False

    return parts if backtrack(s) else None


def translit_token(token):
    """Cyrillize one name token; unknown tokens are returned unchanged."""
    if token in WHOLE_WORD_RU:
        return WHOLE_WORD_RU[token]
    lower = token.lower()
    if lower in SYLLABLES_RU:
        return SYLLABLES_RU[lower].capitalize()
    parts = _segment(lower)
    if parts is None:
        return token
    return ''.join(SYLLABLES_RU[s] for s in parts).capitalize()


def translit_fighter_name(name, tr_name):
    """Render a fighter name in Russian: numbered group-name bases
    ('Thug 2' -> 'Головорез 2') and descriptive tokens ('Beggar' -> 'Нищий')
    go through the names catalog, proper-name tokens are transliterated,
    digits pass through."""
    base, sep, num = name.rpartition(' ')
    if sep and num.isdigit():
        tr_base = tr_name(base)
        if tr_base != base:
            return f'{tr_base} {num}'
    out = []
    for token in name.split(' '):
        if token.isdigit():
            out.append(token)
            continue
        tr = tr_name(token)
        if tr != token:
            out.append(tr)
            continue
        out.append(translit_token(token))
    return ' '.join(out)
