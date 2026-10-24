"""The master's teachings: true fight mechanics, phrased as kung-fu wisdom.

Shared now and then during 'Practice at school' (the MasterTeaching encounter).
Each teaching names the `docs/` section it paraphrases (`doc`, as
'file.md: heading text') and the values it quotes or relies on:
- `ties`: {fighter attribute or class constant: value}, checked against a plain
  fighter by test/test_teachings.py;
- `rule_tests`: existing tests that pin a qualitative rule ('file::Class::name');
- formula facts get their own behaviour checks in test/test_teachings.py.
A rule change then fails a test that names the saying to reword.
"""
from typing import Dict, NamedTuple, Tuple

from kf_lib.i18n import _

FM = 'fight_mechanics.md: '
FE = 'test/test_fight_engine.py::TestDefenseAndCounters::'


class Teaching(NamedTuple):
    id: str
    saying: str  # the master's words
    fact: str  # the plain rule, shown after the saying
    doc: str
    ties: Dict[str, object] = {}
    rule_tests: Tuple[str, ...] = ()


def get_teachings():
    """All teachings in the active language. Built on every call rather than at
    import, since the language is chosen after import in tests and dev tools."""
    return [
        # --- defense ---
        Teaching(
            'guard_doubles',
            _('Stand on guard and you are twice as hard to touch, until you move again.'),
            _('Guard doubles your chances to dodge and block until your next turn.'),
            FM + 'Maneuvers',
            {'GUARD_POWER': 2.0},
            (FE + 'test_guard_raises_defense_and_is_marked',),
        ),
        Teaching(
            'guard_techs',
            _('An untrained guard only shields. A trained guard also lets breath and qi '
              'return.'),
            _('Guard restores nothing by itself. Advanced Guard makes it restore one '
              "turn's worth of stamina and qi, Dragon Guards a Treasure two."),
            FM + 'Maneuvers',
            {'guard_restore': 0.0},
            ('test/test_fight_engine.py::TestDefenseAndCounters::'
             'test_guard_techs_restore_turns_worth_of_stamina_and_qi',),
        ),
        Teaching(
            'full_defense_opening',
            _('A blow that meets only air or a closed door pulls its owner off balance. '
              'That is the moment to answer.'),
            _('A full dodge, or a block that stops all the damage, leaves the attacker '
              'off-balance for a moment and gives you a chance to counter.'),
            FM + '`defend` — dodge / block / hit',
            {},
            (FE + 'test_full_defense_puts_the_attacker_off_balance',
             FE + 'test_full_block_puts_the_attacker_off_balance',
             FE + 'test_counter_answers_dodge_block_or_miss_only'),
        ),
        Teaching(
            'off_balance',
            _('A fighter off balance strikes and defends with only three quarters of '
              'their strength.'),
            _('Being off-balance multiplies your attack and defense by 0.75.'),
            FM + 'Statuses and durations',
            {'off_balance_atk_mult': 0.75, 'off_balance_dfs_mult': 0.75},
        ),
        Teaching(
            'qi_shield',
            _('When the arm cannot stop it all, trained qi takes what the block lets '
              'through.'),
            _('Fighters with qi training spend qi, 1 point per 2 HP, to absorb the '
              'damage that gets past their block.'),
            FM + '`defend` — dodge / block / hit',
            {'QI_SHIELD_HP_PER_QP': 2},
            (FE + 'test_qi_shield_absorbs_what_got_past_a_block',),
        ),
        Teaching(
            'block_from_health',
            _('A block is held up by the body behind it, not by the fist in front of it.'),
            _('Block power comes from health, not strength.'),
            FM + 'Defense numbers — `calc_dfs` (on the defender)',
        ),
        Teaching(
            'weapon_blocks',
            _('A weapon lengthens the arm that blocks, never the legs that dodge.'),
            _("A weapon's defense bonus improves blocking, not dodging."),
            FM + 'Defense numbers — `calc_dfs` (on the defender)',
        ),
        Teaching(
            'repetition',
            _('Show the same strike three times and the third will be waited for.'),
            _('Each repeat of a move among your last three actions makes it easier to '
              'dodge or block, up to about twice as easy.'),
            FM + 'Defense numbers — `calc_dfs` (on the defender)',
        ),
        Teaching(
            'crowd_penalty',
            _('Against many, every blow that comes at you makes the next one harder to '
              'stop.'),
            _('Each strike aimed at you between your own turns lowers your defense by '
              '20%.'),
            FM + '`do_strike` order',
            {'dfs_penalty_step': 0.2},
        ),
        Teaching(
            'lying',
            _('On the ground you defend with half your strength. Rise, or be finished.'),
            _('Lying on the ground halves your chances to dodge and block.'),
            FM + 'Statuses and durations',
            {'lying_dfs_mult': 0.5},
        ),
        Teaching(
            'antiground',
            _('A fallen fighter invites the blows that strike downward.'),
            _('Some moves can only be used against an opponent lying on the ground.'),
            FM + 'Action selection',
        ),
        Teaching(
            'dodge_feeds_qi',
            _('Evasion feeds the qi. A block feeds it too, but only half as well.'),
            _("A successful dodge gives you a turn's worth of qi; a block gives half of "
              "that."),
            FM + '`defend` — dodge / block / hit',
        ),
        # --- counters ---
        Teaching(
            'agility_counters',
            _('The nimble find openings. Every empty strike is a door, and agility '
              'opens it more often.'),
            _('Each point of agility above 3 adds 5% to your chance to counter a strike '
              'that missed or was fully stopped.'),
            FM + 'Pools and derived attributes',
            {'COUNTER_AGILITY_ADJUST': 3, 'COUNTER_PER_AGILITY_POINT': 0.05},
        ),
        Teaching(
            'counter_techs',
            _('One who has trained the counter does not wait for luck. The answer comes '
              'every time, and it is hard to stop.'),
            _('Counter techniques make counters certain, and those counters are twice '
              'as hard to dodge or block.'),
            FM + 'Pools and derived attributes',
            {'COUNTER_TECH_HIT_MULT': 2.0},
            (FE + 'test_counter_techs_give_sure_counters_in_a_row',),
        ),
        Teaching(
            'preemptive',
            _('The highest defense is to strike before the strike.'),
            _('Preemptive techniques give a chance to hit an attacker first, so that '
              'their attack never happens.'),
            FM + 'Strike resolution pipeline',
            {'preemptive_chance': 0.0},  # techniques only
        ),
        # --- attack ---
        Teaching(
            'momentum',
            _('Step in as you strike, and your strike carries your step.'),
            _('Moving closer builds momentum, and each point of momentum adds 10% to '
              'your attack power and accuracy.'),
            FM + 'Maneuvers',
            {'MOMENTUM_EFFECT_SIZE': 0.1},
        ),
        Teaching(
            'momentum_knockback',
            _('One who rushes forward is hard to push back.'),
            _('Momentum from moving closer reduces how far a hit knocks you back.'),
            FM + '`hit_or_miss` — only if `dam > 0`',
        ),
        Teaching(
            'distance',
            _('Every strike has its distance. Too near or too far, the finest technique '
              'is useless.'),
            _('Each attack move works only at one distance (1 to 4); step in or out to '
              'use the others.'),
            FM + 'Action selection',
        ),
        Teaching(
            'complex_forms',
            _('Intricate forms betray clumsy limbs.'),
            _('Complex moves fail more often, and agility lowers that chance.'),
            FM + 'Move failure',
        ),
        Teaching(
            'cost_on_miss',
            _('A wasted strike still costs its breath.'),
            _("A move's stamina and qi are spent even if it misses or fails."),
            FM + 'Strike resolution pipeline',
        ),
        Teaching(
            'unblockable',
            _('Some blows go around the arm. Against those, only the feet can save you.'),
            _('Unblockable techniques give a chance that a strike cannot be blocked, '
              'only dodged.'),
            FM + '`do_strike` order',
            {'unblock_chance': 0.0},  # techniques only
        ),
        Teaching(
            'critical',
            _('Precise hands find the weak point. The nimble strike true more often.'),
            _('Each point of agility above 3 adds 5% to your chance of a critical hit, '
              'which deals 1.5 times the damage.'),
            FM + '`hit_or_miss` — only if `dam > 0`',
            {'CRITICAL_AGILITY_ADJUST': 3, 'CRITICAL_PER_AGILITY_POINT': 0.05,
             'critical_dam_mult': 1.5},
        ),
        Teaching(
            'epic',
            _('Once in a long while, heaven itself moves the fist, and the blow is told '
              'of for generations. The longer you walk the path, the more often heaven '
              'moves.'),
            _('Every fighter has a 0.5% chance per level to land an epic hit, which '
              'deals double damage; an epic critical hit deals triple.'),
            FM + '`hit_or_miss` — only if `dam > 0`',
            {'EPIC_CHANCE_INCR_PER_LV': 0.005, 'epic_dam_mult': 2.0,
             'critical_dam_mult': 1.5},
        ),
        Teaching(
            'no_perfect_blocked',
            _('A blow that is even partly blocked can never be a perfect blow.'),
            _('Critical and epic hits happen only on strikes that were not blocked at '
              'all.'),
            FM + '`hit_or_miss` — only if `dam > 0`',
            {},
            (FE + 'test_blocked_strike_cannot_be_critical_or_epic',),
        ),
        # --- what hits do ---
        Teaching(
            'knockdown',
            _('A blow that takes half of what remains puts a fighter on the ground.'),
            _("A hit that deals at least half of the target's remaining HP knocks them "
              "down."),
            FM + '`hit_or_miss` — only if `dam > 0`',
            {'KNOCKDOWN_HP_THRESHOLD': 0.5},
        ),
        Teaching(
            'fall_damage',
            _('The ground strikes too, and it never misses.'),
            _('Being knocked down costs 25 to 50 HP from the fall itself.'),
            FM + '`hit_or_miss` — only if `dam > 0`',
            {'FALL_DAMAGE': (25, 50)},
        ),
        Teaching(
            'stun',
            _('A heavy enough blow freezes a fighter for a moment. They lose their turn, '
              'but not their eyes.'),
            _("A hit that deals more than about a third of the target's maximum HP stuns "
              "them: they skip their turn and defend at 80%."),
            FM + 'Statuses and durations',
            {'STUN_HP_DIVISOR': 2.8, 'STUN_DFS_MULT': 0.8},
            (FE + 'test_stun_weakens_defense_only_while_it_lasts',),
        ),
        Teaching(
            'shock',
            _('A stun dims the eyes; a shock blinds them. The shocked can neither dodge '
              'nor block.'),
            _("'Shocking' moves make the target skip their turn with no chance to dodge "
              "or block until the shock passes."),
            FM + 'Statuses and durations',
        ),
        Teaching(
            'nerve_slow',
            _('Strike the nerve and the whole body grows slow.'),
            _("'Nerve' moves slow the target down: for a while, all their actions take "
              "about 40% longer."),
            FM + 'Statuses and durations',
            {'MOB_DAM_PENALTY': 0.3},
        ),
        Teaching(
            'solar_breath',
            _('A blow to the solar plexus steals the breath, and with the breath goes '
              'the strength.'),
            _("'Solar' moves drain 20% of the target's maximum stamina."),
            FM + '`hit_or_miss` — only if `dam > 0`',
            {'STAMINA_DAMAGE': 0.2},
        ),
        Teaching(
            'debilitating',
            _('The cruelest strike takes breath, speed and senses all at once.'),
            _("'Debilitating' moves shock the target, slow them down and drain their "
              "stamina, all at once."),
            FM + 'Statuses and durations',
        ),
        Teaching(
            'claws_bleed',
            _('Claw and slash open wounds that do not close until the fight is over.'),
            _("'Claw' moves (all but Dragon Claw) and 'Slashing' moves cause bleeding, "
              "which costs HP at the start of each of the target's turns until the "
              "fight ends."),
            FM + '`hit_or_miss` — only if `dam > 0`',
        ),
        Teaching(
            'any_blow_bleeds',
            _('Even a plain blow can open the skin. Do not ignore the drop that becomes '
              'a stream.'),
            _('Any hit has a small chance (3% for most fighters) to cause bleeding worth '
              '15% of its damage, and new wounds add to the bleeding.'),
            FM + '`hit_or_miss` — only if `dam > 0`',
            {'chance_cause_bleeding': 0.03, 'BLEEDING_PART_OF_DAM': 0.15},
        ),
        Teaching(
            'statuses_speed',
            _('The swift shake off a stun the way a dog shakes off water.'),
            _('Stuns, shocks, falls, being off-balance and being slowed down all wear off '
              'sooner for faster fighters.'),
            FM + 'Statuses and durations',
        ),
        # --- body, breath and qi ---
        Teaching(
            'speed_base',
            _('To the slow, a little more speed is a great gift. To the swift, it is a '
              'small one.'),
            _('Speed counts from a base of 2, so each point of speed matters more when '
              'you are slow.'),
            FM + 'Maneuvers',
            {'TEMPO_SPEED_BASE': 2},
        ),
        Teaching(
            'tired',
            _('A tired body fights at half its worth. Guard your breath as you guard '
              'your face.'),
            _('As your stamina runs out, your attack, defense and block power fall, down '
              'to half when it is empty.'),
            FM + 'Attack numbers — `calc_atk`',
            {'STAMINA_FACTOR_BIAS': 0.5},
        ),
        Teaching(
            'regen',
            _('Breath and qi return a little with every turn. Patience refills what '
              'haste empties.'),
            _('At the start of each of your turns you recover 10% of your maximum '
              'stamina and qi.'),
            FM + 'Pools and derived attributes',
            {'STAMINA_PORTION_RESTORED_PER_TURN': 0.1, 'QP_PORTION_RESTORED_PER_TURN': 0.1},
        ),
        Teaching(
            'catch_breath_focus',
            _('When breath runs short, stop and breathe. When qi runs dry, stop and '
              'gather it.'),
            _("Catch Breath restores two turns' worth of stamina and Focus two turns' "
              "worth of qi, each in the time of a Guard."),
            FM + 'Maneuvers',
            {'CATCH_BREATH_GAIN_MULT': 2, 'FOCUS_GAIN_MULT': 2},
        ),
        Teaching(
            'breath_grows',
            _('A rookie who stops to breathe catches a sip. A master catches a lungful.'),
            _('Catch Breath and Focus restore twice your per-turn recovery, so they grow '
              'with your level and with stamina and qi techniques.'),
            FM + 'Maneuvers',
            {'CATCH_BREATH_GAIN_MULT': 2, 'FOCUS_GAIN_MULT': 2},
        ),
        Teaching(
            'empty_qi_cup',
            _('Every fight begins with an empty cup of qi. Only the trained arrive with '
              'some already poured.'),
            _('Fighters start a fight with no qi unless a qi technique gives them a head '
              'start.'),
            FM + 'Fight setup',
            {'qp_start': 0.0},
        ),
        Teaching(
            'health_bowl',
            _('Health is the bowl that holds your life. The bigger the bowl, the more '
              'blows it takes to empty.'),
            _('Each point of health gives 40 maximum HP.'),
            FM + 'Pools and derived attributes',
            {'HP_PER_HEALTH_LV': 40},
        ),
        Teaching(
            'toughness',
            _('Small blows break on a seasoned body like rain on a rock.'),
            _('Toughness, which grows with your level and a little with your health, is '
              'subtracted from every hit you take.'),
            FM + 'Pools and derived attributes',
            {'TOUGHNESS_PER_LV': 3, 'TOUGHNESS_FROM_HEALTH': 0.2},
        ),
        Teaching(
            'resist_ko',
            _('A trained spirit refuses to fall. Where another would sleep, it stands on '
              'its last breath.'),
            _('Resilience techniques give a chance, up to 50%, to stay on your feet with '
              '1 HP instead of being knocked out.'),
            FM + '`hit_or_miss` — only if `dam > 0`',
            {'MAX_RESIST_KO': 0.5},
        ),
        Teaching(
            'fury',
            _('Pain is fuel to those who have learned to burn it. The deeper the wounds, '
              'the nearer the storm.'),
            _('Fighters with a fury technique may fly into a fury, more likely the more '
              'HP they have lost; in fury, attack power, accuracy and block power rise '
              'by 60%.'),
            FM + 'Statuses and durations',
            {'fury_to_all_mult': 1.6},
        ),
        # --- after the fight ---
        Teaching(
            'exp_strong',
            _('Beating the weak teaches little. Beating the strong teaches much.'),
            _("Experience from a win grows faster than the opponent's strength relative "
              "to yours."),
            FM + 'End of fight',
        ),
        Teaching(
            'exp_bonuses',
            _('A swift victory, an unscratched one, or one over many teaches more than an '
              'ordinary win.'),
            _('Winning within 10 seconds, without taking damage, or with 3 or more '
              'knockouts each adds 25% experience.'),
            FM + 'End of fight',
        ),
        Teaching(
            'sparring',
            _('Even a friendly bout teaches, and it leaves no lasting wounds.'),
            _('Sparring gives experience but causes no injuries.'),
            FM + 'Fight variants',
        ),
        Teaching(
            'injury',
            _('Be knocked out in a real fight and your body will pay for days.'),
            _('A player knocked out in a real fight is injured and must spend one or '
              'more days recovering.'),
            FM + 'End of fight',
        ),
    ]
