from django.core.management.base import BaseCommand
from django.db.models import Q
import logging
from messages.models import Message

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--days',
                    action='store_true',
                    dest='days',
                    default=30,
                    help='Days of history of threads to process'),
    )
    def handle(self, *args, **kwargs):
        for thread in set(Message.objects.filter(created__gt=datetime.datetime.now() - datetime.timedelta(days=kwargs['days']), thread__isnull=False).values_list('thread', flat=True)):
            messages = Message.objects.filter(Q(thread=thread) | Q(id=thread), deleted_for_user=False).order_by('-created')
            if messages.count() > 0:
                messages.update(has_reply_for_user = True)
                last_message = messages[0]
                last_message.has_reply_for_user = False
                last_message.save()
            messages = Message.objects.filter(Q(thread=thread) | Q(id=thread), deleted_for_author=False).order_by('-created')
            if messages.count() > 0:
                messages.update(has_reply_for_author = True)
                last_message = messages[0]
                last_message.has_reply_for_author = False
                last_message.save()
