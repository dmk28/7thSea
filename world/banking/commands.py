from evennia import Command
from world.banking.models import Bank, BankAccount
from evennia.commands.default.muxcommand import MuxCommand


class CmdBank(MuxCommand):
    """
    Perform banking operations.

    Usage:
      bank/open
      bank/deposit <amount> <currency>
      bank/withdraw <amount> <currency>
      bank/balance
      bank/transfer <amount> <currency> to <account_number>

    Switches:
      open - Open a new bank account
      deposit - Deposit money into your account
      withdraw - Withdraw money from your account
      balance - Check your account balance
      transfer - Transfer money to another account

    Examples:
      bank/open
      bank/deposit 100 guilders
      bank/withdraw 50 doubloons
      bank/balance
      bank/transfer 75 guilders to 1234-5678
    """

    key = "bank"
    aliases = ["banking"]
    switches = ["open", "deposit", "withdraw", "balance", "transfer"]
    locks = "cmd:all()"

    def get_bank(self):
        if hasattr(self.caller.location, 'get_bank'):
            return self.caller.location.get_bank()
        return None

    def func(self):
        if not self.switches:
            self.caller.msg("You must use a switch with the bank command. See 'help bank' for usage.")
            return

        bank = self.get_bank()
        if not bank:
            self.caller.msg("You need to be in a bank to perform banking operations.")
            return

        switch = self.switches[0]

        if switch == "open":
            self.open_account(bank)
        elif switch in ["deposit", "withdraw"]:
            self.handle_transaction(bank, switch)
        elif switch == "balance":
            self.check_balance(bank)
        elif switch == "transfer":
            self.transfer_money(bank)
        else:
            self.caller.msg("Invalid bank command. See 'help bank' for usage.")

    def open_account(self, bank):
        account, created = BankAccount.objects.get_or_create(
            bank=bank,
            account_holder=self.caller,
            defaults={'account_number': f"{bank.id}-{self.caller.id}"}
        )
        
        if created:
            self.caller.msg(f"Account opened at {bank.name}. Your account number is {account.account_number}.")
        else:
            self.caller.msg(f"You already have an account at {bank.name}.")

    def handle_transaction(self, bank, transaction_type):
        if not self.args or len(self.args.split()) != 2:
            self.caller.msg(f"Usage: bank/{transaction_type} <amount> <currency>")
            return
        
        amount, currency = self.args.split()
        try:
            amount = int(amount)
        except ValueError:
            self.caller.msg("Amount must be a number.")
            return
        
        if currency not in ['guilders', 'doubloons']:
            self.caller.msg("Currency must be either 'guilders' or 'doubloons'.")
            return
        
        try:
            account = BankAccount.objects.get(bank=bank, account_holder=self.caller)
        except BankAccount.DoesNotExist:
            self.caller.msg(f"You don't have an account at this bank.")
            return
        
        if transaction_type == "deposit":
            if self.caller.character_sheet.money.get(currency, 0) < amount:
                self.caller.msg(f"You don't have enough {currency}.")
                return
            self.caller.character_sheet.money[currency] -= amount
            setattr(account, f"{currency}_balance", getattr(account, f"{currency}_balance") + amount)
            message = f"Deposited {amount} {currency} into your account at {bank.name}."
        else:  # withdraw
            if getattr(account, f"{currency}_balance") < amount:
                self.caller.msg(f"You don't have enough {currency} in your account.")
                return
            setattr(account, f"{currency}_balance", getattr(account, f"{currency}_balance") - amount)
            self.caller.character_sheet.money[currency] = self.caller.character_sheet.money.get(currency, 0) + amount
            message = f"Withdrew {amount} {currency} from your account at {bank.name}."
        
        account.save()
        self.caller.character_sheet.save(update_fields=['money'])
        self.caller.msg(message)

    def check_balance(self, bank):
        try:
            account = BankAccount.objects.get(bank=bank, account_holder=self.caller)
        except BankAccount.DoesNotExist:
            self.caller.msg(f"You don't have an account at this bank.")
            return
        
        self.caller.msg(f"Your balance at {bank.name}:")
        self.caller.msg(f"Guilders: {account.guilders_balance}")
        self.caller.msg(f"Doubloons: {account.doubloons_balance}")

    def transfer_money(self, bank):
        if not self.args or len(self.args.split()) != 4 or "to" not in self.args:
            self.caller.msg("Usage: bank/transfer <amount> <currency> to <account_number>")
            return
        
        amount, currency, _, to_account = self.args.split()
        
        try:
            amount = int(amount)
        except ValueError:
            self.caller.msg("Amount must be a number.")
            return
        
        if currency not in ['guilders', 'doubloons']:
            self.caller.msg("Currency must be either 'guilders' or 'doubloons'.")
            return
        
        try:
            from_account = BankAccount.objects.get(bank=bank, account_holder=self.caller)
        except BankAccount.DoesNotExist:
            self.caller.msg(f"You don't have an account at this bank.")
            return
        
        try:
            to_account = BankAccount.objects.get(bank=bank, account_number=to_account)
        except BankAccount.DoesNotExist:
            self.caller.msg(f"Account {to_account} not found at this bank.")
            return
        
        if getattr(from_account, f"{currency}_balance") < amount:
            self.caller.msg(f"You don't have enough {currency} in your account.")
            return
        
        # Perform the transfer
        setattr(from_account, f"{currency}_balance", getattr(from_account, f"{currency}_balance") - amount)
        setattr(to_account, f"{currency}_balance", getattr(to_account, f"{currency}_balance") + amount)
        from_account.save()
        to_account.save()
        
        self.caller.msg(f"Transferred {amount} {currency} to account {to_account.account_number}.")