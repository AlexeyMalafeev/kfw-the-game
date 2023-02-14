___  
|LV1|DIFF|FIGHTS PER LV|  
|100| 0|2.50|  
|100|10|4.09|  
|100|20|4.52|  
|100|50|7.30|  
___
|LV1|DIFF|FIGHTS PER PLAYER|  
|100| 0|11.91|  
|100|10|23.30|  
|100|20|40.29|  
|100|50|48.32|  
---
Fight loop:
1. start_fight_turn
   * refresh_per_turn_attributes
   * do_per_turn_actions
2. choose_target
3. choose_move
4. exec_move 
   * A) attack
     * apply guard_while_attacking (affects dfs_bonus)
     * a) target.check_preemptive, target.do_preemptive
     * b) try_strike
       * do_strike
         * calc_atk (curr_atk_mult, potential_dam, to_hit)
         * target.calc_dfs (curr_dfs_mult, to_dodge, to_block)
         * target.try_defend (do_dodge, do_block or take a hit)
         * try_hit 
     * b) target.try_counter
   * B) maneuver (dist_change, do_move_functions)
