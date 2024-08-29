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