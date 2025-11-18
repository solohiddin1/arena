from logging import config
import logging
import os
from rest_framework import status
from rest_framework.response import Response

from apps.shared.enum import ResultCodes, ResultMessages
from html.parser import HTMLParser
import json
from typing import Any, Dict, List
import datetime

from arena.settings import BASE_DIR


def SuccessResponse(result=None):
    return Response({
        "success": True,
        "result": result
    }, status=status.HTTP_200_OK)

def ErrorResponse(result: ResultCodes, message=None):
    if message:
        return Response({
            "success": False,
            "error": {
                "code": result.value,
                "message": message["en"],
                "message_language": {
                    "uz": message["uz"],
                    "en": message["en"],
                    "ru": message["ru"],
                }
            }
        }, status=status.HTTP_200_OK)

    return Response({
        "success": False,
        "error": {
            "code": result.value,
            "message": ResultMessages[result.name]["en"],
            "message_language": {
                "uz": ResultMessages[result.name]["uz"],
                "en": ResultMessages[result.name]["en"],
                "ru": ResultMessages[result.name]["ru"],
            }
        }
    }, status=status.HTTP_200_OK)


def parse_json_items_to_dict_list(raw: Any) -> List[Dict[str, Any]]:
    """Normalize incoming JSON/multipart field into a list of dicts.

    Accepts:
    - str: JSON object or JSON array string
    - dict: returned as a single-item list
    - list/tuple: items may be dicts or JSON strings (object/array)

    Returns a list of dicts. Invalid or unparsable items are skipped.
    """
    items: List[Dict[str, Any]] = []
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                items = [parsed]
            elif isinstance(parsed, list):
                items = [x for x in parsed if isinstance(x, dict)]
        except (ValueError, json.JSONDecodeError):
            items = []
    elif isinstance(raw, (list, tuple)):
        for it in raw:
            if isinstance(it, dict):
                items.append(it)
            elif isinstance(it, str):
                try:
                    p = json.loads(it)
                    if isinstance(p, dict):
                        items.append(p)
                    elif isinstance(p, list):
                        items.extend([x for x in p if isinstance(x, dict)])
                except (ValueError, json.JSONDecodeError):
                    continue
    elif isinstance(raw, dict):
        items = [raw]
    return items


class SimpleHTMLCleaner(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts = []

    def handle_data(self, data):
        self.text_parts.append(data)

    def handle_starttag(self, tag, attrs):
        if tag == 'br':
            self.text_parts.append('\n')

    def handle_endtag(self, tag):
        if tag == 'p':
            self.text_parts.append('\n')

    def get_clean_text(self):
        return ''.join(self.text_parts).strip()


def clean_ckeditor_content(raw_html):
    cleaner = SimpleHTMLCleaner()
    cleaner.feed(raw_html)
    return cleaner.get_clean_text()

import requests
from config.config import settings

TELEGRAM_TOKEN = settings.TELEGRAM_TOKEN
CHAT_ID = settings.CHAT_ID

def send_telegram_message(text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.post(url, data=payload)
    

LOG_DIR = os.path.join(BASE_DIR, "logs")

def get_log_file():
    os.makedirs(LOG_DIR, exist_ok=True)
    """Returns today's log file path."""
    today = datetime.date.today().strftime("%Y-%m-%d")

    return os.path.join(LOG_DIR, f"{today}.log")


def get_logger():
    """Returns a logger writing into today's log file."""
    logger = logging.getLogger("daily_logger")
    logger.setLevel(logging.INFO)

    current_log_file = get_log_file()

    # Agar handler mavjud bo'lsa va fayl o'zgarmagan bo'lsa, qaytadan qo'shmaslik
    if logger.handlers:
        # Fayl o'zgargan bo'lsa (yangi kun), eski handlerni o'chirish
        existing_handler = logger.handlers[0]
        if hasattr(existing_handler, 'baseFilename'):
            if existing_handler.baseFilename != current_log_file:
                logger.handlers.clear()  # Eski handlerni o'chirish

    # Handler yo'q bo'lsa yoki tozalangan bo'lsa, yangi handler qo'shish
    if not logger.handlers:
        handler = logging.FileHandler(current_log_file)
        formatter = logging.Formatter("[{asctime}] {levelname} {message}", style="{")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
    