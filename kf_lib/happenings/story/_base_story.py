_all_stories = []


class BaseStory:
    min_level = None
    max_level = None

    def __init__(self, g, state=None, player=None, boss=None):
        self.game = g
        self.name = self.__class__.__name__
        self.state = state
        self.player = player
        self.boss = boss

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        _all_stories.append(cls)

    def __repr__(self):
        return self.get_init_string()

    def advance(self):
        self.state += 1
        p = self.player
        p.cls()
        p.show(p.get_p_info(), align=False)
        exec(f'self.scene{self.state}()')

    def check_hasnt_started(self):
        return self.state is None

    def delete_boss(self):
        self.game.unregister_fighter(self.boss)
        self.boss = None

    def end(self):
        self.state = -1
        if self.boss:
            self.delete_boss()
        self.player.current_story = None

    def get_init_string(self):
        if self.player:
            p_ref = self.game.get_fighter_ref(self.player)
        else:
            p_ref = None
        if self.boss:
            b_ref = self.game.get_fighter_ref(self.boss)
        else:
            b_ref = None
        return 'story.{}(g, state={!r}, player={}, boss={})'.format(
            self.__class__.__name__, self.state, p_ref, b_ref
        )

    def intro(self):
        pass

    def start(self, player):
        p = self.player = player
        p.current_story = self
        p.change_stat('num_stories', 1)
        self.state = 0
        self.intro()

    def test(self, player):
        p = player
        return self.min_level <= p.level <= self.max_level
