from evennia import DefaultObject
from typeclasses.objects import Object, Sword, Weapon



class Panzerhand(Weapon):
    def at_object_creation(self):
        super().at_object_creation()
        super.db.weapon_type = "Panzerhand"
        self.db.damage = 1
        self.db.damage_keep = 2
        self.db.armor += 1
        self.db.soak_keep += 1
class AldanaBlade(Sword):

    def at_object_creation(self):
        super().at_object_creation()
        self.db.weapon_type = "Fencing"
        self.db.damage = 3
        self.db.damage_keep = 3
        self.db.attack_bonus = 1
        self.db.cost = 5000
        
class GallegosBlade(Sword):
    def at_object_creation(self):
        super().at_object_creation()
        self.db.weapon_type = "Fencing"
        self.db.attack_bonus = 2
        self.db.cost = 6000


class SoldanoBlade(Sword):
    def at_object_creation(self):
        super().at_object_creation()
        self.db.weapon_type = "Fencing"
        self.db.attack_bonus = 2
        self.db.parry_bonus = 2
        self.db.maneuver_bonus = 2
        self.db.damage = 4
        self.db.cost = 10000


class TorresBlade(Sword):
    def at_object_creation(self):
        super().at_object_creation()
        self.db.weapon_type = "Fencing"
        self.db.damage = 5
        self.db.cost = 5500


class ZepedaBlade(Sword):
    def at_object_creation(self):
        super().at_object_creation()
        self.db.weapon_type = "Fencing"
        self.db.damage = 3
        self.db.attack_bonus = 1
        self.db.cost = 6750

class SorcerousWeapon(Weapon):
    def at_object_creation(self):
        super().at_object_creation()
        self.db.sorcerous_bonus = {}  # Dictionary to store sorcery-related bonuses

    def get_sorcerous_bonus(self, wielder, knack):
        """
        Check if the wielder is a sorcerer and has the specified knack.
        If so, return the bonus for that knack.
        """
        if hasattr(wielder.db, 'is_sorcerer') and wielder.db.is_sorcerer:
            if knack in wielder.db.sorcery_knacks:
                return self.db.sorcerous_bonus.get(knack, 0)
        return 0

    def at_equip(self, wielder):
        """Called when the weapon is equipped."""
        if self.db.sorcerous_bonus:
            for knack, bonus in self.db.sorcerous_bonus.items():
                current_value = wielder.db.sorcery_knacks.get(knack, 0)
                wielder.db.sorcery_knacks[knack] = current_value + self.get_sorcerous_bonus(wielder, knack)

    def at_remove(self, wielder):
        """Called when the weapon is unequipped."""
        if self.db.sorcerous_bonus:
            for knack, bonus in self.db.sorcerous_bonus.items():
                current_value = wielder.db.sorcery_knacks.get(knack, 0)
                wielder.db.sorcery_knacks[knack] = max(0, current_value - self.get_sorcerous_bonus(wielder, knack))


class FlamingSword(SorcerousWeapon):
    def at_object_creation(self):
        super().at_object_creation()
        self.db.weapon_type = "Fencing"
        self.db.damage = 3
        self.db.attack_skill = "Attack (Fencing)"
        self.db.parry_skill = "Parry (Fencing)"
        self.db.cost = 50000000
        self.db.sorcerous_bonus = {"Flameblade": 1}  # +1 to Flaming Blade knack


class TwistedBlade(SorcerousWeapon):
    def at_object_creation(self):
        super().at_object_creation()
        self.db.weapon_type = "Fencing"
        self.db.damage = 4
        self.db.damage_keep = 5
        self.db.defense_base = 2
        self.db.attack_skill = "Attack (Fencing)"
        self.db.parry_skill = "Parry (Fencing)"
        self.db.cost = 500000000
        self.db.hero_points_cost = 6  # Set the HP to 6
        self.db.damage_bonus = 5

    def calculate_damage(self, wielder):
        """
        Calculate damage as 3 + Finesse, keep 5
        """
        finesse = wielder.db.traits.get('finesse', 0)
        damage_dice = self.db.damage + finesse
        return {'roll': damage_dice, 'keep': self.db.damage_keep}

    def calculate_defense(self, wielder):
        """
        Calculate defense as 2 + Finesse
        """
        finesse = wielder.db.traits.get('finesse', 0)
        return self.db.defense_base + finesse

    def at_equip(self, wielder):
        super().at_equip(wielder)
        wielder.msg(f"You feel the twisted blade's power. Damage: {self.calculate_damage(wielder)}, Defense: {self.calculate_defense(wielder)}")

    def at_remove(self, wielder):
        super().at_remove(wielder)
        wielder.msg("You no longer feel the twisted blade's power.")