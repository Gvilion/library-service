from library_service import settings
from telebot import TeleBot
from borrowings.models import Borrowing
from payment.models import Payment

bot = TeleBot(token=settings.TELEGRAM_BOT_TOKEN)


def send_message_of_borrowing_creation(borrowing: Borrowing) -> None:
    message = (f"📒CREATE NEW BORROWING:📒\n\n"
               f"id: {borrowing.id}\n"
               f"User: {borrowing.user.email}\n"
               f"Book: {borrowing.book.title}\n"
               f"Borrow date: {borrowing.borrow_date}\n"
               f"Actual return date: "
               f"{borrowing.actual_return_date if borrowing.actual_return_date else 'HAVE NOT RETURNED YET'}\n"
               f"Expected return date: {borrowing.expected_return_date}")
    bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=message)


def send_message_borrowing_return_with_payment_success(
        payment: Payment
) -> None:
    message = (f"📗RETURNED THE BORROWING:📗\n\n"
               f"ID: {payment.borrowing.id}\n"
               f"User: {payment.borrowing.user.email}\n"
               f"Book: {payment.borrowing.book.title}\n"
               f"Borrow date: {payment.borrowing.borrow_date}\n"
               f"Actual return date: "
               f"{(payment.borrowing.actual_return_date if payment.borrowing.actual_return_date else 'HAVE NOT RETURNED YET')}\n"
               f"Expected return date: {payment.borrowing.expected_return_date}\n\n"
               f"Payment status: ✅\n"
               f"Payment for borrowing: {payment.money_to_pay} $")
    bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=message)
