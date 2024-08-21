from evennia.utils.utils import delay
from evennia.scripts.scripts import DefaultScript
from evennia.accounts.models import AccountDB
from random import randint
from evennia import ScriptDB
from evennia.typeclasses.chargen import SWORDSMAN_SCHOOLS
class CombatScript(DefaultScript):
    """
    This script handles the combat system.
    """
    
    
    def at_script_creation(self):
        self.key = "CombatScript"
        self.desc = "Handles combat system"
        self.persistent = True
        self.db.participants = []
        self.db.initiative_order = []
        self.db.current_actor = None
        self.db.action_state = None
        self.db.unconscious = False
        self.db.armor = 0
        self.db.round = 0  # Initialize the round counter
        
  
    def at_start(self):
        self.msg_all(f"Debug: Combat script {self.id} started.")

    def at_stop(self):
        self.msg_all(f"Debug: Combat script {self.id} stopped.")

    def start_combat(self):
        self.msg_all(f"Debug: Starting combat {self.id}")
        for participant in self.db.participants:
            participant.db.combat_id = self.id
            self.msg_all(f"Debug: Set combat_id {self.id} for {participant.name}")
            self.ensure_combat_attributes(participant)  # Add this line
            self.add_combat_cmdset(participant)
        self.roll_initiative()
        self.next_round()

    def ensure_combat_attributes(self, character):
        if not hasattr(character.ndb, 'full_defense'):
            character.ndb.full_defense = False
        if not hasattr(character.ndb, 'held_action'):
            character.ndb.held_action = False
        if not hasattr(character.db, 'flesh_wounds'):
            character.db.flesh_wounds = 0
        if not hasattr(character.db, 'dramatic_wounds'):
            character.db.dramatic_wounds = 0
        if not hasattr(character.db, 'unconscious'):
            character.db.unconscious = False
        if not hasattr(character.db, 'armor'):
            character.db.armor = 0
        # Add any other combat-related attributes here

    def add_combat_cmdset(self, character):
        from commands.mycmdset import CombatCmdSet
        character.cmdset.add(CombatCmdSet(), persistent=False)


    
    def add_participant(self, character):
        """
        Add a character to the combat.
        """
        if self.db.participants is None:
            self.db.participants = []
        self.db.participants.append(character)
        character.ndb.combat_id = self.id
        character.msg("You have been added to the combat.")

    def remove_participant(self, character):
        """
        Remove a character from the combat.
        """
        if character in self.db.participants:
            self.db.participants.remove(character)
        if hasattr(character.ndb, 'combat_id'):
            del character.ndb.combat_id
        character.msg("You have been removed from the combat.")

    def end_combat(self):
        if len(self.db.participants) == 1:
            winner = self.db.participants[0]
            self.msg_all(f"Combat has ended. {winner.name} is victorious!")
        else:
            self.msg_all("Combat has ended.")
        
        for char in self.db.participants:
            if hasattr(char.db, 'combat_id'):
                del char.db.combat_id
            self.remove_combat_cmdset(char)
        self.stop()

    def roll_initiative(self):
        initiative_rolls = []
        for char in self.db.participants:
            panache = char.db.traits['panache']
            roll = sum(sorted([randint(1, 10) for _ in range(panache)], reverse=True)[:2])  # Roll and keep highest 2
            initiative_rolls.append((char, roll, panache))
        
        # Sort by initiative roll, then by panache if there's a tie
        initiative_rolls.sort(key=lambda x: (x[1], x[2]), reverse=True)
        
        self.db.initiative_order = [(char, panache) for char, _, panache in initiative_rolls]
        self.msg_all("Initiative has been rolled.")
        for char, roll, _ in initiative_rolls:
            char.msg(f"Your initiative roll: {roll}")

    def next_round(self):
        self.db.round += 1
        self.msg_all(f"Round {self.db.round} begins.")
        # Reset actions for each character at the start of the round
        self.db.initiative_order = [(char, char.db.traits['panache']) for char, _ in self.db.initiative_order]
        # Reset full defense status
        for char in self.db.participants:
            char.ndb.full_defense = False
        self.resolve_held_actions()
        self.process_next_character()

    def process_next_character(self):
        if not self.db.initiative_order:
            self.next_round()
            return

        char, actions_left = self.db.initiative_order.pop(0)
        if actions_left > 0:
            self.db.current_actor = char
            self.offer_action(char)
            self.db.initiative_order.append((char, actions_left - 1))
        else:
            self.process_next_character()

        # Check if all characters have used all their actions
        if all(actions == 0 for _, actions in self.db.initiative_order):
            self.next_round()

            char, actions_left = self.db.initiative_order.pop(0)
            self.msg_all(f"Current actor: {char.name}, Actions left: {actions_left}")
            if actions_left > 0:
                self.db.current_actor = char
                self.offer_action(char)
                self.db.initiative_order.append((char, actions_left - 1))
            else:
                self.process_next_character()

    def offer_action(self, character):
        self.db.action_state = "choosing_action"
        character.msg(f"It's your turn in round {self.db.round}. What do you want to do?")
        character.msg("Use these commands: 'attack', 'defend', 'hold', or 'pass'")
        self.msg_all(f"Waiting for {character.name} to choose an action.")


    # def handle_action_input(self, character, choice):
    #     if self.db.action_state == "choosing_action":
    #         if choice.startswith("attack"):
    #             _, target_name = choice.split(" ", 1)
    #             self.initiate_attack(character, target_name)
    #         elif choice == "defend":
    #             self.set_full_defense(character)
    #             self.finish_turn()
    #         elif choice == "hold":
    #             self.hold_action(character)
    #             self.finish_turn()
    #         elif choice == "pass":
    #             self.pass_turn(character)
    #             self.finish_turn()
    #         else:
    #             character.msg("Invalid choice. Use 'attack <target>', 'defend', 'hold', or 'pass'.")
    #             return
    #     else:
    #         character.msg("It's not your turn to act.")

    def initiate_attack(self, character, target_name):
        target = character.search(target_name)
        if not target:
            character.msg(f"Target '{target_name}' not found.")
            return
        if target not in self.db.participants:
            character.msg(f"{target.name} is not part of this combat.")
            return
        if target == character:
            character.msg("You can't attack yourself.")
            return

        weapon = character.db.wielded_weapon if hasattr(character.db, 'wielded_weapon') else None
        combat_ended = self.perform_attack(character, target, weapon)
        if not combat_ended:
            self.finish_turn()
    
    def perform_special_move(self, character, action, target=None):
        if action == "attack":
            self.initiate_attack(character, target)
        elif action == "feint":
            self.perform_feint(character, target, character.db.wielded_weapon)
        elif action == "lunge":
            self.perform_lunge(character, target, character.db.wielded_weapon)
        elif action == "exploit":
            self.perform_exploit_weakness(character, target)
        elif action == "riposte":
            self.set_riposte(character)
        elif action == "stop-thrust":
            self.set_stop_thrust(character)
        elif action == "double-parry":
            self.set_double_parry(character)
        elif action == "defend":
            self.set_full_defense(character)
        elif action == "hold":
            self.hold_action(character)
        elif action == "pass":
            self.pass_turn(character)
        else:
            character.msg("Invalid special move.")

        if action not in ["hold", "pass"]:
            self.finish_turn()


    def handle_action_input(self, character, choice):
        if self.db.current_actor != character:
            character.msg("It's not your turn to act.")
            return

        parts = choice.split(None, 1)
        action = parts[0].lower()
        target = parts[1] if len(parts) > 1 else None

        if action in ["attack", "feint", "lunge", "exploit"]:
            if not target:
                character.msg(f"You must specify a target for {action}.")
                return
            self.perform_special_move(character, action, target)
        elif action in ["riposte", "stop-thrust", "double-parry", "defend", "hold", "pass"]:
            self.perform_special_move(character, action)
        else:
            character.msg("Invalid action. Use 'attack', a special move, 'defend', 'hold', or 'pass'.")

    

    def set_full_defense(self, character):
        if not hasattr(character.ndb, 'full_defense'):
            character.ndb.full_defense = False
        character.ndb.full_defense = True
        character.msg("You are now in full defense mode until your next action.")
        self.msg_all(f"{character.name} takes a defensive stance.")
        self.finish_turn()

    def hold_action(self, character):
        if not hasattr(character.ndb, 'held_action'):
            character.ndb.held_action = False
        character.ndb.held_action = True
        character.msg("You are holding your action. You can act later in the round.")
        self.msg_all(f"{character.name} holds their action.")
        self.finish_turn()


    def pass_turn(self, character):
            character.msg("You pass your turn.")
            self.msg_all(f"{character.name} passes their turn.")
            self.finish_turn()

    def finish_turn(self):
        self.db.action_state = None
        self.db.current_actor = None
        self.process_next_character()

    def calculate_passive_defense(self, character):
        if not character.db.wielded_weapon:
            footwork = character.db.skills.get('Martial', {}).get('Footwork', {}).get('Basic', 0)
            return 5 + (footwork * 5)
        else:
            return 15  # Default value when wielding a weapon

    def roll_keep(self, num_dice, keep):
        """
        Roll a number of dice and keep the highest.
        """
        rolls = [randint(1, 10) for _ in range(num_dice)]
        return sum(sorted(rolls, reverse=True)[:keep])

    def resolve_wounds(self, character, damage):
        """
        Resolve wounds for a character and handle defeat conditions.
        """
        current_flesh_wounds = getattr(character.db, 'flesh_wounds', 0)
        character.db.flesh_wounds = current_flesh_wounds + damage
        resolve = character.db.traits.get('resolve', 1)
        
        if character.db.flesh_wounds >= resolve * 5:
            current_dramatic_wounds = getattr(character.db, 'dramatic_wounds', 0)
            character.db.dramatic_wounds = current_dramatic_wounds + 1
            character.db.flesh_wounds -= resolve * 5
            character.msg(f"You have received a Dramatic Wound!")
        else:
            character.msg(f"You have received {damage} Flesh Wounds.")

        if character.db.dramatic_wounds >= resolve:
            if self.check_unconsciousness(character):
                self.knock_unconscious(character)
            else:
                self.kill_character(character)
            
            if len(self.db.participants) <= 1:
                self.end_combat()
            return True  # Indicate that a character was defeated
        return False  # Indicate that no character was defeated

    def check_unconsciousness(self, character):
        resolve = character.db.traits.get('resolve', 1)
        roll = self.roll_keep(resolve, resolve)
        target = 10 + character.db.dramatic_wounds
        return roll >= target

    def knock_unconscious(self, character):
        character.msg("|rYou fall unconscious.|n")
        self.msg_all(f"|r{character.name} falls unconscious!|n")
        character.db.unconscious = True
        self.remove_participant(character)

    def kill_character(self, character):
        character.msg("|rYou have been killed!|n")
        self.msg_all(f"|r{character.name} has been killed!|n")
        self.remove_participant(character)

    def attempt_regain_consciousness(self, character):
        if self.check_unconsciousness(character):
            character.db.unconscious = False
            self.msg_all(f"{character.name} has regained consciousness!")
            self.add_participant(character)
    def display_combat_status(self):
        """
        Display the status of the combat.
        """
        status = f"Current Round: {self.db.round}\nParticipants:\n"
        for char in self.db.participants:
            status += f"- {char.name}: Flesh Wounds: {char.db.get('flesh_wounds', 0)}, Dramatic Wounds: {char.db.get('dramatic_wounds', 0)}\n"
        self.msg_all(status)
    def remove_combat_cmdset(self, character):
        from commands.mycmdset import CombatCmdSet
        character.cmdset.delete(CombatCmdSet)
        self.msg_all(f"Debug: Removed CombatCmdSet from {character.name}")  

    def msg_all(self, message, exclude=None):
        """
        Send a message to all participants and observers in the room.
        
        Args:
        message (str): The message to be sent.
        exclude (Character, optional): A character to exclude from the message, if any.
        """
        # Get the room where the combat is taking place
        if self.db.participants:
            room = self.db.participants[0].location
        else:
            return  # No participants, so nowhere to send the message
        
        # Send the message to all characters in the room
        for char in room.contents:
            if char.has_account and char != exclude:  # Check if it's a player-controlled character
                if char in self.db.participants:
                    char.msg(f"|r[Combat]|n {message}")  # Highlight for participants
                else:
                    char.msg(f"|w[Combat Obs]|n {message}")  # Different style for observers
        
        # Optionally, you can also send the message to the room itself
        room.msg_contents(f"|w[Combat]|n {message}", exclude=exclude)
   
    def resolve_held_actions(self):
        held_actors = [char for char in self.db.participants if char.ndb.held_action]
        for char in held_actors:
            char.ndb.held_action = False
            self.offer_action(char)


    
    def calculate_damage(self, attacker, weapon):
        brawn = attacker.db.traits.get('brawn', 1)
        weapon_damage = weapon.db.damage if weapon else 0
        weapon_keep = weapon.db.damage_keep if weapon else 1
        flat_bonus = weapon.db.damage_bonus if weapon else 0

        total_dice = brawn + weapon_damage
        keep_dice = brawn + weapon_keep

        damage_roll = self.roll_keep(total_dice, keep_dice)
        total_damage = damage_roll + flat_bonus

        return total_damage

    def soak_damage(self, character, damage):
        resolve = character.db.traits.get('resolve', 1)
        armor_value = character.get_armor_value()
        armor_soak_keep = character.get_armor_soak_keep()

        soak_roll = self.roll_keep(resolve + armor_value, max(resolve, armor_soak_keep))

        if soak_roll >= 35:
            damage_taken = max(0, damage - soak_roll)
        elif soak_roll >= 15:
            damage_taken = max(0, damage - (soak_roll // 2))
        else:
            damage_taken = damage

        
        
        return damage_taken
        
    def perform_attack(self, attacker, target, weapon):
        # Store Initial DW
        attacker.db.dramatic_wounds_before_attack = attacker.db.dramatic_wounds

        # Check for Stop-Thrust
        if target.ndb.stop_thrust or target.ndb.held_action:
            stop_thrust_success = self.perform_stop_thrust(target, attacker)
            if stop_thrust_success:
                return True  # Attack was interrupted

        weapon_type = weapon.db.weapon_type if weapon else "Unarmed"
        attack_skill = attacker.db.skills.get('Martial', {}).get('Attack', {}).get(f"({weapon_type})", 0)
        attack_roll = self.roll_keep(attacker.db.traits['finesse'] + attack_skill, attacker.db.traits['finesse'])

        # Apply Exploit Weakness bonus if applicable
        if attacker.ndb.exploit_weakness_target == target:
            attack_roll += attacker.ndb.exploit_weakness_bonus
            attacker.ndb.exploit_weakness_target = None
            attacker.ndb.exploit_weakness_bonus = 0

        # Determine defense
        if target.ndb.full_defense:
            if target.ndb.riposte:
                riposte_success = self.perform_riposte(target, attacker, target.db.wielded_weapon)
                if riposte_success:
                    return True  # Attack was interrupted
            defense_skill = target.db.skills.get('Martial', {}).get('Parry', {}).get(f"({weapon_type})", 0)
            defense_roll = self.roll_keep(target.db.traits['wits'], defense_skill)
            defense_roll = max(defense_roll, self.calculate_passive_defense(target))
        else:
            defense_roll = self.calculate_passive_defense(target)

        # Apply Double-Parry bonus if applicable
        if target.ndb.double_parry:
            defense_roll += 5  # Add bonus for Double-Parry
            target.ndb.double_parry = False  # Reset after use

        if attack_roll > defense_roll:
            raw_damage = self.calculate_damage(attacker, weapon)
            is_critical = attack_roll > defense_roll + 15

            if is_critical:
                raw_damage *= 2  # critical hit
                self.msg_all(f"{attacker.name} scored a critical hit on {target.name}!")

            actual_damage = self.soak_damage(target, raw_damage)

            if actual_damage > 0:
                character_defeated = self.resolve_wounds(target, actual_damage)
                self.msg_all(f"{attacker.name} hit {target.name} for |r{actual_damage}|n damage!", exclude=attacker)
                attacker.msg(f"You hit {target.name} for {actual_damage} damage!")
                target.msg(f"{attacker.name} hit you for {actual_damage} damage! (Soaked {raw_damage - actual_damage})")

                if character_defeated:
                    self.msg_all("Combat has ended due to a character being defeated.")
                    return True  # Indicate that the attack was successful and combat ended
            else:
                self.msg_all(f"{target.name} completely |gsoaked the damage|n from {attacker.name}'s attack!", exclude=[attacker, target])
                attacker.msg(f"{target.name} completely soaked the damage from your attack!")
                target.msg(f"You completely soaked the damage ({raw_damage}) from {attacker.name}'s attack!")
        else:
            self.msg_all(f"{attacker.name}'s attack missed {target.name}.", exclude=attacker)
            attacker.msg(f"Your attack misses {target.name}.")

        # Reset special move states
        target.ndb.stop_thrust = False
        target.ndb.riposte = False
        target.ndb.double_parry = False
        target.ndb.full_defense = False

        return False  # Indicate that the attack was resolved but combat continues

    # def calculate_damage(self, attacker, weapon):
    #     if weapon and hasattr(weapon.db, 'damage'):
    #         return self.roll_keep(attacker.db.traits['brawn'] + weapon.db.damage, weapon.db.damage_keep)  # Assuming 'keep' is always 1
    #     else:
    #         # Unarmed attack default
    #         return self.roll_keep(attacker.db.traits.get('brawn', 1), 1)


    def perform_stop_thrust_defense(self, defender, attacker):
        stop_thrust_skill = defender.db.skills.get('Martial', {}).get(defender.db.duelist_style, {}).get('Stop-Thrust', 0)
        defense_roll = self.roll_keep(defender.db.traits['wits'] + stop_thrust_skill, defender.db.traits['wits'])
        attack_roll = self.calculate_passive_defense(attacker)

        if defense_roll > attack_roll:
            raw_damage = self.roll_keep(3, 2)  # 3k2 wounds
            actual_damage = self.soak_damage(attacker, raw_damage)
            
            if actual_damage > 0:
                character_defeated = self.resolve_wounds(attacker, actual_damage)
                self.msg_all(f"{defender.name}'s Stop-Thrust hit {attacker.name} for {actual_damage} damage!")
                
                if character_defeated:
                    self.msg_all("Combat has ended due to a character being defeated.")
                    return True  # Combat ends
                
                if attacker.db.dramatic_wounds > attacker.db.dramatic_wounds_before_attack:
                    self.msg_all(f"{attacker.name}'s attack is interrupted by the Stop-Thrust!")
                    return True  # Attack is interrupted
            else:
                self.msg_all(f"{defender.name}'s Stop-Thrust was soaked by {attacker.name}.")
        else:
            self.msg_all(f"{defender.name}'s Stop-Thrust failed against {attacker.name}.")
        
        return False  # Combat continues, attack proceeds

    def perform_riposte_defense(self, defender, attacker):
        weapon_type = defender.db.wielded_weapon.db.weapon_type if defender.db.wielded_weapon else "Unarmed"
        defense_skill = defender.db.skills.get('Martial', {}).get(defender.db.duelist_style, {}).get('Riposte', 0)
        defense_roll = self.roll_keep(defender.db.traits['wits'] + defense_skill, defender.db.traits['wits'])
        attack_roll = self.calculate_passive_defense(attacker)

        if defense_roll > attack_roll + 10:
            raw_damage = self.calculate_damage(defender, defender.db.wielded_weapon) // 2  # Half damage
            actual_damage = self.soak_damage(attacker, raw_damage)
            
            if actual_damage > 0:
                character_defeated = self.resolve_wounds(attacker, actual_damage)
                self.msg_all(f"{defender.name} successfully riposted and hit {attacker.name} for {actual_damage} damage!")
                if character_defeated:
                    self.msg_all("Combat has ended due to a character being defeated.")
                    return True  # Combat ends
            else:
                self.msg_all(f"{defender.name} riposted, but {attacker.name} soaked all the damage.")
        else:
            self.msg_all(f"{defender.name}'s riposte failed against {attacker.name}.")
        
        return False  # Combat continues




    def force_end_combat(self):
        
        self.msg_all("Combat has been forcefully ended by a staff member.")
        
        for char in self.db.participants:
            if hasattr(char.db, 'combat_id'):
                del char.db.combat_id
            self.remove_combat_cmdset(char)
            char.ndb.full_defense = False
            char.ndb.held_action = False
            # Reset any other combat-specific attributes here

        self.db.participants = []
        self.db.initiative_order = []
        self.db.current_actor = None
        self.db.action_state = None
        self.db.round = 0

        self.stop()

    def set_riposte(self, character):
        if not self.check_knack(character, 'Riposte'):
            character.msg("You don't know how to perform a Riposte.")
            return
        character.ndb.full_defense = True
        character.ndb.riposte = True
        character.msg("You prepare to riposte until your next action.")
        self.msg_all(f"{character.name} prepares to counter-attack.")

    def set_stop_thrust(self, character):
        if not self.check_knack(character, 'Stop-Thrust'):
            character.msg("You don't know how to perform a Stop-Thrust.")
            return
        character.ndb.stop_thrust = True
        character.msg("You prepare to perform a Stop-Thrust against the next attack.")
        self.msg_all(f"{character.name} prepares a defensive stance.")

    def set_double_parry(self, character):
        if not self.check_knack(character, 'Double-Parry'):
            character.msg("You don't know how to perform a Double-Parry.")
            return
        character.ndb.double_parry = True
        character.msg("You prepare to perform a Double-Parry against the next attack.")
        self.msg_all(f"{character.name} prepares an advanced defensive stance.")

    def perform_feint(self, attacker, target, weapon):
        if not self.check_knack(attacker, 'Feint'):
            attacker.msg("You don't know how to perform a Feint.")
            return False
        
        weapon_type = weapon.db.weapon_type if weapon else "Unarmed"
        attack_skill = attacker.db.skills.get('Martial', {}).get('Fencing', {}).get('Feint', 0)
        attack_roll = self.roll_keep(attacker.db.traits['finesse'] + attack_skill, attacker.db.traits['finesse'])
        defense_roll = self.calculate_passive_defense(target)

        if attack_roll > defense_roll:
            move_dice_gain = 1
            if attack_roll > defense_roll + 15:
                move_dice_gain = 3
                self.msg_all(f"{attacker.name} performed a |555brilliant|n feint against {target.name}!")
            else:
                self.msg_all(f"{attacker.name} feinted against {target.name} |455successfully.|n")
            attacker.db.move_dice = attacker.db.move_dice + move_dice_gain if hasattr(attacker.db, 'move_dice') else move_dice_gain
            attacker.msg(f"You gained {move_dice_gain} Drama Dice. Total: {attacker.db.move_dice}")
        else:
            self.msg_all(f"{attacker.name}'s feint |400failed|n against {target.name}.")   

        return False

    def perform_riposte(self, defender):
        if not self.check_knack(defender, 'Riposte'):
            defender.msg("You don't know how to perform a Riposte.")
            return False
        defender.ndb.full_defense = True
        defender.ndb.riposte = True
        defender.msg("You prepare to riposte until your next action.")
        self.msg_all(f"{defender.name} prepares to counter-attack.")

    def perform_lunge(self, attacker, target, weapon):
        if not self.check_knack(attacker, 'Lunge'):
            attacker.msg("You don't know how to perform a Lunge.")
            return False

        weapon_type = weapon.db.weapon_type if weapon else "Unarmed"
        attack_skill = attacker.db.skills.get('Martial', {}).get('Fencing', {}).get('Lunge', 0)
        attack_roll = self.roll_keep(attacker.db.traits['finesse'] + attack_skill, attacker.db.traits['finesse']) - 5  # -5 penalty
        defense_roll = self.calculate_passive_defense(target)

        if attack_roll > defense_roll:
            raw_damage = self.calculate_damage(attacker, weapon) + 10  # +10 damage
            actual_damage = self.soak_damage(target, raw_damage)
            
            if actual_damage > 0:
                character_defeated = self.resolve_wounds(target, actual_damage)
                self.msg_all(f"{attacker.name}'s lunge hit {target.name} for {actual_damage} damage!")
                if character_defeated:
                    self.msg_all("Combat has ended due to a character being defeated.")
                    return True  # Combat ends
            else:
                self.msg_all(f"{attacker.name}'s lunge was soaked by {target.name}.")
        else:
            self.msg_all(f"{attacker.name}'s lunge missed {target.name}.")
        return False

    def perform_stop_thrust(self, defender):
        defender.ndb.stop_thrust = True
        defender.msg("You prepare to perform a Stop-Thrust against the next attack.")
        self.msg_all(f"{defender.name} prepares a defensive stance.")
    def perform_double_parry(self, character):
        character.ndb.double_parry = True
        character.msg("You prepare to use Double-Parry against the next attack.")
        self.msg_all(f"{character.name} prepares a complex defensive stance.")

    def perform_exploit_weakness(self, attacker, target):
        if not self.check_knack(attacker, 'Exploit Weakness'):
            attacker.msg("You don't know how to Exploit Weakness.")
            return False

        exploit_skill = attacker.db.skills.get('Martial', {}).get('Fencing', {}).get('Exploit Weakness', 0)
        exploit_roll = self.roll_keep(attacker.db.traits['wits'] + exploit_skill, attacker.db.traits['wits'])
        defense_roll = self.calculate_passive_defense(target)

        if exploit_roll > defense_roll:
            move_dice_gain = 1
            if exploit_roll > defense_roll + 15:
                move_dice_gain = 2
                self.msg_all(f"{attacker.name} brilliantly exploited {target.name}'s weakness!")
            else:
                self.msg_all(f"{attacker.name} successfully exploited {target.name}'s weakness.")
            attacker.db.move_dice = attacker.db.move_dice + move_dice_gain if hasattr(attacker.db, 'move_dice') else move_dice_gain
            attacker.msg(f"You gained {move_dice_gain} Drama Dice. Total: {attacker.db.move_dice}")
        else:
            self.msg_all(f"{attacker.name} failed to exploit {target.name}'s weakness.")

        return False  # Combat continues

    # def offer_special_moves(self, character):
    #     available_moves = []
    #     for school, details in character.db.skills.get('Martial', {}).items():
    #         if school in SWORDSMAN_SCHOOLS:
    #             for knack in details.keys():
    #                 if knack in ["Feint", "Riposte", "Lunge", "Stop-Thrust", "Double-Parry", "Exploit Weakness"]:
    #                     available_moves.append(knack.lower())
    #         elif school == character.db.duelist_style:
    #             # Add school-specific special moves
    #             for knack in details.keys():
    #                 if knack in ["Feint", "Riposte", "Lunge", "Stop-Thrust", "Double-Parry", "Exploit Weakness"]:
    #                     available_moves.append(knack.lower())

    #     # Remove duplicates and sort
    #     available_moves = sorted(set(available_moves))

    #     if not available_moves:
    #         character.msg("You don't have any special moves available.")
    #         return

    #     move_list = ", ".join(available_moves)
    #     character.msg(f"Available special moves: {move_list}")
    #     character.msg("Choose a special move or type 'cancel' to go back.")
        
    #     # Set the character's state to waiting for special move input
    #     character.ndb.combat_state = "choosing_special_move"
                

        
def get_combat(caller):
    if hasattr(caller.db, 'combat_id'):
        combat_id = caller.db.combat_id
        combat = ScriptDB.objects.filter(id=combat_id, db_key='CombatScript').first()
        if combat:
            return combat
        else:
            caller.msg(f"Debug: Combat with ID {combat_id} not found for {caller.name}")
            del caller.db.combat_id  # Remove the invalid combat_id
    else:
        caller.msg(f"Debug: No combat_id attribute found for {caller.name}")
    return None
    
    