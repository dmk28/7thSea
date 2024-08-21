""" weapon_type = weapon.db.weapon_type if weapon else "Unarmed"
    attack_skill = attacker.db.skills.get('Martial', {}).get('Attack', {}).get(f"({weapon_type})", 0)
    attack_roll = self.roll_keep(attacker.db.traits['finesse'] + attack_skill, attacker.db.traits['finesse'])

    if target.ndb.full_defense:
        defense_skill = target.db.skills.get('Martial', {}).get('Parry', {}).get(f"({weapon_type})", 0)
        defense_roll = self.roll_keep(target.db.traits['wits'], defense_skill)
        defense_roll = max(defense_roll, self.calculate_passive_defense(target))
    else:
        defense_roll = self.calculate_passive_defense(target)

    if attack_roll > defense_roll:
        raw_damage = self.calculate_damage(attacker, weapon)
        is_critical = attack_roll > defense_roll + 15

        if is_critical:
            raw_damage *= 2  # critical hit
            self.msg_all(f"{attacker.name} scored a critical hit on {target.name}!")

        actual_damage = self.soak_damage(target, raw_damage)

        if actual_damage > 0:
            character_defeated = self.resolve_wounds(target, actual_damage)
            self.msg_all(f"{attacker.name} hit {target.name} for {actual_damage} damage!", exclude=attacker)
            attacker.msg(f"You hit {target.name} for {actual_damage} damage!")
            target.msg(f"{attacker.name} hit you for {actual_damage} damage! (Soaked {raw_damage - actual_damage})")

            if character_defeated:
                self.msg_all("Combat has ended due to a character being defeated.")
                return True  # Indicate that the attack was successful and combat ended
        else:
            self.msg_all(f"{target.name} completely soaked the damage from {attacker.name}'s attack!", exclude=[attacker, target])
            attacker.msg(f"{target.name} completely soaked the damage from your attack!")
            target.msg(f"You completely soaked the damage ({raw_damage}) from {attacker.name}'s attack!")
    else:
        self.msg_all(f"{attacker.name}'s attack missed {target.name}.", exclude=attacker)
        attacker.msg(f"Your attack misses {target.name}.")

    return False  # Indicate that the attack was resolved but combat continues

        Forcefully end the combat, cleaning up all participants and stopping the script. """