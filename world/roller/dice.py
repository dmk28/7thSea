# world/dice.py
from random import randint

def roll_keep(num_dice, keep):
    """
    Roll a number of dice and keep the highest.
    
    Args:
    num_dice (int): Number of dice to roll
    keep (int): Number of highest dice to keep
    
    Returns:
    int: Sum of the highest 'keep' dice
    """
    rolls = sorted([randint(1, 10) for _ in range(num_dice)], reverse=True)
    return sum(rolls[:keep])

def roll_keep_explode(num_dice, keep):
    """
    Roll a number of dice, keep the highest, and explode on 10s.
    
    Args:
    num_dice (int): Number of dice to roll
    keep (int): Number of highest dice to keep
    
    Returns:
    int: Sum of the highest 'keep' dice, with 10s exploding
    """
    rolls = []
    for _ in range(num_dice):
        roll = randint(1, 10)
        while roll == 10:
            rolls.append(roll)
            roll = randint(1, 10)
        rolls.append(roll)
    
    return sum(sorted(rolls, reverse=True)[:keep])