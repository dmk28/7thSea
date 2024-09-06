from evennia import DefaultRoom
from world.banking.models import Bank
from world.banking.cmdset import BankingCmdSet

class BankRoom(DefaultRoom):
    def at_object_creation(self):
        super().at_object_creation()
        self.db.bank = None

    def link_bank(self, bank_name):
        bank, created = Bank.objects.get_or_create(name=bank_name)
        self.db.bank = bank

    def get_bank(self):
        return self.db.bank

    def at_object_receive(self, moved_obj, source_location, **kwargs):
        super().at_object_receive(moved_obj, source_location, **kwargs)
        if moved_obj.has_account:
            moved_obj.msg(f"Welcome to {self.db.bank.name if self.db.bank else 'the bank'}!")
            moved_obj.cmdset.add(BankingCmdSet())

    def at_object_leave(self, moved_obj, target_location, **kwargs):
        super().at_object_leave(moved_obj, target_location, **kwargs)
        if moved_obj.has_account:
            moved_obj.cmdset.delete(BankingCmdSet)