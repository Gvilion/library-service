from dispatch import receiver
from django.db.models.signals import post_save
from django.dispatch import Signal
from .models import Borrowing
from .telegram_bot import send_message_of_borrowing_creation

new_borrowing_created = Signal()


@receiver(post_save, sender=Borrowing)
def send_new_borrowing_notification(instance, **kwargs):
    send_message_of_borrowing_creation(instance)
