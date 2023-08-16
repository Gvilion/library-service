from django.conf import settings
from django.utils import timezone

from borrowings.models import Borrowing
from telebot import TeleBot


def get_overdue_borrowings():
    bot = TeleBot(token="6520252403:AAGK5cFu6vjg5PIHYx1UARlurdKGZqetjJU")
    today_date = timezone.datetime.now().date()
    overdue_borrowings = Borrowing.objects.filter(
        actual_return_date__isnull=True, expected_return_date__lt=today_date
    )
    if overdue_borrowings.exists():
        for borrowing in overdue_borrowings:
            bot.send_message(
                chat_id=settings.TELEGRAM_CHAT_ID,
                text=f"{borrowing.user.email} has not returned '{borrowing.book.title}' book by {borrowing.book.author}"
            )
    else:
        bot.send_message(chat_id=-1001938535750, text="No borrowings overdue today!")
