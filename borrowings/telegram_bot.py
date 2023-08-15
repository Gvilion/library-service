from library_service import settings
from telebot import TeleBot
from borrowings.models import Borrowing


bot = TeleBot(token=settings.TELEGRAM_BOT_TOKEN)


def send_message_of_borrowing_creation(borrowing: Borrowing) -> None:
    message = (f"📒CREATE NEW BORROWING:📒\n\n"
               f"User: {borrowing.user.email}\n"
               f"Book: {borrowing.book.title}\n"
               f"Borrow date: {borrowing.borrow_date}\n"
               f"Actual return date: {borrowing.actual_return_date if borrowing.actual_return_date else 'HAVE NOT RETURNED YET'}\n"
               f"Expected return date: {borrowing.expected_return_date}")
    bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=message)


def send_message_of_borrowing_return(borrowing: Borrowing) -> None:
    message = (f"📗RETURNED THE BORROWING:📗\n\n"
               f"User: {borrowing.user.email}\n"
               f"Book: {borrowing.book.title}\n"
               f"Borrow date: {borrowing.borrow_date}\n"
               f"Actual return date: {borrowing.actual_return_date if borrowing.actual_return_date else 'HAVE NOT RETURNED YET'}\n"
               f"Expected return date: {borrowing.expected_return_date}")
    bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=message)
