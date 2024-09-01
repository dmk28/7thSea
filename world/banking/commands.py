from evennia import Command
from evennia.utils.search import search_object
from world.banking.models import Bank, BankAccount

class CmdOpenAccount(Command):
    """
    Open a new bank account.

    Usage:
      openaccount <bank>
    """
    key = "openaccount"
    locks = "cmd:all()"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: openaccount <bank>")
            return
        
        banks = Bank.objects.filter(name__iexact=self.args)
        if not banks:
            self.caller.msg(f"No bank named '{self.args}' found.")
            return
        
        bank = banks[0]
        account, created = BankAccount.objects.get_or_create(
            bank=bank,
            account_holder=self.caller,
            defaults={'account_number': f"{bank.id}-{self.caller.id}"}
        )
        
        if created:
            self.caller.msg(f"Account opened at {bank.name}. Your account number is {account.account_number}.")
        else:
            self.caller.msg(f"You already have an account at {bank.name}.")

class CmdDeposit(Command):
    """
    Deposit money into your bank account.

    Usage:
      deposit <amount> <currency> <bank>
    """
    key = "deposit"
    locks = "cmd:all()"

    def func(self):
        if not self.args or len(self.args.split()) != 3:
            self.caller.msg("Usage: deposit <amount> <currency> <bank>")
            return
        
        amount, currency, bank_name = self.args.split()
        try:
            amount = int(amount)
        except ValueError:
            self.caller.msg("Amount must be a number.")
            return
        
        if currency not in ['guilders', 'doubloons']:
            self.caller.msg("Currency must be either 'guilders' or 'doubloons'.")
            return
        
        banks = Bank.objects.filter(name__iexact=bank_name)
        if not banks:
            self.caller.msg(f"No bank named '{bank_name}' found.")
            return
        
        bank = banks[0]
        try:
            account = BankAccount.objects.get(bank=bank, account_holder=self.caller)
        except BankAccount.DoesNotExist:
            self.caller.msg(f"You don't have an account at {bank.name}.")
            return
        
        if self.caller.character_sheet.money.get(currency, 0) < amount:
            self.caller.msg(f"You don't have enough {currency}.")
            return
        
        self.caller.character_sheet.money[currency] -= amount
        setattr(account, f"{currency}_balance", getattr(account, f"{currency}_balance") + amount)
        account.save()
        self.caller.character_sheet.save(update_fields=['money'])
        
        self.caller.msg(f"Deposited {amount} {currency} into your account at {bank.name}.")

class CmdWithdraw(Command):
    """
    Withdraw money from your bank account.

    Usage:
      withdraw <amount> <currency> <bank>
    """
    key = "withdraw"
    locks = "cmd:all()"

    def func(self):
        if not self.args or len(self.args.split()) != 3:
            self.caller.msg("Usage: withdraw <amount> <currency> <bank>")
            return
        
        amount, currency, bank_name = self.args.split()
        try:
            amount = int(amount)
        except ValueError:
            self.caller.msg("Amount must be a number.")
            return
        
        if currency not in ['guilders', 'doubloons']:
            self.caller.msg("Currency must be either 'guilders' or 'doubloons'.")
            return
        
        banks = Bank.objects.filter(name__iexact=bank_name)
        if not banks:
            self.caller.msg(f"No bank named '{bank_name}' found.")
            return
        
        bank = banks[0]
        try:
            account = BankAccount.objects.get(bank=bank, account_holder=self.caller)
        except BankAccount.DoesNotExist:
            self.caller.msg(f"You don't have an account at {bank.name}.")
            return
        
        if getattr(account, f"{currency}_balance") < amount:
            self.caller.msg(f"You don't have enough {currency} in your account.")
            return
        
        setattr(account, f"{currency}_balance", getattr(account, f"{currency}_balance") - amount)
        account.save()
        self.caller.character_sheet.money[currency] = self.caller.character_sheet.money.get(currency, 0) + amount
        self.caller.character_sheet.save(update_fields=['money'])
        
        self.caller.msg(f"Withdrew {amount} {currency} from your account at {bank.name}.")

# CmdBalance and CmdTransfer can remain largely the same, just update to use Bank.objects.filter() instead of search_object()