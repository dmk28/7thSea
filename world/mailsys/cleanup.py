# in world/mailsys/utils.py

from django.utils import timezone
from .models import MailMessage

def delete_old_mail():
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    old_messages = MailMessage.objects.filter(date_sent__lt=thirty_days_ago, safe=False)
    count = old_messages.count()
    old_messages.delete()
    print(f'Successfully deleted {count} messages older than 30 days')