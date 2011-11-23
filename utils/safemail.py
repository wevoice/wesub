"""Email backend that sends email to both file based and smtp backends.
Loops through all recipients (to, bcc, cc) and removes all non white listed
addresses before sending through smtp.
Requires the setting:
EMAIL_NOTIFICATION_RECEIVERS = (sequence of emails )
This way, only unisubs crew will ever receive notifications.
"""


from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend as SmtpBackend
from django.core.mail.backends.filebased import EmailBackend as FileBackend


class InternalOnlyBackend(object):
    def __init__(self, *args, **kwargs):
        self.file_backend = FileBackend(*args, **kwargs) 
        self.smtp_backend = SmtpBackend(*args, **kwargs )
        self.white_listed_addresses = getattr(settings, "EMAIL_NOTIFICATION_RECEIVERS", [])

    def get_whitelisted(self, addresses):
        return [x for x in addresses if x in self.white_listed_addresses]
        
    def send_messages(self, email_messages):
        self.file_backend.send_messages(email_messages)
        for message in email_messages:
            message.to = self.get_whitelisted(message.to)
            message.bcc = self.get_whitelisted(message.bcc)
            message.cc = self.get_whitelisted(message.cc)
        self.smtp_backend.send_messages(email_messages)
            
            
            
