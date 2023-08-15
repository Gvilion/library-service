from library_service import settings
from telebot import TeleBot
from borrowings.models import Borrowing


def send_message_of_borrowing_creation(borrowing: Borrowing) -> None:
    bot = TeleBot(token=settings.TELEGRAM_BOT_TOKEN)
    message = (f"Create new borrowing:\n"
               f"User: {borrowing.user.email}\n"
               f"Book: {borrowing.book.title}\n"
               f"Borrow date: {borrowing.borrow_date}\n"
               f"Actual return date: {borrowing.actual_return_date}\n"
               f"Expected return date: {borrowing.expected_return_date}")
    bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=message)
