import random
from collections import deque

from kf_lib.fighting import fight


ALL_SCHOOLS_PART_EXP = 20  # small exp for winning-roster players who were not the final winner
ALL_SCHOOLS_MASTER_REP = 10  # significant fame for the player-master of the winning school


class AllSchoolsTournament:
    """Scheduled mega-tournament held on the last day of every month: every school
    fields its students (weakest first, masters don't fight) in a single-elimination
    bracket of school-vs-school gauntlet matches. Whenever a fighter is knocked out,
    the next higher-ranking student of his school takes his place; a school with no
    students left is eliminated. With an odd number of schools, one randomly chosen
    match per round is a three-school free-for-all (same substitution rules).
    HP carries over within a match; everyone heals between matches."""

    def __init__(self, game):
        self.g = self.game = game
        self.rosters = {}  # {school_name: [fighters weakest first]}
        self.last_standing = {}  # {school_name: fighter who won its latest match}
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

    def _do_match(self, school_names):
        """Run one gauntlet match between 2 or 3 schools.
        Return (winning_school, final_standing_fighter) or (None, None) if the match
        ends in a draw (everyone KO'd with no reserves left)."""
        school_names = sorted(
            school_names,
            key=lambda n: not any(f.is_player for f in self.rosters[n]),
        )
        queues = {name: deque(self.rosters[name]) for name in school_names}
        reps = {name: queues[name].popleft() for name in school_names}
        while len(reps) > 1:
            fighters = list(reps.values())
            # damage carries over within the match
            carry = {f: f.hp for f in fighters if 0 < f.hp < f.hp_max} or None
            if len(fighters) == 2:
                fight.fight(
                    fighters[0], fighters[1],
                    environment_allowed=False, items_allowed=False,
                    school_display=True, return_fight_obj=True,
                    hp_carry=carry,
                )
            else:
                fight.free_for_all(
                    fighters,
                    environment_allowed=False, items_allowed=False,
                    school_display=True, return_fight_obj=True,
                    hp_carry=carry,
                )
            for name in list(reps):
                if reps[name].hp <= 0:  # knocked out — the next student steps in
                    if queues[name]:
                        reps[name] = queues[name].popleft()
                    else:
                        del reps[name]  # the school is eliminated from the match
        if not reps:
            return None, None
        winner = next(iter(reps))
        return winner, reps[winner]

    def _do_rounds(self):
        g = self.g
        schools = list(self.rosters)
        current_round = 0
        while len(schools) > 1:
            current_round += 1
            random.shuffle(schools)
            matches = []
            if len(schools) % 2:
                matches.append(schools[:3])
                rest = schools[3:]
            else:
                rest = schools
            matches += [rest[i: i + 2] for i in range(0, len(rest), 2)]
            pairings = '; '.join(' vs '.join(m) for m in matches)
            g.cls()
            g.msg(f'All-Schools Tournament, round {current_round}:\n{pairings}')
            winners = []
            for match in matches:
                # everyone heals between matches
                for name in match:
                    for f in self.rosters[name]:
                        f.hp = f.hp_max
                winner, final_fighter = self._do_match(match)
                if winner is None:
                    g.msg(f'{" vs ".join(match)}: all fighters are down — a draw!')
                else:
                    self.last_standing[winner] = final_fighter
                    winners.append(winner)
                    g.msg(f'{winner} defeats {" and ".join(n for n in match if n != winner)}!')
            if not winners:
                return  # every match drawn — the tournament fizzles out
            schools = winners
        self.champion = schools[0]

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
        final_fighter = self.last_standing.get(self.champion)
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
            'fields its students, weakest first — a knocked-out fighter is replaced by the '
            'next one in rank. Last school standing wins!'
        )
        self._do_rounds()
        self._give_rewards()
        self._heal_npcs()
