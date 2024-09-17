from django.db import models
from evennia.utils.idmapper.models import SharedMemoryModel
from evennia.accounts.models import AccountDB
from evennia.utils.utils import lazy_property
from django.utils import timezone

class MailMessage(SharedMemoryModel):
    sender = models.ForeignKey(AccountDB, on_delete=models.CASCADE, related_name='sent_mails')
    recipient = models.ForeignKey(AccountDB, on_delete=models.CASCADE, related_name='received_mails')
    subject = models.CharField(max_length=255)
    message = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    safe = models.BooleanField(default=False)

    def __str__(self):
        return f"Mail from {self.sender.key} to {self.recipient.key} on {self.date_sent}"