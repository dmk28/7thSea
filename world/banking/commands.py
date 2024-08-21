from evennia import Command
from evennia.utils.search import search_object
from world.banking.models import Bank, BankAccount, HoldingAccount, GuildAccount

class CmdOpenAccount(Command):
    """
    Open a new bank account.

    Usage:
      openaccount <bank>

    Opens a new account at the specified bank.
    """
    key = "openaccount"
    locks = "cmd:all()"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: openaccount <bank>")
            return
        
        banks = search_object(self.args, typeclass="world.banking.rooms.BankRoom")
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

    Deposits the specified amount of the specified currency (guilders/doubloons) into your account at the specified bank.
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
        
        banks = search_object(bank_name, typeclass="world.banking.rooms.BankRoom")
        if not banks:
            self.caller.msg(f"No bank named '{bank_name}' found.")
            return
        
        bank = banks[0]
        try:
            account = BankAccount.objects.get(bank=bank, account_holder=self.caller)
        except BankAccount.DoesNotExist:
            self.caller.msg(f"You don't have an account at {bank.name}.")
            return
        
        if getattr(self.caller.db, currency) < amount:
            self.caller.msg(f"You don't have enough {currency}.")
            return
        
        setattr(self.caller.db, currency, getattr(self.caller.db, currency) - amount)
        setattr(account, f"{currency}_balance", getattr(account, f"{currency}_balance") + amount)
        account.save()
        
        self.caller.msg(f"Deposited {amount} {currency} into your account at {bank.name}.")

class CmdWithdraw(Command):
    """
    Withdraw money from your bank account.

    Usage:
      withdraw <amount> <currency> <bank>

    Withdraws the specified amount of the specified currency (guilders/doubloons) from your account at the specified bank.
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
        
        banks = search_object(bank_name, typeclass="world.banking.rooms.BankRoom")
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
        setattr(self.caller.db, currency, getattr(self.caller.db, currency) + amount)
        
        self.caller.msg(f"Withdrew {amount} {currency} from your account at {bank.name}.")

class CmdBalance(Command):
    """
    Check your bank account balance.

    Usage:
      balance <bank>

    Shows your account balance at the specified bank.
    """
    key = "balance"
    locks = "cmd:all()"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: balance <bank>")
            return
        
        banks = search_object(self.args, typeclass="world.banking.rooms.BankRoom")
        if not banks:
            self.caller.msg(f"No bank named '{self.args}' found.")
            return
        
        bank = banks[0]
        try:
            account = BankAccount.objects.get(bank=bank, account_holder=self.caller)
        except BankAccount.DoesNotExist:
            self.caller.msg(f"You don't have an account at {bank.name}.")
            return
        
        self.caller.msg(f"Your balance at {bank.name}:")
        self.caller.msg(f"Guilders: {account.guilders_balance}")
        self.caller.msg(f"Doubloons: {account.doubloons_balance}")

class CmdTransfer(Command):
    """
    Transfer money between bank accounts.

    Usage:
      transfer <amount> <currency> <from_bank> to <to_account> at <to_bank>

    Transfers the specified amount of the specified currency from your account at from_bank to the specified account at to_bank.
    """
    key = "transfer"
    locks = "cmd:all()"

    def func(self):
        if not self.args or len(self.args.split()) != 7 or "to" not in self.args or "at" not in self.args:
            self.caller.msg("Usage: transfer <amount> <currency> <from_bank> to <to_account> at <to_bank>")
            return
        
        args = self.args.split()
        amount, currency, from_bank = args[:3]
        to_account, to_bank = args[4], args[6]
        
        try:
            amount = int(amount)
        except ValueError:
            self.caller.msg("Amount must be a number.")
            return
        
        if currency not in ['guilders', 'doubloons']:
            self.caller.msg("Currency must be either 'guilders' or 'doubloons'.")
            return
        
        from_banks = search_object(from_bank, typeclass="world.banking.rooms.BankRoom")
        to_banks = search_object(to_bank, typeclass="world.banking.rooms.BankRoom")
        
        if not from_banks or not to_banks:
            self.caller.msg("One or both banks not found.")
            return
        
        from_bank, to_bank = from_banks[0], to_banks[0]
        
        try:
            from_account = BankAccount.objects.get(bank=from_bank, account_holder=self.caller)
        except BankAccount.DoesNotExist:
            self.caller.msg(f"You don't have an account at {from_bank.name}.")
            return
        
        try:
            to_account = BankAccount.objects.get(bank=to_bank, account_number=to_account)
        except BankAccount.DoesNotExist:
            self.caller.msg(f"Account {to_account} not found at {to_bank.name}.")
            return
        
        if getattr(from_account, f"{currency}_balance") < amount:
            self.caller.msg(f"You don't have enough {currency} in your account at {from_bank.name}.")
            return
        
        # Perform the transfer
        setattr(from_account, f"{currency}_balance", getattr(from_account, f"{currency}_balance") - amount)
        setattr(to_account, f"{currency}_balance", getattr(to_account, f"{currency}_balance") + amount)
        from_account.save()
        to_account.save()
        
        self.caller.msg(f"Transferred {amount} {currency} from your account at {from_bank.name} to account {to_account.account_number} at {to_bank.name}.")