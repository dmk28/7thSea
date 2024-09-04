from evennia import DefaultScript
from evennia.utils.utils import inherits_from
from evennia import ScriptDB
from random import randint
from world.character_sheet.models import CharacterSheet
from commands.mycmdset import ReparteeCmdSet

class SocialCombat(DefaultScript):
    """
    This script handles the repartee (social combat) system.
    """
    
    def at_script_creation(self):
        self.key = "SocialCombatScript"
        self.desc = "Handles repartee system"
        self.persistent = True
        self.db.participants = []
        self.db.initiative_order = []
        self.db.current_actor = None
        self.db.action_state = None
        self.db.round = 0

    def at_start(self):
        self.msg_all(f"Debug: Repartee script {self.id} started.")

    def at_stop(self):
        self.msg_all(f"Debug: Repartee script {self.id} stopped.")

    def start_repartee(self):
        for participant in self.db.participants:
            self.initialize_repartee_stats(participant)
            participant.db.repartee_id = self.id
            self.add_repartee_cmdset(participant)
            self.check_repartee_advantages(participant)
            participant.msg(f"Debug: Repartee started. Script info: {self.debug_info()}")
        
        self.roll_initiative()
        self.next_round()

    def initialize_repartee_stats(self, participant):
        participant.ndb.reputation = participant.character_sheet.reputation
        participant.ndb.social_health = participant.ndb.reputation * 10
        participant.ndb.attack_trait = [participant.character_sheet.panache, participant.character_sheet.resolve, participant.character_sheet.wits]
        participant.ndb.defense_trait = [participant.character_sheet.wits, participant.character_sheet.resolve, participant.character_sheet.panache]
        participant.ndb.special_effects = []

    def add_repartee_cmdset(self, character):
        from world.combat_script.repartee_cmdset import ReparteeCmdSet
        character.cmdset.add(ReparteeCmdSet(), persistent=False)

    def check_repartee_advantages(self, character):
        advantages = character.get_advantages()
        for advantage in advantages:
            adv_name = advantage.get('name', '')
            if adv_name == 'Dangerous Beauty':
                character.ndb.special_effects.append("sex_appeal")
            elif adv_name == "Appearance (Above Average)":
                character.ndb.special_effects.append("attractive")
            elif adv_name == "Appearance (Stunning)":
                character.ndb.special_effects.append("beautiful")

    def roll_initiative(self):
        initiative_rolls = []
        for char in self.db.participants:
            panache = char.db.traits['panache']
            roll = randint(1, 10) + panache
            initiative_rolls.append((char, roll))
        
        initiative_rolls.sort(key=lambda x: x[1], reverse=True)
        self.db.initiative_order = [char for char, _ in initiative_rolls]
        self.msg_all("Repartee initiative has been rolled.")

    def next_round(self):
        self.db.round += 1
        self.msg_all(f"Round {self.db.round} of repartee begins.")
        self.db.initiative_order = self.db.participants.copy()  # Reset initiative order
        self.process_next_character()

    def process_next_character(self):
        if not self.db.initiative_order:
            if len(self.db.participants) < 2:
                self.end_repartee()
            else:
                self.next_round()
            return

        self.db.current_actor = self.db.initiative_order.pop(0)
        if self.db.current_actor not in self.db.participants:
            self.process_next_character()  # Skip to the next character
        else:
            self.offer_action(self.db.current_actor)

    def offer_action(self, character):
        self.db.action_state = "choosing_action"
        character.msg(f"It's your turn in the repartee. What do you want to do?")
        character.msg("Use these commands: 'taunt <target>', 'charm <target>', 'intimidate <target>', 'gossip <target>', 'ridicule <target>', 'blackmail <target>', or 'pass'")
        self.msg_all(f"Waiting for {character.name} to choose an action.")

    def handle_action_input(self, character, choice):
        try:
            if self.db.current_actor != character:
                character.msg("It's not your turn to act.")
                return

            parts = choice.split(None, 1)
            action = parts[0].lower()
            target = parts[1] if len(parts) > 1 else None

            valid_actions = ["taunt", "charm", "intimidate", "gossip", "ridicule", "blackmail", "pass"]
            
            if action not in valid_actions:
                character.msg("Invalid action. Use 'taunt', 'charm', 'intimidate', 'gossip', 'ridicule', 'blackmail', or 'pass'.")
                return

            if action == "pass":
                self.pass_turn(character)
            elif not target:
                character.msg(f"You must specify a target for {action}.")
            else:
                self.perform_social_action(character, action, target)

        except Exception as e:
            self.msg_all(f"An error occurred: {str(e)}")
            self.force_end_repartee()

    def force_end_repartee(self):
        self.msg_all("The repartee has been forcibly ended.")
        for char in self.db.participants:
            if hasattr(char.db, 'repartee_id'):
                del char.db.repartee_id
            self.remove_repartee_cmdset(char)
            
            # Clear any repartee-specific attributes
            for attr in ['reputation', 'social_health', 'attack_trait', 'defense_trait', 'special_effects']:
                if hasattr(char.ndb, attr):
                    delattr(char.ndb, attr)

        self.stop()

        
    def perform_social_action(self, attacker, action, target_name):

        try:
            target = attacker.search(target_name)
            if not target or target not in self.db.participants:
                attacker.msg(f"Invalid target: {target_name}")
                return

            if action in ["taunt", "charm", "intimidate"]:
                self.perform_basic_action(attacker, target, action)
            elif action in ["gossip", "ridicule", "blackmail"]:
                self.perform_advanced_action(attacker, target, action)
        except Exception as e:
            self.msg_all(f"An error occurred during social action: {str(e)}")
            self.force_end_repartee()

    def perform_basic_action(self, attacker, target, action):
        action_index = {"taunt": 0, "charm": 2, "intimidate": 1}
        index = action_index[action]
        
        attack_trait = attacker.ndb.attack_trait[index]
        defense_trait = target.ndb.defense_trait[index]
        
        attack_roll = self.roll_keep(attack_trait, attack_trait)
        defense_difficulty = defense_trait * 5

        if attack_roll > defense_difficulty:
            damage = attack_roll - defense_difficulty
            self.apply_damage(target, damage)
            self.msg_all(f"{attacker.name}'s {action} against {target.name} succeeds, dealing {damage} social damage!")
        else:
            self.msg_all(f"{attacker.name}'s {action} against {target.name} fails.")

        self.finish_turn()

    def perform_advanced_action(self, attacker, target, action):
        if action == "gossip":
            attack_roll = self.roll_keep(attacker.db.traits['wits'] + attacker.db.skills.get('Gossip', 0), attacker.db.traits['wits'])
            defense_difficulty = target.db.traits['wits'] * 10
        elif action == "ridicule":
            attack_roll = self.roll_keep(attacker.db.traits['wits'] + attacker.db.skills.get('Oratory', 0), attacker.db.traits['wits'])
            defense_difficulty = target.db.traits['resolve'] * 10
        elif action == "blackmail":
            attack_roll = self.roll_keep(attacker.db.traits['wits'] + attacker.db.skills.get('Interrogation', 0), attacker.db.traits['wits'])
            defense_difficulty = max(target.db.traits['wits'], target.db.traits['resolve']) * 10

        if attack_roll > defense_difficulty:
            damage = (attack_roll - defense_difficulty) * 2
            self.apply_damage(target, damage)
            self.msg_all(f"{attacker.name}'s {action} against {target.name} succeeds, dealing {damage} social damage!")
            
            if action == "gossip":
                attacker.ndb.gossip_bonus = 5
                attacker.msg("You gain a +5 bonus to your next social roll.")
        else:
            self.msg_all(f"{attacker.name}'s {action} against {target.name} fails.")

        self.finish_turn()

    def apply_damage(self, target, damage):
        target.ndb.social_health -= damage
        if target.ndb.social_health <= 0:
            reputation_loss = min(damage // 10, target.ndb.reputation + 5)
            target.ndb.reputation = max(target.ndb.reputation - reputation_loss, -5)
            self.remove_participant(target)
            self.msg_all(f"{target.name} has been socially defeated and loses {reputation_loss} Reputation!")

    def pass_turn(self, character):
        self.msg_all(f"{character.name} passes their turn in the repartee.")
        self.finish_turn()

    def finish_turn(self):
        self.db.action_state = None
        self.db.current_actor = None
        self.process_next_character()

    def roll_keep(self, num_dice, keep):
        rolls = [randint(1, 10) for _ in range(num_dice)]
        return sum(sorted(rolls, reverse=True)[:keep])

    def msg_all(self, message, exclude=None):
        for char in self.db.participants:
            if char != exclude:
                char.msg(message)

    def remove_participant(self, character):
        if character in self.db.participants:
            self.db.participants.remove(character)
        if hasattr(character.ndb, 'repartee_id'):
            del character.ndb.repartee_id
        character.msg("You have been removed from the repartee.")
        
        if len(self.db.participants) < 2:
            self.end_repartee()
    def debug_info(self):
     return f"SocialCombat Script ID: {self.id}, Key: {self.key}, DB fields: {self.db.all()}"

    def end_repartee(self):
        self.msg_all("The repartee has ended.")
        for char in self.db.participants:
            if hasattr(char.db, 'repartee_id'):
                del char.db.repartee_id
            self.remove_repartee_cmdset(char)
            
            # Clear any repartee-specific attributes
            for attr in ['reputation', 'social_health', 'attack_trait', 'defense_trait', 'special_effects']:
                if hasattr(char.ndb, attr):
                    delattr(char.ndb, attr)

        self.stop()

    def remove_repartee_cmdset(self, character):
        character.cmdset.delete(ReparteeCmdSet)

# Add other necessary methods