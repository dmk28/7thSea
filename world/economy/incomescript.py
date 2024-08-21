# world/economy.py
from evennia import DefaultScript
from evennia.utils import gametime
from random import randint
from world.roller import roll_keep


class WeeklyIncomeScript(DefaultScript):
    def at_script_creation(self):
        self.key = "weekly_income_script"
        self.desc = "Runs weekly income rolls for characters"
        self.interval = 60 * 60 * 24 * 7  # 1 week in seconds
        self.persistent = True
        

    def at_repeat(self):
        for character in self.db.characters:
            income = self.roll_income(character)
            if income > 0:
                character.add_money("guilders", income)
                character.msg(f"You've earned {income} guilders this week from your profession.")
            else:
                character.msg("You didn't earn any income this week.")

    # def roll_keep(self, num_dice, keep):
    #     """Roll a number of dice and keep the highest."""
    #     rolls = sorted([randint(1, 10) for _ in range(num_dice)], reverse=True)
    #     return sum(rolls[:keep])

    def roll_income(self, character):
        professional_skills = character.db.skills.get('Professional', {})
        if not professional_skills:
            return 0  # No professional skills, no income

        # Find the highest primary knack
        highest_knack = max(professional_skills.items(), key=lambda x: max(x[1].values() if x[1] else [0]))
        skill_name, knacks = highest_knack
        highest_knack_value = max(knacks.values())

        # Get the character's Wits trait
        wits = character.db.traits.get('wits', 1)

        # Perform two rolls
        roll1 = roll_keep(wits + highest_knack_value, wits)
        roll2 = roll_keep(wits + highest_knack_value, wits)

        # Calculate income based on rolls
        income1 = max(0, roll1 - 15)
        income2 = max(0, roll2 - 15)

        total_income = income1 + income2

        character.msg(f"Using {skill_name} (Knack level: {highest_knack_value}):")
        character.msg(f"First roll: {roll1} (Income: {income1})")
        character.msg(f"Second roll: {roll2} (Income: {income2})")

        return total_income