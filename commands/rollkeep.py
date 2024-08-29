from evennia import Command
from random import randint

from evennia import Command
from random import randint
from world.character_sheet.models import CharacterSheet, KnackValue

class CmdRollKeep(Command):
    """
    Roll and keep command for 7th Sea.
    Usage:
    roll <trait>+<knack>
    Rolls (trait + knack) d10s and keeps the highest trait dice.
    Exploding dice on 10.

    For flat trait-only rolls, use:
    roll <trait>
    
    For rolls with a target number, use:
    roll <trait>+<knack> vs=30
    
    For flat number rolls, you can use roll/number.
    Example: roll/number 4k3
    """
    key = "roll"
    aliases = ["rk", "rollkeep", "@rollkeep", "+rollkeep"]
    locks = "cmd:all()"
    help_category = 'Dice'

    def func(self):
        caller = self.caller
        args = self.args.strip().lower()
        room = caller.location

        try:
            sheet = CharacterSheet.objects.get(db_object=caller)
        except CharacterSheet.DoesNotExist:
            caller.msg("You don't have a character sheet. Please complete character creation first.")
            return

        if "+" not in args:
            # Trait-only roll
            trait = args.strip()
            if not hasattr(sheet, trait):
                caller.msg(f"Invalid trait. Valid traits are: brawn, finesse, wits, resolve, panache")
                return

            trait_value = getattr(sheet, trait)
            num_dice = trait_value
            num_keep = trait_value

            rolls = self.roll_dice(num_dice)
            kept_rolls = sorted(rolls, reverse=True)[:num_keep]
            total = sum(kept_rolls)

            self.broadcast(f"{caller.name} rolls {trait.capitalize()} only: {num_dice}k{num_keep}")
            caller.msg(f"{caller.name} rolls {trait.capitalize()} only: {num_dice}k{num_keep}")
            caller.msg(f"Total: {total}")
            self.broadcast(f"Total: {total}")

            # Check for raises
            raises = total // 5
            if raises > 0:
                self.broadcast(f"Raises: {raises}")
        else:
            # Handle possible "vs" option for target number
            if "vs=" in args:
                args, tn_str = args.split("vs=")
                target_number = max(15, int(tn_str.strip()))
            else:
                target_number = None

            # Trait + Knack roll
            parts = args.split('+', 1)
            if len(parts) != 2:
                caller.msg("Usage: roll <trait>+<knack>")
                return
            trait, knack_input = parts[0].strip(), parts[1].strip()

            if not hasattr(sheet, trait):
                caller.msg(f"Invalid trait. Valid traits are: brawn, finesse, wits, resolve, panache")
                return

            # Search for the knack
            knack_value = KnackValue.objects.filter(
                character_sheet=sheet,
                knack__name__iexact=knack_input
            ).first()

            if not knack_value:
                caller.msg(f"Invalid knack. Please check your input.")
                return

            trait_value = getattr(sheet, trait)
            skill_value = knack_value.value
            num_dice = trait_value + skill_value
            num_keep = trait_value

            rolls = self.roll_dice(num_dice)
            kept_rolls = sorted(rolls, reverse=True)[:num_keep]
            total = sum(kept_rolls)

            self.broadcast(f"{caller.name} rolls {trait.capitalize()} + {knack_input}: {num_dice}k{num_keep}")
            caller.msg(f"{caller.name} rolls {trait.capitalize()} + {knack_input}: {num_dice}k{num_keep}")
            caller.msg(f"Rolls: {rolls}")
            caller.msg(f"Kept Rolls: {kept_rolls}")
            caller.msg(f"Total: {total}")
            self.broadcast(f"Total: {total}")

            # Check for raises
            raises = total // 5
            if raises > 0:
                self.broadcast(f"Raises: {raises}")

            # Check against Target Number (TN) if provided
            if target_number:
                success = total >= target_number
                great_success = total >= (target_number + 10)
                result = "|gGreat Success!|n" if great_success else "|GSuccess!|n" if success else "|rFailure|n"
                caller.msg(f"Result: {result}")
                self.broadcast(f"Result: {result}")
                caller.msg(f"Target Number was: |w{target_number}|n")

    def roll_dice(self, num_dice):
        rolls = []
        while num_dice > 0:
            roll = randint(1, 10)
            rolls.append(roll)
            num_dice -= 1
            if roll == 10:
                num_dice += 1  # Exploding dice
        return rolls

    def broadcast(self, message):
        room = self.caller.location
        room.msg_contents(message, exclude=[self.caller])


class CmdRollNumberKeep(Command):
            """
            Roll and keep command for 7th Sea with specific numbers.
            Usage:
            rnk <number>k<number>
            
            Rolls <number> dice and keeps <number> dice.
            Exploding dice on 10.
            """
            key = "roll/number"
            aliases = ["rnk", "@rnk", "+rnk"]
            locks = "cmd:all()"
            help_category = 'Dice'

            def func(self):
                caller = self.caller
                args = self.args.strip().lower()
                
                try:
                    num_dice, num_keep = map(int, args.split('k'))
                except ValueError:
                    caller.msg("Usage: rnk <number>k<number>")
                    return

                rolls = self.roll_dice(num_dice)
                kept_rolls = sorted(rolls, reverse=True)[:num_keep]
                total = sum(kept_rolls)

                caller.msg(f"Rolling {num_dice}k{num_keep}")
                caller.msg(f"Rolls: {rolls}")
                caller.msg(f"Kept Rolls: {kept_rolls}")
                caller.msg(f"Total: {total}")

                # Check for raises
                raises = total // 5
                if raises > 0:
                    caller.msg(f"Raises: {raises}")

            def roll_dice(self, num_dice):
                rolls = []
                while num_dice > 0:
                    roll = randint(1, 10)
                    rolls.append(roll)
                    num_dice -= 1
                    if roll == 10:
                        num_dice += 1  # Exploding dice
                return rolls