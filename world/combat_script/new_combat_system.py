from evennia import DefaultScript
from evennia import ScriptDB
from random import randint

class CombatScript(DefaultScript):
    def at_script_creation(self):
        self.key = "CombatScript"
        self.desc = "Handles combat system"
        self.persistent = True
        self.db.participants = []
        self.db.initiative_order = []
        self.db.current_actor = None
        self.db.round = 0

    def start_combat(self, *participants):
        self.db.participants = list(participants)
        for participant in self.db.participants:
            self.init_combat_stats(participant)
        self.roll_initiative()
        self.next_round()

    def init_combat_stats(self, character):
        character.ndb.combat = {
            'flesh_wounds': 0,
            'full_defense': False,
            'held_action': False,
            'special_effects': [],
            'has_gone': False,
        }

    def roll_initiative(self):
        initiative_rolls = []
        for char in self.db.participants:
            panache = char.character_sheet.panache
            base_roll = randint(1, 10) + (panache * 3)
            if "combat_reflexes" in char.character_sheet.advantages:
                base_roll += 5
                char.msg("Your Combat Reflexes give you a +5 bonus to initiative!")
            initiative_rolls.append((char, base_roll, panache))
        
        self.db.initiative_order = [char for char, _, _ in sorted(initiative_rolls, key=lambda x: (x[1], x[2]), reverse=True)]
        self.msg_all("Initiative has been rolled.")
        for char, roll, _ in initiative_rolls:
            char.msg(f"Your initiative roll: {roll}")

    def next_round(self):
        self.db.round += 1
        self.msg_all(f"Round {self.db.round} begins.")
        self.roll_initiative()
        self.process_next_turn()
        

    def process_next_turn(self):
    # Logic to determine and handle the current turn
        
       
        
        if not self.db.initiative_order:
            if any(char for char in self.db.participants if char.ndb.combat['held_action']):
                self.db.initiative_order = [char for char in self.db.participants if char.ndb.combat['held_action']]
                for char in self.db.initiative_order:
                    char.ndb.combat['held_action'] = False
                else:
                    # Prepare for the next turn
                    self.advance_to_next_turn()
                    self.db.current_actor = self.db.initiative_order.pop(0)
                    self.offer_action(self.db.current_actor)

    def offer_action(self, character):
        character.msg(f"It's your turn in round {self.db.round}. What do you want to do?")
        character.msg("Use these commands: 'attack <target>', 'defend', 'hold', or 'pass'")
        self.msg_all(f"Waiting for {character.name} to choose an action.")

    def handle_action(self, character, action, target=None):
        if action == "attack":
            if not target:
                character.msg("You must specify a target for attack.")
                return False
            return self.perform_attack(character, target)
        elif action == "defend":
            return self.set_full_defense(character)
        elif action == "hold":
            return self.hold_action(character)
        elif action == "pass":
            return self.pass_turn(character)
        else:
            character.msg(f"Invalid action: {action}")
            return False

    def perform_attack(self, attacker, target_name):
        target = attacker.search(target_name)
        if not target or target not in self.db.participants:
            attacker.msg(f"Invalid target: {target_name}")
            return False

        weapon = attacker.db.wielded_weapon
        weapon_type = weapon.db.weapon_type if weapon else "Unarmed"
        
        attack_roll = self.calculate_attack_roll(attacker, weapon_type)
        defense_roll = self.calculate_defense_roll(target, weapon_type)

        self.msg_all(f"Debug: Attack roll: {attack_roll}, Defense roll: {defense_roll}")

        if attack_roll > defense_roll:
            return self.resolve_successful_attack(attacker, target, weapon, attack_roll, defense_roll)
        else:
            return self.resolve_missed_attack(attacker, target)

    def calculate_attack_roll(self, attacker, weapon_type):
        finesse = attacker.character_sheet.finesse
        attack_skill = self.get_attack_skill(attacker, weapon_type)
        attack_roll = self.roll_keep(finesse + attack_skill, finesse)
        return attack_roll + self.apply_combat_effects(attacker, "attack")

    def calculate_defense_roll(self, defender, weapon_type):
        wits = defender.character_sheet.wits
        defense_skill = self.get_defense_skill(defender, weapon_type)
        defense_roll = self.roll_keep(wits + defense_skill, wits)
        return max(defense_roll, self.calculate_passive_defense(defender)) + self.apply_combat_effects(defender, "defense")

    def get_attack_skill(self, character, weapon_type):
        skills = character.character_sheet.get_skills()
        return skills.get('Martial', {}).get(weapon_type, {}).get(f'Attack ({weapon_type})', 0)

    def get_defense_skill(self, character, weapon_type):
        skills = character.character_sheet.get_skills()
        return skills.get('Martial', {}).get(weapon_type, {}).get(f'Parry ({weapon_type})', 0)

    def calculate_passive_defense(self, character):
        
        if not character.db.wielded_weapon:
            footwork = character.character_sheet.get_skill_value('Martial', 'Footwork', 'Basic')
            return 5 + (footwork * 5)
        else:
            weapon = character.db.wielded_weapon
            passive_defense = (character.character_sheet.get('Martial', {}).get(weapon, {}).get(f'Parry ({wewapon})', 0)) * 5
            return passive_defense

    def resolve_successful_attack(self, attacker, target, weapon, attack_roll, defense_roll):
        raw_damage = self.calculate_damage(attacker, weapon)
        is_critical = attack_roll > defense_roll + 15

        if is_critical:
            raw_damage *= 2
            self.msg_all(f"{attacker.name} scored a critical hit on {target.name}!")

        actual_damage = self.soak_damage(target, raw_damage)

        if actual_damage > 0:
            self.apply_wounds(target, actual_damage)
            self.msg_all(f"{attacker.name} hit {target.name} for {actual_damage} damage!")
        else:
            self.msg_all(f"{target.name} completely soaked the damage from {attacker.name}'s attack!")

        return True

    def resolve_missed_attack(self, attacker, target):
        self.msg_all(f"{attacker.name}'s attack missed {target.name}.")
        return True

    def calculate_damage(self, attacker, weapon):
        brawn = attacker.character_sheet.brawn
        weapon_damage = weapon.db.damage if weapon else 0
        weapon_keep = weapon.db.damage_keep if weapon else 1
        return self.roll_keep(brawn + weapon_damage, min(brawn + weapon_keep, brawn + weapon_damage))

    def soak_damage(self, character, damage):
        resolve = character.character_sheet.resolve
        armor = character.character_sheet.armor
        soak_roll = self.roll_keep(resolve + armor, resolve)
        return max(0, damage - soak_roll)

    def apply_wounds(self, character, damage):
        character.ndb.combat['flesh_wounds'] += damage
        resolve = character.character_sheet.resolve
        if character.ndb.combat['flesh_wounds'] >= resolve * 5:
            character.character_sheet.dramatic_wounds += 1
            character.ndb.combat['flesh_wounds'] -= resolve * 5
            self.msg_all(f"{character.name} has received a Dramatic Wound!")
        
        if character.character_sheet.dramatic_wounds >= resolve * 2:
            self.knock_out_character(character)

    def knock_out_character(self, character):
        self.msg_all(f"{character.name} has been knocked out!")
        self.remove_participant(character)

    def remove_participant(self, character):
        if character in self.db.participants:
            self.db.participants.remove(character)
        if character in self.db.initiative_order:
            self.db.initiative_order.remove(character)
        character.ndb.combat = None

    def set_full_defense(self, character):
        character.ndb.combat['full_defense'] = True
        self.msg_all(f"{character.name} takes a defensive stance.")
        return True

    def hold_action(self, character):
        character.ndb.combat['held_action'] = True
        self.msg_all(f"{character.name} holds their action.")
        return True

    def pass_turn(self, character):
        self.msg_all(f"{character.name} passes their turn.")
        return True

    def roll_keep(self, num_dice, keep):
        rolls = sorted([randint(1, 10) for _ in range(num_dice)], reverse=True)
        kept_rolls = rolls[:keep]
        return sum(kept_rolls)

    def apply_combat_effects(self, character, action_type):
        bonus = 0
        effects = character.ndb.combat['special_effects']
        
        if action_type == "attack" and "left-handed" in effects:
            bonus += 4
        if action_type == "soak" and "toughness" in effects:
            bonus += 1
        # Add more effects as needed
        
        return bonus

    def msg_all(self, message, exclude=None):
        for char in self.db.participants:
            if char != exclude:
                char.msg(f"|r[Combat]|n {message}")

def get_combat(caller):
    if hasattr(caller.ndb, 'combat_id'):
        combat_id = caller.ndb.combat_id
        combat = ScriptDB.objects.filter(id=combat_id, db_typeclass_path__contains='CombatScript').first()
        if combat:
            return combat
        else:
            del caller.ndb.combat_id
    return None