from dispatch import receiver
from django.db.models.signals import post_save
from django.dispatch import Signal
from .models import Borrowing
from .telegram_bot import send_message_of_borrowing_creation, send_message_of_borrowing_return

new_borrowing_created = Signal()


@receiver(post_save, sender=Borrowing)
def send_new_borrowing_notification(instance, created, **kwargs):
    if created:
        send_message_of_borrowing_creation(instance)


@receiver(post_save, sender=Borrowing)
def send_returned_borrowing_notification(instance, created, **kwargs):
    if not created and instance.actual_return_date:
        send_message_of_borrowing_return(instance)
