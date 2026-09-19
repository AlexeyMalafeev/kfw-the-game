import random
from collections import deque

from kf_lib.fighting import fight
from kf_lib.ui import yn


ALL_SCHOOLS_PART_EXP = 20  # small exp for winning-roster players who were not the final winner
ALL_SCHOOLS_MASTER_REP = 10  # significant fame for the player-master of the winning school


class AllSchoolsTournament:
    """Scheduled mega-tournament held on the last day of every month: a
    single-elimination bracket fought by school representatives. Each round,
    every school still in the running fields one fighter — the survivor of its
    previous bout, or, if he was knocked out, the next higher-ranking student
    (schools field their students weakest first; masters don't fight). A
    knocked-out fighter is out for the whole tournament; a school with no
    students left is eliminated. With an odd number of participants, one
    randomly chosen bout per round is a three-way free-for-all. A drawn bout
    (everyone KO'd) knocks out everyone involved. Everyone heals between
    rounds — nobody fights twice in a round. The last fighter standing wins
    the tournament for his school."""

    def __init__(self, game):
        self.g = self.game = game
        self.rosters = {}  # {school_name: [fighters weakest first]}
        self.final_fighter = None  # the last fighter standing
        self.champion = None
        self.run()

    def _gather_rosters(self):
        g = self.g
        rosters = {}
        for school_name, roster in g.schools.items():
            master = g.masters.get(school_name)
            students = [
                f for f in roster
                if f is not master and not (f.is_player and f.inactive)
            ]
            if students:
                # lowest-ranking (weakest) student fights first
                students.sort(key=lambda f: f.get_exp_worth())
                rosters[school_name] = students
        # schools with players come first (protagonist perspective in fights)
        self.rosters = dict(
            sorted(
                rosters.items(),
                key=lambda kv: not any(f.is_player for f in kv[1]),
            )
        )

    def _do_bout(self, fighters):
        """Run one bout between 2 or 3 fighters (one per school)."""
        if len(fighters) == 2:
            fight.fight(
                fighters[0], fighters[1],
                environment_allowed=False, items_allowed=False,
                school_display=True, return_fight_obj=True,
            )
        else:
            fight.free_for_all(
                fighters,
                environment_allowed=False, items_allowed=False,
                school_display=True, return_fight_obj=True,
            )

    def _do_rounds(self):
        g = self.g
        reserves = {name: deque(roster) for name, roster in self.rosters.items()}
        # every school fields its lowest-ranking student
        active = {name: reserves[name].popleft() for name in self.rosters}
        current_round = 0
        while len(active) > 1:
            current_round += 1
            # nobody fights twice in a round, so everyone heals between rounds
            for f in active.values():
                f.hp = f.hp_max
            entries = list(active.items())
            random.shuffle(entries)
            if len(entries) % 2:
                bouts, rest = [entries[:3]], entries[3:]
            else:
                bouts, rest = [], entries
            bouts += [rest[i: i + 2] for i in range(0, len(rest), 2)]
            pairings = '; '.join(
                ' vs '.join(f'{f.name} ({name})' for name, f in bout)
                for bout in bouts
            )
            g.cls()
            g.msg(f'All-Schools Tournament, round {current_round}:\n{pairings}')
            still_active = {}
            for bout in bouts:
                # player fighters first (protagonist perspective in fights)
                bout.sort(key=lambda entry: not entry[1].is_player)
                self._do_bout([f for _, f in bout])
                for name, f in bout:
                    if f.hp > 0:
                        still_active[name] = f  # survives to the next round
                    elif reserves[name]:
                        # knocked out for good — the next student steps in
                        still_active[name] = reserves[name].popleft()
                    else:
                        g.msg(f'{name} is out of students and leaves the tournament!')
            active = still_active
        if active:
            self.champion, self.final_fighter = next(iter(active.items()))
        # else: the final bout(s) knocked everyone out with no reserves left —
        # the tournament ends in a draw

    def _give_rewards(self):
        g = self.g
        if self.champion is None:
            g.msg('The All-Schools Tournament ends in a draw — no school prevails!')
            return
        roster = self.rosters[self.champion]
        # don't leak the style's secret true name to a player who hasn't learned it
        viewer = next((f for f in roster if f.is_player), roster[0])
        displayed_school = viewer.get_displayed_style_name()
        g.msg(
            f'{displayed_school} wins the All-Schools Tournament and is declared '
            f'the Strongest School in {g.town_name}!'
        )
        for f in roster:
            f.log(f'Wins the All-Schools Tournament with {self.champion}.')
        final_fighter = self.final_fighter
        for p in (f for f in roster if f.is_player):
            if p is final_fighter:
                p.add_accompl('All-Schools Champion')
            else:
                # fought and was knocked out, or was present but never got to fight
                p.gain_exp(ALL_SCHOOLS_PART_EXP)
        master = g.masters.get(self.champion)
        if master is not None and master.is_player:
            master.write(f"{master.name}'s school wins the All-Schools Tournament!")
            master.gain_rep(ALL_SCHOOLS_MASTER_REP)
            master.change_stat('all_schools_tourn_won', 1)

    def _heal_npcs(self):
        # so many NPCs get KO'd here that leaving them at zero hp would be odd;
        # players stay as the fight rules left them (KO'd players get injured)
        for roster in self.rosters.values():
            for f in roster:
                if not f.is_player:
                    f.hp = f.hp_max

    def run(self):
        g = self.g
        self._gather_rosters()
        if len(self.rosters) < 2:
            return
        g.cls()
        g.msg(
            f'The masters of {g.town_name} gather for the All-Schools Tournament! Every school '
            'fields its students, weakest first — a knocked-out fighter is out for the whole '
            'tournament, replaced by the next one in rank. Last fighter standing wins the '
            'title for his school!'
        )
        # human participants may opt to skip all their bouts: they are then
        # auto-fought without the per-fight display and prompt; declining
        # keeps the usual "Auto fight?" option for every bout
        skippers = [
            f for roster in self.rosters.values() for f in roster if f.is_human
        ]
        for h in skippers:
            h.auto_fight_all = yn(
                f'{h.name}: auto-fight all your bouts in this tournament?'
            )
        try:
            self._do_rounds()
            self._give_rewards()
        finally:
            for h in skippers:
                h.auto_fight_all = False
        self._heal_npcs()
