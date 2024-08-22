from evennia import DefaultScript
from evennia.utils.utils import inherits_from
from evennia import ScriptDB
from random import randint
from world.character_sheet.models import CharacterSheet


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
        self.db.soak_keep = 0
  
    def at_start(self):
        self.msg_all(f"Debug: Combat script {self.id} started.")

    def at_stop(self):
        self.msg_all(f"Debug: Combat script {self.id} stopped.")

    def start_combat(self):
        for participant in self.db.participants:
            self.ensure_combat_attributes(participant)
            participant.db.combat_id = self.id
            self.add_combat_cmdset(participant)
            
            # Double-check special_effects initialization
            if not hasattr(participant.ndb, 'special_effects') or participant.ndb.special_effects is None:
                participant.ndb.special_effects = []
            
            self.check_combat_advantages(participant)
        
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
        if not hasattr(character.db, 'move_dice'):
            character.db.move_dice = 0
        if not hasattr(character.db, 'special_effects'):
            character.db.special_effects = []
        if not hasattr(character.db, 'soak_keep'):
            character.db.soak_keep = 0
        
        # Ensure ndb.special_effects exists
        if not hasattr(character.ndb, 'special_effects'):
            character.ndb.special_effects = []
            
            # Add any other combat-related attributes here

    def add_combat_cmdset(self, character):
        from commands.mycmdset import CombatCmdSet
        character.cmdset.add(CombatCmdSet(), persistent=False)


    def check_combat_advantages(self, character):
        # Ensure ndb.special_effects is always a list
        if not hasattr(character.ndb, 'special_effects') or character.ndb.special_effects is None:
            character.ndb.special_effects = []
        
        # Get the character's advantages
        advantages = character.get_advantages()
        for advantage in advantages:
            adv_name = advantage.get('name', '')
            adv_level = advantage.get('level', 1)
            
            if adv_name == 'Combat Reflexes' and "combat_reflexes" not in character.ndb.special_effects:
                character.ndb.special_effects.append("combat_reflexes")
                character.msg("Your Combat Reflexes advantage is active.")
            elif adv_name == "Toughness" and "toughness" not in character.ndb.special_effects:
                character.ndb.special_effects.append("toughness")
            elif adv_name == "Indomitable Will" and "indomitable_will" not in character.ndb.special_effects:
                character.ndb.special_effects.append("indomitable_will")

        return character.ndb.special_effects

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

    def is_combat_valid(self):
        if len(self.db.participants) < 2:
            self.end_combat()
            return False
        
        return True 

    def end_combat(self):
        for char in self.db.participants:
            if hasattr(char.db, 'combat_id'):
                del char.db.combat_id
            self.remove_combat_cmdset(char)
            
            # Update the character sheet with final combat results
            if hasattr(char, 'character_sheet'):
                char.character_sheet.save()
            
            # Clear temporary combat effects
            char.ndb.flesh_wounds = 0
            char.ndb.special_effects = []
            char.db.special_effects = []  # Clear persistent special effects too
            char.ndb.full_defense = False
            char.ndb.riposte = False
            char.ndb.held_action = False
            char.ndb.stop_thrust = False
            char.ndb.double_parry = False
            
            char.msg("Combat has ended. Your flesh wounds have healed, but any dramatic wounds remain.")

        self.msg_all("Combat has ended.")
        self.stop()
    
    def offer_action(self, character):
        self.db.action_state = "choosing_action"
        character.msg(f"It's your turn in round {self.db.round}. What do you want to do?")
        character.msg("Use these commands: 'attack', 'defend', 'hold', or 'pass'")
        self.msg_all(f"Waiting for {character.name} to choose an action.")

    def initiate_attack(self, character, target_name):
        target = character.search(target_name)
        if not target:
            character.msg(f"Target '{target_name}' not found.")
            return False

        if target not in self.db.participants:
            character.msg(f"{target.name} is not part of this combat.")
            return False

        if target == character:
            character.msg("You can't attack yourself.")
            return False

        weapon = (character.db.wielded_weapon if hasattr(character.db, 'wielded_weapon') else None)
        combat_ended = self.perform_attack(character, target, weapon)

        return True  # The attack was initiated successfully
    
    
    def apply_combat_effects(self, character, action_type):
        bonus = 0
        
        if "combat_reflexes" in character.ndb.special_effects:
            if action_type == "initiative":
                bonus += 5  # +5 to Initiative

        if "indomitable_will" in character.ndb.special_effects:
            if action_type == "social_defense":
                bonus += 2  # +2 dice when resisting Contested social rolls

        # Other effects remain the same...
        if action_type == "defense" and "portewalk" in character.ndb.special_effects:
            bonus += 2
            self.msg_all(f"{character.name}'s Porte Walk is active, increasing their defense.")
        
        # Sorte effects
        if action_type == "defense" and "cups_boost" in character.ndb.special_effects:
            bonus += 1
        if action_type == "defense" and "cups_curse" in character.ndb.special_effects:
            bonus -= 2
        if action_type == "attack" and "swords_boost" in character.ndb.special_effects:
            bonus += 2
        if action_type == "attack" and "swords_curse" in character.ndb.special_effects:
            bonus -= 1
        if "staves" in character.ndb.special_effects:
            bonus += 1  # Applies to both attack and defense
        if "arcana_boost" in character.ndb.special_effects:
            bonus += 5  # Applies to both attack and defense

        return bonus
    
    def roll_initiative(self):
        initiative_rolls = []
        for char in self.db.participants:
            panache = char.db.traits['panache']
            base_roll = randint(1, 10) + (panache * 3)
            
            if "combat_reflexes" in char.ndb.special_effects:
                base_roll += 5
                char.msg("Your Combat Reflexes give you a +5 bonus to initiative!")

            initiative_rolls.append((char, base_roll))
        
        initiative_rolls.sort(key=lambda x: x[1], reverse=True)
        
        self.db.initiative_order = [char for char, _ in initiative_rolls]
        
        for char, roll in initiative_rolls:
            char.msg(f"Your initiative roll: {roll}")

    def next_round(self):
        self.db.round += 1
        if self.db.round > 100:  # Arbitrary high number
            self.msg_all("Combat has gone on for too many rounds. Ending combat.")
            self.end_combat()
            return

        self.msg_all(f"Round {self.db.round} begins.")
        self.roll_initiative()
        self.process_next_character()

    def process_next_character(self):
        if not self.db.initiative_order:
            self.next_round()
            return

        self.db.current_actor = self.db.initiative_order.pop(0)
        self.offer_action(self.db.current_actor)

    def finish_turn(self):
        current_actor = self.db.current_actor
        if current_actor:
            self.reset_combat_states(current_actor)
        self.db.action_state = None
        self.db.current_actor = None
        self.process_next_character()

    def all_characters_acted(self):
     return len(self.db.initiative_order) == 0

    def reset_combat_states(self, character):
                character.ndb.combat_state = None
                character.ndb.full_defense = False
                character.ndb.riposte = False
                character.ndb.held_action = False
                character.ndb.stop_thrust = False
                character.ndb.double_parry = False
                character.ndb.exploit_weakness_target = None
                character.ndb.exploit_weakness_bonus = 0

    def handle_action_input(self, character, choice):
        try:
            if self.db.current_actor != character:
                character.msg("It's not your turn to act.")
                return

            parts = choice.split(None, 1)
            action = parts[0].lower()
            target = parts[1] if len(parts) > 1 else None

            combat_ended = False

            if action == "attack":
                if not target:
                    character.msg("You must specify a target for attack.")
                    return
                target_character = character.search(target)
                if not target_character or target_character not in self.db.participants:
                    character.msg(f"Invalid target: {target}")
                    return
                combat_ended = self.perform_attack(character, target_character, character.db.wielded_weapon)
            else:
                self.perform_special_move(character, action, target)

            if combat_ended:
                self.end_combat()
            else:
                self.finish_turn()

        except Exception as e:
            self.msg_all(f"Error in combat: {str(e)}")
            self.end_combat()

    def perform_special_move(self, character, action, target=None):
        action_successful = False
        target_character = None

        if target:
            target_character = character.search(target)
            if not target_character or target_character not in self.db.participants:
                character.msg(f"Invalid target: {target}")
                return False

        try:
            if action == "attack":
                if not target_character:
                    character.msg("You must specify a target for attack.")
                    return False
                action_successful = self.initiate_attack(character, target_character)

            elif action == "feint":
                if not target_character:
                    character.msg("You must specify a target for feint.")
                    return False
                action_successful = self.perform_feint(character, target_character, character.db.wielded_weapon)

            elif action == "lunge":
                if not target_character:
                    character.msg("You must specify a target for lunge.")
                    return False
                action_successful = self.perform_lunge(character, target_character, character.db.wielded_weapon)

            elif action == "exploit":
                if not target_character:
                    character.msg("You must specify a target for exploit weakness.")
                    return False
                action_successful = self.perform_exploit_weakness(character, target_character)

            elif action == "riposte":
                action_successful = self.set_riposte(character)

            elif action in ["stop-thrust", "stopthrust"]:
                action_successful = self.set_stop_thrust(character)

            elif action in ["double-parry", "doubleparry"]:
                action_successful = self.set_double_parry(character)

            elif action == "defend":
                action_successful = self.set_full_defense(character)

            elif action == "hold":
                action_successful = self.hold_action(character)

            elif action == "pass":
                action_successful = self.pass_turn(character)

            else:
                character.msg(f"Invalid special move: {action}")
                return False


        except Exception as e:
            self.msg_all(f"Error in perform_special_move: {str(e)}")
            return False



            
    def perform_exploit_weakness(self, attacker, target_name):
        target = attacker.search(target_name)
        if not target or target not in self.db.participants:
            attacker.msg(f"Invalid target: {target_name}")
            return

        if not self.check_knack(attacker, 'Exploit Weakness'):
            attacker.msg("You don't know how to Exploit Weakness.")
            return

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
            attacker.ndb.exploit_weakness_target = target
            attacker.ndb.exploit_weakness_bonus = move_dice_gain * 5  # 5 point bonus per Drama Die
            attacker.msg(f"You gained a +{attacker.ndb.exploit_weakness_bonus} bonus to your next attack against {target.name}.")
        else:
            self.msg_all(f"{attacker.name} failed to exploit {target.name}'s weakness.")


    def offer_special_moves(self, character):
        available_moves = []
        move_checks = [
            ('Feint', 'Feint'),
            ('Riposte', 'Riposte'),
            ('Lunge', 'Lunge'),
            ('Stop-Thrust', 'Stop-Thrust'),
            ('Double-Parry', 'Double-Parry'),
            ('Exploit Weakness', 'Exploit Weakness')
        ]
        
        
        for move, skill_name in move_checks:
            if self.check_knack(character, skill_name):
                available_moves.append(move.lower())

        if not available_moves:
            character.msg("You don't have any special moves available.")
            return

        move_list = ", ".join(available_moves)
        character.msg(f"Available special moves: {move_list}")
        character.msg("Choose a special move or type 'cancel' to go back.")
        
        # Set the character's state to waiting for special move input
        character.ndb.combat_state = "choosing_special_move"

    def handle_special_move(self, character, move):
        if move == "feint":
            if not self.check_knack(character, 'Feint'):
                character.msg("You don't know how to perform a Feint.")
                return
            character.msg("Specify a target for your Feint.")
            character.ndb.combat_state = "feint_target"
        elif move == "riposte":
            if not self.check_knack(character, 'Riposte'):
                character.msg("You don't know how to perform a Riposte.")
                return
            self.set_riposte(character)
        elif move == "lunge":
            if not self.check_knack(character, 'Lunge'):
                character.msg("You don't know how to perform a Lunge.")
                return
            character.msg("Specify a target for your Lunge.")
            character.ndb.combat_state = "lunge_target"
        elif move == "stop-thrust":
            if not self.check_knack(character, 'Stop-Thrust'):
                character.msg("You don't know how to perform a Stop-Thrust.")
                return
            character.ndb.combat_state = "stop-thrust"
            character.msg("You prepare to perform a Stop-Thrust against the next attack.")
            # self.msg_all(f"{character.name} prepares a defensive stance.")
            self.finish_turn()
        else:
            character.msg("Invalid special move.")

    def set_stop_thrust(self, character):
        if not self.check_knack(character, 'Stop-Thrust'):
            character.msg("You don't know how to perform a Stop-Thrust.")
            return False
        if 'stopthrusted' not in character.db.special_effects:
            character.db.special_effects.append('stopthrusted')
        # character.msg("You prepare to perform a Stop-Thrust against the next attack.")
        self.msg_all(f"{character.name} prepares a defensive stance.")
        return True

    def set_double_parry(self, character):
        if not (self.check_knack(character, 'Double Parry') or 
                self.check_knack(character, 'Double-Parry') or 
                self.check_knack(character, 'Double Parry (Sword/Cane)') or
                self.check_knack(character, 'Double Parry (Sword/Knife)')):
            character.msg("You don't know how to perform a Double-Parry.")
            return False
        
        if 'doubleparry' not in character.db.special_effects:
            character.db.special_effects.append('doubleparry')
        # character.msg("You prepare to perform a Double-Parry against the next attack.")
        self.msg_all(f"{character.name} brings both weapons to bear for a defense.")
        return True
            

    def set_full_defense(self, character):
        if not hasattr(character.ndb, 'full_defense'):
            character.ndb.full_defense = False
        character.ndb.full_defense = True
        character.ndb.riposte = False  # Reset riposte
        # character.msg("You are now in full defense mode until your next action.")
        self.msg_all(f"{character.name} takes a defensive stance.")
        self.finish_turn()

    def set_riposte(self, character):
        if not hasattr(character.ndb, 'full_defense'):
            character.ndb.full_defense = False
        if not self.check_knack(character, 'Riposte'):
            character.msg("You don't know how to perform a Riposte.")
            return False
        if 'riposte_prepared' not in character.db.special_effects:
            character.db.special_effects.append('riposte_prepared')
        character.ndb.full_defense = True
        character.ndb.riposte = True
        character.msg("You prepare to riposte until your next action.")
        # self.msg_all(f"{character.name} prepares to counter-attack.")
        self.finish_turn()

    def hold_action(self, character):
        if not hasattr(character.ndb, 'held_action'):
            character.ndb.held_action = False
        character.ndb.held_action = True
        character.msg("You are holding your action. You can act later in the round.")
        # self.msg_all(f"{character.name} holds their action.")
        self.finish_turn()


    def pass_turn(self, character):
            # character.msg("You pass your turn.")
            self.msg_all(f"{character.name} passes their turn.")
            self.finish_turn()

    

    def calculate_passive_defense(self, character):
        if not character.db.wielded_weapon:
            footwork = character.db.skills.get('Martial', {}).get('Footwork', {}).get('Basic', 0)
            return 5 + (footwork * 5)
        
        else:
            return 15  # Default value when wielding a weapon

    def roll_keep(self, num_dice, keep):
        """
        Roll a number of dice and keep the highest.
        
        Args:
        num_dice (int): Number of dice to roll
        keep (int): Number of highest dice to keep
        
        Returns:
        int: Sum of the highest 'keep' dice rolls
        """
        try:
            # Ensure inputs are valid integers
            num_dice = max(1, int(num_dice))
            keep = max(1, min(int(keep), num_dice))
            
            rolls = []
            for _ in range(num_dice):
                roll = randint(1, 10)
                rolls.append(roll)
                # Exploding dice: if you roll a 10, roll again and add it
                while roll == 10:
                    roll = randint(1, 10)
                    rolls.append(roll)
            
            # Sort rolls in descending order and keep the highest 'keep' number of rolls
            kept_rolls = sorted(rolls, reverse=True)[:keep]
            total = sum(kept_rolls)
            
            self.msg_all(f"Debug: roll_keep - Dice: {num_dice}, Keep: {keep}")
            self.msg_all(f"Debug: All rolls: {rolls}")
            self.msg_all(f"Debug: Kept rolls: {kept_rolls}")
            self.msg_all(f"Debug: Total: {total}")
            
            return total
        
        except Exception as e:
            self.msg_all(f"Error in roll_keep: {str(e)}")
            return 0  # Return 0 as a safe default if an error occurs

            
    def resolve_automatic_wounds(self, character, damage):

        current_flesh_wounds = character.db.flesh_wounds
        character.db.flesh_wounds = current_flesh_wounds + damage

    def resolve_wounds(self, character, damage):
        current_flesh_wounds = character.character_sheet.flesh_wounds
        character.character_sheet.flesh_wounds = current_flesh_wounds + damage
        character.character_sheet.save(update_fields=['flesh_wounds'])
        resolve = character.db.traits.get('resolve', 1)
        
        if character.character_sheet.flesh_wounds >= resolve * 5:
            character.character_sheet.dramatic_wounds = character.character_sheet.dramatic_wounds + 1
            character.character_sheet.flesh_wounds -= resolve * 5
            character.character_sheet.save(update_fields=['dramatic_wounds'])
            self.msg_all(f"{character.name} has received a Dramatic Wound!", exclude=None)

        if character.character_sheet.dramatic_wounds >= resolve * 2:
            if self.check_unconsciousness(character):
                self.msg_all(f"{character.name} stands at the edge of death and remains standing!")
            else:
                self.knock_unconscious(character)
            return True  # Indicate that the character was defeated
        if character.character_sheet.dramatic_wounds >= resolve * 2 + 2:
            if self.check_death(character):
                self.msg_all(f"{character.name}, despite all odds, remains alive.")
            else:
                self.kill_character(character)
                return True
        character.msg(f"You have received {damage} Flesh Wounds.")
        self.msg_all(f"{character.name} has received {damage} Flesh Wounds.", exclude=character)
        return False  # Indicate that the character was not defeated


    def check_death(self, charaacter):
        resolve = charaacter.db.traits.get('resolve', 1)
        roll = self.roll_keep(resolve, resolve)
        target = 5 + character.db.dramatic_wounds
        return roll >= target

    def check_unconsciousness(self, character):
        resolve = character.db.traits.get('resolve', 1)
        roll = self.roll_keep(resolve, resolve)
        target = 10 + character.db.dramatic_wounds
        return roll >= target

    def knock_unconscious(self, character):
        character.msg("|rYou fall unconscious.|n")
        self.msg_all(f"|352{character.name} falls unconscious!|n")
        character.ndb.unconscious = True
        self.remove_participant(character)

    def kill_character(self, character):
        character.msg("|rYou have been killed!|n")
        self.msg_all(f"|500{character.name} has been killed!|n")
        self.remove_participant(character)
        character.character_sheet.approved = False
        character.character_sheet.save(update_fields=['approved'])

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

    def msg_all(self, message, exclude=None):
        """
        Send a message to all participants and observers in the room.
        
        Args:
        message (str): The message to be sent.
        exclude (Character or list, optional): A character or list of characters to exclude from the message.
        """
        if not self.db.participants:
            return  # No participants, so nowhere to send the message

        room = self.db.participants[0].location
        
        # Prepare the messages
        combat_msg = f"|r[Combat]|n {message}"
        observer_msg = f"|w[Combat Obs]|n {message}"
        
        # Ensure exclude is a list
        if exclude and not isinstance(exclude, list):
            exclude = [exclude]
        elif not exclude:
            exclude = []

        # Send messages to all characters in the room
        for char in room.contents:
            if char.has_account and char not in exclude:
                if char in self.db.participants:
                    char.msg(combat_msg)
                else:
                    char.msg(observer_msg)

        # No need to send a separate message to the room
   
    def resolve_held_actions(self):
        held_actors = [char for char in self.db.participants if char.ndb.held_action]
        for char in held_actors:
            char.ndb.held_action = False
            self.offer_action(char)

    def check_knack(self, character, move_name):
        # Check regular skills first
        for category, skills in character.db.skills.items():
            for skill, knacks in skills.items():
                if move_name.lower() == skill.lower():
                    return True
                for knack in knacks.keys():
                    if move_name.lower() in knack.lower():
                        return True

        # Check swordsman school knacks
        swordsman_knacks = character.get_swordsman_knacks()
        for school, knacks in swordsman_knacks.items():
            for knack in knacks.keys():
                if move_name.lower() in knack.lower():
                    return True

        return False




    def calculate_damage(self, attacker, weapon):
        brawn = attacker.db.traits.get('brawn', 1)
        weapon_damage = getattr(weapon.db, 'damage', 0) if weapon else 0
        weapon_keep = getattr(weapon.db, 'damage_keep', 1) if weapon else 1
        flat_bonus = getattr(weapon.db, 'damage_bonus', 0) if weapon else 0

        total_dice = brawn + weapon_damage
        keep_dice = min(brawn + weapon_keep, total_dice)  # Ensure we don't keep more dice than we roll

        damage_roll = self.roll_keep(total_dice, keep_dice)
        total_damage = damage_roll + flat_bonus

        self.msg_all(f"Debug: Damage calculation - Brawn: {brawn}, Weapon damage: {weapon_damage}, "
                    f"Weapon keep: {weapon_keep}, Flat bonus: {flat_bonus}, Total damage: {total_damage}")

        return total_damage

            
    def soak_damage(self, character, damage):
        try:
            resolve = character.db.traits.get('resolve', 1)
            total_armor = getattr(character.db, 'total_armor', 0)
            soak_dice = int(resolve)
          
            self.msg_all(f"Debug: Soak dice: {soak_dice}")
            
            soak_bonus = self.apply_combat_effects(character, "soak") + total_armor
            soak_bonus = 0 if soak_bonus is None else soak_bonus + (total_armor // 3)
            self.msg_all(f"Debug: Soak bonus from effects: {soak_bonus}")
            soak_keep = character.db.traits['resolve'] + (total_armor // 3)
            soak_roll = self.roll_keep(soak_dice, soak_keep)
            self.msg_all(f"Debug: Soak roll result: {soak_roll}")
            
            total_soak = soak_roll + soak_bonus
            self.msg_all(f"Debug: Total soak (roll + bonus): {total_soak}")
            
            # Ensure total_soak is an integer
            total_soak = int(total_soak)
            
            if total_soak >= 35:
                damage_taken = max(0, damage - total_soak)
            elif total_soak >= 15:
                damage_taken = max(0, damage - (total_soak // 2))
            else:
                damage_taken = damage
            
            self.msg_all(f"Debug: Final damage taken: {damage_taken}")
            return damage_taken
        
        except Exception as e:
            self.msg_all(f"Error in soak_damage: {str(e)}")
            self.msg_all(f"Debug: resolve={resolve}, total_armor={total_armor}, soak_dice={soak_dice}, "
                        f"soak_keep={soak_keep}, soak_bonus={soak_bonus}, "
                        f"soak_roll={soak_roll}, total_soak={total_soak}")
            return damage  # If an error occurs, return full damage
                
    def get_double_parry_skill(self, character):
        skill_value = 0
        weapon_combination = None
        
        double_parry_variants = [
            "Double-Parry (Fencing/Knife)",  # Valroux and Villanova
            "Double-Parry (Cloak/Fencing)",  # Torres
            "Double-Parry (Fencing/Fencing)",  # Soldano
            "Double-Parry",  # Generic version without weapons specified
            "Double Parry"  # Version without hyphen
        ]
        
        for category, skills in character.db.skills.items():
            for skill, knacks in skills.items():
                for knack, value in knacks.items():
                    for variant in double_parry_variants:
                        if variant.lower() in knack.lower():
                            if value > skill_value:
                                skill_value = value
                                weapon_combination = variant.split('(')[-1].strip(')') if '(' in variant else None
                            break  # Found a match, no need to check other variants for this knack
        
        return skill_value, weapon_combination

    def set_double_parry(self, character):
        double_parry_skill, weapon_combination = self.get_double_parry_skill(character)
        
        if double_parry_skill == 0:
            character.msg("You don't know how to perform a Double-Parry.")
            return False
        
        if 'doubleparry' not in character.db.special_effects:
            character.db.special_effects.append('doubleparry')
        
        if weapon_combination:
            character.msg(f"You prepare to perform a Double-Parry with {weapon_combination} (skill level: {double_parry_skill}) against the next attack.")
            # self.msg_all(f"{character.name} brings {weapon_combination} to bear for a Double-Parry defense.")
        else:
            character.msg(f"You prepare to perform a Double-Parry (skill level: {double_parry_skill}) against the next attack.")
            # self.msg_all(f"{character.name} prepares for a Double-Parry defense.")
        
        return True



    def perform_attack(self, attacker, target, weapon):
        try:
            weapon = weapon
            # Store Initial DW and prepare for attack
            attacker.ndb.dramatic_wounds_before_attack = attacker.db.dramatic_wounds
            # Handle the case where weapon is None
            if weapon is None:
                dirty_fighting_option = True if attacker.db.skills.get('Dirty Fighting', {}).get(f'Attack (Dirty Fighting)', 0) > 0 else "Unarmed"
                pugilism_option = True if attacker.db.skills.get('Pugilism', {}).get(f'Attack (Pugilism)', 0) > 0 else "Unarmed"
                if pugilism_option:
                    weapon_type = "Pugilism" if pugilism_option else "Unarmed"
                    weapon_attack = "Attack (Pugilism)" if pugilism_option else "Attack (Unarmed)"
                elif dirty_fighting_option:
                    weapon_type = "Dirty Fighting"
                    weapon_attack = "Attack (Dirty Fighting)"
                else:
                    weapon_type = "Unarmed"
                    weapon_attack = "Attack (Unarmed)"
            
            weapon_type = weapon.db.weapon_type
            weapon_attack = weapon.db.attack_skill

            # Check for Stop-Thrust
            if self.check_stop_thrust(target):
                stop_thrust_success = self.perform_stop_thrust(target, attacker)
                if stop_thrust_success:
                    return False  # Attack was interrupted

            # Calculate attack roll
            attack_roll = self.calculate_attack_roll(attacker, weapon_type, weapon_attack)
            
            # Determine defense
            defense_roll = self.calculate_defense_roll(target, weapon_type)

            self.msg_all(f"Debug: Attack roll: {attack_roll}, Defense roll: {defense_roll}")

            # Resolve the attack
            if attack_roll > defense_roll:
                return self.resolve_successful_attack(attacker, target, weapon, attack_roll, defense_roll)
            else:
                return self.resolve_missed_attack(attacker, target)

        except Exception as e:
            self.msg_all(f"Error in perform_attack: {str(e)}")
            return False

    def check_stop_thrust(self, target):
        return (target.ndb.stop_thrust or 
                target.ndb.held_action or 
                'stopthrusted' in target.db.special_effects)

    def calculate_attack_roll(self, attacker, weapon_type, weapon_attack):
        attack_bonus = self.apply_combat_effects(attacker, "attack")
        
        # Attempt to fetch the skill for the weapon type
        attack_skill = attacker.db.skills.get('Martial', {}).get(weapon_type, {}).get(weapon_attack, 0)
        
        # If not found, try to fetch under a different structure
        if attack_skill == 0:
            attack_skill = attacker.db.skills.get('Martial', {}).get(weapon_attack, {}).get(f'Attack ({weapon_type})', 0)
        
        # Calculate the roll
        attack_roll = self.roll_keep(attacker.db.traits['finesse'] + attack_skill, attacker.db.traits['finesse'])
        attack_roll += attack_bonus

        # Apply Exploit Weakness bonus if applicable
        if attacker.ndb.exploit_weakness_target == attacker:
            attack_roll += attacker.ndb.exploit_weakness_bonus
            attacker.ndb.exploit_weakness_target = None
            attacker.ndb.exploit_weakness_bonus = 0

        return attack_roll

    def calculate_defense_roll(self, target, weapon_type):
        defense_bonus = self.apply_combat_effects(target, "defense")
        if target.ndb.full_defense:
            if target.ndb.riposte:
                riposte_success = self.perform_riposte(target, self.db.current_actor, target.db.wielded_weapon)
                if riposte_success:
                    return None  # Indicates that the attack was interrupted
            
            defense_skill = target.db.skills.get('Martial', {}).get('Parry', {}).get(f"({weapon_type})", 0)
            defense_roll = self.roll_keep(target.db.traits['wits'] + defense_skill, target.db.traits['wits'])
            defense_roll = max(defense_roll, self.calculate_passive_defense(target)) + defense_bonus
        else:
            defense_roll = self.calculate_passive_defense(target) + defense_bonus
        
        # Apply Double-Parry bonus if applicable
        if target.ndb.double_parry or 'doubleparry' in target.ndb.special_effects:
            double_parry_skill, _ = self.get_double_parry_skill(target)
            defense_roll += 5 * double_parry_skill
            if 'doubleparry' in target.ndb.special_effects:
                target.ndb.special_effects.remove('doubleparry')
            target.ndb.double_parry = False  # Reset after use
        
        return defense_roll



    def resolve_successful_attack(self, attacker, target, weapon, attack_roll, defense_roll):
        try:
            raw_damage = self.calculate_damage(attacker, weapon)
            is_critical = attack_roll > defense_roll + 25

            if is_critical:
                raw_damage *= 2  # critical hit
                self.msg_all(f"{attacker.name} scored a critical hit on {target.name}!")

            self.msg_all(f"Debug: Raw damage before soak: {raw_damage}")

            actual_damage = self.soak_damage(target, raw_damage)

            self.msg_all(f"Debug: Actual damage after soak: {actual_damage}")

            if actual_damage > 0:
                character_defeated = self.resolve_wounds(target, actual_damage)
                self.msg_all(f"{attacker.name} hit {target.name} for |r{actual_damage}|n damage!", exclude=attacker)
                attacker.msg(f"You hit {target.name} for {actual_damage} damage!")
                target.msg(f"{attacker.name} hit you for {actual_damage} damage! (Soaked {raw_damage - actual_damage})")

                if character_defeated:
                    self.msg_all("Combat has ended due to a character being defeated.")
                    self.end_combat()
                    return True  # Indicate that the attack was successful and combat ended
            else:
                self.msg_all(f"{target.name} completely |gsoaked the damage|n from {attacker.name}'s attack!", exclude=[attacker, target])

            return False
        except Exception as e:
            self.msg_all(f"Error in resolve_successful_attack: {str(e)}")
            return False

    def resolve_missed_attack(self, attacker, target):
        self.msg_all(f"{attacker.name}'s attack missed {target.name}.", exclude=attacker)
        attacker.msg(f"Your attack misses {target.name}.")
        return False
    # def calculate_damage(self, attacker, weapon):
    #     if weapon and hasattr(weapon.db, 'damage'):
    #         return self.roll_keep(attacker.db.traits['brawn'] + weapon.db.damage, weapon.db.damage_keep)  # Assuming 'keep' is always 1
    #     else:
    #         # Unarmed attack default
    #         return self.roll_keep(attacker.db.traits.get('brawn', 1), 1)

    def reset_combat_states(self, character):
        character.ndb.combat_state = None
        character.ndb.full_defense = False
        character.ndb.riposte = False
        character.ndb.held_action = False
        character.ndb.stop_thrust = False

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

    def perform_feint(self, attacker, target_name, weapon):
        target = attacker.search(target_name)
        if not target or target not in self.db.participants:
            attacker.msg(f"Invalid target: {target_name}")
            return

        if not self.check_knack(attacker, 'Feint'):
            attacker.msg("You don't know how to perform a Feint.")
            return

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
            
            # Safely update move_dice
            current_move_dice = attacker.db.move_dice or 0
            attacker.db.move_dice = current_move_dice + move_dice_gain
            attacker.msg(f"You gained {move_dice_gain} Drama Dice. Total: {attacker.db.move_dice}")
        else:
            self.msg_all(f"{attacker.name}'s feint |400failed|n against {target.name}.")

        self.finish_turn()

    def perform_riposte(self, defender, attacker, weapon):
            if not self.check_knack(defender, 'Riposte'):
                defender.msg("You don't know how to perform a Riposte.")
                return False
            else:
                weapon_type = weapon.db.weapon_type if weapon else "Unarmed"
                defense_skill = defender.db.skills.get('Martial', {}).get('Fencing', {}).get('Riposte', 0)
                defense_roll = self.roll_keep(defender.db.traits['wits'] + defense_skill, defender.db.traits['wits'])
                attack_roll = self.calculate_passive_defense(attacker)

                if defense_roll > attack_roll + 10:
                    raw_damage = self.calculate_damage(defender, weapon) // 2  # Half damage
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

    def perform_lunge(self, attacker, target_name, weapon):
        target = attacker.search(target_name)
        if not target or target not in self.db.participants:
            attacker.msg(f"Invalid target: {target_name}")
            return

        if not self.check_knack(attacker, 'Lunge'):
            attacker.msg("You don't know how to perform a Lunge.")
            return

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

    def perform_stop_thrust(self, defender, attacker):
        self.msg_all(f"Debug: Performing Stop-Thrust for {defender.name} against {attacker.name}")
        defense_weapon = defender.db.wielded_weapon if hasattr(attacker.db, 'wielded_weapon') else None
        offense_weapon = attacker.db.wielded_weapon if hasattr(defender.db, 'wielded_weapon' ) else None
        offense_weapon_type = offense_weapon.db.weapon_type if offense_weapon else "Unarmed"
        self.msg_all(f"{offense_weapon.db.weapon_type}")
        defense_weapon_type = defense_weapon.db.weapon_type if defense_weapon else "Unarmed"
        self.msg_all(f"{defense_weapon.db.weapon_type}")
        offense_weapon_attack = offense_weapon.db.attack_skill if offense_weapon else 0
        self.msg_all(f"{offense_weapon_attack}")

        defender_knack = defender.character_sheet.get_knack_value("Stop-Thrust (Fencing)")
        self.msg_all(f"{defender_knack}")
        stop_thrust_skill = 0
        if defender_knack > stop_thrust_skill:
            stop_thrust_skill = defender_knack

        if stop_thrust_skill == 0:
            self.msg_all(f"{defender.name} doesn't know how to perform a Stop-Thrust with the current weapon type.")
            return False

        attack_skill = attacker.character_sheet.get_knack_value(f"{offense_weapon_attack}")
        self.msg_all(f"{attack_skill}")
        defense_roll = self.roll_keep((defender.db.traits['wits'] + stop_thrust_skill), defender.db.traits['wits'])
        attack_roll = self.roll_keep((attacker.db.traits['finesse'] + attack_skill), attacker.db.traits['finesse'])

    # ... rest of the method ...

        self.msg_all(f"Debug: Stop-Thrust roll: {defense_roll}, Attack roll: {attack_roll}")

        if defense_roll > attack_roll:
            damage = self.roll_keep(3, 2)  # 3k2 wounds for Stop-Thrust
            actual_damage = self.soak_damage(attacker, damage)
            
            if actual_damage > 0:
                self.resolve_wounds(attacker, actual_damage)
                self.msg_all(f"{defender.name}'s Stop-Thrust succeeds and deals {actual_damage} damage to {attacker.name}!")
            else:
                self.msg_all(f"{defender.name}'s Stop-Thrust succeeds but deals no damage to {attacker.name}.")
            
            if 'stopthrusted' in defender.db.special_effects:
                defender.db.special_effects.remove('stopthrusted')
            return True  # Stop-Thrust was successful
        else:
            self.msg_all(f"{defender.name}'s Stop-Thrust fails against {attacker.name}'s attack.")
            if 'stopthrusted' in defender.db.special_effects:
                defender.db.special_effects.remove('stopthrusted')
            return False  # Stop-Thrust failed





def get_combat(caller):
    if hasattr(caller.db, 'combat_id'):
        combat_id = caller.db.combat_id
        combat = ScriptDB.objects.filter(id=combat_id, db_key='CombatScript').first()
        if combat:
            return combat
        else:
            del caller.db.combat_id  # Remove the invalid combat_id
  
    return None
    
