from evennia import Command
from evennia.utils import evtable
from evennia.utils.utils import time_format
from django.utils import timezone
from evennia.commands.default.muxcommand import MuxCommand
from world.mailsys.models import MailMessage
from django.utils.timezone import localtime

class CmdMail(MuxCommand):
    """
    Send and read mail

    Usage:
    @mail = <subject>/<message>
    @mail <player> = <subject>/<message>
    @mail/read [<id>]
    @mail/delete <id>
    @mail/unread <id>
    @mail/sent
    @mail/safe
    @mail/list
    Switches:
    read - Read a message or list all messages
    delete - Delete a message
    unread - Mark a message as unread
    sent - List sent messages
    safe - sets a @mail as safe
    list - List all received messages.  
    """

    key = "@mail"
    aliases = ["mail", "+mail"]
    locks = "cmd:all()"
    switches = ["read", "delete", "unread", "sent", "safe"]

    def func(self):
        if not self.args and not self.switches:
            self.caller.msg("Usage: @mail <player> = <subject>/<message>")
            return

        if not self.switches:
            self.send_mail()
        elif "read" in self.switches:
            self.read_mail()
        elif "delete" in self.switches:
            self.delete_mail()
        elif "unread" in self.switches:
            self.mark_unread()
        elif "sent" in self.switches:
            self.list_sent_mail()
        elif "safe" in self.switches:
            self.mark_safe()
        elif "list" in self.switches:
            self.list_mail()

    def send_mail(self):
        if "=" not in self.args:
            self.caller.msg("Usage: @mail <player> = <subject>/<message>")
            return
        recipients, content = self.args.split("=", 1)
        recipients = recipients.strip()
        if "/" not in content:
            self.caller.msg("You must specify a subject and a message, separated by '/'.")
            return
        subject, body = content.split("/", 1)
        subject = subject.strip()
        body = body.strip()

        if not recipients:
            recipients = [self.caller]
        else:
            recipients = recipients.split(",")
            recipients = [self.caller.search(recipient.strip()) for recipient in recipients]
            recipients = [r for r in recipients if r]

        if not recipients:
            self.caller.msg("No valid recipients found.")
            return

        for recipient in recipients:
            if not recipient.account:
                self.caller.msg(f"Cannot send mail to {recipient.key}: no valid account found.")
                continue
            try:
                new_message = MailMessage.objects.create(
                    sender=self.caller.account,
                    recipient=recipient.account,
                    subject=subject,
                    message=body
                )
                if not hasattr(recipient.db, 'mails') or recipient.db.mails is None:
                    recipient.db.mails = []
                recipient.db.mails.append(new_message.id)
                self.caller.msg(f"Mail sent to {recipient.key}.")
            except Exception as e:
                self.caller.msg(f"Error sending mail to {recipient.key}: {str(e)}")

        self.caller.msg("Mail sending process completed.")

    def list_mail(self):
        if not hasattr(self.caller.db, 'mails'):
            self.caller.db.mails = []
        
        messages = MailMessage.objects.filter(id__in=self.caller.db.mails).order_by('-date_sent')
        
        if not messages:
            self.caller.msg("You have no messages.")
            return

        table = evtable.EvTable("ID", "From", "Subject", "Date", "Read", "Safe", border="cells")
        for msg in messages:
            table.add_row(
                msg.id,
                msg.sender.username,
                msg.subject,
                time_format(msg.date_sent, "%Y-%m-%d %H:%M"),
                "Yes" if msg.read else "No"
                "Yes" if msg.safe else "No"
            )
        self.caller.msg(str(table))

    def read_mail(self):
        if not self.args:
            return self.list_mail()
        try:
            mail_id = int(self.args)
            message = MailMessage.objects.get(id=mail_id, recipient=self.caller.account)
            
            # Create a table for metadata
            metadata_table = evtable.EvTable(border="table", width=78)
            metadata_table.add_row("|555From|n:", message.sender.username)
            metadata_table.add_row("|555To|n:", message.recipient.username)
            metadata_table.add_row("|555Subject|n:", message.subject)
            metadata_table.add_row("|555Sent|n:", localtime(message.date_sent).strftime('%Y-%m-%d %H:%M'))
            
            # Create a separator
            separator = "-" * 78
            
            # Format the message content
            formatted_message = f"\n{message.message}\n"
            
            # Combine all parts
            full_message = (
                f"{metadata_table}"
                f"{formatted_message}"
                f"{separator}"
            )
            
            self.caller.msg(full_message)
            
            message.read = True
            message.save()
        except (ValueError, MailMessage.DoesNotExist):
            self.caller.msg("Message not found.")
    def delete_mail(self):
        try:
            mail_id = int(self.args)
            message = MailMessage.objects.get(id=mail_id, recipient=self.caller.account)
            message.delete()
            if hasattr(self.caller.db, 'mails'):
                self.caller.db.mails.remove(mail_id)
            self.caller.msg("Message deleted.")
        except (ValueError, MailMessage.DoesNotExist):
            self.caller.msg("Message not found.")

    def mark_unread(self):
        try:
            mail_id = int(self.args)
            message = MailMessage.objects.get(id=mail_id, recipient=self.caller.account)
            message.read = False
            message.save()
            self.caller.msg("Message marked as unread.")
        except (ValueError, MailMessage.DoesNotExist):
            self.caller.msg("Message not found.")

    def list_sent_mail(self):
        messages = MailMessage.objects.filter(sender=self.caller.account).order_by('-date_sent')
        
        if not messages:
            self.caller.msg("You haven't sent any messages.")
            return

        table = evtable.EvTable("ID", "To", "Subject", "Date", border="cells")
        for msg in messages:
            table.add_row(
                msg.id,
                msg.recipient.username,
                msg.subject,
                time_format(msg.date_sent, "%Y-%m-%d %H:%M")
            )
        self.caller.msg(str(table))
    def list_mail(self):
        messages = MailMessage.objects.filter(recipient=self.caller.account).order_by('-date_sent')
        
        if not messages:
            self.caller.msg("You have no messages.")
            return

        table = evtable.EvTable("ID", "From", "Subject", "Date", "Read", "Safe", border="cells")
        for msg in messages:
            table.add_row(
                msg.id,
                msg.sender.username,
                msg.subject[:30],  # Limit subject to 30 characters
                localtime(msg.date_sent).strftime('%Y-%m-%d %H:%M'),
                "Yes" if msg.read else "No",
                "Yes" if msg.safe else "No"
            )
        self.caller.msg(str(table))
    def mark_safe(self):
        if not self.args:
            self.caller.msg("Usage: @mail/safe <id>")
            return
        try:
            mail_id = int(self.args)
            message = MailMessage.objects.get(id=mail_id, recipient=self.caller.account)
            message.safe = True
            message.save()
            self.caller.msg(f"Message {mail_id} has been marked as safe.")
        except (ValueError, MailMessage.DoesNotExist):
            self.caller.msg("Message not found.")