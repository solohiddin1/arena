from celery import shared_task
from apps.shared.utils import send_telegram_message

@shared_task
def send_telegram_message_celery(text: str):
    send_telegram_message(text)