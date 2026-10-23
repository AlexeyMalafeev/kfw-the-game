"""Where does fighters' qi come from and go? A qi ledger per level tier.

Mirror matches like the fight-balance harness (two fresh random fighters at the
same random level 1-20, default fight AI), single process. Every change of a
fighter's qi is booked by its source: regeneration at turn start, Focus, Guard,
dodge/block, a damaging strike (only under rules that give qi for hits), move
costs; qi that a gain would have added above the max is booked as lost to the
cap. Per tier it prints the qi in/out per fighter per fight, the share of max qi
a fighter holds when it strikes and at fight end, the mean qi cost of a strike,
and the share of strike damage done by qi-based damage (do_qi_based_dam).

    python run_test_qi_flow.py
    python run_test_qi_flow.py -n 3000 --variants rule_variants.py:QF
Prints a table only (no report file). Runs from any cwd.
"""
import argparse
import os
import random
import sys
from collections import defaultdict
from pathlib import Path

ORIG_CWD = os.getcwd()  # for the user's relative paths
lib_path = Path(__file__).resolve().parents[2]
os.chdir(lib_path)
if str(lib_path) not in sys.path:
    sys.path.append(str(lib_path))

TIERS = ((1, 7), (8, 14), (15, 20))


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('-n', type=int, default=6000, help='fights')
    parser.add_argument('--seed', type=int, default=5)
    parser.add_argument('--variants', default='', metavar='FILE:NAMES')
    args = parser.parse_args()

    from kf_lib.actors import fighter_factory as ff
    from kf_lib.actors.fighter import Fighter as F
    from kf_lib.fighting import fight
    if args.variants:  # before the ledger's own patches, which wrap the variants'
        import importlib.util
        path, names = args.variants.rsplit(':', 1)
        spec = importlib.util.spec_from_file_location('variants', Path(ORIG_CWD, path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.apply(names)

    led = defaultdict(float)  # (tier, key) -> sum
    ctx = {'src': None}  # the source of the qi change in progress

    oc = F.change_qp
    def change_qp(self, amount):
        before = self.qp
        oc(self, amount)
        if not amount:
            return
        src = ctx['src'] or 'other'
        if src == 'move cost' and amount > 0:
            src = 'Focus'  # Focus is a move with qi_cost -20
        led[(self.tier_, ('in:' if amount > 0 else 'out:') + src)] += abs(self.qp - before)
        if amount > 0:
            led[(self.tier_, 'capped:' + src)] += amount - (self.qp - before)
    F.change_qp = change_qp

    def tag(name, src):
        orig = getattr(F, name)
        def wrapper(self, *a, **k):
            prev = ctx['src']
            ctx['src'] = src
            try:
                return orig(self, *a, **k)
            finally:
                ctx['src'] = prev
        setattr(F, name, wrapper)
    tag('start_fight_turn', 'regen')
    tag('guard', 'Guard')
    tag('defend', 'dodge/block')  # nested inside the attacker's do_strike
    tag('do_strike', 'hit')
    tag('apply_move_cost', 'move cost')

    oq = F.do_qi_based_dam
    def do_qi_based_dam(self):
        hp = self.target.hp
        oq(self)
        led[(self.tier_, 'qi-based dam')] += hp - self.target.hp
        led[(self.tier_, 'qi-based hits')] += 1
    F.do_qi_based_dam = do_qi_based_dam

    ods = F.do_strike
    def do_strike(self):
        hp = self.target.hp
        led[(self.tier_, 'strikes')] += 1
        led[(self.tier_, 'qp share at strike')] += self.qp / self.qp_max if self.qp_max else 0
        led[(self.tier_, 'qi cost of strikes')] += self.action.qi_cost
        ods(self)
        led[(self.tier_, 'dam')] += hp - self.target.hp
    F.do_strike = do_strike

    random.seed(args.seed)
    for _ in range(args.n):
        lv = random.randint(1, 20)
        tier = next(i for i, (a, b) in enumerate(TIERS) if a <= lv <= b)
        f1 = ff.new_fighter(lv=lv)
        f1.name = 'Dummy A'
        f2 = ff.new_fighter(lv=lv)
        f2.name = 'Dummy B'
        for f in (f1, f2):
            f.tier_ = tier
        fight.AutoFight([f1], [f2])
        for f in (f1, f2):
            used = f.fight_stats['moves_used']
            led[(tier, 'fighters')] += 1
            led[(tier, 'actions')] += sum(used.values())
            led[(tier, 'focus')] += used.get('Focus', 0)
            led[(tier, 'qp_max')] += f.qp_max
            led[(tier, 'end qp share')] += f.qp / f.qp_max if f.qp_max else 0

    print(f'qi ledger, n={args.n} fights, seed {args.seed}'
          + (f', variants {args.variants}' if args.variants else ''))
    for t, (a, b) in enumerate(TIERS):
        def g(key):
            return led[(t, key)]
        nf = g('fighters') or 1

        def booked(prefix):
            return {k[1][len(prefix):]: v for k, v in led.items()
                    if k[0] == t and k[1].startswith(prefix) and v}
        ins, outs, capped = booked('in:'), booked('out:'), booked('capped:')
        total_in = sum(ins.values()) or 1
        print(f'\nlv {a}-{b}: {int(nf)} fighters, max qi {g("qp_max") / nf:.1f}; per fighter '
              f'and fight: actions {g("actions") / nf:.1f}, strikes {g("strikes") / nf:.1f}, '
              f'Focus {g("focus") / nf:.2f}')
        print('  qi in:  ' + ', '.join(f'{k} {v / nf:.1f} ({v / total_in * 100:.0f}%)'
                                       for k, v in sorted(ins.items(), key=lambda x: -x[1])))
        print('  lost to the cap: ' + ', '.join(f'{k} {v / nf:.1f}' for k, v in capped.items()))
        print('  qi out: ' + ', '.join(f'{k} {v / nf:.1f}' for k, v in outs.items()))
        strikes = g('strikes') or 1
        print(f'  held at a strike {g("qp share at strike") / strikes * 100:.0f}% of max, '
              f'at fight end {g("end qp share") / nf * 100:.0f}%; '
              f'mean qi cost of a strike {g("qi cost of strikes") / strikes:.1f}')
        print(f'  qi-based damage {g("qi-based dam") / (g("dam") or 1) * 100:.1f}% of strike '
              f'damage ({g("qi-based hits") / nf:.2f} hits per fighter and fight)')


if __name__ == '__main__':
    main()
