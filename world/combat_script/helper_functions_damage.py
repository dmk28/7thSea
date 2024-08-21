from typeclasses.characters import Character


def soak_damage(character, damage):
    try:
        soak_dice, soak_keep = calculate_soak_parameters(character)
        soak_bonus = apply_combat_effects(character, "soak")
        soak_roll = roll_keep(soak_dice, soak_keep)
        total_soak = calculate_total_soak(soak_roll, soak_bonus)

        msg_all(f"Debug: Soak dice: {soak_dice}, Soak keep: {soak_keep}")
        msg_all(f"Debug: Soak bonus from effects: {soak_bonus}")
        msg_all(f"Debug: Soak roll result: {soak_roll}")
        msg_all(f"Debug: Total soak (roll + bonus): {total_soak}")

        damage_taken = apply_soak_rules(damage, total_soak)
        self.msg_all(f"Debug: Final damage taken: {damage_taken}")

        return damage_taken
    except Exception as e:
        self.msg_all(f"Error in soak_damage: {str(e)}")
        self.msg_all(f"Debug: {self.get_soak_debug_info(character)}")
        return damage  # If an error occurs, return full damage




def calculate_soak_parameters(character):
    total_armor = getattr(character.db, 'total_armor', 0)
    if not character.db.equipped_armor:
        total_armor = 0
    resolve = character.db.traits.get('resolve', 1)
    soak_dice = resolve + total_armor
    armor_soak_keep = getattr(character.db, 'armor_soak_keep', 0)
    soak_keep = max(resolve, armor_soak_keep) if character.db.armor_soak_keep is not None else max(resolve, 0)
    return soak_dice, soak_keep

def calculate_total_soak(soak_roll, soak_bonus):
    return int(soak_roll + (soak_bonus or 0))

def apply_soak_rules(damage, total_soak):
    if total_soak >= 35:
        return max(0, damage - total_soak)
    elif total_soak >= 15:
        return max(0, damage - (total_soak // 2))
    else:
        return damage

def get_soak_debug_info(character):
    return (f"resolve={character.db.traits.get('resolve', 1)}, "
            f"total_armor={getattr(character.db, 'total_armor', 0)}, "
            f"armor_soak_keep={getattr(character.db, 'armor_soak_keep', 0)}")