from abc import ABC

from kf_lib.actors.fighter._abc import FighterAPI
from kf_lib.utils import choose_adverb


class FightDisplayMethods(FighterAPI, ABC):
    def display_bleed_pass_out(self) -> None:
        self.current_fight.display(f'{self.name} passes out because of bleeding!')
        self.current_fight.pak()

    def display_block(self) -> None:
        adv = choose_adverb(self.block_chance, 'barely', 'easily')
        self.current_fight.display(f'{self.name} {adv}blocks! ({self.dfs_pwr})')

    def display_block_disarm(self) -> None:
        self.current_fight.display(f'{self.name} disarms {self.target.name} while blocking')

    def display_counter(self) -> None:
        self.current_fight.display('+COUNTER!+')
        self.current_fight.display(f'{self.name}: {self.action.name} @ {self.target.name}')

    def display_dodge(self) -> None:
        self.current_fight.display(f"{self.name} {choose_adverb(self.dodge_chance, 'barely', 'easily')}dodges!")

    def display_fail(self) -> None:
        self.current_fight.display('Fail!')

    def display_fury(self) -> None:
        s = self.current_fight.get_f_name_string(self)
        self.current_fight.display(f'{s} is in FURY!')
        self.current_fight.pak()

    def display_grab_impro_wp(self) -> None:
        s = self.current_fight.get_f_name_string(self)
        self.current_fight.display(f'{s} grabs an improvised weapon!')
        self.current_fight.pak()

    def display_hit(self) -> None:
        if self.target.dam_reduc:
            self.current_fight.display('damage is reduced!')
        self.current_fight.display(f'hit: -{self.dam} HP ({self.target.hp})')

    def display_ko(self) -> None:
        self.current_fight.display(' KNOCK-OUT!'.format(self.target.name), align=False)

    def display_miss(self) -> None:
        self.current_fight.display('Miss!')

    def display_preemptive(self) -> None:
        self.current_fight.display('<-PREEMPTIVE!-<')
        s = f'{self.name}: {self.action.name} @ {self.target.name}'
        self.current_fight.display(s)

    def display_resist_ko(self) -> None:
        self.current_fight.display(f'{self.target.name} resists being knocked out!')

    def display_start_of_attack(self) -> None:
        n1 = self.current_fight.get_f_name_string(self)
        fury = ' *FURY*' if self.check_status('fury') else ''
        n2 = self.current_fight.get_f_name_string(self.target)
        s = f'{n1}{fury}: {self.action.name} @ {n2}'
        self.current_fight.display(s)
        if self.guard_while_attacking:
            self.current_fight.display(' (guarding while attacking)')
        self.current_fight.display('=' * len(s))

    def display_start_of_maneuver(self) -> None:
        n = self.current_fight.get_f_name_string(self)
        s = f'{n}: {self.action.name}'
        self.current_fight.display(s)
        self.current_fight.display('=' * len(s))
