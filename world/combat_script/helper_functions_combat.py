from typeclasses.characters import Character




def calculate_passive_defense(character):
    if not character.db.wielded_weapon:
        footwork = character.db.skills.get('Martial', {}).get('Footwork', {}).get('Basic', 0)
        return 5 + (footwork * 5)
    else:
        return 15  # Default value when wielding a weapon

def calculate_attack_roll(attacker, weapon_type):
    attack_skill = attacker.db.skills.get('Martial', {}).get('Attack', {}).get(f"({weapon_type})", 0)
    return self.roll_keep(attacker.db.traits['finesse'] + attack_skill, attacker.db.traits['finesse'])

def calculate_defense_roll(target, weapon_type):
    if target.ndb.full_defense:
        defense_skill = target.db.skills.get('Martial', {}).get('Parry', {}).get(f"({weapon_type})", 0)
        defense_roll = self.roll_keep(target.db.traits['wits'], defense_skill)
        return max(defense_roll, calculate_passive_defense(target))
    else:
        return calculate_passive_defense(target)


def resolve_successful_attack(attacker, target, weapon, attack_roll, defense_roll):
    raw_damage = self.calculate_damage(attacker, weapon)
    is_critical = attack_roll > defense_roll + 20

    if is_critical:
        raw_damage *= 2  # critical hit
        self.msg_all(f"{attacker.name} scored a critical hit on {target.name}!")

    actual_damage = soak_damage(target, raw_damage)

    if actual_damage > 0:
        character_defeated = resolve_wounds(target, actual_damage)
        msg_all(f"{attacker.name} hit {target.name} for |r{actual_damage}|n damage!", exclude=attacker)
        attacker.msg(f"You hit {target.name} for {actual_damage} damage!")
        target.msg(f"{attacker.name} hit you for {actual_damage} damage! (Soaked {raw_damage - actual_damage})")

        if character_defeated:
            msg_all("Combat has ended due to a character being defeated.")
            return True  # Indicate that the attack was successful and combat ended
    else:
        msg_all(f"{target.name} completely |gsoaked the damage|n from {attacker.name}'s attack!", exclude=[attacker, target])
        attacker.msg(f"{target.name} completely soaked the damage from your attack!")
        target.msg(f"You completely soaked the damage ({raw_damage}) from {attacker.name}'s attack!")

    return False  # Indicate that the attack was resolved but combat continues

def resolve_missed_attack(attacker, target):
    msg_all(f"{attacker.name}'s attack missed {target.name}.", exclude=attacker)
    attacker.msg(f"Your attack misses {target.name}.")
    return False