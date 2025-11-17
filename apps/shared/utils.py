from rest_framework import status
from rest_framework.response import Response

from apps.shared.enum import ResultCodes, ResultMessages
from html.parser import HTMLParser
import json
from typing import Any, Dict, List


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
